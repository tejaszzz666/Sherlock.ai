# backend/detectors/trust_fusion.py

import numpy as np

class TemporalTrustFusion:
    """
    Combines Eye physics, Lip physics, Face stability into per-frame
    and per-video trust scores for deepfake detection.
    """

    def __init__(self,
                 eye_weight=0.3,
                 lip_weight=0.3,
                 face_weight=0.4,
                 min_frames=10):
        self.eye_weight = eye_weight
        self.lip_weight = lip_weight
        self.face_weight = face_weight
        self.min_frames = min_frames

        self.frame_scores = []

    def compute_frame_trust(self, eye_verdict, lip_verdict, face_stability):
        """
        Convert individual metrics into a 0-1 score
        """
        # Eye score
        if eye_verdict == "NORMAL":
            eye_score = 1.0
        elif eye_verdict == "SUSPICIOUS":
            eye_score = 0.5
        else:  # UNSTABLE / UNKNOWN
            eye_score = 0.2

        # Lip score
        if lip_verdict == "NORMAL":
            lip_score = 1.0
        elif lip_verdict == "SUSPICIOUS":
            lip_score = 0.5
        else:
            lip_score = 0.2

        # Face stability score (0-1)
        face_score = max(0.0, min(1.0, 1.0 - face_stability))  # jitter → less trust

        # Weighted frame trust
        frame_trust = (
            self.eye_weight * eye_score +
            self.lip_weight * lip_score +
            self.face_weight * face_score
        )
        self.frame_scores.append(frame_trust)
        return frame_trust

    def compute_video_trust(self):
        """
        Aggregate per-frame trust scores → video trust score & verdict
        """
        if len(self.frame_scores) < self.min_frames:
            return {"trust_score": None, "verdict": "UNKNOWN"}

        avg_trust = np.mean(self.frame_scores) * 100  # 0-100 scale

        # Thresholds (customizable)
        if avg_trust > 70:
            verdict = "REAL"
        elif avg_trust < 40:
            verdict = "FAKE"
        else:
            verdict = "UNKNOWN"

        return {"trust_score": avg_trust, "verdict": verdict}
