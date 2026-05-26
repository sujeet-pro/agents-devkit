#!/usr/bin/env python3
"""decision_logger.py — append a JSONL line to $ADK_DATA_HOME/improve/learning/decisions.jsonl.

Called from skills whenever a non-trivial fork is resolved.

Usage:
  python3 scripts/decision_logger.py --skill adk-implement --sub-flow from-jira \\
      --fork-id scope --fork-type user-answered \\
      --default-offered vertical-slice --user-chose full \\
      --reason "demo Monday" --repo storefront-bff --task-slug implement-SF-1234

  # or stdin a full JSON object:
  echo '{"skill":"adk-implement",...}' | python3 scripts/decision_logger.py --json
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

_LIB_DIR = Path(__file__).resolve().parent / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from config import adk_learning_home  # noqa: E402

LOG_DIR = adk_learning_home()
LOG_FILE = LOG_DIR / "decisions.jsonl"

VALID_FORK_TYPES = {"user-answered", "auto-defaulted", "override-applied", "inferred", "escalation"}


def ensure_log_dir() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="append a decision-log entry")
    p.add_argument("--json", action="store_true", help="read a JSON object from stdin")
    p.add_argument("--skill", help="e.g. adk-implement")
    p.add_argument("--sub-flow", default=None)
    p.add_argument("--fork-id", help="stable identifier for this fork")
    p.add_argument("--fork-type", choices=sorted(VALID_FORK_TYPES))
    p.add_argument("--question", default=None)
    p.add_argument("--options", default=None, help="comma-separated")
    p.add_argument("--default-offered", default=None)
    p.add_argument("--user-chose", default=None)
    p.add_argument("--reason", default=None)
    p.add_argument("--evidence", default=None)
    p.add_argument("--repo", default=None)
    p.add_argument("--workspace", default=None)
    p.add_argument("--task-slug", default=None)
    return p.parse_args()


def from_args(a: argparse.Namespace) -> dict[str, object]:
    if a.json:
        return json.loads(sys.stdin.read())
    if not (a.skill and a.fork_id and a.fork_type):
        raise SystemExit("--skill, --fork-id, --fork-type are required (or use --json)")
    entry: dict[str, object] = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "skill": a.skill,
        "sub_flow": a.sub_flow,
        "fork_id": a.fork_id,
        "fork_type": a.fork_type,
    }
    if a.question:
        entry["question"] = a.question
    if a.options:
        entry["options"] = [o.strip() for o in a.options.split(",") if o.strip()]
    if a.default_offered:
        entry["default_offered"] = a.default_offered
    if a.user_chose:
        entry["user_chose"] = a.user_chose
    if a.reason:
        entry["reason_if_given"] = a.reason
    if a.evidence:
        entry["evidence"] = a.evidence
    if a.repo:
        entry["repo"] = a.repo
    if a.workspace:
        entry["workspace"] = a.workspace
    if a.task_slug:
        entry["task_slug"] = a.task_slug
    return entry


def append_decision(skill: str, fork_id: str, fork_type: str,
                    sub_flow: str | None = None,
                    question: str | None = None,
                    options: list[str] | None = None,
                    default_offered: str | None = None,
                    user_chose: str | None = None,
                    reason: str | None = None,
                    evidence: str | None = None,
                    repo: str | None = None,
                    workspace: str | None = None,
                    task_slug: str | None = None,
                    **extras: object) -> None:
    """Importable helper — one call per fork from any skill script.

    Never raises: a decision-log write must NEVER block the actual skill
    work. Caller passes None for fields it doesn't have; only populated
    fields land in the JSONL.

    Schema: shared/decision-log-schema.md.
    """
    if fork_type not in VALID_FORK_TYPES:
        # Refuse silently rather than raising — but log the issue so it
        # surfaces in stderr without breaking the parent run.
        sys.stderr.write(f"decision_logger: bad fork_type {fork_type!r}; dropping entry\n")
        return
    entry: dict[str, object] = {
        "ts": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "skill": skill,
        "sub_flow": sub_flow,
        "fork_id": fork_id,
        "fork_type": fork_type,
    }
    for k, v in (
        ("question", question),
        ("default_offered", default_offered),
        ("user_chose", user_chose),
        ("reason_if_given", reason),
        ("evidence", evidence),
        ("repo", repo),
        ("workspace", workspace),
        ("task_slug", task_slug),
    ):
        if v is not None:
            entry[k] = v
    if options:
        entry["options"] = list(options)
    if extras:
        entry.update(extras)
    try:
        ensure_log_dir()
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        sys.stderr.write(f"decision_logger: write failed ({e}); dropping entry\n")


def main() -> int:
    args = parse_args()
    entry = from_args(args)
    if entry.get("fork_type") not in VALID_FORK_TYPES:
        raise SystemExit(f"fork_type must be one of {sorted(VALID_FORK_TYPES)}")
    ensure_log_dir()
    line = json.dumps(entry, ensure_ascii=False)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
