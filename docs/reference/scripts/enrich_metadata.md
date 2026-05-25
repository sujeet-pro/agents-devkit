---
title: 'enrich_metadata.py'
description: 'enrich_metadata.py — populate $ADK_DATA_HOME/improve/metadata/<source>.json'
script: 'enrich_metadata.py'
source: 'scripts/enrich_metadata.py'
group: 'scripts'
order: 4004
---
# enrich_metadata.py

enrich_metadata.py — populate $ADK_DATA_HOME/improve/metadata/<source>.json

## Source

`scripts/enrich_metadata.py`

## Contents

```python
#!/usr/bin/env python3
"""enrich_metadata.py — populate $ADK_DATA_HOME/improve/metadata/<source>.json
by introspecting reachable MCPs / CLI tools.

This script does the PROGRAMMATIC enrichment. The AI step in /adk-setup --enrich
produces nice prose around the results and decides what to lift into
$ADK_CONFIG_HOME/connectors/<name>.md frontmatter; this just gathers raw
data into the metadata cache.

Usage:
  python3 scripts/enrich_metadata.py [--source datadog|statsig|mixpanel|atlassian|github|snowflake|looker|all]
                                      [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

METADATA_DIR = Path(os.path.expanduser("$ADK_DATA_HOME/improve/metadata"))


def run(cmd: list[str], env: dict[str, str] | None = None) -> tuple[int, str, str]:
    """Run a shell command, return (rc, stdout, stderr). Never raises."""
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            env={**os.environ, **(env or {})},
            check=False,
        )
        return p.returncode, p.stdout, p.stderr
    except FileNotFoundError as e:
        return 127, "", f"command not found: {e}"
    except subprocess.TimeoutExpired:
        return 124, "", "timed out after 60s"


def enrich_github() -> dict[str, Any]:
    """Use gh CLI; if missing, skip."""
    if not shutil.which("gh"):
        return {"_status": "skipped", "_reason": "gh CLI not installed"}
    rc, out, err = run(["gh", "auth", "status"])
    if rc != 0:
        return {"_status": "skipped", "_reason": f"gh not authed: {err.strip()[:120]}"}
    rc, out, err = run(["gh", "api", "/user", "--jq", ".login"])
    user = out.strip() if rc == 0 else "unknown"
    rc, out, err = run(["gh", "api", "/user/orgs", "--jq", "[.[].login]"])
    orgs = json.loads(out) if rc == 0 and out.strip() else []
    return {
        "_status": "ok",
        "user": user,
        "orgs": orgs,
    }


def enrich_datadog() -> dict[str, Any]:
    site = os.environ.get("DD_SITE", "datadoghq.com")
    api_key = os.environ.get("DATADOG_API_KEY_CRED")
    app_key = os.environ.get("DATADOG_APP_KEY_CRED")
    if not (api_key and app_key):
        return {"_status": "skipped", "_reason": "DATADOG_API_KEY_CRED / DATADOG_APP_KEY_CRED not set"}
    base = f"https://api.{site}/api/v1"
    headers_curl = [
        "-H", f"DD-API-KEY: {api_key}",
        "-H", f"DD-APPLICATION-KEY: {app_key}",
        "-H", "Accept: application/json",
    ]
    out: dict[str, Any] = {"_status": "ok", "site": site}
    # Dashboards
    rc, body, _ = run(["curl", "-sS", f"{base}/dashboard", *headers_curl])
    if rc == 0 and body:
        try:
            data = json.loads(body)
            out["dashboards_count"] = len(data.get("dashboards", []))
            out["dashboards_sample"] = [
                {"id": d.get("id"), "title": d.get("title")} for d in data.get("dashboards", [])[:5]
            ]
        except Exception:
            pass
    # Monitors
    rc, body, _ = run(["curl", "-sS", f"{base}/monitor", *headers_curl])
    if rc == 0 and body:
        try:
            data = json.loads(body)
            if isinstance(data, list):
                out["monitors_count"] = len(data)
                out["monitors_sample"] = [
                    {"id": m.get("id"), "name": m.get("name"), "type": m.get("type")} for m in data[:5]
                ]
        except Exception:
            pass
    return out


def enrich_statsig() -> dict[str, Any]:
    key = os.environ.get("STATSIG_CONSOLE_API_KEY_CRED")
    if not key:
        return {"_status": "skipped", "_reason": "STATSIG_CONSOLE_API_KEY_CRED not set"}
    out: dict[str, Any] = {"_status": "ok"}
    for resource in ("gates", "experiments", "metrics"):
        rc, body, _ = run([
            "curl", "-sS", "-H", f"STATSIG-API-KEY: {key}",
            f"https://statsigapi.net/console/v1/{resource}?limit=10",
        ])
        if rc == 0 and body:
            try:
                data = json.loads(body)
                items = data.get("data", []) if isinstance(data, dict) else data
                out[f"{resource}_count_sample"] = len(items)
                out[f"{resource}_sample"] = [
                    {"id": i.get("id"), "name": i.get("name")} for i in items[:5]
                ]
            except Exception:
                pass
    return out


def enrich_atlassian() -> dict[str, Any]:
    site = os.environ.get("ATLASSIAN_SITE")
    user = os.environ.get("ATLASSIAN_USERNAME")
    token = os.environ.get("ATLASSIAN_API_TOKEN_CRED")
    if not (site and user and token):
        return {"_status": "skipped", "_reason": "ATLASSIAN_SITE/USERNAME/API_TOKEN_CRED not all set"}
    site = site.removeprefix("https://").removeprefix("http://").split("/", 1)[0]
    auth = ["-u", f"{user}:{token}"]
    out: dict[str, Any] = {"_status": "ok", "site": site}
    # Jira projects
    rc, body, _ = run(["curl", "-sS", *auth, f"https://{site}/rest/api/3/project/search"])
    if rc == 0 and body:
        try:
            data = json.loads(body)
            values = data.get("values", []) if isinstance(data, dict) else []
            out["jira_projects_count"] = len(values)
            out["jira_projects_sample"] = [
                {"key": p.get("key"), "name": p.get("name")} for p in values[:10]
            ]
        except Exception:
            pass
    # Confluence spaces
    rc, body, _ = run(["curl", "-sS", *auth, f"https://{site}/wiki/rest/api/space?limit=10"])
    if rc == 0 and body:
        try:
            data = json.loads(body)
            results = data.get("results", []) if isinstance(data, dict) else []
            out["confluence_spaces_count_sample"] = len(results)
            out["confluence_spaces_sample"] = [
                {"key": s.get("key"), "name": s.get("name")} for s in results[:10]
            ]
        except Exception:
            pass
    return out


def enrich_mixpanel() -> dict[str, Any]:
    # Mixpanel hosted MCP uses OAuth; no programmatic enrichment without the user being browser-OAuthed.
    # We surface "OAuth required" so /adk-setup can prompt the agent to drive the OAuth flow.
    return {"_status": "manual", "_reason": "Mixpanel hosted MCP uses OAuth — enrich via the MCP after first connect"}


def enrich_snowflake() -> dict[str, Any]:
    acct = os.environ.get("SNOWFLAKE_ACCOUNT")
    user = os.environ.get("SNOWFLAKE_USER")
    if not (acct and user):
        return {"_status": "skipped", "_reason": "SNOWFLAKE_ACCOUNT / SNOWFLAKE_USER not set"}
    return {"_status": "manual", "_reason": "Snowflake enrichment requires query execution — run via /adk-setup --enrich with the MCP loaded"}


def enrich_looker() -> dict[str, Any]:
    url = os.environ.get("LOOKER_SITE")
    if not url:
        return {"_status": "skipped", "_reason": "LOOKER_SITE not set"}
    return {"_status": "manual", "_reason": "Looker enrichment requires OAuth + MCP — run via /adk-setup --enrich"}


def write_metadata(name: str, data: dict[str, Any]) -> Path:
    METADATA_DIR.mkdir(parents=True, exist_ok=True)
    p = METADATA_DIR / f"{name}.json"
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="all",
                    choices=("all", "github", "datadog", "statsig", "atlassian", "mixpanel", "snowflake", "looker"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    runners = {
        "github": enrich_github,
        "datadog": enrich_datadog,
        "statsig": enrich_statsig,
        "atlassian": enrich_atlassian,
        "mixpanel": enrich_mixpanel,
        "snowflake": enrich_snowflake,
        "looker": enrich_looker,
    }
    targets = list(runners) if args.source == "all" else [args.source]
    summary: dict[str, Any] = {}
    for t in targets:
        result = runners[t]()
        summary[t] = result
        if args.dry_run:
            print(f"[dry-run] would write metadata/{t}.json:")
            print(json.dumps(result, indent=2))
        else:
            p = write_metadata(t, result)
            print(f"wrote {p}  [{result.get('_status', '?')}]", file=sys.stderr)

    if not args.dry_run:
        print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
