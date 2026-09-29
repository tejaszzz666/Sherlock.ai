import torch
import torch.nn as nn
import torch.optim as optim
from model import get_model
from dataset import get_dataloader
import os

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "dataset")
SAVE_DIR = os.path.join(os.path.dirname(__file__), "saved_models")
os.makedirs(SAVE_DIR, exist_ok=True)

BATCH_SIZE = 32
EPOCHS = 5  # Start small for testing
LEARNING_RATE = 1e-3

train_loader, class_to_idx = get_dataloader(DATA_DIR, batch_size=BATCH_SIZE)
model = get_model().to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

for epoch in range(EPOCHS):
    total_loss = 0
    model.train()
    for images, labels in train_loader:
        images, labels = images.to(DEVICE), labels.to(DEVICE)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch {epoch+1}/{EPOCHS} - Loss: {total_loss/len(train_loader):.4f}")

# Save model
torch.save(model.state_dict(), os.path.join(SAVE_DIR, "image_detector.pth"))

# Save class map
import json
with open(os.path.join(SAVE_DIR, "class_map.json"), "w") as f:
    json.dump(class_to_idx, f)
