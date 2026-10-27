$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\Activate.ps1

if (-not (Test-Path ".venv\.installed")) {
    pip install -q -r requirements.txt -r requirements-dev.txt
    New-Item ".venv\.installed" -ItemType File | Out-Null
}

ruff check .
pytest -q
