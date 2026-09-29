"""
Sherlock.ai - Video Detection Module
Phase 7-9 Video Analysis with Temporal Trust Fusion
"""

import cv2
import warnings
import numpy as np
from pathlib import Path
from PIL import Image
from collections import Counter, deque
from typing import Dict, Any, List

# Import detectors
from detectors.face_tracker import FaceTracker
from detectors.lip_sync import LipSyncAnalyzer
from detectors.trust_fusion import TemporalTrustFusion

# Import prediction utilities
from predict_utils import predict_image_phase6
from core.logging import get_logger

logger = get_logger(__name__)


def analyze_video(
    video_path: str,
    upload_dir: Path,
    unknown_dir: Path,
    heatmap_dir: Path,
    resnet_model,
    efficient_model,
    feature_model,
    REAL_INDEX: int,
    FAKE_INDEX: int,
    real_mean: np.ndarray,
    fake_mean: np.ndarray,
    inv_cov: np.ndarray,
    smoothing_window: int = 3
) -> Dict[str, Any]:
    """
    Analyze video for deepfake detection using multi-phase approach
    
    Phase 7: Multi-model voting + adaptive thresholds + Mahalanobis OOD
    Phase 8: Face/Eye/Lip tracking + Temporal Trust Fusion
    Phase 9: Sliding-window weighted temporal trust
    
    Args:
        video_path: Path to video file
        upload_dir: Directory for temporary files
        unknown_dir: Directory for uncertain frames
        heatmap_dir: Directory for heatmaps
        resnet_model: ResNet18 classifier
        efficient_model: EfficientNet-B0 classifier
        feature_model: Feature extractor
        REAL_INDEX: Index of 'real' class
        FAKE_INDEX: Index of 'fake' class
        real_mean: Mean features for real class
        fake_mean: Mean features for fake class
        inv_cov: Inverse covariance matrix
        smoothing_window: Window size for trust smoothing
        
    Returns:
        Dictionary with phase verdicts, trust scores, and frame-level analysis
    """
    
    logger.info(f"📹 Analyzing video: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Failed to open video: {video_path}")
        raise RuntimeError(f"Failed to open video: {video_path}")
    
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
    total_frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    FRAME_SKIP = max(1, fps)  # Sample ~1 frame per second
    
    logger.info(f"Video: {fps} FPS, {total_frame_count} total frames, sampling every {FRAME_SKIP} frames")
    
    # Initialize Phase 8 trackers
    face_tracker = FaceTracker()
    lip_analyzer = LipSyncAnalyzer()
    trust_fusion = TemporalTrustFusion()
    
    frame_results: List[Dict[str, Any]] = []
    phase8_trust_window = deque(maxlen=smoothing_window)
    frame_id = 0
    processed_count = 0
    
    # ============ Step 1: Process Frames ============
    logger.info("Processing frames...")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_id % FRAME_SKIP == 0:
            try:
                # Convert frame to PIL Image
                frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                # -------- Phase 7: Image Detection --------
                phase7_info = predict_image_phase6(
                    image=frame_pil,
                    filename=f"frame_{frame_id}.jpg",
                    upload_dir=upload_dir,
                    unknown_dir=unknown_dir,
                    heatmap_dir=heatmap_dir,
                    resnet_model=resnet_model,
                    efficient_model=efficient_model,
                    feature_model=feature_model,
                    REAL_INDEX=REAL_INDEX,
                    FAKE_INDEX=FAKE_INDEX,
                    real_mean=real_mean,
                    fake_mean=fake_mean,
                    inv_cov=inv_cov
                )
                
                # -------- Phase 8: Face/Eye/Lip Analysis --------
                face_data = face_tracker.process_frame(frame)
                
                if face_data.get("face_found"):
                    x1, y1, x2, y2 = face_data["bbox"]
                    face_width = x2 - x1
                    face_height = y2 - y1
                    face_area_norm = (face_width * face_height) / (frame.shape[1] * frame.shape[0])
                    
                    # Lip sync analysis
                    lip_landmarks = [face_data["landmarks"][i] for i in LipSyncAnalyzer.OUTER_LIPS_IDX]
                    lip_result = lip_analyzer.update(lip_landmarks)
                    
                    # Eye verdict (simplified - based on face size)
                    eye_verdict = "NORMAL" if face_area_norm > 0.05 else "SUSPICIOUS"
                    
                    # Compute trust
                    raw_trust = trust_fusion.compute_frame_trust(
                        eye_verdict=eye_verdict,
                        lip_verdict=lip_result["verdict"],
                        face_stability=1.0 - abs(face_area_norm - 0.15)  # Penalty for unusual sizes
                    )
                else:
                    eye_verdict = "UNKNOWN"
                    lip_result = {"verdict": "UNKNOWN"}
                    face_area_norm = None
                    raw_trust = trust_fusion.compute_frame_trust(
                        eye_verdict="UNKNOWN",
                        lip_verdict="UNKNOWN",
                        face_stability=0.5
                    )
                
                # Phase 8 smoothing
                phase8_trust_window.append(raw_trust)
                smoothed_trust = float(np.mean(phase8_trust_window))
                
                # Store frame result
                frame_results.append({
                    "frame_id": frame_id,
                    "verdict": phase7_info["verdict"],
                    "real_probability": phase7_info["real_probability"],
                    "fake_probability": phase7_info["fake_probability"],
                    "entropy": phase7_info["entropy"],
                    "ood_distance": phase7_info["ood_distance"],
                    "phase8_trust": smoothed_trust,
                    "phase9_trust": 0.0,  # Will be computed later
                    "eye_verdict": eye_verdict,
                    "lip_verdict": lip_result["verdict"],
                    "face_stability": face_area_norm
                })
                
                processed_count += 1
                
            except Exception as e:
                logger.warning(f"Error processing frame {frame_id}: {e}")
        
        frame_id += 1
    
    cap.release()
    logger.info(f"Processed {processed_count} frames out of {total_frame_count} total")
    
    # ============ Handle Empty Results ============
    if not frame_results:
        logger.warning("No frames were successfully processed")
        return {
            "phase7_verdict": "UNKNOWN",
            "phase8_verdict": "UNKNOWN",
            "phase8_trust_score": 0.0,
            "phase9_verdict": "UNKNOWN",
            "phase9_trust_score": 0.0,
            "total_frames": 0,
            "frames": [],
            "phase7_distribution": {},
            "phase8_eyes_distribution": {},
            "phase8_lips_distribution": {}
        }
    
    # ============ Step 2: Adaptive Thresholds (Phase 7) ============
    logger.info("Computing adaptive thresholds...")
    
    real_probs = np.array([f["real_probability"] for f in frame_results])
    fake_probs = np.array([f["fake_probability"] for f in frame_results])
    entropies = np.array([f["entropy"] for f in frame_results])
    ood_distances = np.array([f["ood_distance"] for f in frame_results])
    
    CONF_THRESH = max(0.55, np.median(np.maximum(real_probs, fake_probs)))
    MARGIN_THRESH = max(0.15, np.median(np.abs(real_probs - fake_probs)))
    ENTROPY_THRESH = np.percentile(entropies, 65)
    OOD_THRESH = np.median(ood_distances) + 1.5 * (
        np.percentile(ood_distances, 75) - np.percentile(ood_distances, 25)
    )
    
    logger.debug(f"Thresholds: CONF={CONF_THRESH:.3f}, MARGIN={MARGIN_THRESH:.3f}, "
                f"ENTROPY={ENTROPY_THRESH:.3f}, OOD={OOD_THRESH:.2f}")
    
    # Re-classify frames with adaptive thresholds
    for f in frame_results:
        max_prob = max(f["real_probability"], f["fake_probability"])
        margin = abs(f["real_probability"] - f["fake_probability"])
        
        if (max_prob >= CONF_THRESH and 
            margin >= MARGIN_THRESH and 
            f["entropy"] <= ENTROPY_THRESH and 
            f["ood_distance"] <= OOD_THRESH):
            f["verdict"] = "REAL" if f["real_probability"] > f["fake_probability"] else "FAKE"
        else:
            f["verdict"] = "UNKNOWN"
    
    # ============ Step 3: Phase 7 Video Verdict ============
    num_frames = len(frame_results)
    num_fake = sum(1 for f in frame_results if f["verdict"] == "FAKE")
    num_real = sum(1 for f in frame_results if f["verdict"] == "REAL")
    
    if num_fake >= 0.6 * num_frames:
        phase7_video_verdict = "FAKE"
    elif num_real >= 0.6 * num_frames:
        phase7_video_verdict = "REAL"
    else:
        phase7_video_verdict = "UNKNOWN"
    
    logger.info(f"Phase 7 verdict: {phase7_video_verdict} (Real: {num_real}, Fake: {num_fake}, Unknown: {num_frames - num_real - num_fake})")
    
    # ============ Step 4: Phase 8 Video Trust ============
    phase8_trust_scores = [f["phase8_trust"] for f in frame_results]
    video_phase8_trust = float(np.mean(phase8_trust_scores))
    
    if video_phase8_trust > 0.6:
        phase8_video_verdict = "REAL"
    elif video_phase8_trust < 0.4:
        phase8_video_verdict = "FAKE"
    else:
        phase8_video_verdict = "UNKNOWN"
    
    logger.info(f"Phase 8 verdict: {phase8_video_verdict} (Trust: {video_phase8_trust:.2%})")
    
    # ============ Step 5: Phase 8 Distributions ============
    phase7_distribution = dict(Counter(f["verdict"] for f in frame_results))
    phase8_eyes_distribution = dict(Counter(f["eye_verdict"] for f in frame_results))
    phase8_lips_distribution = dict(Counter(f["lip_verdict"] for f in frame_results))
    
    # ============ Step 6: Phase 9 Temporal Trust ============
    logger.info("Computing Phase 9 temporal trust...")
    
    phase9_window = 5
    phase9_trust_scores = []
    
    for i in range(len(frame_results)):
        start = max(0, i - phase9_window + 1)
        window_trusts = [frame_results[j]["phase8_trust"] for j in range(start, i + 1)]
        
        # Weighted average (more recent frames have higher weight)
        weights = np.linspace(0.5, 1.0, len(window_trusts))
        weighted_trust = float(np.average(window_trusts, weights=weights))
        
        phase9_trust_scores.append(weighted_trust)
        frame_results[i]["phase9_trust"] = weighted_trust
    
    video_phase9_trust = float(np.mean(phase9_trust_scores))
    
    if video_phase9_trust > 0.6:
        phase9_verdict = "REAL"
    elif video_phase9_trust < 0.4:
        phase9_verdict = "FAKE"
    else:
        phase9_verdict = "UNKNOWN"
    
    logger.info(f"Phase 9 verdict: {phase9_verdict} (Trust: {video_phase9_trust:.2%})")
    
    # ============ Return Results ============
    return {
        "phase7_verdict": phase7_video_verdict,
        "phase8_verdict": phase8_video_verdict,
        "phase8_trust_score": video_phase8_trust,
        "phase9_verdict": phase9_verdict,
        "phase9_trust_score": video_phase9_trust,
        "total_frames": num_frames,
        "frames": frame_results,
        "phase7_distribution": phase7_distribution,
        "phase8_eyes_distribution": phase8_eyes_distribution,
        "phase8_lips_distribution": phase8_lips_distribution
    }
