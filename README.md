# PII Pseudonymization Microservice

A small FastAPI-based microservice that deidentifies and reidentifies PII in four medical document formats using reversible pseudonymization.

- Deidentify: Replaces only PII fields in `PII` with stable tokens like `TKN_...`
- Reidentify: Restores original PII from tokens
- Persistence: Encrypted PII values are stored in SQLite, keyed by token
- Security: Symmetric key (Fernet) stored at `app/secret.key`

## Supported Document Types
- Medical Report
- Lab Report
- Discharge Summary
- Admission Slip

Only fields inside the `PII` object are transformed.

### PII keys by type
- Medical Report: `Name`, `DOB`, `ID`, `Date`
- Lab Report: `Name`, `DOB`, `ID`, `Date`
- Discharge Summary: `Name`, `DOB`, `ID`, `Admission_Date`, `Discharge_Date`
- Admission Slip: `Name`, `DOB`, `ID`, `Date`

## Project Structure
```
Privacy - Windsurf/
├─ app/
│  ├─ main.py              # FastAPI app and endpoints
│  ├─ pseudonymizer.py     # Deidentify/reidentify logic
│  ├─ security.py          # Token generation + Fernet encryption
│  ├─ storage.py           # SQLite persistence for token -> ciphertext
│  ├─ secret.key           # Auto-created symmetric key (keep safe!)
│  └─ pii_store.sqlite3    # Auto-created SQLite database
└─ requirements.txt        # Python dependencies
```

## Requirements
- Python 3.9+

## Setup (Windows)
1) Create and activate a virtual environment (optional but recommended)
```
python -m venv .venv
.venv\Scripts\activate
```

2) Install dependencies
```
pip install -r requirements.txt
```

3) Run the API locally
```
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4) Health check
```
curl http://127.0.0.1:8000/health
```

## API

### POST /deidentify
- Input: One of the four supported JSON formats
- Output: Same structure with only PII fields in `PII` replaced by tokens

Example request (Medical Report):
```json
{
  "Document_Type": "Medical Report",
  "PII": {"Name": "John Doe", "DOB": "1990-01-01", "ID": "MRN-1234", "Date": "2024-12-01"},
  "Disease_disorder": ["Hypertension"],
  "Medication": ["Lisinopril"],
  "Dosage": ["10mg"],
  "Procedure": ["ECG"]
}
```

Example response:
```json
{
  "Document_Type": "Medical Report",
  "PII": {
    "Name": "TKN_...",
    "DOB": "TKN_...",
    "ID": "TKN_...",
    "Date": "TKN_..."
  },
  "Disease_disorder": ["Hypertension"],
  "Medication": ["Lisinopril"],
  "Dosage": ["10mg"],
  "Procedure": ["ECG"]
}
```

### POST /reidentify
- Input: A previously deidentified document that contains `TKN_...` tokens in `PII`
- Output: Same structure with tokens replaced by original PII (if mapping exists)

## Design & Security
- Tokens: Deterministic HMAC (with the service key) over the PII value, base64-url encoded and prefixed with `TKN_`. The same input string yields the same token.
- Encryption: Original values are encrypted using Fernet (symmetric AES + HMAC) before being stored in SQLite.
- Key management: The key is stored at `app/secret.key` and is generated automatically on first run. Anyone with both the DB and the key can reidentify; protect both.
- Persistence: SQLite DB is `app/pii_store.sqlite3`. You can back it up and migrate off-device if needed. DB records are idempotent (INSERT OR IGNORE).

## Key Rotation (manual procedure)
If you need to rotate the key, consider this approach:
1) Stop the service.
2) Export all mappings by decrypting with the current key.
3) Generate a new key file and restart the service in a migration mode/script.
4) Re-encrypt and reinsert the values with the new key, recreating tokens if you change the HMAC key.
5) Verify and then archive the old key securely.

Note: Changing the key changes both encryption and token derivation. If stable tokens across rotations are required, you need to separate the HMAC key (for token derivation) from the encryption key and rotate them independently. The provided implementation uses one key for both.

## Backups
- Backup both files to preserve reidentification capability:
  - `app/secret.key`
  - `app/pii_store.sqlite3`

## Limitations
- Only string values inside `PII` are transformed; non-strings are left as-is.
- Unknown `Document_Type` or malformed JSON returns 400.
- If a token is provided with no mapping in the DB, reidentify will leave it unchanged.

## Extending
- Add new `Document_Type`: Update the `PII_KEYS_BY_DOC` mapping in `app/pseudonymizer.py`.
- Validate payloads strictly: Introduce Pydantic models for each type in `app/main.py`.
- External DB: Replace `storage.py` with a proper RDBMS or key-value store.
- KMS/HSM: Load encryption/HMAC keys from a secure secrets manager.

## Testing (quick manual)
1) Start the server.
2) Deidentify:
```
curl -s -X POST http://127.0.0.1:8000/deidentify -H "Content-Type: application/json" -d "{\n  \"Document_Type\": \"Lab Report\",\n  \"PII\": {\"Name\": \"Alice\", \"DOB\": \"1992-05-12\", \"ID\": \"LAB-9\", \"Date\": \"2025-01-10\"},\n  \"Lab_Tests\": [{\"Name\": \"HbA1c\", \"Value\": \"5.2\", \"Unit\": \"%\", \"Reference_Range\": \"4-5.6\"}]\n}"
```
3) Reidentify: Take the response from step 2 and POST it to `/reidentify`.

## Troubleshooting
- 400 Unsupported or missing Document_Type: Ensure `Document_Type` is exactly one of the four supported values.
- Tokens not reidentifying: Ensure `app/secret.key` and `app/pii_store.sqlite3` are present and unchanged; tokens must exist in the DB.
- Permission issues on Windows: Run the terminal with appropriate permissions, or move the project out of protected folders.

## License
This project is provided as-is without warranty; choose and add a suitable license for your organization as needed.
