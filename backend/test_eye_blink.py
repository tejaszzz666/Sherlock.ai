import cv2
from detectors.face_tracker import FaceTracker
from detectors.eye_blink import EyeBlinkAnalyzer

cap = cv2.VideoCapture(0)
tracker = FaceTracker()
eye_analyzer = EyeBlinkAnalyzer()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    face = tracker.process_frame(frame)

    if face.get("face_found"):
        result = eye_analyzer.update(face["left_eye"], face["right_eye"])
        text = f'{result["verdict"]} | EAR: {result["avg_ear"]:.2f} | Blink: {result["blink_detected"]}'
        cv2.putText(frame, text, (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    frame = tracker.draw_debug(frame, face)
    cv2.imshow("Phase-8 Step-3 – Eye & Blink Physics", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
