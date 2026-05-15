import sqlite3
from pathlib import Path

from config.settings import DB_PATH


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema_path = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
    schema = schema_path.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(schema)
