import torch
import numpy as np
import os
from torchvision import models, transforms
from PIL import Image
import json
import torch.nn as nn
from tqdm import tqdm

# -----------------------------
# Paths (FIXED)
# -----------------------------
BASE_DIR = os.path.dirname(__file__)

# Dataset is at: Sherlock.ai/dataset/
DATASET_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../dataset"))
REAL_DIR = os.path.join(DATASET_DIR, "real")
FAKE_DIR = os.path.join(DATASET_DIR, "fake")

SAVE_DIR = os.path.join(BASE_DIR, "saved_models")
os.makedirs(SAVE_DIR, exist_ok=True)

MODEL_PATH = os.path.join(SAVE_DIR, "image_detector.pth")
SAVE_PATH = os.path.join(SAVE_DIR, "mahalanobis.json")

# -----------------------------
# Load feature extractor
# -----------------------------
model = models.resnet18(weights=None)
model.fc = nn.Identity()  # remove classifier head
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"), strict=False)
model.eval()

# -----------------------------
# Transform
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485, 0.456, 0.406],
        [0.229, 0.224, 0.225]
    )
])

# -----------------------------
# Feature extraction
# -----------------------------
def extract_features(folder):
    features = []

    for fname in tqdm(os.listdir(folder), desc=f"Extracting {os.path.basename(folder)}"):
        path = os.path.join(folder, fname)

        if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
            continue

        try:
            img = Image.open(path).convert("RGB")
            x = transform(img).unsqueeze(0)

            with torch.no_grad():
                feat = model(x).cpu().numpy().squeeze()

            features.append(feat)

        except Exception as e:
            print(f"⚠️ Skipping {fname}: {e}")

    return np.array(features)

# -----------------------------
# Run extraction
# -----------------------------
print("🔍 Extracting REAL features...")
real_feats = extract_features(REAL_DIR)

print("🔍 Extracting FAKE features...")
fake_feats = extract_features(FAKE_DIR)

assert len(real_feats) > 0 and len(fake_feats) > 0, "❌ Empty feature set!"

# -----------------------------
# Compute statistics
# -----------------------------
real_mean = real_feats.mean(axis=0)
fake_mean = fake_feats.mean(axis=0)

all_feats = np.vstack([real_feats, fake_feats])
cov = np.cov(all_feats, rowvar=False)

# -----------------------------
# Save stats
# -----------------------------
stats = {
    "real_mean": real_mean.tolist(),
    "fake_mean": fake_mean.tolist(),
    "cov": cov.tolist()
}

with open(SAVE_PATH, "w") as f:
    json.dump(stats, f)

print("✅ Mahalanobis stats saved to:", SAVE_PATH)
