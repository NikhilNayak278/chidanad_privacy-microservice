.\acenv\Scripts\Activate.ps1
# if ($LASTEXITCODE -eq 0) {
uvicorn app.main:app --port 5001 --reload
# }
