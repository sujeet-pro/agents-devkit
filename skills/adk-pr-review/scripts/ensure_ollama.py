#!/usr/bin/env python3
"""ensure_ollama.py — probe ollama install + daemon + embedding model.

Refuses to install for the user. Prints the install command on miss.

Usage:
  python3 ensure_ollama.py --model nomic-embed-text [--json] [--probe-only]
Exit codes:
  0 — all checks passed
  2 — ollama binary missing
  3 — daemon not responding at :11434
  4 — model not pulled
  5 — daemon responding but /api/embed failed
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import which, emit_json  # noqa: E402

try:
    import requests
except ImportError:
    print(
        "adk-pr-review: `requests` not installed. Install: pip install -r "
        f"{Path(__file__).parent / 'requirements.txt'}",
        file=sys.stderr,
    )
    raise SystemExit(1)

OLLAMA_HOST = "http://localhost:11434"


def check_binary() -> str | None:
    return which("ollama")


def check_daemon(timeout: float = 2.0) -> bool:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/version", timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return False


def check_model(name: str, timeout: float = 5.0) -> bool:
    try:
        r = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=timeout)
        if r.status_code != 200:
            return False
        data = r.json()
        return any(m.get("name", "").split(":")[0] == name.split(":")[0] for m in data.get("models", []))
    except requests.RequestException:
        return False


def exercise_embed(name: str, timeout: float = 10.0) -> tuple[bool, int]:
    """Hit /api/embed with a 5-token input; return (ok, dim)."""
    try:
        r = requests.post(
            f"{OLLAMA_HOST}/api/embed",
            json={"model": name, "input": "ping", "keep_alive": "1m"},
            timeout=timeout,
        )
        if r.status_code != 200:
            return False, 0
        data = r.json()
        emb = data.get("embeddings", [])
        if emb and isinstance(emb[0], list):
            return True, len(emb[0])
        return False, 0
    except requests.RequestException:
        return False, 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="nomic-embed-text")
    ap.add_argument("--probe-only", action="store_true", help="don't exercise /api/embed, just check tags")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result: dict[str, object] = {"model": args.model, "host": OLLAMA_HOST}

    bin_path = check_binary()
    result["binary"] = bin_path or None
    if not bin_path:
        result["status"] = "binary_missing"
        result["hint"] = "Install: brew install ollama (macOS) or https://ollama.com/download"
        if args.json:
            return emit_json(result)
        print(json.dumps(result, indent=2), file=sys.stderr)
        return 2

    if not check_daemon():
        result["status"] = "daemon_not_responding"
        result["hint"] = "Start: `ollama serve &` (or run the Ollama.app)"
        if args.json:
            return emit_json(result)
        print(json.dumps(result, indent=2), file=sys.stderr)
        return 3

    if not check_model(args.model):
        result["status"] = "model_not_pulled"
        result["hint"] = f"Pull: ollama pull {args.model}"
        if args.json:
            return emit_json(result)
        print(json.dumps(result, indent=2), file=sys.stderr)
        return 4

    if not args.probe_only:
        ok, dim = exercise_embed(args.model)
        result["embed_ok"] = ok
        result["dim"] = dim
        if not ok:
            result["status"] = "embed_failed"
            result["hint"] = "Daemon responds but /api/embed failed. Check `ollama logs`."
            if args.json:
                return emit_json(result)
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 5

    result["status"] = "ok"
    if args.json:
        return emit_json(result)
    print("ollama: ok", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
