"""Datadog — API key + Application key (key-based, no login)."""

from __future__ import annotations

import os
import random

from creds_lib import http
from creds_lib.status import FAIL, MISCONFIGURED, OK, Result, required_env

NAME = "datadog"
MINT_URL = "https://app.datadoghq.com/organization-settings/api-keys"
LOGIN_HINT = (
    "Key-based — no login. Create an API key and an Application key in "
    "Organization Settings, then set DATADOG_API_KEY / DATADOG_APP_KEY in ~/.zshenv."
)


def validate() -> Result:
    env, missing = required_env("DATADOG_API_KEY", "DATADOG_APP_KEY")
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    site = os.environ.get("DATADOG_SITE", "datadoghq.com")
    headers = {
        "DD-API-KEY": env["DATADOG_API_KEY"],
        "DD-APPLICATION-KEY": env["DATADOG_APP_KEY"],
    }

    # 1) API key validity.
    status, _h, body = http.request(
        "GET", f"https://api.{site}/api/v1/validate", headers=headers
    )
    j = http.json_or_text(body)
    if status == 403:
        return Result(NAME, FAIL, "403 — invalid API key")
    if status >= 400 or not (isinstance(j, dict) and j.get("valid")):
        return Result(NAME, FAIL, f"/api/v1/validate HTTP {status}")

    # 2) App key validity (dashboards needs both keys).
    status, _h, body = http.request(
        "GET", f"https://api.{site}/api/v1/dashboard", headers=headers
    )
    j = http.json_or_text(body)
    if status == 403:
        return Result(NAME, FAIL, "API key ok but Application key rejected (403)")
    if status >= 400:
        return Result(NAME, FAIL, f"/api/v1/dashboard HTTP {status}")

    boards = j.get("dashboards") or [] if isinstance(j, dict) else []
    sample = random.choice(boards).get("title") if boards else ""
    return Result(NAME, OK, "api + app keys valid", sample=sample)
