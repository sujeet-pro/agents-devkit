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
import tomllib
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

# Vars whose MCP wrappers normalize a full URL down to the bare host.
NORMALIZED_HOST_VARS: set[str] = {"ATLASSIAN_SITE"}

# Aliases — if right-hand var is set, the left-hand var is "satisfied".
# Empty since 2026-05-19: every consumer reads the canonical `_CRED`
# names directly. MCP json configs interpolate ${X_CRED} into the third-
# party server's native env name (e.g. DD_API_KEY) at subprocess startup,
# which means no shell-level alias is needed.
ALIASES: dict[str, str] = {}

VAR_REF_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}")
VAR_REF_WITH_DEFAULT_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::-(.*?))?\}")
ADK_MCP_PREFIX = "adk-mcp-"
CURSOR_ADK_DESCRIPTOR_PREFIX = "user-adk-mcp-"
CURSOR_BUILTIN_DESCRIPTOR_PREFIX = "cursor-"


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


def mcp_disabled(cfg: dict[str, Any]) -> str | None:
    """Return the disabled reason for MCPs that are intentionally not loaded."""
    name = cfg.get("name")
    if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
        return "disabled (RAG_MCP_URL unset)"
    return None


def env_status(var: str) -> str:
    val = os.environ.get(var)
    if val:
        if var in NORMALIZED_HOST_VARS:
            if val.startswith("/"):
                # Don't echo the value — just flag the shape. A path-only value
                # cannot be normalized into a host.
                return "present BUT INVALID (must include host)"
            if "://" in val or "/" in val:
                return "present (will normalize to bare host)"
        return "present"
    alias = ALIASES.get(var)
    if alias and os.environ.get(alias):
        return f"present-via-fallback({alias})"
    if var in VARS_WITH_DEFAULTS:
        return "unset (using default)"
    return "MISSING"


def expand_env_refs(s: str) -> str:
    """Expand ${VAR} and ${VAR:-default} for probes without printing values."""
    def repl(m: re.Match[str]) -> str:
        var = m.group(1)
        default = m.group(2)
        val = os.environ.get(var)
        if val is not None:
            return val
        alias = ALIASES.get(var)
        if alias and os.environ.get(alias) is not None:
            return os.environ[alias]
        return default if default is not None else ""
    return VAR_REF_WITH_DEFAULT_RE.sub(repl, s)


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
    expanded_url = expand_env_refs(url)
    cmd = ["curl", "-sS", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
           "-H", "Accept: application/json, text/event-stream",
           "-H", "Content-Type: application/json"]
    for k, v in headers.items():
        cmd.extend(["-H", f"{k}: {expand_env_refs(v)}"])
    cmd.extend([
        "--data",
        '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{}}}',
        expanded_url,
    ])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15, check=False)
        code = int(result.stdout.strip()) if result.stdout.strip().isdigit() else None
        return code, None
    except subprocess.TimeoutExpired:
        return None, "timed out"
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def expected_enabled_mcp_names(mcps: list[dict[str, Any]]) -> set[str]:
    names: set[str] = set()
    for cfg in mcps:
        if "_error" in cfg or mcp_disabled(cfg):
            continue
        names.add(str(cfg.get("name") or Path(cfg["_path"]).stem))
    return names


def _inspect_json_mcp_config(path: Path, expected: set[str]) -> dict[str, Any]:
    item: dict[str, Any] = {"path": str(path), "status": "absent"}
    if not path.exists():
        return item
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        item.update({"status": "invalid-json", "error": str(e)})
        return item
    servers = data.get("mcpServers", {}) or {}
    if not isinstance(servers, dict):
        item.update({"status": "invalid-shape", "error": "mcpServers is not an object"})
        return item
    names = set(map(str, servers))
    non_adk = sorted(n for n in names if not n.startswith(ADK_MCP_PREFIX))
    missing = sorted(expected - names)
    item.update({
        "status": "ok" if not non_adk and not missing else "fail",
        "server_count": len(names),
        "non_adk": non_adk,
        "missing_adk": missing,
    })
    return item


def _inspect_codex_config(path: Path, expected: set[str]) -> dict[str, Any]:
    item: dict[str, Any] = {"path": str(path), "status": "absent"}
    if not path.exists():
        return item
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        item.update({"status": "invalid-toml", "error": str(e)})
        return item
    servers = data.get("mcp_servers", {}) or {}
    if not isinstance(servers, dict):
        item.update({"status": "invalid-shape", "error": "mcp_servers is not a table"})
        return item
    names = set(map(str, servers))
    non_adk = sorted(n for n in names if not n.startswith(ADK_MCP_PREFIX))
    missing = sorted(expected - names)
    item.update({
        "status": "ok" if not non_adk and not missing else "fail",
        "server_count": len(names),
        "non_adk": non_adk,
        "missing_adk": missing,
    })
    return item


def _inspect_cursor_descriptor_caches() -> dict[str, Any]:
    projects = Path.home() / ".cursor" / "projects"
    item: dict[str, Any] = {"path": str(projects), "status": "absent", "projects": []}
    if not projects.exists():
        return item
    bad: list[dict[str, Any]] = []
    for mcp_dir in sorted(projects.glob("*/mcps"), key=lambda p: str(p)):
        if not mcp_dir.exists():
            continue
        names = sorted(p.name for p in mcp_dir.iterdir() if p.is_dir())
        non_adk = [
            n for n in names
            if not n.startswith(CURSOR_ADK_DESCRIPTOR_PREFIX)
            and not n.startswith(CURSOR_BUILTIN_DESCRIPTOR_PREFIX)
        ]
        row = {
            "project": mcp_dir.parent.name,
            "descriptor_count": len(names),
            "non_adk": non_adk,
        }
        item["projects"].append(row)
        if non_adk:
            bad.append(row)
    item["status"] = "ok" if not bad else "fail"
    item["non_adk_projects"] = bad
    return item


def inspect_agent_configs(expected: set[str]) -> dict[str, Any]:
    return {
        "claude": _inspect_json_mcp_config(Path.home() / ".claude.json", expected),
        "cursor": _inspect_json_mcp_config(Path.home() / ".cursor" / "mcp.json", expected),
        "junie": _inspect_json_mcp_config(Path.home() / ".junie" / "mcp" / "mcp.json", expected),
        "codex": _inspect_codex_config(Path.home() / ".codex" / "config.toml", expected),
        "cursor_descriptor_caches": _inspect_cursor_descriptor_caches(),
    }


def collect_failures(report: dict[str, Any], *, require_creds: bool, strict_probe: bool) -> list[str]:
    failures: list[str] = []
    for m in report.get("mcps", []):
        name = m.get("name", "<unknown>")
        if m.get("status") not in {"env-ok", "disabled"}:
            failures.append(f"{name}: {m.get('status')}")
        if require_creds and "creds_validate" in m and m["creds_validate"] not in {"OK", "SKIPPED"}:
            failures.append(f"{name}: creds {m['creds_validate']}")
        if strict_probe and "probe" in m:
            probe = m["probe"]
            if probe.get("error") or not probe.get("http_code"):
                failures.append(f"{name}: probe {probe.get('error') or probe.get('http_code')}")
    for agent, cfg in (report.get("agent_configs") or {}).items():
        if cfg.get("status") == "absent":
            continue
        if cfg.get("status") != "ok":
            failures.append(f"{agent}: {cfg.get('status')}")
    return failures


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--probe", action="store_true", help="curl-probe http MCPs (read-only init call)")
    ap.add_argument("--check-agent-configs", action="store_true",
                    help="Verify Claude/Cursor/Codex/Junie MCP configs contain only enabled adk-mcp-* entries.")
    ap.add_argument("--strict", action="store_true",
                    help="Exit nonzero if env, creds, probe, or agent-config checks fail.")
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
        disabled = mcp_disabled(cfg)
        if disabled:
            item["status"] = "disabled"
            item["disabled_reason"] = disabled
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

    if args.check_agent_configs:
        report["agent_configs"] = inspect_agent_configs(expected_enabled_mcp_names(mcps))

    failures = collect_failures(
        report,
        require_creds=bool(creds_data),
        strict_probe=args.probe,
    )
    if failures:
        report["failure_summary"] = failures

    if args.json:
        print(json.dumps(report, indent=2))
        return 1 if args.strict and failures else 0

    # Pretty print
    print(f"[adk_mcp_health] reading {MCP_DIR.relative_to(REPO)}/")
    print()
    print("MCPs:")
    for m in report["mcps"]:
        marker = {"env-ok": "✓", "env-missing": "✗", "disabled": "·"}.get(m["status"], "!")
        line = f"  {marker} {m['name']:24} {m['status']}"
        if "missing_env_vars" in m:
            line += f"  (missing: {', '.join(m['missing_env_vars'])})"
        if "disabled_reason" in m:
            line += f"  ({m['disabled_reason']})"
        if "probe" in m:
            p = m["probe"]
            line += f"  [probe: {p.get('http_code') or p.get('error')}]"
        if "creds_validate" in m:
            line += f"  [creds: {m['creds_validate']}]"
        print(line)
    print()
    print("env vars referenced by adk:")
    for var, status in report["env_vars"].items():
        if "INVALID" in status:
            marker = "✗"
            hint = f"  ({DECLARED_VARS[var]})"
        elif status.startswith("present"):
            marker = "✓"
            hint = ""
        elif status.startswith("unset (using default)"):
            marker = "·"
            hint = ""
        else:
            marker = "✗"
            hint = f"  ({DECLARED_VARS[var]})"
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
    if "agent_configs" in report:
        print()
        print("agent MCP configs:")
        for agent, cfg in report["agent_configs"].items():
            marker = {"ok": "✓", "absent": "·"}.get(cfg.get("status"), "✗")
            detail = ""
            if cfg.get("non_adk"):
                detail += f" non-adk={','.join(cfg['non_adk'])}"
            if cfg.get("missing_adk"):
                detail += f" missing={','.join(cfg['missing_adk'])}"
            if agent == "cursor_descriptor_caches" and cfg.get("non_adk_projects"):
                detail += f" non-adk-projects={len(cfg['non_adk_projects'])}"
            print(f"  {marker} {agent:24} {cfg.get('status')}{detail}")
    if failures:
        print()
        print("failures:")
        for f in failures:
            print(f"  - {f}")
    return 1 if args.strict and failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
