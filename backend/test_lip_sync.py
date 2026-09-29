import cv2
from detectors.face_tracker import FaceTracker
from detectors.lip_sync import LipSyncAnalyzer

cap = cv2.VideoCapture(0)
tracker = FaceTracker()
lip_analyzer = LipSyncAnalyzer()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    face = tracker.process_frame(frame)

    if face.get("face_found"):
        lip_landmarks = [face["landmarks"][i] for i in LipSyncAnalyzer.OUTER_LIPS_IDX]
        result = lip_analyzer.update(lip_landmarks)
        text = f'{result["verdict"]} | Mouth: {result["openness"]:.2f} | Motion: {result["motion"]:.3f}'
        cv2.putText(frame, text, (20, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    frame = tracker.draw_debug(frame, face)
    cv2.imshow("Phase-8 Step-4 – Lip Sync Physics", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
