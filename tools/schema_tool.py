import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "hotel.db"


def get_database_schema() -> str:
    """
    Return a readable schema summary from the SQLite database.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """).fetchall()

    schema_lines = []

    for (table_name,) in tables:
        schema_lines.append(f"\nTable: {table_name}")

        columns = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            pk = " PRIMARY KEY" if col[5] else ""
            schema_lines.append(f"- {col_name}: {col_type}{pk}")

    conn.close()
    return "\n".join(schema_lines)


def get_table_names() -> list[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    rows = cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name;
    """).fetchall()
    conn.close()
    return [r[0] for r in rows]
