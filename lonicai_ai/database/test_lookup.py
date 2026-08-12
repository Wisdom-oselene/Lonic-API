from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "usda.db"

connection = sqlite3.connect(DATABASE)
cursor = connection.cursor()

food_name = input("Search food: ")

cursor.execute("""
SELECT
    name,
    calories,
    protein,
    fat,
    carbohydrates,
    fiber,
    sugar,
    sodium
FROM foods
WHERE LOWER(name) LIKE LOWER(?)
LIMIT 10
""", (f"%{food_name}%",))

rows = cursor.fetchall()

if not rows:
    print("\nNo foods found.")
else:
    print("\nResults:\n")

    for row in rows:
        print("-" * 60)
        print(f"Food         : {row[0]}")
        print(f"Calories     : {row[1]}")
        print(f"Protein      : {row[2]}")
        print(f"Fat          : {row[3]}")
        print(f"Carbohydrate : {row[4]}")
        print(f"Fiber        : {row[5]}")
        print(f"Sugar        : {row[6]}")
        print(f"Sodium       : {row[7]}")