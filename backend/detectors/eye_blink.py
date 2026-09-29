# backend/detectors/eye_blink.py

import numpy as np

class EyeBlinkAnalyzer:
    """
    Eye & Blink physics for detecting deepfake inconsistencies.
    Uses Eye Aspect Ratio (EAR) and blink timing analysis.
    """

    LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
    RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]

    def __init__(self, blink_threshold=0.22, history_size=15):
        self.blink_threshold = blink_threshold  # EAR below = blink
        self.history_size = history_size
        self.ear_history = []
        self.blink_count = 0

    def _eye_aspect_ratio(self, eye_points):
        """
        Compute Eye Aspect Ratio (EAR)
        eye_points: list of 6 (x,y) landmarks
        """
        p = np.array(eye_points, dtype=np.float32)
        # vertical
        A = np.linalg.norm(p[1] - p[5])
        B = np.linalg.norm(p[2] - p[4])
        # horizontal
        C = np.linalg.norm(p[0] - p[3])
        ear = (A + B) / (2.0 * C + 1e-6)
        return ear

    def update(self, left_eye, right_eye):
        """
        Call every frame with eye landmarks.
        Returns dict with:
        - left_ear, right_ear
        - avg_ear
        - blink_detected (bool)
        - verdict (NORMAL / SUSPICIOUS / UNSTABLE)
        """
        if left_eye is None or right_eye is None:
            return {
                "left_ear": None,
                "right_ear": None,
                "avg_ear": None,
                "blink_detected": False,
                "verdict": "NO_FACE"
            }

        left_ear = self._eye_aspect_ratio(left_eye)
        right_ear = self._eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0

        # Detect blink
        blink = avg_ear < self.blink_threshold
        if blink:
            self.blink_count += 1

        self.ear_history.append(avg_ear)
        if len(self.ear_history) > self.history_size:
            self.ear_history.pop(0)

        # Temporal verdict
        mean_ear = np.mean(self.ear_history)
        if mean_ear < 0.18:
            verdict = "UNSTABLE"
        elif mean_ear < 0.22:
            verdict = "SUSPICIOUS"
        else:
            verdict = "NORMAL"

        return {
            "left_ear": left_ear,
            "right_ear": right_ear,
            "avg_ear": avg_ear,
            "blink_detected": blink,
            "verdict": verdict
        }
