"""Mixpanel — hosted OAuth MCP. No local credential; login via MCP client."""

from __future__ import annotations

from creds_lib import http
from creds_lib.status import FAIL, LOGIN, Result

NAME = "mixpanel"
MINT_URL = "https://mixpanel.com"
LOGIN_HINT = (
    "Hosted OAuth — no key in ~/.zshenv. Authenticate from your MCP client "
    "(Claude/Cursor): trigger the Mixpanel server once and complete the "
    "browser OAuth prompt."
)


def validate() -> Result:
    # No local secret to probe — just confirm the hosted endpoint is reachable.
    status, _h, _body = http.request(
        "POST",
        "https://mcp.mixpanel.com/mcp",
        headers={"Accept": "application/json, text/event-stream"},
        json_body={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "adk-creds", "version": "1"},
            },
        },
        timeout=15.0,
    )
    # 401/403 simply means OAuth not yet done in the client — endpoint is up.
    if status in (200, 400, 401, 403, 405):
        return Result(NAME, LOGIN, "hosted MCP reachable — log in via MCP client")
    return Result(NAME, FAIL, f"hosted MCP unreachable — HTTP {status}")
