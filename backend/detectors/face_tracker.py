import cv2
import mediapipe as mp
import numpy as np


class FaceTracker:
    def __init__(
        self,
        max_num_faces=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    ):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=max_num_faces,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )

    def process_frame(self, frame):
        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.face_mesh.process(rgb)

        if not result.multi_face_landmarks:
            return {"face_found": False}

        landmarks = result.multi_face_landmarks[0]
        points = []

        xs, ys = [], []
        for lm in landmarks.landmark:
            x, y = int(lm.x * w), int(lm.y * h)
            points.append((x, y))
            xs.append(x)
            ys.append(y)

        points = np.array(points)

        bbox = (
            max(0, min(xs)),
            max(0, min(ys)),
            min(w, max(xs)),
            min(h, max(ys)),
        )

        LEFT_EYE = [33, 160, 158, 133, 153, 144]
        RIGHT_EYE = [362, 385, 387, 263, 373, 380]

        return {
            "face_found": True,
            "bbox": bbox,
            "landmarks": points,
            "left_eye": points[LEFT_EYE],
            "right_eye": points[RIGHT_EYE],
        }

    def draw_debug(self, frame, data):
        if not data.get("face_found"):
            return frame

        x1, y1, x2, y2 = data["bbox"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        for x, y in data["left_eye"]:
            cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

        for x, y in data["right_eye"]:
            cv2.circle(frame, (x, y), 2, (0, 0, 255), -1)

        return frame
