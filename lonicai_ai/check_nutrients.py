from pathlib import Path
import sqlite3

db = Path(__file__).resolve().parent / "database" / "usda.db"

conn = sqlite3.connect(db)
cursor = conn.cursor()

fdc = input("FDC ID: ")

cursor.execute("""
SELECT nutrient_id, amount
FROM food_nutrient
WHERE fdc_id = ?
LIMIT 20
""", (fdc,))

for row in cursor.fetchall():
    print(row)

conn.close()