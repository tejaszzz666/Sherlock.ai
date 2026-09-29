import cv2
from detectors.face_tracker import FaceTracker

cap = cv2.VideoCapture(0)
tracker = FaceTracker()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    data = tracker.process_frame(frame)
    frame = tracker.draw_debug(frame, data)

    cv2.imshow("Sherlock.ai – Face Tracker", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
