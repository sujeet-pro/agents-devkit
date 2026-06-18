"""Looker — API3 client_id/client_secret (key-based, no browser login)."""

from __future__ import annotations

from creds_lib import http
from creds_lib.status import FAIL, MISCONFIGURED, OK, Result, required_env

NAME = "looker"
MINT_URL = "https://your.cloud.looker.com/admin/users"  # Admin → Users → API Keys
LOGIN_HINT = (
    "Key-based — no login. In Looker, open Admin → Users → your user → Edit "
    "Keys, generate an API3 key, then set LOOKER_BASE_URL, LOOKER_CLIENT_ID "
    "and LOOKER_CLIENT_SECRET in ~/.zshenv."
)


def _login_token(base: str, cid: str, secret: str) -> tuple[int, str | None]:
    status, _h, body = http.request(
        "POST",
        f"{base}/api/4.0/login",
        data={"client_id": cid, "client_secret": secret},
    )
    j = http.json_or_text(body)
    token = j.get("access_token") if isinstance(j, dict) else None
    return status, token


def validate() -> Result:
    env, missing = required_env("LOOKER_BASE_URL", "LOOKER_CLIENT_ID", "LOOKER_CLIENT_SECRET")
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    base = env["LOOKER_BASE_URL"].rstrip("/")
    status, token = _login_token(base, env["LOOKER_CLIENT_ID"], env["LOOKER_CLIENT_SECRET"])
    # Some self-hosted instances expose the API on :19999.
    if status == 404 and ":19999" not in base:
        status, token = _login_token(
            f"{base}:19999", env["LOOKER_CLIENT_ID"], env["LOOKER_CLIENT_SECRET"]
        )
        if token:
            base = f"{base}:19999"

    if status in (401, 403) or (status >= 400 and not token):
        return Result(NAME, FAIL, f"/login {status} — bad client_id/secret")
    if not token:
        return Result(NAME, FAIL, f"/login HTTP {status} — no access_token")

    status, _h, body = http.request(
        "GET", f"{base}/api/4.0/user", headers={"Authorization": f"Bearer {token}"}
    )
    j = http.json_or_text(body)
    if status >= 400:
        return Result(NAME, FAIL, f"/user HTTP {status}")
    who = j.get("display_name") if isinstance(j, dict) else ""
    return Result(NAME, OK, "api3 login ok", sample=who)
