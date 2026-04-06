#!/usr/bin/env python3
"""
Optional external TUI for adk-interactivity sessions.

This script edits a JSON/YAML session file in place by collecting answers in a
terminal UI. It prefers Python Textual when available, and falls back to plain
terminal prompts if Textual is not installed.

Usage:
    python3 interactivity.py <session-file>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

try:
    # Optional runtime dependency for richer terminal interactivity.
    from textual.app import App  # type: ignore
except Exception:  # pragma: no cover
    App = None


def load_session(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML session files")
        return yaml.safe_load(text) or {}
    return json.loads(text or "{}")


def save_session(path: Path, data: dict) -> None:
    if path.suffix.lower() in {".yaml", ".yml"}:
        if yaml is None:
            raise RuntimeError("PyYAML is required for YAML session files")
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    else:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def prompt_one(item: dict) -> dict:
    item_id = item.get("id", "unknown")
    prompt = item.get("prompt", item_id)
    item_type = item.get("type", "text")
    options = item.get("options", [])

    print(f"\n[{item_id}] {prompt}")

    if item_type in {"single_choice", "multi_choice"} and options:
        for idx, opt in enumerate(options, start=1):
            print(f"  {idx}. {opt.get('label', opt.get('id', f'option-{idx}'))}")
        if item_type == "single_choice":
            raw = input("Select one number: ").strip()
            try:
                picked = options[int(raw) - 1]
                value = picked.get("id")
            except Exception:
                value = None
        else:
            raw = input("Select one or more numbers (comma-separated): ").strip()
            ids: list[str] = []
            for part in [p.strip() for p in raw.split(",") if p.strip()]:
                try:
                    ids.append(str(options[int(part) - 1].get("id")))
                except Exception:
                    continue
            value = ids
    elif item_type == "boolean":
        raw = input("Answer [y/n]: ").strip().lower()
        value = raw in {"y", "yes", "true", "1"}
    else:
        value = input("Answer: ")

    return {"id": item_id, "value": value}


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python3 interactivity.py <session-file>")
        return 1

    session_path = Path(sys.argv[1]).expanduser().resolve()
    if not session_path.exists():
        print(f"Session file not found: {session_path}")
        return 1

    data = load_session(session_path)
    items = data.get("items", [])
    if not isinstance(items, list):
        print("Invalid session format: 'items' must be a list")
        return 1

    if App is None:
        print("Textual not installed; using prompt fallback mode.")

    results = []
    for item in items:
        if isinstance(item, dict):
            results.append(prompt_one(item))

    data["results"] = results
    data["status"] = "completed"
    save_session(session_path, data)
    print(f"\nUpdated session written to: {session_path}")
    print("Return to the agent and continue.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
