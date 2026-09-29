import torch
import json
import os
import math
from torchvision import transforms, models
from PIL import Image
import torch.nn as nn

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "image_detector.pth")
CLASS_MAP_PATH = os.path.join(BASE_DIR, "saved_models", "class_map.json")

# CHANGE THIS
VAL_DIR = os.path.join(BASE_DIR, "dataset_val")  
# dataset_val/
#   real/
#   fake/

# -----------------------------
# Load class map
# -----------------------------
with open(CLASS_MAP_PATH) as f:
    class_map = json.load(f)

REAL_IDX = class_map["real"]
FAKE_IDX = class_map["fake"]

# -----------------------------
# Load model
# -----------------------------
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# -----------------------------
# Transform
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485,0.456,0.406],
        [0.229,0.224,0.225]
    )
])

# -----------------------------
# Load images
# -----------------------------
def load_images(label):
    folder = os.path.join(VAL_DIR, label)
    images = []
    for f in os.listdir(folder):
        if f.lower().endswith((".jpg",".png",".jpeg")):
            images.append((os.path.join(folder, f), label))
    return images

val_data = load_images("real") + load_images("fake")

# -----------------------------
# Calibration test
# -----------------------------
def test_temperature(T):
    total_entropy = 0
    correct = 0

    for path, label in val_data:
        img = Image.open(path).convert("RGB")
        img = transform(img).unsqueeze(0)

        with torch.no_grad():
            logits = model(img)
            probs = torch.softmax(logits / T, dim=1)[0]

        real_p = probs[REAL_IDX].item()
        fake_p = probs[FAKE_IDX].item()

        entropy = -(
            real_p * math.log(real_p + 1e-8) +
            fake_p * math.log(fake_p + 1e-8)
        )

        total_entropy += entropy

        pred = "real" if real_p > fake_p else "fake"
        if pred == label:
            correct += 1

    avg_entropy = total_entropy / len(val_data)
    accuracy = correct / len(val_data)

    return accuracy, avg_entropy

# -----------------------------
# Run calibration
# -----------------------------
temps = [1.0, 1.5, 2.0, 2.5, 3.0]

print("\nTemperature Calibration Results\n")
for T in temps:
    acc, ent = test_temperature(T)
    print(f"T={T} | Accuracy={acc:.3f} | Avg Entropy={ent:.3f}")
