"""
auth.py — CLI auth commands: login, logout, whoami.

Flow:
  1. Generate PKCE (verifier + challenge)
  2. Open backend /auth/github
  3. Local server receives ?code=&state=
  4. CLI sends code + verifier to /auth/github/exchange
  5. Store tokens locally
"""

import hashlib
import base64
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import click
import httpx

from .credentials import (
    save_credentials,
    clear_credentials,
    get_backend_url,
    get_tokens,
)
from .output import print_success, print_error, print_info, console

CALLBACK_PORT = 8899
CALLBACK_HOST = "localhost"


def _generate_pkce() -> tuple[str, str]:
    verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(verifier.encode()).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return verifier, challenge


def _generate_state() -> str:
    return secrets.token_urlsafe(32)


def login(backend_url: str):
    code_verifier, code_challenge = _generate_pkce()
    state = _generate_state()

    result: dict = {}
    server_ready = threading.Event()

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)

            if parsed.path == "/callback":
                qs = parse_qs(parsed.query)
                result["code"] = qs.get("code", [None])[0]
                result["state"] = qs.get("state", [None])[0]

                html = (
                    b"<html><body style='font-family:sans-serif;text-align:center;padding:60px'>"
                    b"<h3>Login Successful</h3>"
                    b"<p>You can safely close this tab.</p>"
                    b"</body></html>"
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(html)

        def log_message(self, *args):
            pass

    server = HTTPServer((CALLBACK_HOST, CALLBACK_PORT), CallbackHandler)

    def _serve():
        server_ready.set()
        server.handle_request()

    thread = threading.Thread(target=_serve, daemon=True)
    thread.start()
    server_ready.wait()

    oauth_url = (
        f"{backend_url}/auth/github"
        f"?redirect_uri=http://localhost:{CALLBACK_PORT}/callback"
        f"&code_challenge={code_challenge}"
        f"&state={state}"
    )

    print_info("Opening GitHub login in browser...")
    webbrowser.open(oauth_url)

    console.print(f"[dim]If not opened:[/dim] {oauth_url}")

    thread.join(timeout=120)

    code = result.get("code")
    returned_state = result.get("state")

    if not code:
        print_error("Login failed or timed out.")
        raise SystemExit(1)

    if returned_state != state:
        print_error("State mismatch. Possible CSRF attack.")
        raise SystemExit(1)

    try:
        # ✅ FIX: use POST instead of GET + JSON body
        resp = httpx.post(
            f"{backend_url}/auth/github/exchange",
            json={
                "code": code,
                "code_verifier": code_verifier,
            },
            timeout=20.0,
        )
        resp.raise_for_status()
        data = resp.json()

    except Exception as e:
        print_error(f"Token exchange failed: {e}")
        raise SystemExit(1)

    save_credentials(
        {
            "access_token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "username": data.get("username", ""),
            "backend_url": backend_url,
        }
    )

    print_success(f"Logged in as @{data.get('username', 'unknown')}")


@click.command("login")
@click.option("--backend", default=None)
def login_cmd(backend):
    url = backend or get_backend_url()
    login(url)


@click.command("logout")
def logout_cmd():
    access_token, refresh_token = get_tokens()

    if not refresh_token:
        print_info("Not logged in.")
        return

    backend_url = get_backend_url()

    try:
        httpx.post(
            f"{backend_url}/auth/logout",
            json={"refresh_token": refresh_token},
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10.0,
        )
    except Exception:
        pass

    clear_credentials()
    print_success("Logged out.")


@click.command("whoami")
def whoami_cmd():
    from . import api

    data = api.request("GET", "/auth/me")
    user = data.get("data", {})

    console.print(
        f"[bold cyan]@{user.get('username')}[/bold cyan] "
        f"· role=[yellow]{user.get('role')}[/yellow] "
        f"· email={user.get('email') or '(none)'}"
    )
