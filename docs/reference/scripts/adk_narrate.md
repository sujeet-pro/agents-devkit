---
title: 'adk_narrate.py'
description: 'adk_narrate.py — consistent CLI narration helpers for adk skills.'
script: 'adk_narrate.py'
source: 'scripts/adk_narrate.py'
group: 'scripts'
order: 4002
---
# adk_narrate.py

adk_narrate.py — consistent CLI narration helpers for adk skills.

## Source

`scripts/adk_narrate.py`

## Contents

```python
#!/usr/bin/env python3
"""adk_narrate.py — consistent CLI narration helpers for adk skills.

Every adk skill should narrate its progress per `shared/narration.md`. Skill
orchestrators can either format their own one-line status updates or import this
module to keep the glyph set + spacing identical across skills.

The functions here print to **stderr** so they don't pollute structured stdout
output (some scripts emit JSON to stdout that downstream parsers consume).

API:
  narrate.start(skill, input)
  narrate.phase(name)              # phase boundary
  narrate.decision(fork, choice, reason)
  narrate.step(cmd_summary)        # `$ …`
  narrate.gap(name, reason)        # `! …`
  narrate.ask(question)            # `? …` — caller decides whether to wait
  narrate.tick(message)            # progress tick during a long phase
  narrate.done(elapsed_s, summary_path=None)

CLI usage (for shell-only orchestrators):
  python3 adk_narrate.py start  --skill pr-review --input "<url>"
  python3 adk_narrate.py phase  --name "worktree (serialized)"
  python3 adk_narrate.py decision --fork scope --choice vertical-slice --reason "prior 3 tickets"
  python3 adk_narrate.py step   --cmd "git fetch --all --prune"
  python3 adk_narrate.py gap    --name statsig --reason "unreachable"
  python3 adk_narrate.py done   --elapsed 134 --report /path/to/report.md
"""
from __future__ import annotations

import argparse
import os
import sys
import time

# Use ASCII glyphs if NO_UTF8=1 or the terminal is dumb. Otherwise the prettier set.
_PRETTY = not os.environ.get("NO_UTF8") and os.environ.get("TERM", "") not in ("dumb", "")

START_GLYPH = "▶" if _PRETTY else ">"
PHASE_GLYPH = "·" if _PRETTY else "-"
DEC_GLYPH = "→" if _PRETTY else ">"
STEP_GLYPH = "$"
GAP_GLYPH = "⚠" if _PRETTY else "!"
ASK_GLYPH = "❓" if _PRETTY else "?"
TICK_GLYPH = "…" if _PRETTY else "..."
DONE_GLYPH = "▣" if _PRETTY else "#"


def _emit(line: str) -> None:
    sys.stderr.write(line + "\n")
    sys.stderr.flush()


def start(skill: str, input_: str) -> None:
    _emit(f"{START_GLYPH} /adk-{skill} {input_}")


def phase(name: str) -> None:
    _emit(f"  {PHASE_GLYPH} {name}")


def decision(fork: str, choice: str, reason: str = "") -> None:
    suffix = f"  ({reason})" if reason else ""
    _emit(f"  {DEC_GLYPH} {fork}={choice}{suffix}")


def step(cmd_summary: str) -> None:
    _emit(f"  {STEP_GLYPH} {cmd_summary}")


def gap(name: str, reason: str = "") -> None:
    suffix = f" — {reason}" if reason else ""
    _emit(f"  {GAP_GLYPH} {name}{suffix}")


def ask(question: str) -> None:
    """Print a confirmation question. Caller decides whether to wait for stdin."""
    _emit(f"  {ASK_GLYPH} {question}")


def tick(message: str) -> None:
    _emit(f"  {TICK_GLYPH} {message}")


def done(elapsed_s: float, summary_path: str | None = None) -> None:
    bits = [f"{DONE_GLYPH} done in {_fmt_elapsed(elapsed_s)}"]
    if summary_path:
        bits.append(f"summary: {summary_path}")
    _emit("  ".join(bits))


def _fmt_elapsed(seconds: float) -> str:
    if seconds < 1:
        return f"{int(seconds * 1000)}ms"
    if seconds < 60:
        return f"{seconds:.1f}s"
    m = int(seconds // 60)
    s = int(seconds - 60 * m)
    return f"{m}m{s:02d}s"


def _cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start"); p.add_argument("--skill", required=True); p.add_argument("--input", required=True)
    p = sub.add_parser("phase"); p.add_argument("--name", required=True)
    p = sub.add_parser("decision"); p.add_argument("--fork", required=True); p.add_argument("--choice", required=True); p.add_argument("--reason", default="")
    p = sub.add_parser("step"); p.add_argument("--cmd", required=True)
    p = sub.add_parser("gap"); p.add_argument("--name", required=True); p.add_argument("--reason", default="")
    p = sub.add_parser("ask"); p.add_argument("--question", required=True)
    p = sub.add_parser("tick"); p.add_argument("--message", required=True)
    p = sub.add_parser("done"); p.add_argument("--elapsed", type=float, required=True); p.add_argument("--report", default=None)
    args = ap.parse_args()

    if args.cmd == "start":     start(args.skill, args.input)
    elif args.cmd == "phase":    phase(args.name)
    elif args.cmd == "decision": decision(args.fork, args.choice, args.reason)
    elif args.cmd == "step":     step(args.cmd)
    elif args.cmd == "gap":      gap(args.name, args.reason)
    elif args.cmd == "ask":      ask(args.question)
    elif args.cmd == "tick":     tick(args.message)
    elif args.cmd == "done":     done(args.elapsed, args.report)
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())

```
