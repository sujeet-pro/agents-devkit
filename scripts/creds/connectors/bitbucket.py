"""Bitbucket Cloud — Basic auth with Atlassian email + scoped API token.

Feeds the @aashari/mcp-server-atlassian-bitbucket server, which reads
ATLASSIAN_USER_EMAIL + ATLASSIAN_API_TOKEN (mapped in .mcp.json from
ATLASSIAN_USERNAME + BITBUCKET_API_TOKEN). Bitbucket Cloud only — the
server hardcodes https://api.bitbucket.org, so there is no base-URL var.
"""

from __future__ import annotations

import os

from creds_lib import http
from creds_lib.status import FAIL, MISCONFIGURED, OK, Result, required_env

NAME = "bitbucket"
API = "https://api.bitbucket.org/2.0"
MINT_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
LOGIN_HINT = (
    "Key-based — no login. Create a scoped API token at id.atlassian.com "
    "(grant Bitbucket read scopes), then set BITBUCKET_API_TOKEN and "
    "ATLASSIAN_USERNAME (your email) in ~/.zshenv. Optionally set "
    "BITBUCKET_DEFAULT_WORKSPACE to a workspace slug (e.g. acme-team)."
)


def validate() -> Result:
    env, missing = required_env("ATLASSIAN_USERNAME", "BITBUCKET_API_TOKEN")
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    auth = http.basic_auth(env["ATLASSIAN_USERNAME"], env["BITBUCKET_API_TOKEN"])
    accept = {"Authorization": auth, "Accept": "application/json"}

    # Preferred access check: list repos in the configured workspace. This is the
    # core read scope the MCP server relies on — and, unlike /workspaces/{ws} or
    # /user, it does not require the (often un-granted) account/workspace scopes.
    ws = (os.environ.get("BITBUCKET_DEFAULT_WORKSPACE") or "").strip()
    if ws:
        status, _h, body = http.request(
            "GET", f"{API}/repositories/{ws}", headers=accept, params={"pagelen": 1}
        )
        j = http.json_or_text(body)
        if status == 401:
            return Result(NAME, FAIL, "401 — bad email/token")
        if status == 403:
            return Result(NAME, FAIL, f"403 — token lacks repository read scope for {ws!r}")
        if status == 404:
            return Result(NAME, FAIL, f"workspace {ws!r} not found")
        if status >= 400:
            return Result(NAME, FAIL, f"repositories/{ws} HTTP {status}")
        vals = j.get("values") if isinstance(j, dict) else None
        sample = ""
        if isinstance(vals, list) and vals and isinstance(vals[0], dict):
            sample = vals[0].get("full_name") or vals[0].get("name") or ""
        return Result(NAME, OK, f"repos ok ({ws})", sample=sample)

    # No workspace configured: a 403 here still proves the email/token pair is
    # accepted (401 would mean rejected) — the token just lacks the account scope.
    status, _h2, body = http.request("GET", f"{API}/user", headers=accept)
    j = http.json_or_text(body)
    if status == 401:
        return Result(NAME, FAIL, "401 — bad email/token")
    if status == 403:
        return Result(NAME, OK, "creds accepted; set BITBUCKET_DEFAULT_WORKSPACE to verify repo access")
    if status >= 400:
        return Result(NAME, FAIL, f"/user HTTP {status}")
    who = j.get("display_name") if isinstance(j, dict) else ""
    return Result(NAME, OK, "user ok", sample=who)
