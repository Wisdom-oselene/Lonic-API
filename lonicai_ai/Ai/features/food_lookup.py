import os
import requests

from food_map import FOOD_MAP
import os
import requests
from dotenv import load_dotenv

from food_map import FOOD_MAP

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

def lookup_food(prediction):

    search = FOOD_MAP.get(
        prediction.lower(),
        prediction.lower(),
    )

    api_key = os.getenv("USDA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "USDA_API_KEY environment variable is not set."
        )

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

    data = response.json()

    foods = data.get("foods", [])

    if not foods:

        print("\nNo USDA match found.")

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
    # PRINT
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

        if item in nutrition:

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