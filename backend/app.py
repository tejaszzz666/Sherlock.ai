"""
Sherlock.ai - Main API Server
FastAPI backend with deepfake detection endpoints
"""

import json
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io

# Local imports
from config import get_settings
from core.logging import setup_logging, get_logger
from core.security import FileValidator, create_image_validator, create_video_validator
from api.models import (
    HealthResponse,
    ImageDetectionResponse,
    VideoDetectionResponse,
    ErrorResponse
)
from predict_utils import predict_image_phase6

# ============ Configuration ============
settings = get_settings()
logger = setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE,
    log_dir=settings.BASE_DIR
)

# ============ Global State ============
app_state = {
    "models_loaded": False,
    "resnet_model": None,
    "efficient_model": None,
    "feature_model": None,
    "class_map": None,
    "maha_stats": None
}


# ============ Lifespan Events ============
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load models on startup, cleanup on shutdown"""
    
    logger.info("🚀 Sherlock.ai starting up...")
    
    # Validate model files exist
    if not settings.validate_models():
        logger.error("❌ Required model files not found!")
        logger.error(f"Expected models in: {settings.MODEL_DIR}")
        logger.warning("⚠️  API will start but detection endpoints will fail")
    else:
        logger.info("✅ Model files found")
        
        try:
            # Load models
            logger.info("Loading ML models...")
            
            with torch.no_grad():
                # ResNet18 classifier
                resnet_model = torch.hub.load(
                    "pytorch/vision:v0.14.0",
                    "resnet18",
                    weights=None
                )
                resnet_model.fc = nn.Linear(resnet_model.fc.in_features, 2)
                resnet_model.load_state_dict(
                    torch.load(settings.MODEL_PATH, map_location="cpu")
                )
                resnet_model.eval()
                app_state["resnet_model"] = resnet_model
                logger.info("✅ ResNet18 loaded")
                
                # EfficientNet-B0 classifier
                efficient_model = torch.hub.load(
                    "pytorch/vision:v0.14.0",
                    "efficientnet_b0",
                    weights=None
                )
                efficient_model.classifier[1] = nn.Linear(
                    efficient_model.classifier[1].in_features, 2
                )
                efficient_model.load_state_dict(
                    torch.load(settings.MODEL_PATH, map_location="cpu"),
                    strict=False
                )
                efficient_model.eval()
                app_state["efficient_model"] = efficient_model
                logger.info("✅ EfficientNet-B0 loaded")
                
                # Feature extractor for Mahalanobis
                feature_model = torch.hub.load(
                    "pytorch/vision:v0.14.0",
                    "resnet18",
                    weights=None
                )
                feature_model.fc = nn.Identity()
                feature_model.load_state_dict(
                    torch.load(settings.MODEL_PATH, map_location="cpu"),
                    strict=False
                )
                feature_model.eval()
                app_state["feature_model"] = feature_model
                logger.info("✅ Feature extractor loaded")
            
            # Load metadata
            with open(settings.CLASS_MAP_PATH, "r") as f:
                app_state["class_map"] = json.load(f)
            logger.info("✅ Class map loaded")
            
            with open(settings.MAHA_PATH, "r") as f:
                app_state["maha_stats"] = json.load(f)
            logger.info("✅ Mahalanobis statistics loaded")
            
            app_state["models_loaded"] = True
            logger.info("🎉 All models loaded successfully!")
            
        except Exception as e:
            logger.error(f"❌ Failed to load models: {e}")
            logger.error("⚠️  Detection endpoints will not work")
    
    yield
    
    # Cleanup
    logger.info("👋 Sherlock.ai shutting down...")


# ============ FastAPI App ============
app = FastAPI(
    title="Sherlock.ai",
    description="AI-powered deepfake detection system using multi-phase analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ Exception Handlers ============
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler"""
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTPException",
            "message": exc.detail,
            "detail": None
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else None
        }
    )


# ============ Routes ============

@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return {
        "status": "alive",
        "version": "1.0.0",
        "models_loaded": app_state["models_loaded"]
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy" if app_state["models_loaded"] else "degraded",
        "version": "1.0.0",
        "models_loaded": app_state["models_loaded"]
    }


@app.post("/detect-image", response_model=ImageDetectionResponse)
async def detect_image(file: UploadFile = File(...)):
    """
    Detect if an image is real or AI-generated
    
    Args:
        file: Image file (JPEG, PNG, WebP)
        
    Returns:
        Detection result with verdict and confidence scores
    """
    
    if not app_state["models_loaded"]:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Service unavailable."
        )
    
    # Validate file
    validator = create_image_validator(
        settings.MAX_IMAGE_SIZE_MB,
        settings.ALLOWED_IMAGE_TYPES
    )
    
    is_valid, error_msg = await validator.validate_file(file, check_magic=True)
    if not is_valid:
        logger.warning(f"File validation failed: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Parse image
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        logger.error(f"Failed to parse image: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")
    
    # Sanitize filename
    safe_filename = validator.sanitize_filename(file.filename or "upload.jpg")
    
    # Run detection
    try:
        class_map = app_state["class_map"]
        maha_stats = app_state["maha_stats"]
        
        real_mean = np.array(maha_stats["real_mean"])
        fake_mean = np.array(maha_stats["fake_mean"])
        inv_cov = np.linalg.inv(np.array(maha_stats["cov"]))
        
        result = predict_image_phase6(
            image=image,
            filename=safe_filename,
            upload_dir=settings.UPLOAD_DIR,
            unknown_dir=settings.UNKNOWN_DIR,
            heatmap_dir=settings.HEATMAP_DIR,
            resnet_model=app_state["resnet_model"],
            efficient_model=app_state["efficient_model"],
            feature_model=app_state["feature_model"],
            REAL_INDEX=class_map["real"],
            FAKE_INDEX=class_map["fake"],
            real_mean=real_mean,
            fake_mean=fake_mean,
            inv_cov=inv_cov,
            TEMPERATURE=settings.TEMPERATURE
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Image detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@app.post("/detect-video", response_model=VideoDetectionResponse)
async def detect_video(file: UploadFile = File(...)):
    """
    Detect if a video is real or AI-generated using frame-by-frame analysis
    
    Args:
        file: Video file (MP4, WebM, AVI, MOV)
        
    Returns:
        Detection result with per-frame analysis and temporal trust scores
    """
    
    if not app_state["models_loaded"]:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Service unavailable."
        )
    
    # Validate file
    validator = create_video_validator(
        settings.MAX_VIDEO_SIZE_MB,
        settings.ALLOWED_VIDEO_TYPES
    )
    
    is_valid, error_msg = await validator.validate_file(file, check_magic=False)
    if not is_valid:
        logger.warning(f"File validation failed: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Sanitize filename
    safe_filename = validator.sanitize_filename(file.filename or "upload.mp4")
    temp_video_path = settings.UPLOAD_DIR / safe_filename
    
    # Save video temporarily
    try:
        await validator.save_upload_file(file, temp_video_path)
    except Exception as e:
        logger.error(f"Failed to save video: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save video: {str(e)}")
    
    # Run video detection
    try:
        # Import video_detect module
        from video_detect import analyze_video
        
        class_map = app_state["class_map"]
        maha_stats = app_state["maha_stats"]
        
        real_mean = np.array(maha_stats["real_mean"])
        fake_mean = np.array(maha_stats["fake_mean"])
        inv_cov = np.linalg.inv(np.array(maha_stats["cov"]))
        
        video_result = analyze_video(
            video_path=str(temp_video_path),
            upload_dir=settings.UPLOAD_DIR,
            unknown_dir=settings.UNKNOWN_DIR,
            heatmap_dir=settings.HEATMAP_DIR,
            resnet_model=app_state["resnet_model"],
            efficient_model=app_state["efficient_model"],
            feature_model=app_state["feature_model"],
            REAL_INDEX=class_map["real"],
            FAKE_INDEX=class_map["fake"],
            real_mean=real_mean,
            fake_mean=fake_mean,
            inv_cov=inv_cov,
            smoothing_window=settings.SMOOTHING_WINDOW
        )
        
        return video_result
        
    except Exception as e:
        logger.error(f"Video detection failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
        
    finally:
        # Cleanup
        if temp_video_path.exists():
            try:
                temp_video_path.unlink()
                logger.debug(f"Deleted temporary video: {safe_filename}")
            except Exception as e:
                logger.warning(f"Failed to delete temp video: {e}")


# ============ Run Server ============
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.BACKEND_RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
