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
        print(row)
        return row[0] if row else None
    finally:
        conn.close()


def get_mapping_fuzzy(token: str) -> Optional[bytes]:
    """
    Try to find a mapping even if the case is messed up (e.g. Title Case vs Base64).
    This is expensive but necessary if upstream mangles the token string.
    """
    # 1. Try exact match first
    exact = get_mapping(token)
    if exact:
        return exact

    # 2. Try simple case-insensitive match via DB
    conn = _get_conn()
    try:
        # SQLite LIKE is case-insensitive by default for ASCII
        cur = conn.execute("SELECT token, ciphertext FROM mappings WHERE token LIKE ?", (token,))
        rows = cur.fetchall()
        
        target_lower = token.lower()
        for cand_token, ciphertext in rows:
            if cand_token.lower() == target_lower:
                return ciphertext
        
        # 3. Fallback: Scan all (if LIKE didn't catch it due to collation)
        # Only do this if table is small? For now, do it to be safe.
        cur = conn.execute("SELECT token, ciphertext FROM mappings")
        for cand_token, ciphertext in cur:
            if cand_token.lower() == target_lower:
                return ciphertext
                
        return None
    finally:
        conn.close()
