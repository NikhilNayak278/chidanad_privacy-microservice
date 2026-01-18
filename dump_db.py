
import sqlite3
import os
import sys

# Add current directory to path so we can import app modules
sys.path.append(os.path.dirname(__file__))

from app.security import decrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "app", "pii_store.sqlite3")

def dump_db():
    print(f"Connecting to database at: {DB_PATH}")
    if not os.path.exists(DB_PATH):
        print("Database file not found!")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            print(f"\n--- Table: {table_name} ---")
            
            # Get columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in cursor.fetchall()]
            print(f"Columns: {columns}")
            
            # Get data
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            if not rows:
                print("(No Data)")
            else:
                for row in rows:
                    # Assuming table structure is (token, encrypted_blob)
                    # We print raw, but try to decrypt the second column if it looks like a blob
                    try:
                        token = row[0]
                        encrypted_val = row[1]
                        decrypted_val = decrypt(encrypted_val)
                        print(f"Token: {token} | Decrypted: {decrypted_val}")
                    except Exception:
                        # Fallback if decryption fails or schema is different
                        print(f"Row (Raw): {row}")
                    
        conn.close()
        
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    dump_db()
