from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent

DATABASE = BASE_DIR / "database" / "usda.db"

connection = sqlite3.connect(DATABASE)

cursor = connection.cursor()

cursor.execute("""
SELECT name
FROM sqlite_master
WHERE type='table';
""")

tables = cursor.fetchall()

print("\nTables inside usda.db:\n")

for table in tables:
    print(table[0])

connection.close()