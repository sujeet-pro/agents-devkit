#!/usr/bin/env python3
"""parse_pr_url.py — accept a PR URL, emit {host, owner, repo, pr_number} as JSON."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import parse_pr_url, emit_json, die  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="PR URL (github.com/o/r/pull/n or bitbucket.org/ws/r/pull-requests/n)")
    args = ap.parse_args()
    try:
        parsed = parse_pr_url(args.url)
    except ValueError as e:
        die(str(e))
        return 1  # unreachable
    return emit_json(parsed)


if __name__ == "__main__":
    raise SystemExit(main())
