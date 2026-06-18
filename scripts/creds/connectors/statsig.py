"""Statsig — Console API key (key-based, no login)."""

from __future__ import annotations

from creds_lib import http
from creds_lib.status import FAIL, MISCONFIGURED, OK, Result, required_env

NAME = "statsig"
MINT_URL = "https://console.statsig.com/api_keys"
LOGIN_HINT = (
    "Key-based — no login. Create a read-only Console API key in Project "
    "Settings → API Keys, then set STATSIG_CONSOLE_API_KEY_RO in ~/.zshenv."
)


def validate() -> Result:
    env, missing = required_env("STATSIG_CONSOLE_API_KEY_RO")
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    status, _h, body = http.request(
        "GET",
        "https://statsigapi.net/console/v1/gates",
        headers={"STATSIG-API-KEY": env["STATSIG_CONSOLE_API_KEY_RO"]},
        params={"limit": 1},
    )
    j = http.json_or_text(body)
    if status in (401, 403):
        return Result(NAME, FAIL, f"{status} — invalid console key")
    if status >= 400:
        return Result(NAME, FAIL, f"/console/v1/gates HTTP {status}")

    gates = j.get("data") or [] if isinstance(j, dict) else []
    sample = gates[0].get("name") if gates else ""
    return Result(NAME, OK, "console key valid", sample=sample)
