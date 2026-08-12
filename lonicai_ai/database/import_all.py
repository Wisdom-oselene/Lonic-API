from pathlib import Path
import sqlite3
import pandas as pd

# ==========================================
# PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
USDA_DIR = BASE_DIR.parent / "usda_raw"
DB_PATH = BASE_DIR / "usda.db"

conn = sqlite3.connect(DB_PATH)

# ==========================================
# CSV FILES TO IMPORT
# ==========================================

FILES = [
    "food_nutrient.csv",      # <-- ADD THIS
    "nutrient.csv",
    "food_category.csv",
    "measure_unit.csv",
    "food_portion.csv",
    "food_attribute.csv",
    "food_attribute_type.csv",
    "food_component.csv",
    "input_food.csv",
    "lab_method.csv",
    "lab_method_code.csv",
    "lab_method_nutrient.csv",
]

for file in FILES:

    path = USDA_DIR / file

    if not path.exists():
        print(f"❌ Missing: {file}")
        continue

    print(f"Importing {file}...")

    df = pd.read_csv(path, low_memory=False)

    table = file.replace(".csv", "")

    df.to_sql(
        table,
        conn,
        if_exists="replace",
        index=False,
    )

    print(f"   ✓ {len(df):,} rows")

conn.close()

print("\n===================================")
print("USDA import complete.")
print("===================================")