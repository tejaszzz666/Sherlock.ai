# backend/detectors/face_stability.py

import numpy as np

class FaceStabilityAnalyzer:
    """
    Tracks face landmark stability across frames.
    Detects identity drift, landmark jitter, and geometric inconsistency.
    """

    def __init__(self, history_size=15):
        self.history_size = history_size
        self.landmark_history = []

    def _normalize_landmarks(self, landmarks):
        """
        Normalize landmarks for scale + translation invariance
        """
        landmarks = np.array(landmarks, dtype=np.float32)

        center = landmarks.mean(axis=0)
        landmarks -= center

        scale = np.linalg.norm(landmarks.std(axis=0)) + 1e-6
        landmarks /= scale

        return landmarks

    def _compute_drift(self, current, previous):
        """
        Mean Euclidean distance between two landmark sets
        """
        return np.mean(np.linalg.norm(current - previous, axis=1))

    def update(self, landmarks):
        """
        Call once per frame with detected landmarks

        Returns:
            dict:
            - stability_score (0–100)
            - drift_score
            - verdict (STABLE / UNSTABLE / INSUFFICIENT_DATA)
        """

        if landmarks is None or len(landmarks) == 0:
            return {
                "stability_score": 0,
                "drift_score": None,
                "verdict": "NO_FACE"
            }

        norm_landmarks = self._normalize_landmarks(landmarks)

        if len(self.landmark_history) > 0:
            prev = self.landmark_history[-1]
            drift = self._compute_drift(norm_landmarks, prev)
        else:
            drift = 0.0

        self.landmark_history.append(norm_landmarks)

        if len(self.landmark_history) > self.history_size:
            self.landmark_history.pop(0)

        # ---------------- Verdict Logic ----------------
        if len(self.landmark_history) < 5:
            return {
                "stability_score": 100,
                "drift_score": drift,
                "verdict": "INSUFFICIENT_DATA"
            }

        avg_drift = np.mean([
            self._compute_drift(self.landmark_history[i],
                                self.landmark_history[i - 1])
            for i in range(1, len(self.landmark_history))
        ])

        # 🔬 These thresholds are empirical & realistic
        if avg_drift < 0.015:
            verdict = "STABLE"
            stability_score = 95
        elif avg_drift < 0.035:
            verdict = "SUSPICIOUS"
            stability_score = 65
        else:
            verdict = "UNSTABLE"
            stability_score = 30

        return {
            "stability_score": stability_score,
            "drift_score": float(avg_drift),
            "verdict": verdict
        }
