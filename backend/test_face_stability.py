import cv2
from detectors.face_tracker import FaceTracker
from detectors.face_stability import FaceStabilityAnalyzer

cap = cv2.VideoCapture(0)
tracker = FaceTracker()
stability = FaceStabilityAnalyzer()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    face = tracker.process_frame(frame)

    if face.get("face_found"):
        result = stability.update(face["landmarks"])

        text = f'{result["verdict"]} | Stability: {result["stability_score"]}'
        cv2.putText(frame, text, (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    frame = tracker.draw_debug(frame, face)

    cv2.imshow("Phase-8 Step-2 – Face Stability", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
