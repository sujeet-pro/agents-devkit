---
title: 'config_io.py'
description: 'config_io.py — single I/O surface for the new adk config layout.'
script: 'config_io.py'
source: 'scripts/config_io.py'
group: 'scripts'
order: 4004
---
# config_io.py

config_io.py — single I/O surface for the new adk config layout.

## Source

`scripts/config_io.py`

## Contents

```python
#!/usr/bin/env python3
"""config_io.py — single I/O surface for the new adk config layout.

Layout (see shared/paths.md):
  ~/.agents-devkit/
    config/
      core.yaml                      # user + workspaces + defaults + rag + enriched
      repos.md                       # frontmatter = repo defs; body = notes per repo
      links.json5                    # cross-connector entity graph
      connectors/
        datadog.md, mixpanel.md, slack.md, snowflake.md, statsig.md,
        atlassian.md, github.md, bitbucket.md
            ↑ frontmatter (YAML) = the machine-readable config
            ↑ body         (md)  = human-authored notes the agent reads as context

Each connector .md looks like:

    ---
    auth:
      token_env: SLACK_BOT_TOKEN_CRED
    channels:
      - "#sf-web-pr-reviews"
    pr_reviews:
      status_emoji: { … }
    ---

    # Notes
    Body text the agent reads as additional context.

Public API:
  load_core()                            → dict
  load_connector(name)                   → (frontmatter: dict, notes: str)
  load_repos()                           → (frontmatter: dict, notes: str)
  load_links()                           → list[dict]
  save_connector(name, fm, notes)        → None  (atomic, locked)

Graph helpers (consume load_links()):
  entity_key("repo", "ecomm-ssr")        → "repo:ecomm-ssr"
  parse_entity_key("datadog.apm:foo")    → ("datadog.apm", "foo")
  neighbors(links, entity_key)           → list[str]      (1-hop)
  expand(links, entity_key, depth=2)     → set[str]       (N-hop)

CLI usage (handy for debugging):
  python3 config_io.py show-core
  python3 config_io.py show-connector datadog
  python3 config_io.py show-links
  python3 config_io.py neighbors repo:ecomm-ssr
  python3 config_io.py expand repo:ecomm-ssr --depth 3
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------- paths -----

ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
CONFIG_DIR = ADK_HOME / "config"
CONNECTORS_DIR = CONFIG_DIR / "connectors"
CORE_YAML = CONFIG_DIR / "core.yaml"
REPOS_MD = CONFIG_DIR / "repos.md"
LINKS_JSON5 = CONFIG_DIR / "links.json5"

# ---------------------------------------------------------------- lock ------
# fcntl-based exclusive lock for atomic writes. Local copy so this script
# doesn't depend on adk-pr-review's _common.py.
import contextlib
import fcntl
import time


@contextlib.contextmanager
def _file_lock(path: Path, timeout_s: float = 60.0):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR, 0o644)
    try:
        deadline = time.time() + timeout_s
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.time() > deadline:
                    raise TimeoutError(f"file_lock: timeout on {path}")
                time.sleep(0.2)
        yield
    finally:
        try:
            fcntl.flock(fd, fcntl.LOCK_UN)
        except Exception:
            pass
        os.close(fd)


# ---------------------------------------------------------- parsers ---------

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a markdown file into (yaml-frontmatter-dict, body)."""
    m = _FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    yaml_text = m.group(1)
    body = text[m.end():]
    try:
        import yaml  # PyYAML
    except ImportError:
        raise RuntimeError(
            "PyYAML not installed; required to parse frontmatter. "
            "Install: pip install pyyaml"
        )
    data = yaml.safe_load(yaml_text) or {}
    if not isinstance(data, dict):
        raise ValueError(f"frontmatter must be a YAML mapping; got {type(data).__name__}")
    return data, body


def _emit_frontmatter(fm: dict, body: str) -> str:
    import yaml
    yaml_text = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True, default_flow_style=False)
    body = body.lstrip("\n")
    return f"---\n{yaml_text}---\n\n{body}" if body else f"---\n{yaml_text}---\n"


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML not installed; required for core.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level must be a mapping")
    return data


def _load_json5(path: Path) -> Any:
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        import json5
        return json5.loads(text)
    except ImportError:
        # Strict JSON fallback; will fail on // comments / trailing commas.
        return json.loads(text)


# ---------------------------------------------------------- public API ------

def load_core() -> dict:
    """Load core.yaml (workspaces, defaults, rag, learning_state, …)."""
    return _load_yaml(CORE_YAML)


def load_connector(name: str) -> tuple[dict, str]:
    """Load connectors/<name>.md → (frontmatter, body)."""
    path = CONNECTORS_DIR / f"{name}.md"
    if not path.exists():
        return {}, ""
    return _parse_frontmatter(path.read_text(encoding="utf-8"))


def load_repos() -> tuple[dict, str]:
    """Load repos.md → (frontmatter, body)."""
    if not REPOS_MD.exists():
        return {}, ""
    return _parse_frontmatter(REPOS_MD.read_text(encoding="utf-8"))


def load_links() -> list[dict]:
    """Load links.json5 — list of {from, to, relation, [notes]} edges."""
    data = _load_json5(LINKS_JSON5)
    if data is None:
        return []
    if isinstance(data, dict):
        # Tolerate {links: [...]} wrapper.
        return data.get("links", []) or []
    if isinstance(data, list):
        return data
    raise ValueError(f"{LINKS_JSON5}: must be an array or {{links: [...]}}")


def save_connector(name: str, frontmatter: dict, notes: str) -> None:
    """Atomic write of connectors/<name>.md under lock."""
    path = CONNECTORS_DIR / f"{name}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_suffix(".md.lock")
    with _file_lock(lock):
        path.write_text(_emit_frontmatter(frontmatter, notes), encoding="utf-8")


# ---------------------------------------------------------- graph -----------

def entity_key(kind: str, id_: str) -> str:
    return f"{kind}:{id_}"


def parse_entity_key(key: str) -> tuple[str, str]:
    if ":" not in key:
        raise ValueError(f"bad entity key {key!r} — expected kind:id")
    kind, _, ident = key.partition(":")
    return kind, ident


def neighbors(links: list[dict], key: str) -> list[str]:
    """Return 1-hop neighbours of `key`. Bidirectional — both `from` and `to` count."""
    out: list[str] = []
    for e in links:
        if e.get("from") == key and e.get("to"):
            out.append(e["to"])
        elif e.get("to") == key and e.get("from"):
            out.append(e["from"])
    # Dedup while preserving order.
    seen: set[str] = set()
    result: list[str] = []
    for k in out:
        if k not in seen:
            seen.add(k)
            result.append(k)
    return result


def expand(links: list[dict], key: str, depth: int = 2) -> set[str]:
    """N-hop closure starting at `key`."""
    visited = {key}
    frontier = {key}
    for _ in range(depth):
        next_frontier: set[str] = set()
        for k in frontier:
            for n in neighbors(links, k):
                if n not in visited:
                    visited.add(n)
                    next_frontier.add(n)
        if not next_frontier:
            break
        frontier = next_frontier
    return visited


def edges_touching(links: list[dict], key: str) -> list[dict]:
    """All edges where `key` appears as either endpoint."""
    return [e for e in links if e.get("from") == key or e.get("to") == key]


# ---------------------------------------------------------- CLI ------------

def _cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show-core")
    p = sub.add_parser("show-connector"); p.add_argument("name")
    sub.add_parser("show-repos")
    sub.add_parser("show-links")
    p = sub.add_parser("neighbors"); p.add_argument("key")
    p = sub.add_parser("expand"); p.add_argument("key"); p.add_argument("--depth", type=int, default=2)
    args = ap.parse_args()

    if args.cmd == "show-core":
        print(json.dumps(load_core(), indent=2, default=str))
    elif args.cmd == "show-connector":
        fm, notes = load_connector(args.name)
        print(json.dumps({"frontmatter": fm, "notes": notes}, indent=2, default=str))
    elif args.cmd == "show-repos":
        fm, notes = load_repos()
        print(json.dumps({"frontmatter": fm, "notes_chars": len(notes)}, indent=2, default=str))
    elif args.cmd == "show-links":
        print(json.dumps(load_links(), indent=2))
    elif args.cmd == "neighbors":
        print(json.dumps(neighbors(load_links(), args.key), indent=2))
    elif args.cmd == "expand":
        print(json.dumps(sorted(expand(load_links(), args.key, args.depth)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())

```
