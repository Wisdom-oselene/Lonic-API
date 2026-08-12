from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

import tempfile
import os
from pathlib import Path

from .predict import analyze_image

from .features.feedback import save_feedback
from .features.retrain import retrain
from .features.favorites import (
    get_favorites,
    add_favorite,
    remove_favorite,
    is_favorite,
)


app = FastAPI(
    title="LonicAI API",
    version="1.0",
)


# ==========================================
# DIRECTORIES
# ==========================================

# api.py location:
# lonicai_ai/Ai/api.py

BASE_DIR = Path(__file__).resolve().parent

FEEDBACK_DIR = BASE_DIR / "feedback"

APPROVED_DIR = FEEDBACK_DIR / "approved"
REJECTED_DIR = FEEDBACK_DIR / "rejected"
METADATA_DIR = FEEDBACK_DIR / "metadata"


# Make sure directories exist
APPROVED_DIR.mkdir(parents=True, exist_ok=True)
REJECTED_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)



# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {
        "status": "LonicAI API Running"
    }


# ==========================================
# PREDICT
# ==========================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):

    image_bytes = await file.read()

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(
                file.filename or ".jpg"
            )[1],
        ) as temp:

            temp.write(image_bytes)
            temp_path = temp.name

        return analyze_image(temp_path)

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(temp_path)


# ==========================================
# FEEDBACK
# ==========================================

@app.post("/feedback")
async def feedback(
    file: UploadFile = File(...),
    prediction: str = Form(...),
    confidence: float = Form(...),
    approved: bool = Form(...),
    correct: str | None = Form(None),
):

    image_bytes = await file.read()

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(
                file.filename or ".jpg"
            )[1],
        ) as temp:

            temp.write(image_bytes)
            temp_path = temp.name

        return save_feedback(
            image_path=temp_path,
            prediction=prediction,
            confidence=confidence,
            approved=approved,
            correct=correct,
        )

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(temp_path)



# ==========================================
# GET FAVORITES
# ==========================================

@app.get("/favorites")
def favorites():
    return {
        "success": True,
        "favorites": get_favorites(),
    }




# ==========================================
# ADD FAVORITE
# ==========================================

@app.post("/favorites/{food}")
def add_food_favorite(food: str):

    return add_favorite(food)




# ==========================================
# REMOVE FAVORITE
# ==========================================

@app.delete("/favorites/{food}")
def remove_food_favorite(food: str):

    return remove_favorite(food)




# ==========================================
# CHECK FAVORITE
# ==========================================

@app.get("/favorites/check/{food}")
def check_favorite(food: str):

    return {
        "success": True,
        "favorite": is_favorite(food),
    }


# ==========================================
# GET TRAINING DATABASE
# ==========================================

@app.get("/training-data")
def get_training_data():

    items = []

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
    }

    # ======================================
    # APPROVED
    # ======================================

    if APPROVED_DIR.exists():

        for image in APPROVED_DIR.rglob("*"):

            if not image.is_file():
                continue

            if (
                image.suffix.lower()
                not in allowed_extensions
            ):
                continue

            relative_path = (
                image.relative_to(
                    APPROVED_DIR
                )
            )

            # Always use "/" in API IDs.
            relative_path = str(
                relative_path
            ).replace("\\", "/")

            items.append({
                "id": (
                    f"approved:"
                    f"{relative_path}"
                ),

                "type": "approved",

                "food": (
                    image.parent.name
                    .replace("_", " ")
                ),

                "image": (
                    f"approved:"
                    f"{relative_path}"
                ),

                "filename": image.name,
            })

    # ======================================
    # REJECTED
    # ======================================

    if REJECTED_DIR.exists():

        for image in REJECTED_DIR.rglob("*"):

            if not image.is_file():
                continue

            if (
                image.suffix.lower()
                not in allowed_extensions
            ):
                continue

            relative_path = (
                image.relative_to(
                    REJECTED_DIR
                )
            )

            relative_path = str(
                relative_path
            ).replace("\\", "/")

            items.append({
                "id": (
                    f"rejected:"
                    f"{relative_path}"
                ),

                "type": "rejected",

                "food": (
                    image.parent.name
                    .replace("_", " ")
                ),

                "image": (
                    f"rejected:"
                    f"{relative_path}"
                ),

                "filename": image.name,
            })

    return {
        "success": True,
        "count": len(items),
        "items": items,
    }


# ==========================================
# DELETE TRAINING DATA
# ==========================================

@app.delete(
    "/training-data/{item_id:path}"
)
def delete_training_data(
    item_id: str
):

    print("\n==========================================")
    print("DELETE TRAINING DATA")
    print("==========================================")

    try:

        # --------------------------------------
        # NORMALIZE ID
        # --------------------------------------

        item_id = item_id.replace(
            "\\",
            "/",
        )

        print(
            f"Received ID: {item_id}"
        )

        # --------------------------------------
        # DETERMINE DIRECTORY
        # --------------------------------------

        if item_id.startswith(
            "approved:"
        ):

            relative_path = item_id[
                len("approved:"):
            ]

            base_dir = APPROVED_DIR
            item_type = "approved"

        elif item_id.startswith(
            "rejected:"
        ):

            relative_path = item_id[
                len("rejected:"):
            ]

            base_dir = REJECTED_DIR
            item_type = "rejected"

        else:

            raise HTTPException(
                status_code=400,
                detail="Invalid training data ID.",
            )

        # --------------------------------------
        # NORMALIZE RELATIVE PATH
        # --------------------------------------

        relative_path = (
            relative_path
            .replace("\\", "/")
            .lstrip("/")
        )

        print(
            f"Base directory: {base_dir}"
        )

        print(
            f"Relative path: {relative_path}"
        )

        # --------------------------------------
        # BUILD ABSOLUTE PATH
        # --------------------------------------

        base_dir = base_dir.resolve()

        image_path = (
            base_dir / Path(relative_path)
        ).resolve()

        print(
            f"Resolved image: {image_path}"
        )

        # --------------------------------------
        # SECURITY CHECK
        # --------------------------------------

        try:

            image_path.relative_to(
                base_dir
            )

        except ValueError:

            print(
                "SECURITY CHECK FAILED"
            )

            raise HTTPException(
                status_code=400,
                detail="Invalid training data path.",
            )

        # --------------------------------------
        # CHECK FILE
        # --------------------------------------

        if not image_path.exists():

            print(
                "FILE DOES NOT EXIST"
            )

            raise HTTPException(
                status_code=404,
                detail={
                    "message": (
                        "Training image not found."
                    ),
                    "id": item_id,
                    "resolved_path": str(
                        image_path
                    ),
                },
            )

        if not image_path.is_file():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Training item is not a file."
                ),
            )

        # --------------------------------------
        # DELETE IMAGE
        # --------------------------------------

        image_path.unlink()

        print(
            "IMAGE DELETED"
        )

        # --------------------------------------
        # REMOVE EMPTY FOOD DIRECTORY
        # --------------------------------------

        parent = image_path.parent

        if (
            parent != base_dir
            and parent.exists()
        ):

            try:

                if not any(
                    parent.iterdir()
                ):

                    parent.rmdir()

                    print(
                        f"Removed empty directory: "
                        f"{parent}"
                    )

            except OSError as e:

                print(
                    f"Could not remove directory: "
                    f"{e}"
                )

        # --------------------------------------
        # RETRAIN
        # --------------------------------------

        memory_result = None

        try:

            pass
            print(
                "MEMORY REBUILT"
            )

        except Exception as e:

            print(
                f"Retraining failed: {e}"
            )

            memory_result = {
                "success": False,
                "error": str(e),
            }

        # --------------------------------------
        # SUCCESS
        # --------------------------------------

        print(
            "DELETE COMPLETE"
        )

        print(
            "=========================================="
        )

        return {
            "success": True,
            "deleted": relative_path,
            "type": item_type,
            "memory_rebuilt": memory_result,
        }

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"DELETE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ==========================================
# RETRAIN AI
# ==========================================

@app.post("/retrain")
def retrain_ai():

    return retrain()


# ==========================================
# SERVE TRAINING IMAGE
# ==========================================

@app.get("/training-image")
def training_image(
    path: str
):

    print("\n==========================================")
    print("TRAINING IMAGE")
    print("==========================================")

    try:

        # --------------------------------------
        # NORMALIZE ID
        # --------------------------------------

        path = path.replace(
            "\\",
            "/",
        )

        print(
            f"Requested ID: {path}"
        )

        # --------------------------------------
        # DETERMINE DIRECTORY
        # --------------------------------------

        if path.startswith(
            "approved:"
        ):

            relative_path = path[
                len("approved:"):
            ]

            base_dir = APPROVED_DIR

        elif path.startswith(
            "rejected:"
        ):

            relative_path = path[
                len("rejected:"):
            ]

            base_dir = REJECTED_DIR

        else:

            raise HTTPException(
                status_code=400,
                detail="Invalid training image ID.",
            )

        # --------------------------------------
        # NORMALIZE PATH
        # --------------------------------------

        relative_path = (
            relative_path
            .replace("\\", "/")
            .lstrip("/")
        )

        base_dir = base_dir.resolve()

        image_path = (
            base_dir / Path(relative_path)
        ).resolve()

        print(
            f"Resolved image: {image_path}"
        )

        # --------------------------------------
        # SECURITY CHECK
        # --------------------------------------

        try:

            image_path.relative_to(
                base_dir
            )

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail="Invalid training image path.",
            )

        # --------------------------------------
        # CHECK FILE
        # --------------------------------------

        if not image_path.exists():

            raise HTTPException(
                status_code=404,
                detail={
                    "message": (
                        "Training image not found."
                    ),
                    "requested_id": path,
                    "resolved_path": str(
                        image_path
                    ),
                    "base_dir": str(
                        base_dir
                    ),
                },
            )

        if not image_path.is_file():

            raise HTTPException(
                status_code=400,
                detail=(
                    "Training item is not a file."
                ),
            )

        # --------------------------------------
        # RETURN IMAGE
        # --------------------------------------

        return FileResponse(
            path=str(image_path)
        )

    except HTTPException:
        raise

    except Exception as e:

        print(
            f"TRAINING IMAGE ERROR: "
            f"{type(e).__name__}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
