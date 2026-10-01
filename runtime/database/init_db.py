import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from runtime.database.db import get_connection


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, content TEXT NOT NULL)")


if __name__ == "__main__":
    init_db()
    print("Fenrir Memory Online")
