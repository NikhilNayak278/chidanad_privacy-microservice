import sqlite3
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pii_store.sqlite3"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mappings (
            token TEXT PRIMARY KEY,
            ciphertext BLOB NOT NULL
        )
        """
    )
    return conn


def save_mapping(token: str, ciphertext: bytes) -> None:
    conn = _get_conn()
    print(f"DEBUG: Saving mapping for token: {token}")
    try:
        conn.execute(
            "INSERT OR IGNORE INTO mappings(token, ciphertext) VALUES (?, ?)",
            (token, ciphertext),
        )
        conn.commit()
        print("DEBUG: Saved mapping successfully.")
    except Exception as e:
        print(f"DEBUG: Save mapping ERROR: {e}")
        raise
    finally:
        conn.close()


def get_mapping(token: str) -> Optional[bytes]:
    conn = _get_conn()
    try:
        cur = conn.execute("SELECT ciphertext FROM mappings WHERE token = ?", (token,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()
