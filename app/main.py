from typing import Any, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from .pseudonymizer import deidentify as do_deidentify, reidentify as do_reidentify

ALLOWED_TYPES = {
    "Medical Report",
    "Lab Report",
    "Discharge Summary",
    "Admission Slip",
}

app = FastAPI(title="PII Pseudonymization Service", version="1.0.0")


@app.get("/health")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


def _validate_document(doc: Dict[str, Any]) -> None:
    if not isinstance(doc, dict):
        raise HTTPException(status_code=400, detail="Body must be a JSON object")
    dtype = doc.get("Document_Type")
    if dtype not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported or missing Document_Type")
    pii = doc.get("PII")
    if not isinstance(pii, dict):
        raise HTTPException(status_code=400, detail="Missing or invalid PII object")


@app.post("/deidentify")
async def deidentify(doc: Dict[str, Any]) -> JSONResponse:
    _validate_document(doc)
    out = do_deidentify(doc)
    return JSONResponse(content=out)


@app.post("/reidentify")
async def reidentify(doc: Dict[str, Any]) -> JSONResponse:
    _validate_document(doc)
    out = do_reidentify(doc)
    return JSONResponse(content=out)


# To run locally: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
