import torch
import torch.nn.functional as F

def compute_uncertainty(logits):
    probs = F.softmax(logits, dim=1)
    confidence, pred_class = torch.max(probs, dim=1)

    entropy = -torch.sum(probs * torch.log(probs + 1e-8), dim=1)

    return {
        "confidence": confidence.item(),
        "entropy": entropy.item(),
        "pred_class": pred_class.item()
    }
