"""
Sherlock.ai - Image Prediction Utilities
Phase 6 Detection with Multi-Model Voting & Mahalanobis OOD
"""

import os
import math
import shutil
import numpy as np
import torch
from pathlib import Path
from torchvision import transforms
from typing import Dict, Any, Optional

from core.logging import get_logger

logger = get_logger(__name__)


def predict_image_phase6(
    image,
    filename: str,
    upload_dir: Path,
    unknown_dir: Path,
    heatmap_dir: Path,
    resnet_model: torch.nn.Module,
    efficient_model: torch.nn.Module,
    feature_model: torch.nn.Module,
    REAL_INDEX: int = 0,
    FAKE_INDEX: int = 1,
    inv_cov: Optional[np.ndarray] = None,
    real_mean: Optional[np.ndarray] = None,
    fake_mean: Optional[np.ndarray] = None,
    OOD_THRESH: float = 200.0,
    TEMPERATURE: float = 2.0
) -> Dict[str, Any]:
    """
    Predict if an image is real or AI-generated using Phase 6 logic
    
    Args:
        image: PIL Image object
        filename: Original filename
        upload_dir: Directory for temporary uploads
        unknown_dir: Directory for uncertain predictions
        heatmap_dir: Directory for heatmaps (unused currently)
        resnet_model: ResNet18 classifier
        efficient_model: EfficientNet-B0 classifier
        feature_model: Feature extractor for Mahalanobis
        REAL_INDEX: Index of 'real' class
        FAKE_INDEX: Index of 'fake' class
        inv_cov: Inverse covariance matrix for Mahalanobis
        real_mean: Mean features for real class
        fake_mean: Mean features for fake class
        OOD_THRESH: Out-of-distribution threshold
        TEMPERATURE: Temperature scaling for calibration
        
    Returns:
        Dictionary with verdict, trust_score, probabilities, etc.
    """
    
    logger.info(f"Processing image: {filename}")
    
    # Image preprocessing
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            [0.485, 0.456, 0.406],
            [0.229, 0.224, 0.225]
        )
    ])
    
    # Save temporary copy
    temp_path = upload_dir / filename
    try:
        image.save(temp_path)
    except Exception as e:
        logger.error(f"Failed to save image {filename}: {e}")
        raise
    
    # -------- Model Predictions --------
    try:
        with torch.no_grad():
            x = transform(image).unsqueeze(0)
            
            # ResNet prediction
            logits_resnet = resnet_model(x)
            probs_resnet = torch.softmax(logits_resnet / TEMPERATURE, dim=1)[0]
            
            # EfficientNet prediction
            logits_effi = efficient_model(x)
            probs_effi = torch.softmax(logits_effi / TEMPERATURE, dim=1)[0]
            
            logger.debug(
                f"ResNet probs: Real={probs_resnet[REAL_INDEX]:.4f}, "
                f"Fake={probs_resnet[FAKE_INDEX]:.4f}"
            )
            logger.debug(
                f"EfficientNet probs: Real={probs_effi[REAL_INDEX]:.4f}, "
                f"Fake={probs_effi[FAKE_INDEX]:.4f}"
            )
    
    except Exception as e:
        logger.error(f"Model inference failed: {e}")
        raise
    
    # -------- Ensemble Voting --------
    vote_real = int(probs_resnet[REAL_INDEX] > probs_resnet[FAKE_INDEX]) + \
                int(probs_effi[REAL_INDEX] > probs_effi[FAKE_INDEX])
    
    real_prob = float((probs_resnet[REAL_INDEX] + probs_effi[REAL_INDEX]) / 2)
    fake_prob = float((probs_resnet[FAKE_INDEX] + probs_effi[FAKE_INDEX]) / 2)
    
    # -------- Entropy (Uncertainty) --------
    entropy = -(
        real_prob * math.log(real_prob + 1e-8) +
        fake_prob * math.log(fake_prob + 1e-8)
    )
    
    # -------- Out-of-Distribution Detection (Mahalanobis) --------
    min_distance = float('inf')
    if inv_cov is not None and real_mean is not None and fake_mean is not None:
        try:
            with torch.no_grad():
                features = feature_model(x).cpu().numpy().squeeze()
            
            d_real = np.sqrt((features - real_mean) @ inv_cov @ (features - real_mean))
            d_fake = np.sqrt((features - fake_mean) @ inv_cov @ (features - fake_mean))
            min_distance = float(min(d_real, d_fake))
            
            logger.debug(f"Mahalanobis distances: Real={d_real:.2f}, Fake={d_fake:.2f}")
            
        except Exception as e:
            logger.warning(f"Mahalanobis calculation failed: {e}")
    
    # -------- Adaptive Decision Thresholds --------
    max_prob = max(real_prob, fake_prob)
    margin = abs(real_prob - fake_prob)
    
    # Dynamic thresholds based on entropy
    CONF = 0.6 + 0.2 * entropy
    MARGIN = 0.25 + 0.3 * entropy
    OOD_LIMIT = np.percentile([min_distance], 85) if min_distance != float('inf') else OOD_THRESH
    
    # -------- Final Verdict --------
    if max_prob >= CONF and margin >= MARGIN and min_distance <= OOD_LIMIT:
        verdict = "REAL" if real_prob > fake_prob else "FAKE"
        logger.info(f"Image {filename} classified as {verdict} (confidence: {max_prob:.2%})")
    else:
        verdict = "UNKNOWN"
        logger.info(f"Image {filename} classified as UNKNOWN (low confidence)")
        
        # Save to unknown directory
        try:
            unknown_path = unknown_dir / filename
            shutil.copy(temp_path, unknown_path)
            logger.debug(f"Saved to unknown_images: {filename}")
        except Exception as e:
            logger.warning(f"Failed to save to unknown_images: {e}")
    
    # -------- Cleanup --------
    try:
        if temp_path.exists():
            temp_path.unlink()
    except Exception as e:
        logger.warning(f"Failed to delete temp file {temp_path}: {e}")
    
    # -------- Build Response --------
    trust_score = int(real_prob * 100) if verdict == "REAL" else int((1 - fake_prob) * 100)
    
    result = {
        "verdict": verdict,
        "trust_score": trust_score,
        "real_probability": round(real_prob, 4),
        "fake_probability": round(fake_prob, 4),
        "entropy": round(entropy, 4),
        "ood_distance": round(min_distance, 2),
        
        # Phase scores for frontend compatibility
        "phase7_score": round(max_prob, 4),
        "phase8_score": None,  # Not applicable for images
        "phase9_score": None   # Not applicable for images
    }
    
    return result
