#!/usr/bin/env python3
"""Generate/exchange/verify the HDE Google OAuth scopes without printing tokens.

This is intentionally stdlib-only so it can run on the Hermes host without
installing packages. It never prints access_token, refresh_token, or client
secret values. Generated credentials are written outside the repository.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/analytics.edit",
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/tagmanager.edit.containers",
    "https://www.googleapis.com/auth/tagmanager.manage.accounts",
    "https://www.googleapis.com/auth/tagmanager.readonly",
    "https://www.googleapis.com/auth/webmasters",
    "https://www.googleapis.com/auth/siteverification",
]

DEFAULT_TOKEN_PATH = pathlib.Path(
    os.environ.get(
        "HDE_GOOGLE_OAUTH_TOKEN_PATH",
        "/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json",
    )
)
DEFAULT_CLIENT_SECRETS = os.environ.get(
    "HDE_GOOGLE_OAUTH_CLIENT_SECRETS",
    "/home/ubuntu/mounts/synology-photo/Antigravity/credentials.json",
)
AUTH_URI = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URI = "https://oauth2.googleapis.com/token"
TOKENINFO_URI = "https://oauth2.googleapis.com/tokeninfo"
REDIRECT_URI = "http://localhost"


class OAuthError(RuntimeError):
    pass


def load_client(path: str) -> dict[str, str]:
    raw = json.loads(pathlib.Path(path).read_text())
    data = raw.get("installed") or raw.get("web") or raw
    required = ["client_id", "client_secret"]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise OAuthError(f"client secrets file is missing: {', '.join(missing)}")
    return {"client_id": data["client_id"], "client_secret": data["client_secret"]}


def request_json(url: str, *, data: dict[str, str] | None = None, token: str | None = None) -> dict:
    encoded = None
    headers: dict[str, str] = {}
    if data is not None:
        encoded = urllib.parse.urlencode(data).encode()
        headers["Content-Type"] = "application/x-www-form-urlencoded"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, data=encoded, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read(500).decode("utf-8", "replace")
        raise OAuthError(f"HTTP {exc.code} from {url}: {body}") from exc


def build_auth_url(client_id: str, scopes: list[str]) -> str:
    params = {
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(scopes),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    return f"{AUTH_URI}?{urllib.parse.urlencode(params)}"


def extract_code(value: str) -> str:
    value = value.strip()
    if value.startswith("http://") or value.startswith("https://"):
        parsed = urllib.parse.urlparse(value)
        qs = urllib.parse.parse_qs(parsed.query)
        if qs.get("code"):
            return qs["code"][0]
        raise OAuthError("redirect URL did not contain a code= parameter")
    return value


def exchange_code(client: dict[str, str], code_or_url: str) -> dict:
    code = extract_code(code_or_url)
    token = request_json(
        TOKEN_URI,
        data={
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
    )
    if "refresh_token" not in token:
        raise OAuthError("Google did not return a refresh_token; re-run with prompt=consent")
    return token


def refresh_token(client: dict[str, str], token_doc: dict) -> str:
    refresh = token_doc.get("refresh_token")
    if not refresh:
        raise OAuthError("token file has no refresh_token")
    refreshed = request_json(
        TOKEN_URI,
        data={
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "refresh_token": refresh,
            "grant_type": "refresh_token",
        },
    )
    access = refreshed.get("access_token")
    if not access:
        raise OAuthError("refresh response did not contain access_token")
    return access


def tokeninfo(access_token: str) -> dict:
    return request_json(f"{TOKENINFO_URI}?{urllib.parse.urlencode({'access_token': access_token})}")


def save_authorized_user(client: dict[str, str], token: dict, path: pathlib.Path) -> None:
    doc = {
        "type": "authorized_user",
        "client_id": client["client_id"],
        "client_secret": client["client_secret"],
        "refresh_token": token["refresh_token"],
        "created_at": int(time.time()),
        "note": "HDE GA/GTM/Search Console OAuth credential; do not commit.",
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    path.chmod(stat.S_IRUSR | stat.S_IWUSR)


def summarize_scopes(scope_text: str, required: list[str]) -> tuple[list[str], list[str]]:
    granted = set(scope_text.split())
    return sorted(granted.intersection(required)), sorted(set(required) - granted)


def cmd_url(args: argparse.Namespace) -> int:
    client = load_client(args.client_secrets)
    print(build_auth_url(client["client_id"], args.scopes))
    return 0


def cmd_exchange(args: argparse.Namespace) -> int:
    client = load_client(args.client_secrets)
    token = exchange_code(client, args.code)
    access = token.get("access_token")
    info = tokeninfo(access) if access else {}
    has, missing = summarize_scopes(info.get("scope", ""), args.scopes)
    save_authorized_user(client, token, args.token_path)
    print(f"saved_token_path={args.token_path}")
    print(f"authenticated_email={info.get('email', '<unknown>')}")
    print(f"has_required_scopes={json.dumps(has)}")
    print(f"missing_required_scopes={json.dumps(missing)}")
    if missing:
        return 2
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    client = load_client(args.client_secrets)
    token_doc = json.loads(args.token_path.read_text())
    access = refresh_token(client, token_doc)
    info = tokeninfo(access)
    has, missing = summarize_scopes(info.get("scope", ""), args.scopes)
    print(f"token_path={args.token_path}")
    print(f"authenticated_email={info.get('email', '<unknown>')}")
    print(f"has_required_scopes={json.dumps(has)}")
    print(f"missing_required_scopes={json.dumps(missing)}")
    return 2 if missing else 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--client-secrets", default=DEFAULT_CLIENT_SECRETS)
    p.add_argument("--token-path", type=pathlib.Path, default=DEFAULT_TOKEN_PATH)
    p.add_argument("--scopes", nargs="+", default=DEFAULT_SCOPES)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("url", help="print the consent URL; no tokens are created").set_defaults(func=cmd_url)
    ex = sub.add_parser("exchange", help="exchange a human-returned code or localhost redirect URL")
    ex.add_argument("--code", required=True, help="authorization code or failed localhost redirect URL")
    ex.set_defaults(func=cmd_exchange)
    sub.add_parser("verify", help="refresh and verify a saved token file without printing tokens").set_defaults(func=cmd_verify)
    return p


def main() -> int:
    args = parser().parse_args()
    try:
        return args.func(args)
    except OAuthError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
