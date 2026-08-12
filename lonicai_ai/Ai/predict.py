from .features.clip_model import predict
from .features.memory_search import search_memory
from .features.food_lookup import lookup_food

def analyze_image(image_path: str):

    # ==========================================
    # CLIP
    # ==========================================

    result = predict(image_path)

    embedding = result.get("embedding")
    predictions = result.get("predictions", [])

    if embedding is None:
        raise ValueError("Model did not return an embedding.")

    if not predictions:
        raise ValueError(
            "No predictions returned by the model."
        )

    # ==========================================
    # LEARNED MEMORY
    # ==========================================
    #
    # memory_search should contain examples that
    # came from user feedback.
    #
    # This is where corrected/rejected images
    # should eventually influence prediction.
    #

    memory = search_memory(embedding)

    if memory:
        prediction = memory["food"]
        confidence = float(memory["confidence"])
        learned = True

    else:
        # ======================================
        # CLIP FALLBACK
        # ======================================

        best_prediction = predictions[0]

        prediction = best_prediction["food"]
        confidence = float(
            best_prediction["confidence"]
        )

        learned = False

    # ==========================================
    # FOOD / NUTRITION LOOKUP
    # ==========================================

    nutrition = lookup_food(prediction)

    # ==========================================
    # RESPONSE
    # ==========================================

    return {
        "prediction": prediction,
        "confidence": confidence,
        "predictions": predictions,
        "nutrition": nutrition,
        "learned": learned,
    }


# ==========================================
# TERMINAL TEST
# ==========================================

if __name__ == "__main__":

    image_path = (
        input("Image: ")
        .strip()
        .strip('"')
        .strip("'")
    )

    try:

        result = analyze_image(image_path)

        print("\n==============================")
        print("LonicAI Prediction")
        print("==============================")

        print(
            "Prediction:",
            result["prediction"],
        )

        print(
            "Confidence:",
            result["confidence"],
        )

        print(
            "Learned:",
            result["learned"],
        )

        print(
            "Nutrition:",
            result["nutrition"],
        )

        print("\nOther predictions:")

        for item in result["predictions"]:
            print(
                f"  {item['food']}: "
                f"{item['confidence']}"
            )

    except Exception as e:

        print(
            "\nPrediction failed:",
            e,
        )
