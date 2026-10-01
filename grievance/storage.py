"""Persist only coarse aggregate fields. No identity, narrative or files."""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "analytics.sqlite3"

def connection():
    DB.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS analytics (id TEXT PRIMARY KEY, day TEXT, category TEXT, region TEXT, status TEXT)")
    return conn

def save_aggregate(case):
    with connection() as conn:
        conn.execute("INSERT OR IGNORE INTO analytics VALUES (?, ?, ?, ?, ?)",
                     (case["id"], case["created"].date().isoformat(), case["route"]["category"], case["region"], case["dispatch"]["status"]))

def aggregates():
    with connection() as conn:
        return [dict(zip(("day", "category", "region", "status", "count"), row)) for row in conn.execute(
            "SELECT day, category, region, status, COUNT(*) FROM analytics GROUP BY day, category, region, status")]
