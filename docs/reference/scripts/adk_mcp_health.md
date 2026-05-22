---
title: 'adk_mcp_health.py'
description: 'adk_mcp_health.py — report which MCPs are configured + reachable + which env vars'
script: 'adk_mcp_health.py'
source: 'scripts/adk_mcp_health.py'
group: 'scripts'
order: 4000
---
# adk_mcp_health.py

adk_mcp_health.py — report which MCPs are configured + reachable + which env vars

## Source

`scripts/adk_mcp_health.py`

## Contents

```python
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
    "DATADOG_SITE": "default: datadoghq.com",
    "DATADOG_MCP_URL": "default: https://mcp.datadoghq.com/api/unstable/mcp-server/mcp",
    # Statsig
    "STATSIG_CONSOLE_API_KEY_CRED": "https://console.statsig.com/api_keys",
    # Atlassian
    "ATLASSIAN_SITE": "your Atlassian site host (e.g. acme.atlassian.net)",
    "ATLASSIAN_USERNAME": "your Atlassian email",
    "ATLASSIAN_API_TOKEN_CRED": "https://id.atlassian.com/manage-profile/security/api-tokens",
    # Snowflake (PAT layout)
    "SNOWFLAKE_ACCESS_TOKEN_CRED": "Programmatic Access Token — Snowflake → Admin → Users → PATs",
    "SNOWFLAKE_HOME": "default: ~/.config/creds/snowflake",
    "SNOWFLAKE_CONNECTION_NAME": "default: adk (selects block in connections.toml)",
    "SNOWFLAKE_SERVICE_CONFIG_FILE": "snowflake-labs-mcp service-config.yaml path",
    # Looker
    "LOOKER_BASE_URL": "your Looker base URL",
    "LOOKER_CLIENT_ID_CRED": "Looker API3 client id",
    "LOOKER_CLIENT_SECRET_CRED": "Looker API3 client secret",
    "LOOKER_VERIFY_SSL": "default: true",
    # Slack
    "SLACK_CREDENTIALS_FILE": "shell-sourceable file exporting SLACK_BOT_TOKEN / SLACK_USER_TOKEN",
    "SLACK_CLIENT_ID": "Slack app client id (non-secret)",
    "SLACK_CLIENT_SECRET_CRED": "Slack app client secret",
    # Google
    "GOOGLE_CLIENT_ID_CRED": "OAuth client id",
    "GOOGLE_CLIENT_SECRET_CRED": "OAuth client secret",
    "USER_GOOGLE_EMAIL": "Google email the workspace-mcp acts as (e.g. you@company.com)",
    "GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR": "workspace-mcp OAuth token cache",
    # Bitbucket
    "BITBUCKET_URL": "default: https://api.bitbucket.org/2.0",
    "BITBUCKET_USERNAME": "your Bitbucket account email",
    "BITBUCKET_WORKSPACE": "default workspace slug (e.g. acme)",
    "BITBUCKET_TOKEN_CRED": "Atlassian API token — https://id.atlassian.com/manage-profile/security/api-tokens",
    # RAG (optional)
    "RAG_MCP_URL": "your company RAG MCP endpoint (optional)",
    "RAG_MCP_TOKEN_CRED": "your company RAG MCP bearer token (optional)",
}

# Vars that have a sensible default in the MCP config (`${VAR:-default}`) or
# in upstream tooling — DO NOT flag them red if unset.
VARS_WITH_DEFAULTS: set[str] = {
    "DATADOG_SITE",
    "DATADOG_MCP_URL",
    "SNOWFLAKE_HOME",
    "SNOWFLAKE_CONNECTION_NAME",
    "GOOGLE_WORKSPACE_MCP_CREDENTIALS_DIR",
    "LOOKER_VERIFY_SSL",
    "BITBUCKET_URL",
}

# Aliases — if right-hand var is set, the left-hand var is "satisfied".
# Empty since 2026-05-19: every consumer reads the canonical `_CRED`
# names directly. MCP json configs interpolate ${X_CRED} into the third-
# party server's native env name (e.g. DD_API_KEY) at subprocess startup,
# which means no shell-level alias is needed.
ALIASES: dict[str, str] = {}

VAR_REF_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}")


def _creds_cmd() -> str | None:
    """Return path to the `creds` CLI if installed, else None."""
    p = shutil.which("creds")
    if p:
        return p
    home_local = Path.home() / ".local" / "bin" / "creds"
    return str(home_local) if home_local.is_file() else None


def fetch_creds_status() -> dict[str, Any]:
    """Shell out to `creds validate --json --no-log` and parse the result.

    Returns {} if the creds CLI is unavailable or any error occurs — the
    cross-reference is purely additive. Never echoes any credential value.

    Timeout is generous (180s) because the full sweep across 8 connectors
    hits each provider's API sequentially — Looker self-hosted instances
    behind a corporate TLS proxy can take 20-40s on their own.
    """
    cmd = _creds_cmd()
    if not cmd:
        return {}
    try:
        result = subprocess.run(
            [cmd, "validate", "--json", "--no-log"],
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if not result.stdout.strip():
            return {}
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return {}


def fetch_creds_registry() -> list[dict[str, Any]]:
    """Service registry from `creds validate --list-json`; [] if unavailable."""
    cmd = _creds_cmd()
    if not cmd:
        return []
    try:
        result = subprocess.run(
            [cmd, "validate", "--list-json"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if not result.stdout.strip():
            return []
        return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return []


def mcp_to_service(name: str) -> str | None:
    """Map MCP name (adk-mcp-foo) → creds service name (foo).

    Returns None for MCPs that don't have a corresponding creds-system
    service (e.g. adk-mcp-rag).
    """
    if not name.startswith("adk-mcp-"):
        return None
    svc = name[len("adk-mcp-"):]
    if svc == "rag":
        return None
    return svc


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
    ap.add_argument(
        "--no-creds",
        action="store_true",
        help="Skip the ~/.config/creds cross-reference (auto-skips anyway if creds CLI not installed).",
    )
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

    # --- Cross-reference with the ~/.config/creds system (Stage 4) ---
    creds_data: dict[str, Any] = {} if args.no_creds else fetch_creds_status()
    if creds_data:
        report["creds"] = creds_data
        services = creds_data.get("services", {}) or {}
        for m in report["mcps"]:
            svc = mcp_to_service(m["name"])
            if svc is None:
                m["creds_service"] = None
            elif svc in services:
                m["creds_service"] = svc
                m["creds_validate"] = services[svc]["status"]
                if services[svc].get("message"):
                    m["creds_message"] = services[svc]["message"]
            else:
                m["creds_service"] = svc
                m["creds_validate"] = "no-validator"

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
        if "creds_validate" in m:
            line += f"  [creds: {m['creds_validate']}]"
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

    # Optional creds-system section (only when the cross-reference succeeded).
    if "creds" in report:
        services = report["creds"].get("services", {}) or {}
        if services:
            print()
            print("creds-system validators (from `creds validate --json`):")
            for svc, info in services.items():
                state = info.get("status", "?")
                m = {"OK": "✓", "FAIL": "✗", "MISCONFIGURED": "!", "SKIPPED": "·"}.get(state, "?")
                msg = info.get("message") or ""
                line = f"  {m} {svc:16} {state}"
                if msg:
                    line += f"  — {msg}"
                print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
