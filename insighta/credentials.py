"""
credentials.py — Read/write ~/.insighta/credentials.json

Stores:
  {
    "access_token": "...",
    "refresh_token": "...",
    "username": "...",
    "backend_url": "https://your-backend.com"
  }
"""

import json
import os
from pathlib import Path
from typing import Optional

CREDENTIALS_DIR = Path.home() / ".insighta"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials.json"
DEFAULT_BACKEND_URL = os.getenv("INSIGHTA_BACKEND_URL", "http://localhost:8000")


def load_credentials() -> dict:
    """Return stored credentials or empty dict."""
    if not CREDENTIALS_FILE.exists():
        return {}
    try:
        return json.loads(CREDENTIALS_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return {}


def save_credentials(data: dict) -> None:
    """Persist credentials atomically."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2))
    # Restrict permissions — owner read/write only
    CREDENTIALS_FILE.chmod(0o600)


def clear_credentials() -> None:
    """Remove stored credentials."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()


def get_tokens() -> tuple[Optional[str], Optional[str]]:
    """Return (access_token, refresh_token) or (None, None)."""
    creds = load_credentials()
    return creds.get("access_token"), creds.get("refresh_token")


def get_backend_url() -> str:
    creds = load_credentials()
    return creds.get("backend_url", DEFAULT_BACKEND_URL)


def get_username() -> Optional[str]:
    return load_credentials().get("username")
