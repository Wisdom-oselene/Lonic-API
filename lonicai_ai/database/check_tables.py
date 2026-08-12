from pathlib import Path
import sqlite3
import pandas as pd

DB = Path(__file__).resolve().parent / "usda.db"

conn = sqlite3.connect(DB)

tables = pd.read_sql(
    """
    SELECT name
    FROM sqlite_master
    WHERE type='table'
    ORDER BY name
    """,
    conn,
)

print(tables)

conn.close()