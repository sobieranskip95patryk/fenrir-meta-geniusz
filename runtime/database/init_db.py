import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from runtime.database.db import get_connection


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY, category TEXT NOT NULL DEFAULT 'fact',
            title TEXT NOT NULL DEFAULT '', content TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        columns = {row[1] for row in conn.execute("PRAGMA table_info(memories)")}
        for name, definition in (("category", "TEXT"), ("title", "TEXT"),
                                 ("created_at", "TEXT"), ("updated_at", "TEXT")):
            if name not in columns:
                conn.execute(f"ALTER TABLE memories ADD COLUMN {name} {definition}")
        conn.execute("UPDATE memories SET category = COALESCE(category, 'fact'), title = COALESCE(title, ''), created_at = COALESCE(created_at, CURRENT_TIMESTAMP), updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)")
        conn.execute("""CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE, path TEXT NOT NULL,
            ide TEXT NOT NULL DEFAULT 'code', terminal TEXT NOT NULL DEFAULT 'powershell',
            notes TEXT NOT NULL DEFAULT ''
        )""")


if __name__ == "__main__":
    init_db()
    print("Fenrir Memory Online")
