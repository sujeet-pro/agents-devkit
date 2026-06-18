"""Google Workspace (workspace-mcp) — OAuth client + browser login.

The OAuth client ID/secret live in ~/.zshenv, but the per-user grant is done
interactively by workspace-mcp on first use (a browser consent flow). The
resulting token is cached under GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR. So
validation here = config present + a cached credential exists; otherwise the
user must complete the browser login (see LOGIN_HINT).
"""

from __future__ import annotations

import os
from pathlib import Path

from creds_lib.status import LOGIN, MISCONFIGURED, OK, Result, required_env

NAME = "google"
MINT_URL = "https://console.cloud.google.com/apis/credentials"
LOGIN_HINT = (
    "OAuth — run the workspace MCP once and complete the browser consent for "
    "USER_GOOGLE_EMAIL. The grant is cached under "
    "GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR. The client ID/secret come from a "
    "Google Cloud OAuth client (console.cloud.google.com → APIs → Credentials)."
)


def validate() -> Result:
    env, missing = required_env(
        "GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET", "USER_GOOGLE_EMAIL"
    )
    if missing:
        return Result(NAME, MISCONFIGURED, "missing env", missing=missing)

    cred_dir = os.environ.get("GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR")
    if not cred_dir:
        return Result(
            NAME, MISCONFIGURED, "missing env", missing=["GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR"]
        )

    p = Path(os.path.expanduser(os.path.expandvars(cred_dir)))
    creds = list(p.glob("*.json")) if p.exists() else []
    if not creds:
        return Result(
            NAME,
            LOGIN,
            f"client configured but no cached grant in {cred_dir} — complete browser OAuth",
            sample=env["USER_GOOGLE_EMAIL"],
        )
    return Result(
        NAME,
        OK,
        f"client configured; {len(creds)} cached grant(s)",
        sample=env["USER_GOOGLE_EMAIL"],
    )
