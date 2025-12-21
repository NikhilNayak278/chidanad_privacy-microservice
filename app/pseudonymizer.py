from typing import Any, Dict
from .security import token_for_value, encrypt, decrypt
from . import storage

TOKEN_PREFIX = "TKN_"


def _is_token(value: str) -> bool:
    return isinstance(value, str) and value.startswith(TOKEN_PREFIX)


def _pseudo_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if _is_token(value):
        return value
    token = token_for_value(value)
    storage.save_mapping(token, encrypt(value))
    return token


def _restore_value(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if not _is_token(value):
        return value
    blob = storage.get_mapping(value)
    return decrypt(blob) if blob is not None else value


PII_KEYS_BY_DOC = {
    "Medical Report": ["Name", "DOB", "ID", "Date"],
    "Lab Report": ["Name", "DOB", "ID", "Date"],
    "Discharge Summary": ["Name", "DOB", "ID", "Admission_Date", "Discharge_Date"],
    "Admission Slip": ["Name", "DOB", "ID", "Date"],
}


def deidentify(doc: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(doc)
    dtype = out.get("Document_Type")
    pii = out.get("PII")
    if isinstance(pii, dict) and dtype in PII_KEYS_BY_DOC:
        pii_out = dict(pii)
        for k in PII_KEYS_BY_DOC[dtype]:
            if k in pii_out and pii_out[k] is not None:
                pii_out[k] = _pseudo_value(pii_out[k])
        out["PII"] = pii_out
    return out


def reidentify(doc: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(doc)
    dtype = out.get("Document_Type")
    pii = out.get("PII")
    if isinstance(pii, dict) and dtype in PII_KEYS_BY_DOC:
        pii_out = dict(pii)
        for k in PII_KEYS_BY_DOC[dtype]:
            if k in pii_out and pii_out[k] is not None:
                pii_out[k] = _restore_value(pii_out[k])
        out["PII"] = pii_out
    return out
