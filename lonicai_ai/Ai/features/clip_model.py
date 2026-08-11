from pathlib import Path

from PIL import Image

import torch
import open_clip

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from food101_classes import FOOD101_CLASSES
# ==========================================
# DEVICE
# ==========================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# ==========================================
# LOAD CLIP
# ==========================================

try:

    print("Loading CLIP...")

    MODEL, _, PREPROCESS = open_clip.create_model_and_transforms(
        "ViT-B-32",
        pretrained="laion2b_s34b_b79k",
    )

    MODEL = MODEL.to(DEVICE)
    MODEL.eval()

    TEXT = open_clip.tokenize(
        FOOD101_CLASSES
    ).to(DEVICE)

    with torch.no_grad():

        TEXT_FEATURES = MODEL.encode_text(TEXT)

        TEXT_FEATURES /= TEXT_FEATURES.norm(
            dim=-1,
            keepdim=True,
        )

    print("CLIP Ready.\n")

except Exception as e:

    raise RuntimeError(
        f"Failed to load CLIP:\n{e}"
    )

# ==========================================
# PREDICT
# ==========================================

def predict(image_path):

    image_path = Path(image_path).expanduser().resolve()

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )

    if not image_path.is_file():
        raise RuntimeError(
            f"Expected an image file, got:\n{image_path}"
        )
    try:

        image = PREPROCESS(
            Image.open(image_path).convert("RGB")
        ).unsqueeze(0).to(DEVICE)

    except Exception as e:

        raise RuntimeError(
            f"Unable to open image:\n{e}"
        )

    try:

        with torch.no_grad():

            image_features = MODEL.encode_image(image)

            image_features /= image_features.norm(
                dim=-1,
                keepdim=True,
            )

            similarity = (
                100 * image_features @ TEXT_FEATURES.T
            ).softmax(dim=-1)

    except Exception as e:

        raise RuntimeError(
            f"Prediction failed:\n{e}"
        )

    values, indices = similarity[0].topk(5)

    predictions = []

    for score, idx in zip(values, indices):

        predictions.append(
            {
                "food": FOOD101_CLASSES[idx],
                "confidence": round(score.item() * 100, 2),
            }
        )

    return {
        "embedding": image_features.cpu(),
        "predictions": predictions,
    }