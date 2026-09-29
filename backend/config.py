"""
Sherlock.ai - Centralized Configuration
Loads environment variables and provides typed configuration objects
"""

import os
from pathlib import Path
from typing import List
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables"""
    
    # ============ Base Paths ============
    BASE_DIR: Path = Path(__file__).parent
    ROOT_DIR: Path = BASE_DIR.parent
    
    # ============ Server Config ============
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "127.0.0.1")
    # Render (and most PaaS) inject PORT; fall back to BACKEND_PORT for local/HF
    BACKEND_PORT: int = int(os.getenv("PORT") or os.getenv("BACKEND_PORT", "8000"))
    BACKEND_RELOAD: bool = os.getenv("BACKEND_RELOAD", "true").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # ============ CORS ============
    CORS_ORIGINS: List[str] = [
        o.strip().rstrip("/")
        for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173"
        ).split(",")
        if o.strip()
    ]
    
    # ============ Upload Limits ============
    MAX_IMAGE_SIZE_MB: int = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))
    MAX_VIDEO_SIZE_MB: int = int(os.getenv("MAX_VIDEO_SIZE_MB", "100"))
    
    MAX_IMAGE_SIZE_BYTES: int = MAX_IMAGE_SIZE_MB * 1024 * 1024
    MAX_VIDEO_SIZE_BYTES: int = MAX_VIDEO_SIZE_MB * 1024 * 1024
    
    ALLOWED_IMAGE_TYPES: List[str] = os.getenv(
        "ALLOWED_IMAGE_TYPES",
        "image/jpeg,image/png,image/webp"
    ).split(",")
    
    ALLOWED_VIDEO_TYPES: List[str] = os.getenv(
        "ALLOWED_VIDEO_TYPES",
        "video/mp4,video/webm,video/avi,video/mov"
    ).split(",")
    
    # ============ Directories ============
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    UNKNOWN_DIR: Path = BASE_DIR / "unknown_images"
    HEATMAP_DIR: Path = BASE_DIR / "heatmaps"
    
    # ============ Model Paths ============
    MODEL_DIR: Path = ROOT_DIR / os.getenv("MODEL_DIR", "ml/image_detector/saved_models")
    MODEL_FILE: str = os.getenv("MODEL_FILE", "image_detector.pth")
    CLASS_MAP_FILE: str = os.getenv("CLASS_MAP_FILE", "class_map.json")
    MAHALANOBIS_FILE: str = os.getenv("MAHALANOBIS_FILE", "mahalanobis.json")
    
    MODEL_PATH: Path = MODEL_DIR / MODEL_FILE
    CLASS_MAP_PATH: Path = MODEL_DIR / CLASS_MAP_FILE
    MAHA_PATH: Path = MODEL_DIR / MAHALANOBIS_FILE
    
    # ============ Processing Parameters ============
    VIDEO_FRAME_SKIP: int = int(os.getenv("VIDEO_FRAME_SKIP", "30"))
    SMOOTHING_WINDOW: int = int(os.getenv("SMOOTHING_WINDOW", "5"))
    PHASE9_WINDOW: int = int(os.getenv("PHASE9_WINDOW", "5"))
    
    # ============ Detection Thresholds ============
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.6"))
    MARGIN_THRESHOLD: float = float(os.getenv("MARGIN_THRESHOLD", "0.25"))
    ENTROPY_THRESHOLD: float = float(os.getenv("ENTROPY_THRESHOLD", "0.7"))
    OOD_THRESHOLD: float = float(os.getenv("OOD_THRESHOLD", "200.0"))
    TEMPERATURE: float = 2.0  # For model calibration
    
    # ============ Logging ============
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "sherlock.log")
    
    @classmethod
    def ensure_directories(cls):
        """Create required directories if they don't exist"""
        cls.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        cls.UNKNOWN_DIR.mkdir(parents=True, exist_ok=True)
        cls.HEATMAP_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_models(cls) -> bool:
        """Check if all required model files exist"""
        required_files = [cls.MODEL_PATH, cls.CLASS_MAP_PATH, cls.MAHA_PATH]
        missing = [f for f in required_files if not f.exists()]
        
        if missing:
            print(f"⚠️  Missing model files: {[str(f) for f in missing]}")
            return False
        return True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Initialize directories on import
Settings.ensure_directories()
