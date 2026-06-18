"""Atlassian (Jira + Confluence) — Basic auth with email + API token."""

from __future__ import annotations

import os

from creds_lib import http
from creds_lib.status import FAIL, MISCONFIGURED, OK, Result, required_env

NAME = "atlassian"
MINT_URL = "https://id.atlassian.com/manage-profile/security/api-tokens"
LOGIN_HINT = (
    "Key-based — no login. Create an API token at id.atlassian.com, then set "
    "ATLASSIAN_USERNAME (your email), ATLASSIAN_API_TOKEN, JIRA_URL and "
    "CONFLUENCE_URL in ~/.zshenv."
)


def validate() -> Result:
    env, missing = required_env("JIRA_URL", "ATLASSIAN_USERNAME", "ATLASSIAN_API_TOKEN")
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    auth = http.basic_auth(env["ATLASSIAN_USERNAME"], env["ATLASSIAN_API_TOKEN"])
    accept = {"Authorization": auth, "Accept": "application/json"}

    # Jira — authenticated user lookup.
    jira = env["JIRA_URL"].rstrip("/")
    status, _h, body = http.request("GET", f"{jira}/rest/api/3/myself", headers=accept)
    j = http.json_or_text(body)
    if status in (401, 403):
        return Result(NAME, FAIL, f"jira /myself {status} — bad email/token")
    if status >= 400:
        return Result(NAME, FAIL, f"jira /myself HTTP {status}")
    who = j.get("displayName") if isinstance(j, dict) else ""

    # Confluence — optional, only if CONFLUENCE_URL is configured.
    extra = ""
    conf = (os.environ.get("CONFLUENCE_URL") or "").rstrip("/")
    if conf:
        cs, _h2, _cb = http.request(
            "GET", f"{conf}/rest/api/space", headers=accept, params={"limit": 1}
        )
        extra = " + confluence ok" if cs < 400 else f" + confluence HTTP {cs}"

    return Result(NAME, OK, f"jira ok{extra}", sample=who)
