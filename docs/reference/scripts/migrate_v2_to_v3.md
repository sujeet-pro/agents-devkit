---
title: 'migrate_v2_to_v3.py'
description: 'migrate_v2_to_v3.py — read v2 per-topic ~/.agents-devkit/config/*.md files and synthesize'
script: 'migrate_v2_to_v3.py'
source: 'scripts/migrate_v2_to_v3.py'
group: 'scripts'
order: 4009
---
# migrate_v2_to_v3.py

migrate_v2_to_v3.py — read v2 per-topic ~/.agents-devkit/config/*.md files and synthesize

## Source

`scripts/migrate_v2_to_v3.py`

## Contents

```python
#!/usr/bin/env python3
"""migrate_v2_to_v3.py — read v2 per-topic ~/.agents-devkit/config/*.md files and synthesize
a v3 ~/.agents-devkit/config/overrides.yaml.

v2 files (if present):
  ~/.agents-devkit/config/info.md, repos.md, github.md, datadog.md, mixpanel.md, statsig.md,
  snowflake.md, slack.md, review.md, docs.md

Each v2 file is YAML-frontmatter + markdown notes. We read the frontmatter,
merge into a single v3 overrides.yaml, and write to a draft path (never
overwrites existing v3 file).

Usage:
  python3 scripts/migrate_v2_to_v3.py [--dry-run] [--out PATH]
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Any

ADK_DIR = Path(os.path.expanduser("~/.agents-devkit/config"))
V2_TOPICS = ["info", "repos", "github", "datadog", "mixpanel", "statsig",
             "snowflake", "slack", "review", "docs"]
OUT_DEFAULT = ADK_DIR / "overrides.yaml"

YAML_FM = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _try_yaml_load(text: str) -> dict[str, Any]:
    """Light YAML loader. Prefers PyYAML if installed; else falls back to a tiny
    parser that handles the subset we ship (key: value, lists of dicts)."""
    try:
        import yaml  # type: ignore
        loaded = yaml.safe_load(text) or {}
        return loaded if isinstance(loaded, dict) else {"_raw": loaded}
    except ImportError:
        # Minimal fallback — only handles key: value and key: [ … ]; nested dicts unsupported.
        out: dict[str, Any] = {}
        for line in text.splitlines():
            line = line.split("#", 1)[0].rstrip()
            if not line or ":" not in line:
                continue
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip("\"'")
        out["_warning"] = "PyYAML not installed; nested structures were not parsed. Install pyyaml for full migration."
        return out


def read_v2_topic(topic: str) -> dict[str, Any]:
    p = ADK_DIR / f"{topic}.md"
    if not p.exists():
        return {}
    text = p.read_text(encoding="utf-8")
    m = YAML_FM.search(text)
    if not m:
        return {}
    return _try_yaml_load(m.group(1))


def build_v3(topics: dict[str, dict[str, Any]]) -> str:
    info = topics.get("info", {})
    github = topics.get("github", {})
    datadog = topics.get("datadog", {})
    mixpanel = topics.get("mixpanel", {})
    statsig = topics.get("statsig", {})
    snowflake = topics.get("snowflake", {})
    slack = topics.get("slack", {})
    repos = topics.get("repos", {})

    workspace_name = "work"
    user_email = info.get("email") or "you@example.com"
    user_name = info.get("name") or "you"
    github_user = github.get("default_user") or "your-github-user"
    github_org = github.get("default_org") or "your-org"

    lines: list[str] = []
    lines.append("# ~/.agents-devkit/config/overrides.yaml — v3 (migrated from v2)")
    lines.append("# Review and edit. The migration is best-effort — nested fields may be flattened.")
    lines.append("")
    lines.append("workspaces:")
    lines.append(f"  - name: {workspace_name}")
    lines.append("    type: work")
    lines.append("    default: true")
    lines.append(f"    email: {user_email}")
    lines.append(f"    github_user: {github_user}")
    lines.append(f"    orgs: [{github_org}]")
    lines.append("")
    lines.append("repos: []   # TODO: populate from your v2 repos.md or fill manually")
    lines.append("")
    lines.append("data_sources:")
    if snowflake:
        lines.append("  snowflake:")
        for k, v in snowflake.items():
            if k.startswith("_"):
                continue
            lines.append(f"    {k}: {v}")
    if mixpanel:
        lines.append("  mixpanel:")
        for k, v in mixpanel.items():
            if k.startswith("_"):
                continue
            lines.append(f"    {k}: {v}")
    lines.append("")
    lines.append("rag:")
    lines.append("  enabled: false")
    lines.append("  mcp_name: adk-mcp-rag")
    lines.append("  trigger_keywords: []")
    lines.append("")
    lines.append("defaults: {}")
    lines.append("enriched: {}")
    lines.append("learning_state:")
    lines.append("  last_improve_run: null")
    lines.append("  last_metadata_refresh: null")
    lines.append("  pending_proposals: []")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    args = ap.parse_args()

    if not ADK_DIR.exists():
        print(f"no v2 directory at {ADK_DIR}; nothing to migrate", file=sys.stderr)
        return 0

    topics = {t: read_v2_topic(t) for t in V2_TOPICS}
    nonempty = {k: v for k, v in topics.items() if v}
    if not nonempty:
        print("no v2 topic files found with frontmatter", file=sys.stderr)
        return 0

    v3 = build_v3(topics)
    out = Path(os.path.expanduser(args.out))
    if args.dry_run:
        print(v3)
        return 0
    if out.exists():
        print(f"refusing to overwrite existing {out}; writing to {out}.migrated instead", file=sys.stderr)
        out = out.with_suffix(out.suffix + ".migrated")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(v3, encoding="utf-8")
    print(f"wrote {out}", file=sys.stderr)
    print(f"migrated {len(nonempty)} v2 topic(s): {sorted(nonempty)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
