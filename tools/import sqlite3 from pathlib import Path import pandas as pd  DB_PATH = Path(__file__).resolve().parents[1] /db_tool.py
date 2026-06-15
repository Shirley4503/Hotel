import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path(__file__).resolve().parents[1] / "hotel.db"


def run_query(query: str, params=None) -> pd.DataFrame:
    """
    Run a read-only SQL query against the hotel SQLite database.
    """
    if params is None:
        params = []

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn, params=params)
    finally:
        conn.close()

    return df


def get_scalar(query: str, params=None):
    """
    Run a query that returns one value.
    """
    df = run_query(query, params)
    if df.empty:
        return None
    return df.iloc[0, 0]
