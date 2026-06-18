"""Slack — validates bot/user tokens; rotates app-config tokens.

`.mcp.json` consumes SLACK_BOT_TOKEN (xoxb-) and SLACK_USER_TOKEN (xoxp-).
Those are minted via OAuth (an interactive login — see LOGIN_HINT). What this
connector *can* automate is rotating the app-configuration tokens that Slack
itself rotates on a schedule: read SLACK_APP_CONFIG_REFRESH_TOKEN_CRED, call
tooling.tokens.rotate, and write the new access+refresh pair back to ~/.zshenv.
"""

from __future__ import annotations

import os

from creds_lib import http, zshenv_io
from creds_lib.status import FAIL, MISCONFIGURED, OK, Result

NAME = "slack"
MINT_URL = "https://api.slack.com/apps"
LOGIN_HINT = (
    "Bot/user tokens are minted via OAuth. Install/authorize the Slack app "
    "(OAuth & Permissions → Install), then set SLACK_BOT_TOKEN (xoxb-) and "
    "SLACK_USER_TOKEN (xoxp-) in ~/.zshenv. Rotate the app-config tokens with "
    "`rotate.py slack`."
)


def _clean(value: str | None) -> str | None:
    if not value or value.strip() in ("", "ADD_VALUE") or value.upper().startswith("PLACEHOLDER"):
        return None
    return value.strip()


def validate() -> Result:
    bot = _clean(os.environ.get("SLACK_BOT_TOKEN"))
    user = _clean(os.environ.get("SLACK_USER_TOKEN"))
    if not bot and not user:
        return Result(NAME, MISCONFIGURED, "no SLACK_BOT_TOKEN / SLACK_USER_TOKEN")

    parts: list[str] = []
    team = ""
    all_ok = True
    for label, tok in (("bot", bot), ("user", user)):
        if not tok:
            continue
        status, _h, body = http.request(
            "GET",
            "https://slack.com/api/auth.test",
            headers={"Authorization": f"Bearer {tok}"},
        )
        j = http.json_or_text(body)
        if isinstance(j, dict) and j.get("ok"):
            team = j.get("team") or team
            parts.append(f"{label} ok")
        else:
            all_ok = False
            err = j.get("error") if isinstance(j, dict) else f"HTTP {status}"
            parts.append(f"{label} FAIL({err})")

    return Result(NAME, OK if all_ok else FAIL, ", ".join(parts), sample=team)


def rotate() -> Result:
    refresh = _clean(os.environ.get("SLACK_APP_CONFIG_REFRESH_TOKEN_CRED"))
    if not refresh:
        return Result(
            NAME,
            MISCONFIGURED,
            "SLACK_APP_CONFIG_REFRESH_TOKEN_CRED unset — mint the initial pair at "
            "https://api.slack.com/authentication/config-tokens",
        )

    status, _h, body = http.request(
        "POST",
        "https://slack.com/api/tooling.tokens.rotate",
        data={"refresh_token": refresh},
    )
    j = http.json_or_text(body)
    if not (isinstance(j, dict) and j.get("ok")):
        err = j.get("error") if isinstance(j, dict) else body[:200]
        return Result(NAME, FAIL, f"slack rejected rotate: {err}")

    new_access = j.get("token")
    new_refresh = j.get("refresh_token")
    if not new_access or not new_refresh:
        return Result(NAME, FAIL, f"rotate response missing tokens: keys={list(j)}")

    updated: list[str] = []
    if zshenv_io.set_value("SLACK_APP_CONFIG_ACCESS_TOKEN_CRED", new_access):
        updated.append("ACCESS")
    if zshenv_io.set_value("SLACK_APP_CONFIG_REFRESH_TOKEN_CRED", new_refresh):
        updated.append("REFRESH")
    if not updated:
        return Result(
            NAME,
            FAIL,
            "rotated upstream but no matching export lines in ~/.zshenv to update",
        )

    return Result(
        NAME,
        OK,
        f"rotated app-config tokens ({'+'.join(updated)}); new token exp unix "
        f"{j.get('exp')} — run `source ~/.zshenv` to reload",
    )
