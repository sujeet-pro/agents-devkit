"""skill_run.py — run any /adk-* skill in a selected agent harness."""
from __future__ import annotations

import argparse
import shlex
import subprocess
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from agent_harness import build_agent_cmd, resolve_runner_model  # noqa: E402


def _normalize_skill(name: str) -> str:
    name = name.strip()
    if name.startswith("/"):
        name = name[1:]
    if not name.startswith("adk-"):
        name = f"adk-{name}"
    return name


def _prompt_for(skill: str, skill_args: list[str], *, detailed: bool,
                deep: bool) -> str:
    parts = [f"/{_normalize_skill(skill)}"]
    parts.extend(skill_args)
    if detailed and "--detailed" not in parts:
        parts.append("--detailed")
    if deep and "--deep" not in parts:
        parts.append("--deep")
    return " ".join(shlex.quote(p) for p in parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        prog="adk skill-run",
        description="Run any ADK slash skill in Claude, Cursor, Codex, or a custom harness.",
    )
    ap.add_argument("skill", help="skill name, with or without leading slash/adk-")
    ap.add_argument("skill_args", nargs=argparse.REMAINDER,
                    help="arguments passed through to the skill; use -- before args that look like flags")
    ap.add_argument("--runner", choices=("claude", "cursor", "codex", "custom"),
                    default="claude")
    ap.add_argument("--agent", default=None,
                    help="override runner binary")
    ap.add_argument("--agent-model", default=None,
                    help="explicit model override for harnesses that support --model")
    ap.add_argument("--workspace", default=str(Path.cwd()),
                    help="workspace passed to Cursor/Codex harnesses")
    ap.add_argument("--detailed", action="store_true",
                    help="forward --detailed to the skill (programmatic detail, e.g. embeddings)")
    ap.add_argument("--deep", action="store_true",
                    help="forward --deep and choose the deep model profile")
    ap.add_argument("--planning", action="store_true",
                    help="choose the planning model profile unless --deep is set")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the command that would run")
    args = ap.parse_args(argv)

    skill_args = list(args.skill_args or [])
    if skill_args and skill_args[0] == "--":
        skill_args = skill_args[1:]
    prompt = _prompt_for(
        args.skill,
        skill_args,
        detailed=args.detailed,
        deep=args.deep,
    )
    model = resolve_runner_model(
        runner=args.runner,
        explicit_model=args.agent_model,
        deep=args.deep,
        planning=args.planning,
    )
    try:
        cmd = build_agent_cmd(
            prompt,
            runner=args.runner,
            agent=args.agent,
            model=model,
            workspace=Path(args.workspace),
        )
    except ValueError as e:
        print(f"adk skill-run: {e}", file=sys.stderr)
        return 2

    if args.dry_run:
        print(" ".join(shlex.quote(c) for c in cmd))
        return 0
    return subprocess.run(cmd, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
