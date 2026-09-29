# test_video_phase9.py

import os
import numpy as np
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

# ---------------- CONFIG ----------------
VIDEO_FILE = "sample_video.mp4"  # put a small test video in backend/uploads/
video_path = os.path.join(os.path.dirname(__file__), "uploads", VIDEO_FILE)
if not os.path.exists(video_path):
    raise FileNotFoundError(f"Place a test video at {video_path}")

# ---------------- COLORS ----------------
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"

# ---------------- UPLOAD VIDEO ----------------
with open(video_path, "rb") as f:
    response = client.post(
        "/detect-video",
        files={"file": (VIDEO_FILE, f, "video/mp4")}
    )

# ---------------- PROCESS RESULTS ----------------
if response.status_code == 200:
    data = response.json()
    frames = data["frames"]
    total_frames = len(frames)

    # ---------------- VIDEO VERDICTS ----------------
    print("\n" + "="*75)
    print(" 🕵️ Sherlock.ai Video Analysis Dashboard (Phase-9)")
    print("="*75)
    print(f"\nPhase-7 Verdict : {data['phase7_verdict']}")
    print(f"Phase-8 Verdict : {data['phase8_verdict']} (Trust: {round(data['phase8_trust_score'],3)})")
    print(f"Phase-9 Verdict : {data['phase9_verdict']} (Trust: {round(data['phase9_trust_score'],3)})")
    print(f"Total Frames   : {total_frames}\n")

    # ---------------- FRAME DISTRIBUTIONS ----------------
    print("--- Frame Distributions ---")
    print("Phase-7:", data["phase7_distribution"])
    print("Phase-8 Eyes:", data["phase8_eyes_distribution"])
    print("Phase-8 Lips:", data["phase8_lips_distribution"])
    print()

    # ---------------- FIRST 5 FRAMES ----------------
    print("--- First 5 Frame Results ---")
    for frame in frames[:5]:
        print(frame)
    print()

    # ---------------- PHASE-8 SMOOTHED TRUST ----------------
    print("--- Phase-8 Smoothed & Weighted Trust Graph ---")
    max_bar = 50
    alpha = 0.6  # exponential smoothing factor
    smoothed_phase8 = []
    prev_trust = 0.0
    for f in frames:
        current = f.get("phase8_trust", 0.0)
        smoothed = alpha * current + (1 - alpha) * prev_trust
        smoothed_phase8.append(smoothed)
        prev_trust = smoothed

    print(f"{CYAN}{'Frame':>5} | {'Phase-8 Trust Graph':<60} | Trust{RESET}")
    for i, f in enumerate(frames):
        trust = smoothed_phase8[i]
        bar_len = int(trust * max_bar)
        bar = "█" * bar_len + "-" * (max_bar - bar_len)
        eye = f.get("eye_verdict", "UNKNOWN")
        lip = f.get("lip_verdict", "UNKNOWN")
        if eye == "SUSPICIOUS" or lip == "SUSPICIOUS":
            color = RED
        elif eye == "NORMAL" and lip == "NORMAL":
            color = GREEN
        else:
            color = YELLOW
        print(f"{CYAN}{i:03d}{RESET} |{color}{bar}{RESET} {trust:.3f}")

    # ---------------- PHASE-9 TEMPORAL TRUST ----------------
    print("\n--- Phase-9 Temporal Consistency Trust Graph ---")
    phase9_window = 5
    phase9_trust_scores = []
    for i in range(total_frames):
        start = max(0, i - phase9_window + 1)
        window_trusts = [frames[j]["phase8_trust"] for j in range(start, i+1)]
        weights = np.linspace(0.5, 1.0, len(window_trusts))
        weighted_trust = np.average(window_trusts, weights=weights)
        phase9_trust_scores.append(weighted_trust)

    print(f"{MAGENTA}{'Frame':>5} | {'Phase-9 Trust Graph':<60} | Trust{RESET}")
    for i, trust in enumerate(phase9_trust_scores):
        bar_len = int(trust * max_bar)
        bar = "█" * bar_len + "-" * (max_bar - bar_len)
        print(f"{MAGENTA}{i:03d}{RESET} |{bar}| {trust:.3f}")

else:
    print("Error:", response.status_code, response.text)
