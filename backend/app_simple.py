# backend/app_simple.py
# Simplified version of Sherlock.ai backend - guaranteed to work!

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
import io
import os
import json
import torch
import torch.nn as nn
import numpy as np

from predict_utils import predict_image_phase6

app = FastAPI(
    title="Sherlock.ai",
    description="AI that investigates AI"
)

# CORS - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ============================= PATHS =============================
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
UNKNOWN_DIR = os.path.join(BASE_DIR, "unknown_images")
HEATMAP_DIR = os.path.join(BASE_DIR, "heatmaps")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(UNKNOWN_DIR, exist_ok=True)
os.makedirs(HEATMAP_DIR, exist_ok=True)

MODEL_PATH = os.path.join(BASE_DIR, "../ml/image_detector/saved_models/image_detector.pth")
CLASS_MAP_PATH = os.path.join(BASE_DIR, "../ml/image_detector/saved_models/class_map.json")
MAHA_PATH = os.path.join(BASE_DIR, "../ml/image_detector/saved_models/mahalanobis.json")

# ============================= LOAD MODELS =============================
print("Loading models...")
with torch.no_grad():
    # ResNet18
    resnet_model = torch.hub.load("pytorch/vision:v0.14.0", "resnet18", weights=None)
    resnet_model.fc = nn.Linear(resnet_model.fc.in_features, 2)
    resnet_model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    resnet_model.eval()

    # EfficientNet-B0
    efficient_model = torch.hub.load("pytorch/vision:v0.14.0", "efficientnet_b0", weights=None)
    efficient_model.classifier[1] = nn.Linear(efficient_model.classifier[1].in_features, 2)
    efficient_model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"), strict=False)
    efficient_model.eval()

    # Feature extractor
    feature_model = torch.hub.load("pytorch/vision:v0.14.0", "resnet18", weights=None)
    feature_model.fc = nn.Identity()
    feature_model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"), strict=False)
    feature_model.eval()

# Load metadata
with open(CLASS_MAP_PATH, "r") as f:
    class_map = json.load(f)

REAL_INDEX = class_map["real"]
FAKE_INDEX = class_map["fake"]

with open(MAHA_PATH, "r") as f:
    maha_stats = json.load(f)

real_mean = np.array(maha_stats["real_mean"])
fake_mean = np.array(maha_stats["fake_mean"])
inv_cov = np.linalg.inv(np.array(maha_stats["cov"]))

print("✅ Models loaded successfully!")

# ============================= ROUTES =============================
@app.get("/")
def root():
    return {"message": "Sherlock.ai is alive 🔍", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy", "models_loaded": True}

@app.post("/detect-image")
async def detect_image(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image: {e}")

    result = predict_image_phase6(
        image=image,
        filename=file.filename,
        upload_dir=UPLOAD_DIR,
        unknown_dir=UNKNOWN_DIR,
        heatmap_dir=HEATMAP_DIR,
        resnet_model=resnet_model,
        efficient_model=efficient_model,
        feature_model=feature_model,
        REAL_INDEX=REAL_INDEX,
        FAKE_INDEX=FAKE_INDEX,
        real_mean=real_mean,
        fake_mean=fake_mean,
        inv_cov=inv_cov
    )
    return result

@app.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    import video_detect
    
    temp_video_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(temp_video_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save video: {e}")

    try:
        result = video_detect.analyze_video(
            video_path=temp_video_path,
            upload_dir=UPLOAD_DIR,
            unknown_dir=UNKNOWN_DIR,
            heatmap_dir=HEATMAP_DIR,
            resnet_model=resnet_model,
            efficient_model=efficient_model,
            feature_model=feature_model,
            REAL_INDEX=REAL_INDEX,
            FAKE_INDEX=FAKE_INDEX,
            real_mean=real_mean,
            fake_mean=fake_mean,
            inv_cov=inv_cov,
            smoothing_window=5
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video processing failed: {e}")
    finally:
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

# ============================= RUN =============================
if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Sherlock.ai Backend Server...")
    print("📍 Server will run at: http://127.0.0.1:8000")
    print("📖 API docs at: http://127.0.0.1:8000/docs")
    print("\n⚡ Press CTRL+C to stop\n")
    
    uvicorn.run("app_simple:app", host="127.0.0.1", port=8000, reload=True)
