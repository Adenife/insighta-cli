"""
api.py — Token-aware HTTP client with automatic refresh.

Every request:
  1. Attaches Bearer token from credentials
  2. On 401 → attempts silent refresh
  3. If refresh fails → prompts re-login
"""
import httpx
from typing import Optional, Any

from .credentials import (
    get_tokens,
    save_credentials,
    clear_credentials,
    get_backend_url,
)
from .output import print_error, print_info


API_VERSION_HEADER = {"X-API-Version": "1"}


def _auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}", **API_VERSION_HEADER}


def _do_refresh(backend_url: str, refresh_token: str) -> Optional[str]:
    """
    Attempt a token refresh. Returns the new access token, or None on failure.
    """
    try:
        resp = httpx.post(
            f"{backend_url}/auth/refresh",
            json={"refresh_token": refresh_token},
            timeout=10.0,
        )
        if resp.status_code == 200:
            data = resp.json()
            access_token = data["access_token"]
            new_refresh = data["refresh_token"]
            # Persist rotated tokens
            from .credentials import load_credentials
            creds = load_credentials()
            creds["access_token"] = access_token
            creds["refresh_token"] = new_refresh
            save_credentials(creds)
            return access_token
    except Exception:
        pass
    return None


def request(
    method: str,
    path: str,
    params: Optional[dict] = None,
    json: Optional[dict] = None,
    stream: bool = False,
) -> Any:
    """
    Make an authenticated API request.

    Args:
        method: HTTP method (GET, POST, DELETE …)
        path: Path relative to backend, e.g. '/api/profiles'
        params: Query string parameters
        json: JSON body
        stream: If True, return the raw Response for streaming (CSV export)

    Returns:
        Parsed JSON dict, or raw Response if stream=True.

    Raises:
        SystemExit on auth failure prompting re-login.
    """
    access_token, refresh_token = get_tokens()
    backend_url = get_backend_url()

    if not access_token:
        print_error("Not logged in. Run: insighta login")
        raise SystemExit(1)

    url = f"{backend_url}{path}"

    def _make_request(token: str):
        return httpx.request(
            method,
            url,
            headers=_auth_headers(token),
            params=params,
            json=json,
            timeout=30.0,
            follow_redirects=True,
        )

    resp = _make_request(access_token)

    if resp.status_code == 401 and refresh_token:
        print_info("Access token expired — refreshing…")
        new_access = _do_refresh(backend_url, refresh_token)
        if new_access:
            resp = _make_request(new_access)
        else:
            clear_credentials()
            print_error("Session expired. Please run: insighta login")
            raise SystemExit(1)

    if stream:
        return resp

    if resp.status_code >= 400:
        try:
            body = resp.json()
            msg = body.get("message", resp.text)
        except Exception:
            msg = resp.text
        print_error(f"API error ({resp.status_code}): {msg}")
        raise SystemExit(1)

    return resp.json()
