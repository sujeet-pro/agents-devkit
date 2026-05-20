#!/usr/bin/env python3
"""adk_info.py — read ~/.agents-devkit/config/overrides.yaml and emit JSON.

Three modes:
  - dump-all (default): full merged JSON of overrides + repo-level .adk/overrides.yaml if cwd is in a configured repo
  - --topic <name>: just one top-level key (workspaces / repos / data_sources / rag / defaults / enriched / learning_state)
  - --key <dotted.path>: one specific value, e.g. --key repos.0.datadog.apm_service

Never prints secrets — env-var values, even if interpolated.

Usage:
  python3 scripts/adk_info.py
  python3 scripts/adk_info.py --topic repos
  python3 scripts/adk_info.py --key defaults.adk-implement.scope
  python3 scripts/adk_info.py --check
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

OVERRIDES = Path(os.path.expanduser("~/.agents-devkit/config/overrides.yaml"))


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
    except ImportError:
        sys.stderr.write(
            "adk_info: PyYAML not installed (`pip install pyyaml` or `uv pip install pyyaml`). "
            "Falling back to a flat parse — nested fields will be unavailable.\n"
        )
        return _flat_parse(path)
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _flat_parse(path: Path) -> dict[str, Any]:
    """Minimal fallback if PyYAML unavailable. Only top-level key: value."""
    out: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].rstrip()
        if not line or line.startswith(" ") or ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip("\"'") or {}
    return out


def find_repo_overrides(cwd: Path, base: dict[str, Any]) -> dict[str, Any] | None:
    """If cwd is in a repo with .adk/overrides.yaml, return it."""
    p = cwd
    while p != p.parent:
        repo_overrides = p / ".adk" / "overrides.yaml"
        if repo_overrides.exists():
            return load_yaml(repo_overrides)
        if (p / ".git").exists():
            break
        p = p.parent
    return None


def deep_merge(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    """Right (b) wins on scalar conflicts. Lists are concatenated."""
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = deep_merge(out[k], v)
        elif k in out and isinstance(out[k], list) and isinstance(v, list):
            out[k] = out[k] + v
        else:
            out[k] = v
    return out


def get_dotted(obj: Any, path: str) -> Any:
    for part in path.split("."):
        if isinstance(obj, list):
            try:
                idx = int(part)
            except ValueError:
                return None
            if 0 <= idx < len(obj):
                obj = obj[idx]
            else:
                return None
        elif isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
        if obj is None:
            return None
    return obj


def _detect_unset_envs(merged: dict[str, Any], path: str = "") -> list[str]:
    """Find ${VAR} placeholders in string values that aren't set in env."""
    unset: list[str] = []
    if isinstance(merged, dict):
        for k, v in merged.items():
            unset.extend(_detect_unset_envs(v, f"{path}.{k}" if path else k))
    elif isinstance(merged, list):
        for i, v in enumerate(merged):
            unset.extend(_detect_unset_envs(v, f"{path}.{i}"))
    elif isinstance(merged, str):
        import re
        for m in re.finditer(r"\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}", merged):
            var = m.group(1)
            if var not in os.environ:
                unset.append(f"{var} (referenced at {path})")
    return unset


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", help="emit one top-level key")
    ap.add_argument("--key", help="emit one dotted-path value")
    ap.add_argument("--check", action="store_true", help="list referenced env vars that are unset")
    ap.add_argument("--no-repo-merge", action="store_true", help="don't merge cwd's .adk/overrides.yaml")
    args = ap.parse_args()

    base = load_yaml(OVERRIDES)
    if not base:
        sys.stderr.write(
            f"adk_info: {OVERRIDES} not found or empty. Run `/adk-setup --init` first.\n"
        )
        return 1

    merged = base
    if not args.no_repo_merge:
        repo_layer = find_repo_overrides(Path.cwd(), base)
        if repo_layer:
            merged = deep_merge(base, repo_layer)

    if args.check:
        unset = _detect_unset_envs(merged)
        if unset:
            print(json.dumps({"unset_env_vars": unset}, indent=2))
            return 1
        print(json.dumps({"unset_env_vars": []}, indent=2))
        return 0

    if args.key:
        val = get_dotted(merged, args.key)
        if val is None:
            sys.stderr.write(f"adk_info: key not found: {args.key}\n")
            return 2
        print(json.dumps(val, indent=2, ensure_ascii=False))
        return 0

    if args.topic:
        val = merged.get(args.topic)
        if val is None:
            sys.stderr.write(f"adk_info: topic not found: {args.topic}\n")
            return 2
        print(json.dumps(val, indent=2, ensure_ascii=False))
        return 0

    print(json.dumps(merged, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
