from pathlib import Path
from datetime import datetime
import json
import shutil

from features.clip_model import predict
from features.memory_search import add_memory


# ==========================================
# DIRECTORIES
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

FEEDBACK = BASE_DIR / "feedback"

APPROVED = FEEDBACK / "approved"
REJECTED = FEEDBACK / "rejected"
METADATA = FEEDBACK / "metadata"


APPROVED.mkdir(parents=True, exist_ok=True)
REJECTED.mkdir(parents=True, exist_ok=True)
METADATA.mkdir(parents=True, exist_ok=True)


# ==========================================
# SAVE FEEDBACK
# ==========================================

def save_feedback(
    image_path,
    prediction,
    confidence,
    approved,
    correct=None,
):

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    # ==========================================
    # SCAN IMAGE AGAIN
    # ==========================================

    print()
    print("==========================================")
    print("SCANNING FEEDBACK IMAGE")
    print("==========================================")
    print(f"Original prediction: {prediction}")
    print(f"Original confidence: {confidence}%")
    print()

    result = predict(image_path)

    embedding = result["embedding"]
    predictions = result["predictions"]

    print("New CLIP scan:")
    print(predictions)

    # ==========================================
    # APPROVED
    # ==========================================

    if approved:

        label = prediction

        folder = APPROVED / label.replace(" ", "_")
        folder.mkdir(parents=True, exist_ok=True)

        saved_path = folder / (
            f"{timestamp}{image_path.suffix}"
        )

        shutil.copy2(
            image_path,
            saved_path,
        )

        # ------------------------------------------
        # TEACH MEMORY
        # ------------------------------------------

        memory_result = add_memory(
            embedding=embedding,
            label=label,
        )

        # ------------------------------------------
        # SAVE METADATA
        # ------------------------------------------

        metadata = {
            "type": "approved",
            "prediction": prediction,
            "confidence": confidence,
            "correct": label,
            "image": str(saved_path),
            "embedding_saved": True,
            "created_at": timestamp,
            "predictions": predictions,
        }

        with open(
            METADATA / f"{timestamp}.json",
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                metadata,
                f,
                indent=4,
            )

        print()
        print("==========================================")
        print("APPROVED FEEDBACK SAVED")
        print("==========================================")
        print(f"Food: {label}")
        print(f"Image: {saved_path}")
        print("Embedding: saved")
        print("Memory: updated")
        print("==========================================")

        return {
            "success": True,
            "type": "approved",
            "prediction": prediction,
            "correct": label,
            "image": str(saved_path),
            "memory": memory_result,
            "predictions": predictions,
        }

    # ==========================================
    # DISAPPROVED
    # ==========================================

    if not correct:
        raise ValueError(
            "Correct food is required."
        )

    correct = correct.strip()

    if not correct:
        raise ValueError(
            "Correct food cannot be empty."
        )

    # ==========================================
    # SAVE CORRECT IMAGE
    # ==========================================

    good = APPROVED / correct.replace(" ", "_")

    bad = REJECTED / prediction.replace(" ", "_")

    good.mkdir(parents=True, exist_ok=True)
    bad.mkdir(parents=True, exist_ok=True)

    # Correct/training copy
    good_path = good / (
        f"{timestamp}{image_path.suffix}"
    )

    # Rejected prediction copy
    bad_path = bad / (
        f"{timestamp}{image_path.suffix}"
    )

    shutil.copy2(
        image_path,
        good_path,
    )

    shutil.copy2(
        image_path,
        bad_path,
    )

    # ==========================================
    # TEACH MEMORY
    # ==========================================

    memory_result = add_memory(
        embedding=embedding,
        label=correct,
    )

    # ==========================================
    # SAVE METADATA
    # ==========================================

    metadata = {
        "type": "correction",
        "prediction": prediction,
        "confidence": confidence,
        "correct": correct,
        "correct_image": str(good_path),
        "rejected_image": str(bad_path),
        "embedding_saved": True,
        "created_at": timestamp,
        "predictions": predictions,
    }

    with open(
        METADATA / f"{timestamp}.json",
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            metadata,
            f,
            indent=4,
        )

    # ==========================================
    # PRINT RESULT
    # ==========================================

    print()
    print("==========================================")
    print("FEEDBACK LEARNED")
    print("==========================================")
    print(f"Original prediction: {prediction}")
    print(f"Original confidence: {confidence}%")
    print(f"Correct answer: {correct}")
    print()
    print("Image: saved")
    print("Image scanned again: YES")
    print("Embedding: generated")
    print("Embedding: saved")
    print("Memory: updated")
    print()
    print(f"Correct image: {good_path}")
    print(f"Rejected image: {bad_path}")
    print("==========================================")
    print()

    return {
        "success": True,
        "type": "correction",
        "prediction": prediction,
        "confidence": confidence,
        "correct": correct,
        "image": str(good_path),
        "rejected_image": str(bad_path),
        "memory": memory_result,
        "predictions": predictions,
    }