import cv2
from detectors.face_tracker import FaceTracker
from detectors.lip_sync import LipSyncAnalyzer
from detectors.trust_fusion import TemporalTrustFusion

cap = cv2.VideoCapture(0)
tracker = FaceTracker()
lip_analyzer = LipSyncAnalyzer()
fusion = TemporalTrustFusion()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    face = tracker.process_frame(frame)

    # Eye physics (simplified: face bbox stability)
    if face.get("face_found"):
        # Measure jitter as normalized bbox change
        x1, y1, x2, y2 = face["bbox"]
        face_width = x2 - x1
        face_height = y2 - y1
        face_stability = 1.0 - (face_width * face_height) / (frame.shape[1] * frame.shape[0])

        # Lip physics
        lip_landmarks = [face["landmarks"][i] for i in LipSyncAnalyzer.OUTER_LIPS_IDX]
        lip_result = lip_analyzer.update(lip_landmarks)

        # Eye verdict: assume NORMAL if face stable (placeholder)
        eye_verdict = "NORMAL" if face_stability > 0.8 else "SUSPICIOUS"

        frame_trust = fusion.compute_frame_trust(
            eye_verdict=eye_verdict,
            lip_verdict=lip_result["verdict"],
            face_stability=1.0 - face_stability  # inverse → jitter
        )

        cv2.putText(frame,
                    f'{lip_result["verdict"]} | Frame trust: {frame_trust:.2f}',
                    (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    frame = tracker.draw_debug(frame, face)
    cv2.imshow("Phase-8 Step-5 – Temporal Trust Fusion", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# Video-level verdict
video_trust = fusion.compute_video_trust()
print("=== Video Trust Analysis ===")
print(video_trust)

cap.release()
cv2.destroyAllWindows()
