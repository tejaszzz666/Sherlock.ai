"""
Sherlock.ai - API Response Models
Pydantic models for type-safe API responses
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


# ============ Base Models ============

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")


# ============ Image Detection ============

class ImageDetectionResponse(BaseModel):
    """Response for image detection endpoint"""
    verdict: str = Field(..., description="Final verdict: REAL, FAKE, or UNKNOWN")
    trust_score: int = Field(..., ge=0, le=100, description="Trust score (0-100)")
    real_probability: float = Field(..., ge=0, le=1, description="Probability of being real")
    fake_probability: float = Field(..., ge=0, le=1, description="Probability of being fake")
    entropy: float = Field(..., description="Prediction entropy")
    ood_distance: float = Field(..., description="Out-of-distribution distance")
    
    # Phase scores for frontend
    phase7_score: Optional[float] = Field(None, description="Phase 7 confidence score")
    phase8_score: Optional[float] = Field(None, description="Phase 8 confidence score")
    phase9_score: Optional[float] = Field(None, description="Phase 9 confidence score")
    
    class Config:
        json_schema_extra = {
            "example": {
                "verdict": "REAL",
                "trust_score": 87,
                "real_probability": 0.8745,
                "fake_probability": 0.1255,
                "entropy": 0.4532,
                "ood_distance": 45.23,
                "phase7_score": 0.87,
                "phase8_score": 0.85,
                "phase9_score": 0.89
            }
        }


# ============ Video Detection ============

class FrameAnalysis(BaseModel):
    """Individual frame analysis"""
    frame_id: int = Field(..., description="Frame number")
    verdict: str = Field(..., description="Frame verdict")
    phase8_trust: float = Field(..., ge=0, le=1, description="Phase 8 trust score")
    phase9_trust: float = Field(..., ge=0, le=1, description="Phase 9 trust score")
    real_probability: float = Field(..., ge=0, le=1)
    fake_probability: float = Field(..., ge=0, le=1)
    eye_verdict: str = Field(..., description="Eye blink analysis")
    lip_verdict: str = Field(..., description="Lip sync analysis")
    entropy: Optional[float] = None
    ood_distance: Optional[float] = None


class VideoDetectionResponse(BaseModel):
    """Response for video detection endpoint"""
    phase7_verdict: str = Field(..., description="Phase 7 verdict")
    phase8_verdict: str = Field(..., description="Phase 8 verdict")
    phase9_verdict: str = Field(..., description="Phase 9 verdict (final)")
    
    phase8_trust_score: float = Field(..., ge=0, le=1, description="Phase 8 trust")
    phase9_trust_score: float = Field(..., ge=0, le=1, description="Phase 9 trust")
    
    total_frames: int = Field(..., description="Total frames analyzed")
    frames: List[FrameAnalysis] = Field(..., description="Per-frame analysis")
    
    phase7_distribution: Dict[str, int] = Field(..., description="Phase 7 verdict counts")
    phase8_eyes_distribution: Dict[str, int] = Field(..., description="Eye verdict counts")
    phase8_lips_distribution: Dict[str, int] = Field(..., description="Lip verdict counts")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phase7_verdict": "REAL",
                "phase8_verdict": "REAL",
                "phase9_verdict": "REAL",
                "phase8_trust_score": 0.82,
                "phase9_trust_score": 0.85,
                "total_frames": 120,
                "frames": [],
                "phase7_distribution": {"REAL": 95, "FAKE": 15, "UNKNOWN": 10},
                "phase8_eyes_distribution": {"NORMAL": 100, "SUSPICIOUS": 20},
                "phase8_lips_distribution": {"REAL": 90, "FAKE": 30}
            }
        }


# ============ Error Responses ============

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error message")
    detail: Optional[str] = Field(None, description="Additional details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "ValidationError",
                "message": "File too large",
                "detail": "Maximum file size is 10MB"
            }
        }
