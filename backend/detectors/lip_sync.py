# backend/detectors/lip_sync.py

import numpy as np

class LipSyncAnalyzer:
    """
    Lip movement & sync analysis for deepfake detection.
    Uses MediaPipe landmarks to compute mouth openness and motion stability.
    """

    # MediaPipe outer lip landmarks
    OUTER_LIPS_IDX = [61, 291, 0, 17, 78, 308, 13, 14]

    def __init__(self, motion_threshold=0.02, history_size=10):
        self.motion_threshold = motion_threshold
        self.history_size = history_size
        self.mouth_open_history = []

    def _mouth_openness(self, lip_points):
        """
        Compute normalized mouth openness.
        lip_points: list of (x, y) landmarks
        """
        p = np.array(lip_points, dtype=np.float32)
        width = np.linalg.norm(p[0] - p[1])
        height = np.linalg.norm(p[2] - p[3])
        if width == 0:
            return 0.0
        return height / width

    def update(self, lip_landmarks):
        """
        Call every frame with outer lip landmarks
        Returns dict with:
        - openness
        - motion (delta from previous frame)
        - verdict (NORMAL / SUSPICIOUS / UNSTABLE)
        """
        if lip_landmarks is None or len(lip_landmarks) < 4:
            return {"openness": None, "motion": None, "verdict": "NO_FACE"}

        openness = self._mouth_openness(lip_landmarks)
        motion = 0.0

        if self.mouth_open_history:
            motion = abs(openness - self.mouth_open_history[-1])

        self.mouth_open_history.append(openness)
        if len(self.mouth_open_history) > self.history_size:
            self.mouth_open_history.pop(0)

        # Temporal verdict
        mean_motion = np.mean([abs(self.mouth_open_history[i] - self.mouth_open_history[i-1])
                               for i in range(1, len(self.mouth_open_history))])

        if mean_motion > self.motion_threshold * 3:
            verdict = "UNSTABLE"
        elif mean_motion > self.motion_threshold:
            verdict = "SUSPICIOUS"
        else:
            verdict = "NORMAL"

        return {
            "openness": openness,
            "motion": motion,
            "verdict": verdict
        }
