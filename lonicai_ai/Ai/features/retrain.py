from pathlib import Path
import subprocess
import sys

from github_upload import upload_image
# ==========================================
# DIRECTORIES
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[1]

FEEDBACK_DIR = BASE_DIR / "feedback"

APPROVED_DIR = FEEDBACK_DIR / "approved"


# ==========================================
# RETRAIN AI
# ==========================================

def retrain():

    # ==========================================
    # STEP 1 — REBUILD MEMORY
    # ==========================================

    memory_script = BASE_DIR.parent / "memory.py"

    result = subprocess.run(
        [sys.executable, str(memory_script)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:

        return {
            "success": False,
            "stage": "memory",
            "error": result.stderr,
        }

    # ==========================================
    # STEP 2 — FIND TRAINING IMAGES
    # ==========================================

    if not APPROVED_DIR.exists():

        return {
            "success": True,
            "message": "Memory rebuilt. No training images found.",
            "uploaded": 0,
        }

    images = []

    for image in APPROVED_DIR.rglob("*"):

        if image.is_file() and image.suffix.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
        }:

            images.append(image)

    # ==========================================
    # STEP 3 — UPLOAD TO GITHUB
    # ==========================================

    uploaded = 0
    failed = []

    for image in images:

        try:

            relative_path = image.relative_to(
                APPROVED_DIR
            )

            github_path = (
                "training_data/"
                + str(relative_path).replace("\\", "/")
            )

            upload_image(
                image_path=str(image),
                github_path=github_path,
                commit_message=(
                    f"Add training image: {image.name}"
                ),
            )

            uploaded += 1

        except Exception as e:

            failed.append({
                "image": str(image),
                "error": str(e),
            })

    # ==========================================
    # RESULT
    # ==========================================

    return {
        "success": len(failed) == 0,
        "message": "AI training data updated.",
        "memory_rebuilt": True,
        "training_images": len(images),
        "uploaded": uploaded,
        "failed": failed,
    }