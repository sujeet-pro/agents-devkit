"""pr_pipeline/approach.py — per-stage approach picker.

pick_approach() is the narrow bridge between the pipeline stages and the
question-first / decision-log contract.  In auto mode (default) it returns the
recommended option immediately and logs an `auto-defaulted` entry to
decisions.jsonl.  In interactive mode (-i) it prints the options to stderr and
reads the user's choice from stdin, then logs a `user-answered` entry.

Usage:
  from pr_pipeline.approach import pick_approach

  mode = pick_approach(
      fork_id="index-mode",
      options=["incremental", "rebuild", "skip", "seed-and-overlay"],
      recommended="seed-and-overlay",
      interactive=False,
      repo="my-repo",
      task_slug="my-repo_pr-42",
  )
"""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

try:
    from decision_logger import append_decision  # noqa: E402
except Exception:
    def append_decision(*_a, **_kw):  # type: ignore[misc]
        pass


def pick_approach(
    *,
    fork_id: str,
    options: list[str],
    recommended: str,
    interactive: bool = False,
    repo: str = "",
    task_slug: str = "",
    sub_flow: str | None = None,
) -> str:
    """Return the chosen option and log the fork to decisions.jsonl.

    In auto mode (default): returns `recommended` without prompting.
    In interactive mode: prompts on stderr + reads from stdin; falls back to
    `recommended` on EOF or invalid input.
    """
    if not interactive:
        chosen = recommended
        try:
            append_decision(
                skill="adk-pr-review",
                sub_flow=sub_flow,
                fork_id=fork_id,
                fork_type="auto-defaulted",
                options=options,
                default_offered=recommended,
                user_chose=recommended,
                repo=repo or None,
                task_slug=task_slug or None,
            )
        except Exception:
            pass
        return chosen

    # Interactive mode: ask on stderr so stdout stays machine-readable.
    sys.stderr.write(f"\n  fork: {fork_id}\n")
    for i, opt in enumerate(options, 1):
        marker = " [recommended]" if opt == recommended else ""
        sys.stderr.write(f"    {i}. {opt}{marker}\n")
    sys.stderr.write(f"  choose [1-{len(options)}] or press Enter for recommended: ")
    sys.stderr.flush()
    try:
        raw = sys.stdin.readline().strip()
    except (EOFError, OSError):
        raw = ""

    chosen = recommended
    if raw.isdigit():
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            chosen = options[idx]

    fork_type = "user-answered" if (raw and chosen != recommended) else "auto-defaulted"
    try:
        append_decision(
            skill="adk-pr-review",
            sub_flow=sub_flow,
            fork_id=fork_id,
            fork_type=fork_type,
            options=options,
            default_offered=recommended,
            user_chose=chosen,
            repo=repo or None,
            task_slug=task_slug or None,
        )
    except Exception:
        pass
    return chosen
