"""Snowflake — programmatic access token against the SQL API (best effort).

The MCP server reads a connections.toml (in $SNOWFLAKE_HOME) plus a bearer
token in $SNOWFLAKE_ACCESS_TOKEN. These tokens are short-lived, so the most
common failure is expiry — re-mint and update ~/.zshenv (see LOGIN_HINT).
"""

from __future__ import annotations

import base64
import json
import os
import re
import time
from pathlib import Path

from creds_lib import http
from creds_lib.status import FAIL, LOGIN, MISCONFIGURED, OK, Result, required_env

NAME = "snowflake"
MINT_URL = "https://app.snowflake.com"
LOGIN_HINT = (
    "The access token is short-lived. Re-mint it (Snowsight, or the `snow` "
    "CLI / connections.toml flow) and update SNOWFLAKE_ACCESS_TOKEN in "
    "~/.zshenv. SNOWFLAKE_HOME must contain a connections.toml with an "
    "[<SNOWFLAKE_CONNECTION_NAME>] section that has `account = ...`."
)


def _account_from_connections(home: str | None, conn: str) -> str | None:
    if not home:
        return None
    toml_path = Path(os.path.expanduser(home)) / "connections.toml"
    if not toml_path.exists():
        return None
    text = toml_path.read_text(encoding="utf-8")

    # Find the requested [section]; fall back to the first account = line.
    section_re = re.compile(r"^\s*\[(?P<name>[^\]]+)\]\s*$")
    account_re = re.compile(r'^\s*account\s*=\s*["\']?(?P<acct>[^"\'#\s]+)')
    current = None
    first_account = None
    target_account = None
    for line in text.splitlines():
        sm = section_re.match(line)
        if sm:
            current = sm.group("name").strip().strip('"').strip("'")
            continue
        am = account_re.match(line)
        if am:
            acct = am.group("acct")
            first_account = first_account or acct
            if conn and current == conn:
                target_account = acct
    return target_account or first_account


def _account_host(account: str) -> str:
    if account.endswith("snowflakecomputing.com"):
        return account
    # account locators use underscores in the toml but dots in the host.
    return f"{account.replace('_', '-')}.snowflakecomputing.com"


def _token_expired(token: str) -> tuple[bool, str]:
    """Decode a JWT exp claim if present. Returns (expired, human_exp)."""
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        claims = json.loads(base64.urlsafe_b64decode(payload))
        exp = int(claims.get("exp", 0))
        if exp:
            human = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(exp))
            return (exp < time.time(), human)
    except Exception:  # noqa: BLE001 — not a JWT / undecodable
        pass
    return (False, "")


def validate() -> Result:
    env, missing = required_env("SNOWFLAKE_ACCESS_TOKEN")
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    token = env["SNOWFLAKE_ACCESS_TOKEN"]
    expired, human_exp = _token_expired(token)
    if expired:
        return Result(NAME, LOGIN, f"access token expired ({human_exp}) — re-mint it")

    home = os.environ.get("SNOWFLAKE_HOME")
    conn = os.environ.get("SNOWFLAKE_CONNECTION_NAME", "")
    account = _account_from_connections(home, conn)
    if not account:
        return Result(
            NAME,
            MISCONFIGURED,
            "couldn't read `account` from $SNOWFLAKE_HOME/connections.toml",
        )

    # The SQL API token-type header must match how the token was minted, and
    # there's no reliable way to tell a PAT from an OAuth token by inspection.
    # Try the PAT type first (this deployment's case), fall back to OAUTH.
    host = _account_host(account)

    def _probe(token_type: str):
        return http.request(
            "POST",
            f"https://{host}/api/v2/statements",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Snowflake-Authorization-Token-Type": token_type,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            params={"async": "false"},
            json_body={"statement": "SELECT 1", "timeout": 20},
            timeout=30.0,
        )

    status, _h, body = _probe("PROGRAMMATIC_ACCESS_TOKEN")
    if status in (401, 403):
        status, _h, body = _probe("OAUTH")
    if status in (401, 403):
        exp_note = f" (token exp {human_exp})" if human_exp else ""
        return Result(NAME, FAIL, f"{status} — token rejected{exp_note}; re-mint")
    if status >= 400:
        j = http.json_or_text(body)
        msg = j.get("message") if isinstance(j, dict) else f"HTTP {status}"
        return Result(NAME, FAIL, f"SQL API {status}: {msg}")
    return Result(NAME, OK, "SELECT 1 ok", sample=account)
