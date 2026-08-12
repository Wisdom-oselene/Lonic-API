from pathlib import Path

from PIL import Image

import torch
import open_clip


# ==========================================
# LONICAI FOOD CLASSES
# ==========================================
#
# These are YOUR labels.
# Food-101 is not used.
#
# Add/remove foods here as your LonicAI
# food database grows.
#

FOOD_CLASSES = [
    "rice",
    "fried rice",
    "jollof rice",
    "white rice",
    "brown rice",
    "chicken",
    "fried chicken",
    "grilled chicken",
    "beef",
    "fish",
    "fried fish",
    "egg",
    "boiled egg",
    "fried egg",
    "beans",
    "yam",
    "fried yam",
    "pounded yam",
    "plantain",
    "fried plantain",
    "potato",
    "french fries",
    "bread",
    "sandwich",
    "burger",
    "pizza",
    "pasta",
    "spaghetti",
    "noodles",
    "salad",
    "soup",
    "stew",
    "porridge",
    "oatmeal",
    "fruit",
    "apple",
    "banana",
    "orange",
    "watermelon",
    "pineapple",
    "mango",
    "grapes",
]


# ==========================================
# DEVICE
# ==========================================

DEVICE = (
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ==========================================
# LOAD CLIP
# ==========================================

try:

    print("Loading CLIP...")

    MODEL, _, PREPROCESS = (
        open_clip.create_model_and_transforms(
            "ViT-B-32",
            pretrained="laion2b_s34b_b79k",
        )
    )

    MODEL = MODEL.to(DEVICE)

    MODEL.eval()


    # ======================================
    # TEXT FEATURES
    # ======================================

    TEXT = open_clip.tokenize(
        FOOD_CLASSES
    ).to(DEVICE)


    with torch.no_grad():

        TEXT_FEATURES = MODEL.encode_text(
            TEXT
        )

        TEXT_FEATURES /= TEXT_FEATURES.norm(
            dim=-1,
            keepdim=True,
        )


    print(
        f"CLIP Ready. "
        f"{len(FOOD_CLASSES)} food classes loaded.\n"
    )


except Exception as e:

    raise RuntimeError(
        f"Failed to load CLIP:\n{e}"
    )


# ==========================================
# PREDICT
# ==========================================

def predict(image_path: str):

    image_path = (
        Path(image_path)
        .expanduser()
        .resolve()
    )


    # ======================================
    # VALIDATE IMAGE
    # ======================================

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found:\n{image_path}"
        )


    if not image_path.is_file():

        raise RuntimeError(
            f"Expected an image file, got:\n"
            f"{image_path}"
        )


    # ======================================
    # LOAD IMAGE
    # ======================================

    try:

        image = (
            PREPROCESS(
                Image.open(
                    image_path
                ).convert("RGB")
            )
            .unsqueeze(0)
            .to(DEVICE)
        )

    except Exception as e:

        raise RuntimeError(
            f"Unable to open image:\n{e}"
        )


    # ======================================
    # CLIP INFERENCE
    # ======================================

    try:

        with torch.no_grad():

            image_features = (
                MODEL.encode_image(image)
            )


            image_features /= (
                image_features.norm(
                    dim=-1,
                    keepdim=True,
                )
            )


            similarity = (
                100
                * image_features
                @ TEXT_FEATURES.T
            ).softmax(dim=-1)


    except Exception as e:

        raise RuntimeError(
            f"Prediction failed:\n{e}"
        )


    # ======================================
    # TOP PREDICTIONS
    # ======================================

    top_k = min(
        5,
        len(FOOD_CLASSES)
    )


    values, indices = (
        similarity[0].topk(top_k)
    )


    predictions = []


    for score, idx in zip(
        values,
        indices,
    ):

        predictions.append(
            {
                "food": FOOD_CLASSES[
                    idx.item()
                ],

                "confidence": round(
                    score.item() * 100,
                    2,
                ),
            }
        )


    # ======================================
    # RETURN
    # ======================================

    return {
        "embedding": (
            image_features.cpu()
        ),

        "predictions": predictions,
    }
