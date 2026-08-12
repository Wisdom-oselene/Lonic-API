from pathlib import Path
import sqlite3
import pandas as pd

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent

DATABASE = BASE_DIR / "usda.db"
FOOD_NUTRIENT_CSV = PROJECT_DIR / "usda_raw" / "food_nutrient.csv"

# ============================================================
# CHECK FILE
# ============================================================

if not FOOD_NUTRIENT_CSV.exists():
    raise FileNotFoundError(
        f"Cannot find:\n{FOOD_NUTRIENT_CSV}"
    )

# ============================================================
# LOAD CSV
# ============================================================

print("=" * 60)
print("Loading food_nutrient.csv...")
print("=" * 60)

nutrients = pd.read_csv(
    FOOD_NUTRIENT_CSV,
    low_memory=False
)

print(f"Loaded {len(nutrients):,} nutrient records.")

# ============================================================
# NUTRIENTS TO IMPORT
# ============================================================

NUTRIENTS = {
    1008: "calories",
    1003: "protein",
    1004: "fat",
    1005: "carbohydrates",
    1079: "fiber",
    2000: "sugar",
    1093: "sodium",
}

nutrients = nutrients[nutrients["nutrient_id"].isin(NUTRIENTS)]

print(f"Keeping {len(nutrients):,} useful nutrient records.")

# ============================================================
# CONNECT DATABASE
# ============================================================

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

# Get all imported foods
cursor.execute("SELECT fdc_id FROM foods")
existing_foods = {row[0] for row in cursor.fetchall()}

print(f"Foods in database: {len(existing_foods):,}")

print("\nUpdating foods table...\n")

# ============================================================
# UPDATE DATABASE
# ============================================================

updated = 0
skipped = 0

connection.execute("BEGIN")

try:

    for _, row in nutrients.iterrows():

        fdc_id = int(row["fdc_id"])

        if fdc_id not in existing_foods:
            skipped += 1
            continue

        if pd.isna(row["amount"]):
            skipped += 1
            continue

        nutrient_id = int(row["nutrient_id"])
        amount = float(row["amount"])

        column = NUTRIENTS[nutrient_id]

        cursor.execute(
            f"""
            UPDATE foods
            SET {column} = ?
            WHERE fdc_id = ?
            """,
            (amount, fdc_id),
        )

        updated += 1

        if updated % 1000 == 0:
            print(f"Updated {updated:,} nutrient values...")

    connection.commit()

except Exception:
    connection.rollback()
    raise

finally:
    connection.close()

# ============================================================
# DONE
# ============================================================

print("\n" + "=" * 60)
print("Import Complete")
print("=" * 60)
print(f"Updated : {updated:,}")
print(f"Skipped : {skipped:,}")
print("=" * 60)