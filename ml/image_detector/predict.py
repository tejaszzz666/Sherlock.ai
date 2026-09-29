import torch
from torchvision import transforms, models
from PIL import Image
import json
import os
import torch.nn as nn

# -----------------------------
# Paths
# -----------------------------
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, "saved_models", "image_detector.pth")
CLASS_MAP_PATH = os.path.join(BASE_DIR, "saved_models", "class_map.json")

# -----------------------------
# Load class map
# -----------------------------
with open(CLASS_MAP_PATH, "r") as f:
    class_map = json.load(f)

REAL_IDX = class_map["real"]
FAKE_IDX = class_map["fake"]

# -----------------------------
# Load model (ResNet18)
# -----------------------------
model = models.resnet18(weights=None)
model.fc = nn.Linear(model.fc.in_features, 2)
model.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
model.eval()

# -----------------------------
# Image transform
# -----------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# -----------------------------
# Prediction function
# -----------------------------
def predict_image(image_path: str):
    """
    Predicts whether an image is REAL, FAKE, or UNKNOWN.

    Args:
        image_path (str): Path to the image.

    Returns:
        dict: {
            "label": "REAL" | "FAKE" | "UNKNOWN",
            "real_probability": float,
            "fake_probability": float,
            "confidence": float
        }
    """
    if not os.path.exists(image_path):
        return {"error": f"File not found: {image_path}"}

    try:
        img = Image.open(image_path).convert("RGB")
    except Exception as e:
        return {"error": f"Cannot open image: {e}"}

    img = transform(img).unsqueeze(0)

    with torch.no_grad():
        logits = model(img)
        probs = torch.softmax(logits, dim=1)[0]

    real_prob = float(probs[REAL_IDX])
    fake_prob = float(probs[FAKE_IDX])

    max_prob = max(real_prob, fake_prob)
    margin = abs(real_prob - fake_prob)

    # -----------------------------
    # UNKNOWN LOGIC
    # -----------------------------
    CONFIDENCE_THRESHOLD = 0.80  # model must be at least 80% confident
    MARGIN_THRESHOLD = 0.30      # difference between real and fake prob

    if max_prob < CONFIDENCE_THRESHOLD or margin < MARGIN_THRESHOLD:
        return {
            "label": "UNKNOWN",
            "real_probability": round(real_prob, 4),
            "fake_probability": round(fake_prob, 4),
            "confidence": round(max_prob, 4)
        }

    # Determine label
    label = "REAL" if real_prob > fake_prob else "FAKE"

    return {
        "label": label,
        "real_probability": round(real_prob, 4),
        "fake_probability": round(fake_prob, 4),
        "confidence": round(max_prob, 4)
    }


# -----------------------------
# Optional: Test main
# -----------------------------
if __name__ == "__main__":
    test_images = [
        os.path.join(BASE_DIR, "dataset", "real", "0000 (9).jpg"),
        os.path.join(BASE_DIR, "dataset", "fake", "0001.jpg"),
        "D:\\valley-of-gods-john-mueller.jpg"  # outside dataset
    ]

    for img_path in test_images:
        result = predict_image(img_path)
        print(f"{img_path} => {result}")
