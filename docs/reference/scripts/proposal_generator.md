---
title: 'proposal_generator.py'
description: 'proposal_generator.py — analyze ~/.config/adk/learning/decisions.jsonl and'
script: 'proposal_generator.py'
source: 'scripts/proposal_generator.py'
group: 'scripts'
order: 4008
---
# proposal_generator.py

proposal_generator.py — analyze ~/.config/adk/learning/decisions.jsonl and

## Source

`scripts/proposal_generator.py`

## Contents

```python
#!/usr/bin/env python3
"""proposal_generator.py — analyze ~/.config/adk/learning/decisions.jsonl and
suggest defaults to update in ~/.config/adk/overrides.yaml.

This is the PROGRAMMATIC pattern-detector. /adk-improve calls it, then uses
the AI step to wrap the proposals in user-facing prose + apply diffs after
user confirms.

Usage:
  python3 scripts/proposal_generator.py [--skill <name>] [--since <date>] [--min-evidence N]

Output: JSON proposals to stdout. Each proposal lists evidence lines verbatim.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

LEARNING = Path(os.path.expanduser("~/.config/adk/learning"))
DECISIONS = LEARNING / "decisions.jsonl"
DEFAULT_MIN_EVIDENCE = 3


def read_decisions(since: dt.datetime | None) -> list[dict[str, Any]]:
    if not DECISIONS.exists():
        return []
    rows: list[dict[str, Any]] = []
    with DECISIONS.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if since is not None:
                ts = row.get("ts")
                if ts:
                    try:
                        rts = dt.datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        if rts < since:
                            continue
                    except ValueError:
                        pass
            rows.append(row)
    return rows


def detect_patterns(rows: list[dict[str, Any]], skill_filter: str | None,
                     min_evidence: int) -> list[dict[str, Any]]:
    """Group by (skill, sub_flow, fork_id); count user_chose values; emit proposals
    where one choice dominates over the prior default_offered with >= min_evidence."""
    bucket: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        # Skip non-learning fork types
        if r.get("fork_type") not in ("user-answered", "auto-defaulted"):
            continue
        if skill_filter and r.get("skill") != skill_filter:
            continue
        key = (r.get("skill") or "?", r.get("sub_flow") or "", r.get("fork_id") or "?")
        bucket[key].append(r)

    proposals: list[dict[str, Any]] = []
    for key, group in bucket.items():
        skill, sub_flow, fork_id = key
        choices = Counter(r.get("user_chose") for r in group if r.get("user_chose"))
        if not choices:
            continue
        top_choice, top_count = choices.most_common(1)[0]
        if top_count < min_evidence:
            continue
        # Were users overriding a different default?
        offered_counter = Counter(r.get("default_offered") for r in group if r.get("default_offered"))
        usual_offered = offered_counter.most_common(1)[0][0] if offered_counter else None
        # Only propose if the top choice differs from the usual default (otherwise nothing to update).
        if usual_offered is None or top_choice == usual_offered:
            continue
        # Confidence
        total = sum(choices.values())
        confidence = "high" if top_count / total >= 0.75 else "medium"
        evidence = [
            {
                "ts": r.get("ts"),
                "task_slug": r.get("task_slug"),
                "reason": r.get("reason_if_given"),
                "fork_type": r.get("fork_type"),
            }
            for r in group if r.get("user_chose") == top_choice
        ][:5]
        proposals.append({
            "skill": skill,
            "sub_flow": sub_flow,
            "fork_id": fork_id,
            "current_default": usual_offered,
            "proposed_default": top_choice,
            "evidence_count": top_count,
            "evidence_total": total,
            "confidence": confidence,
            "evidence": evidence,
            "yaml_path": f"defaults.{skill}.{fork_id}",
        })
    proposals.sort(key=lambda p: (-p["evidence_count"], p["skill"], p["fork_id"]))
    return proposals


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", default=None)
    ap.add_argument("--since", default=None, help="ISO date, e.g. 2026-05-01")
    ap.add_argument("--min-evidence", type=int, default=DEFAULT_MIN_EVIDENCE)
    args = ap.parse_args()

    since: dt.datetime | None = None
    if args.since:
        try:
            since = dt.datetime.fromisoformat(args.since).replace(tzinfo=dt.timezone.utc)
        except ValueError:
            print(f"bad --since value: {args.since}", file=sys.stderr)
            return 2

    rows = read_decisions(since)
    proposals = detect_patterns(rows, args.skill, args.min_evidence)
    print(json.dumps({
        "decisions_scanned": len(rows),
        "since": args.since,
        "min_evidence": args.min_evidence,
        "proposals": proposals,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

```
