import os

import requests
from dotenv import load_dotenv


load_dotenv()


# ==========================================
# USDA API
# ==========================================

USDA_API_URL = (
    "https://api.nal.usda.gov/fdc/v1/foods/search"
)


# ==========================================
# LOOKUP
# ==========================================

def lookup_food(prediction: str):

    if not prediction:
        raise ValueError(
            "No food prediction was provided."
        )

    # Use the CLIP prediction directly.
    search = prediction.strip().lower()

    api_key = os.getenv("USDA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "USDA_API_KEY environment variable is not set."
        )

    # ======================================
    # USDA REQUEST
    # ======================================

    try:

        response = requests.get(
            USDA_API_URL,
            params={
                "api_key": api_key,
                "query": search,
                "pageSize": 20,
            },
            timeout=15,
        )

        response.raise_for_status()

    except requests.RequestException as e:

        raise RuntimeError(
            f"USDA API request failed: {e}"
        )

    # ======================================
    # RESPONSE
    # ======================================

    try:

        data = response.json()

    except ValueError as e:

        raise RuntimeError(
            f"USDA returned invalid JSON: {e}"
        )

    foods = data.get("foods", [])

    if not foods:

        print(
            f"\nNo USDA match found for: {prediction}"
        )

        return None

    # ======================================
    # BEST MATCH
    # ======================================

    food = foods[0]

    food_name = food.get(
        "description",
        prediction,
    )

    print("\n==============================")
    print("USDA Match")
    print("==============================")
    print(food_name)

    # ======================================
    # NUTRITION
    # ======================================

    wanted = {
        "Energy": "Calories",
        "Protein": "Protein",
        "Total lipid (fat)": "Fat",
        "Carbohydrate, by difference": "Carbohydrates",
        "Fiber, total dietary": "Fiber",
        "Sugars, Total": "Sugar",
        "Total Sugars": "Sugar",
        "Sodium, Na": "Sodium",
    }

    nutrition = {}

    for nutrient in food.get(
        "foodNutrients",
        [],
    ):

        name = nutrient.get(
            "nutrientName"
        )

        if name not in wanted:
            continue

        nutrition[wanted[name]] = {
            "amount": nutrient.get(
                "value",
                0,
            ),
            "unit": nutrient.get(
                "unitName",
                "",
            ),
        }

    # ======================================
    # PRINT NUTRITION
    # ======================================

    print("\n==============================")
    print("Nutrition")
    print("==============================")

    order = [
        "Calories",
        "Protein",
        "Fat",
        "Carbohydrates",
        "Fiber",
        "Sugar",
        "Sodium",
    ]

    for item in order:

        if item not in nutrition:
            continue

        value = nutrition[item]

        print(
            f"{item:<15}"
            f"{value['amount']:.2f} "
            f"{value['unit']}"
        )

    # ======================================
    # RETURN
    # ======================================

    return {
        "food": food_name,
        "nutrition": nutrition,
    }
