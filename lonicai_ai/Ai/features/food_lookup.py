from pathlib import Path
import sqlite3

from food_map import FOOD_MAP

# ==========================================
# DATABASE
# ==========================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE = BASE_DIR / "database" / "usda.db"

if not DATABASE.exists():
    raise FileNotFoundError(
        f"USDA database not found:\n{DATABASE}"
    )

# ==========================================
# SCORING
# ==========================================

def score_food(search, name):

    search_words = set(search.lower().split())
    name_words = set(name.lower().split())

    score = len(search_words & name_words)

    if name.lower().startswith(search.lower()):
        score += 5

    if "frozen" in name.lower():
        score -= 1

    if "school lunch" in name.lower():
        score -= 2

    if "fast food" in name.lower():
        score -= 1

    return score

# ==========================================
# LOOKUP
# ==========================================

def lookup_food(prediction):

    search = FOOD_MAP.get(
        prediction.lower(),
        prediction.lower()
    )

    with sqlite3.connect(DATABASE) as connection:

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                fdc_id,
                name
            FROM foods
            WHERE LOWER(name) LIKE LOWER(?)
            LIMIT 20
            """,
            (f"%{search}%",),
        )

        foods = cursor.fetchall()

        if not foods:

            print("\nNo USDA match found.")

            return None

        fdc_id, food_name = max(
            foods,
            key=lambda x: score_food(search, x[1])
        )

        print("\n==============================")
        print("USDA Match")
        print("==============================")
        print(food_name)

        cursor.execute(
            """
            SELECT
                n.name,
                fn.amount,
                n.unit_name
            FROM food_nutrient fn
            JOIN nutrient n
            ON fn.nutrient_id = n.id
            WHERE fn.fdc_id = ?
            """,
            (fdc_id,),
        )

        rows = cursor.fetchall()

    wanted = {
        ("Energy", "KCAL"): "Calories",
        ("Protein", "G"): "Protein",
        ("Total lipid (fat)", "G"): "Fat",
        ("Carbohydrate, by difference", "G"): "Carbohydrates",
        ("Fiber, total dietary", "G"): "Fiber",
        ("Sugars, Total", "G"): "Sugar",
        ("Sodium, Na", "MG"): "Sodium",
    }

    nutrition = {}

    for name, amount, unit in rows:

        key = (name, unit.upper())

        if key in wanted:

            nutrition[wanted[key]] = {
                "amount": amount,
                "unit": unit
            }

    print("\n==============================")
    print("Nutrition (per 100g)")
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

    return {
        "food": food_name,
        "nutrition": nutrition
    }