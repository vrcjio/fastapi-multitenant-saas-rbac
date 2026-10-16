import sqlite3
from typing import Generator
from app.core.config import settings

# Raw DB path extract from SQLite URL
DB_PATH = settings.DATABASE_URL.replace("sqlite:///", "")


def get_db_connection() -> sqlite3.Connection:
    """
    Creates and returns a new sqlite3 connection.
    - Enables foreign keys support.
    - Sets row_factory to sqlite3.Row for dictionary-like column access.
    """
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    FastAPI dependency that yields a database connection per request
    and guarantees safe closure after the request completes.
    """
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()