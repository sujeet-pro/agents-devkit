"""Connector registry.

One module per MCP server in plugins/adk/.mcp.json. Every connector
exposes ``NAME`` and ``validate() -> Result``. Optional extras:
  ``rotate() -> Result``   — programmatic credential rotation
  ``LOGIN_HINT: str``      — what the user must do for an interactive login
  ``MINT_URL: str``        — console URL to open during ``login``
"""

from __future__ import annotations

from importlib import import_module
from types import ModuleType

# Display order = the order .mcp.json declares the servers.
NAMES: list[str] = [
    "datadog",
    "atlassian",
    "slack",
    "statsig",
    "mixpanel",
    "snowflake",
    "looker",
    "google",
]

_ALIASES = {
    "dd": "datadog",
    "jira": "atlassian",
    "confluence": "atlassian",
    "atl": "atlassian",
    "sk": "slack",
    "sf": "snowflake",
    "snow": "snowflake",
    "gws": "google",
    "workspace": "google",
    "mp": "mixpanel",
}


def resolve(name: str) -> str:
    key = name.strip().lower()
    if key in NAMES:
        return key
    if key in _ALIASES:
        return _ALIASES[key]
    raise KeyError(f"unknown service or alias: {name!r}")


def load(name: str) -> ModuleType:
    canonical = resolve(name)
    return import_module(f"connectors.{canonical}")
