import os
import base64
import hmac
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet

BASE_DIR = Path(__file__).resolve().parent
KEY_PATH = BASE_DIR / "secret.key"


def _load_or_create_key() -> bytes:
    if KEY_PATH.exists():
        return KEY_PATH.read_bytes()
    key = Fernet.generate_key()
    KEY_PATH.write_bytes(key)
    return key


FERNET_KEY = _load_or_create_key()
fernet = Fernet(FERNET_KEY)


def token_for_value(value: str) -> str:
    digest = hmac.new(FERNET_KEY, value.encode("utf-8"), hashlib.sha256).digest()
    tok = base64.urlsafe_b64encode(digest).decode("utf-8").rstrip("=")
    return f"TKN_{tok[:24]}"


def encrypt(value: str) -> bytes:
    return fernet.encrypt(value.encode("utf-8"))


def decrypt(blob: bytes) -> str:
    return fernet.decrypt(blob).decode("utf-8")
