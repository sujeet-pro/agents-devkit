#!/usr/bin/env python3
"""adk_mcp_health.py — report which MCPs are configured + reachable + which env vars
referenced by mcp/adk-mcp-*.json are unset.

Reads:
  - mcp/adk-mcp-*.json (this repo)
  - process env (for ${VAR} placeholders)

Never prints env-var VALUES — only presence + reachability.

Usage:
  python3 scripts/adk_mcp_health.py
  python3 scripts/adk_mcp_health.py --json
  python3 scripts/adk_mcp_health.py --probe        # also send a curl probe to http MCPs (read-only)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
MCP_DIR = REPO / "mcp"

# Env vars referenced across MCPs — declared here so we report cleanly even if
# a config file's env block omits them. Aligned with the post-2026-05-19
# ~/.zshenv + ~/.config/creds/<svc>/creds.sh layout.
DECLARED_VARS: dict[str, str] = {
    # GitHub
    "GITHUB_TOKEN_CRED": "https://github.com/settings/personal-access-tokens/new",
    # Datadog
    "DATADOG_API_KEY_CRED": "https://app.datadoghq.com/organization-settings/api-keys",
    "DATADOG_APP_KEY_CRED": "https://app.datadoghq.com/organization-settings/application-keys",
    "DD_SITE": "default: datadoghq.com",
    "DD_MCP_URL": "default: https://mcp.datadoghq.com/api/unstable/mcp-server/mcp",
    # Statsig
    "STATSIG_CONSOLE_API_KEY_CRED": "https://console.statsig.com/api_keys",
    # Atlassian
    "ATLASSIAN_SITE": "your Atlassian site host (e.g. acme.atlassian.net)",
    "ATLASSIAN_USERNAME": "your Atlassian email",
    "ATLASSIAN_API_TOKEN_CRED": "https://id.atlassian.com/manage-profile/security/api-tokens",
    # Snowflake (new schema: connections.toml + PAT)
    "SNOWFLAKE_ACCESS_TOKEN_CRED": "Programmatic Access Token — Snowflake → Admin → Users → PATs",
    "SNOWFLAKE_HOME": "default: ~/.snowflake (we use ~/.config/creds/snowflake)",
    "SNOWFLAKE_CONNECTION_NAME": "default: adk (selects block in connections.toml)",
    "SNOWFLAKE_SERVICE_CONFIG_FILE": "snowflake-labs-mcp service-config.yaml path",
    # Looker
    "LOOKER_SITE": "your Looker base URL",
    "LOOKER_CLIENT_ID": "Looker API3 client id",
    "LOOKER_CLIENT_SECRET_CRED": "Looker API3 client secret",
    "LOOKER_VERIFY_SSL": "default: true",
    # Slack
    "SLACK_CREDENTIALS_FILE": "shell-sourceable file exporting SLACK_BOT_TOKEN / SLACK_USER_TOKEN",
    "SLACK_CLIENT_ID": "Slack app client id (non-secret)",
    "SLACK_CLIENT_SECRET_CRED": "Slack app client secret",
    # Google (Workspace MCP)
    "GOOGLE_CLIENT_ID": "OAuth client id (non-secret)",
    "GOOGLE_CLIENT_SECRET_CRED": "OAuth client secret",
    "USER_GOOGLE_EMAIL": "Google email the workspace-mcp acts as (e.g. you@company.com)",
    "WORKSPACE_MCP_CREDENTIALS_DIR": "workspace-mcp OAuth token cache (default: ~/.google_workspace_mcp/credentials)",
    # RAG (optional)
    "RAG_MCP_URL": "your company RAG MCP endpoint (optional)",
    "RAG_MCP_TOKEN_CRED": "your company RAG MCP bearer token (optional)",
}

# Vars that have a sensible default in the MCP config (`${VAR:-default}`) or
# in upstream tooling — DO NOT flag them red if unset. They appear as "present
# (default)" in the report.
VARS_WITH_DEFAULTS: set[str] = {
    "DD_SITE",
    "DD_MCP_URL",
    "SNOWFLAKE_HOME",
    "SNOWFLAKE_CONNECTION_NAME",
    "WORKSPACE_MCP_CREDENTIALS_DIR",
    "LOOKER_VERIFY_SSL",
}

# Aliases — if right-hand var is set, the left-hand var is "satisfied".
# Since 2026-05-19 secret env vars are canonical-named `<NAME>_CRED`; the
# only remaining aliases are between DD_SITE / DATADOG_SITE (both legitimate
# Datadog SDK conventions; either may be set).
ALIASES: dict[str, str] = {
    "DD_SITE": "DATADOG_SITE",
    "DATADOG_SITE": "DD_SITE",
}

VAR_REF_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}")


def env_status(var: str) -> str:
    if os.environ.get(var):
        return "present"
    alias = ALIASES.get(var)
    if alias and os.environ.get(alias):
        return f"present-via-fallback({alias})"
    if var in VARS_WITH_DEFAULTS:
        return "unset (using default)"
    return "MISSING"


def read_mcp_configs() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in sorted(MCP_DIR.glob("adk-mcp-*.json")):
        try:
            out.append({"_path": str(p.relative_to(REPO)), **json.loads(p.read_text(encoding="utf-8"))})
        except json.JSONDecodeError as e:
            out.append({"_path": str(p.relative_to(REPO)), "_error": str(e)})
    return out


def referenced_env_vars(cfg: dict[str, Any]) -> list[str]:
    """Return env vars referenced by ${VAR} in this MCP's url/headers/env/args."""
    refs: set[str] = set()
    blob = json.dumps(cfg)
    for m in VAR_REF_RE.finditer(blob):
        refs.add(m.group(1))
    return sorted(refs)


def probe_http(url: str, headers: dict[str, str] | None) -> tuple[int | None, str | None]:
    if not shutil.which("curl"):
        return None, "curl not installed"
    headers = headers or {}
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
           "-H", "Accept: application/json, text/event-stream",
           "-H", "Content-Type: application/json"]
    for k, v in headers.items():
        # interpolate ${VAR}
        for m in VAR_REF_RE.finditer(v):
            var = m.group(1)
            val = os.environ.get(var)
            if val is None:
                # try alias
                alias = ALIASES.get(var)
                if alias:
                    val = os.environ.get(alias)
            if val is None:
                v = v.replace(m.group(0), "")
            else:
                v = v.replace(m.group(0), val)
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["--data", '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{}}}', url.split("?")[0]])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
        code = int(result.stdout.strip()) if result.stdout.strip().isdigit() else None
        return code, None
    except subprocess.TimeoutExpired:
        return None, "timed out"
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--probe", action="store_true", help="curl-probe http MCPs (read-only init call)")
    args = ap.parse_args()

    mcps = read_mcp_configs()

    report: dict[str, Any] = {"mcps": [], "env_vars": {}}

    for cfg in mcps:
        item: dict[str, Any] = {
            "name": cfg.get("name") or Path(cfg["_path"]).stem,
            "config_path": cfg["_path"],
        }
        if "_error" in cfg:
            item["status"] = f"invalid-json: {cfg['_error']}"
            report["mcps"].append(item)
            continue
        refs = referenced_env_vars(cfg)
        # A missing var that has a default OR an alias is NOT a real miss.
        missing = []
        for v in refs:
            s = env_status(v)
            if s == "MISSING":
                missing.append(v)
        if missing:
            item["status"] = "env-missing"
            item["missing_env_vars"] = missing
        else:
            item["status"] = "env-ok"
        if args.probe and "url" in cfg:
            code, error = probe_http(cfg["url"], cfg.get("headers"))
            item["probe"] = {"http_code": code, "error": error}
        report["mcps"].append(item)

    for var in DECLARED_VARS:
        report["env_vars"][var] = env_status(var)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    # Pretty print
    print(f"[adk_mcp_health] reading {MCP_DIR.relative_to(REPO)}/")
    print()
    print("MCPs:")
    for m in report["mcps"]:
        marker = {"env-ok": "✓", "env-missing": "✗"}.get(m["status"], "!")
        line = f"  {marker} {m['name']:24} {m['status']}"
        if "missing_env_vars" in m:
            line += f"  (missing: {', '.join(m['missing_env_vars'])})"
        if "probe" in m:
            p = m["probe"]
            line += f"  [probe: {p.get('http_code') or p.get('error')}]"
        print(line)
    print()
    print("env vars referenced by adk:")
    for var, status in report["env_vars"].items():
        if status.startswith("present"):
            marker = "✓"
        elif status.startswith("unset (using default)"):
            marker = "·"
        else:
            marker = "✗"
        hint = "" if status.startswith("present") else f"  ({DECLARED_VARS[var]})"
        print(f"  {marker} {var:32} {status}{hint}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
