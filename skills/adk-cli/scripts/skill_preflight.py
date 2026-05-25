"""Skill dependency preflight shared by CLI, TUI, and skill launchers."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
MCP_DIR = REPO_ROOT / "mcp"

sys.path.insert(0, str(THIS_DIR))
from agent_harness import resolve_runner_model  # noqa: E402


def load_skill_metadata(skill: str) -> dict:
    name = _normalize_skill(skill)
    path = SKILLS_DIR / name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"skill not found: {name}")
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    _, _, rest = text.partition("---")
    fm, _, _body = rest.partition("---")
    try:
        import yaml
        data = yaml.safe_load(fm) or {}
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def preflight(skill: str, *, runner: str = "inherit", agent: str | None = None,
              model: str | None = None, deep: bool = False) -> dict:
    meta = load_skill_metadata(skill).get("metadata") or {}
    required_cli = list(meta.get("needs_cli") or [])
    optional_cli = list(meta.get("needs_cli_optional") or [])
    required_mcp = list(meta.get("needs_mcp_required") or [])
    optional_mcp = list(meta.get("needs_mcp_optional") or [])

    cli = [_check_cli(name, required=True) for name in required_cli]
    cli += [_check_cli(name, required=False) for name in optional_cli]
    mcp = [_check_mcp(name, required=True) for name in required_mcp]
    mcp += [_check_mcp(name, required=False) for name in optional_mcp]
    runner_info = _check_runner(runner, agent=agent)
    resolved_model = None if model in {None, "", "inherit"} else model
    if resolved_model is None and runner != "inherit":
        resolved_model = resolve_runner_model(runner=runner, explicit_model=None, deep=deep)
    blockers = [
        item for item in [*cli, *mcp, runner_info]
        if item.get("required") and item.get("status") in {"missing", "fail"}
    ]
    degraded = [
        item for item in [*cli, *mcp]
        if not item.get("required") and item.get("status") in {"missing", "fail"}
    ]
    status = "blocked" if blockers else ("degraded" if degraded else "ok")
    return {
        "skill": _normalize_skill(skill),
        "status": status,
        "decision": "stop" if status == "blocked" else ("proceed_degraded" if status == "degraded" else "proceed"),
        "runner": runner_info,
        "model": {
            "mode": model or "inherit",
            "resolved": resolved_model,
        },
        "cli": cli,
        "mcp": mcp,
        "blockers": blockers,
    }


def _check_cli(name: str, *, required: bool) -> dict:
    path = shutil.which(name)
    return {
        "name": name,
        "required": required,
        "status": "ok" if path else "missing",
        "detail": path or f"{name} not found on PATH",
        "fallback": None if required else _optional_cli_fallback(name),
    }


def _check_mcp(name: str, *, required: bool) -> dict:
    descriptor = MCP_DIR / f"{name}.json"
    exists = descriptor.exists()
    return {
        "name": name,
        "required": required,
        "status": "ok" if exists else "missing",
        "detail": str(descriptor) if exists else f"{descriptor} missing",
        "fallback": None if required else "skip MCP-backed enrichment and record degraded mode",
    }


def _check_runner(runner: str, *, agent: str | None) -> dict:
    if runner == "inherit":
        return {"mode": "inherit", "resolved": None, "available": True, "required": False, "status": "ok"}
    binary = agent or {"claude": "claude", "cursor": "cursor", "codex": "codex"}.get(runner, agent)
    path = shutil.which(binary) if binary else None
    return {
        "mode": runner,
        "resolved": binary,
        "available": bool(path),
        "required": True,
        "status": "ok" if path else "missing",
        "detail": path or f"{binary} not found on PATH",
    }


def _optional_cli_fallback(name: str) -> str:
    if name.startswith("scip-"):
        return "fall back to chunk parent_symbol + grep"
    return "skip optional enhancement"


def _normalize_skill(name: str) -> str:
    name = name.strip().lstrip("/")
    if not name.startswith("adk-"):
        name = f"adk-{name}"
    return name


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk skill-preflight")
    ap.add_argument("skill")
    ap.add_argument("--runner", choices=("inherit", "claude", "cursor", "codex", "custom"),
                    default="inherit")
    ap.add_argument("--agent", default=None)
    ap.add_argument("--model", default="inherit")
    ap.add_argument("--deep", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        result = preflight(args.skill, runner=args.runner, agent=args.agent,
                           model=args.model, deep=args.deep)
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
