#!/usr/bin/env python3
"""
Generate runtime-specific custom agent projections from canonical agent personas.

Usage:
    python3 scripts/generate_agent_projections.py
    python3 scripts/generate_agent_projections.py --check
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CANONICAL_AGENTS_DIR = ROOT / "agent-personas"

CLAUDE_AGENTS_DIR = ROOT / "agents-claude"
CURSOR_AGENTS_DIR = ROOT / "agents-cursor"
CODEX_AGENTS_DIR = ROOT / "agents-codex"


AGENT_CONFIGS: dict[str, dict[str, object]] = {
    "adk-code-reviewer": {
        "description": (
            "Review code for correctness, regressions, and missing validation. "
            "Use proactively after implementation, before commit, and before merge."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "disallowedTools": ["Write", "Edit"],
            "maxTurns": 20,
            "skills": ["adk-review-local-changes", "adk-review-pr"],
            "effort": "high",
            "background": True,
            "color": "yellow",
        },
        "cursor": {
            "model": "inherit",
            "readonly": True,
            "is_background": True,
        },
        "codex": {
            "model": "gpt-5.4",
            "model_reasoning_effort": "high",
            "sandbox_mode": "read-only",
            "nickname_candidates": ["Atlas", "Delta", "Echo"],
        },
    },
    "adk-security-reviewer": {
        "description": (
            "Audit security-sensitive changes for vulnerabilities, data exposure, "
            "and auth gaps. Use proactively for auth, payments, secrets, and untrusted input."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "disallowedTools": ["Write", "Edit"],
            "maxTurns": 20,
            "skills": ["adk-review-pr", "adk-audit-repo"],
            "effort": "high",
            "background": True,
            "color": "red",
        },
        "cursor": {
            "model": "inherit",
            "readonly": True,
            "is_background": True,
        },
        "codex": {
            "model": "gpt-5.4",
            "model_reasoning_effort": "high",
            "sandbox_mode": "read-only",
            "nickname_candidates": ["Sentinel", "Aegis", "Bastion"],
        },
    },
    "adk-test-engineer": {
        "description": (
            "Run tests, add focused coverage, and report fresh pass or fail evidence. "
            "Use proactively after code changes or before marking work complete."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "maxTurns": 25,
            "skills": ["adk-test", "adk-build"],
            "effort": "medium",
            "background": True,
            "color": "green",
            "memory": "local",
        },
        "cursor": {
            "model": "fast",
            "readonly": False,
            "is_background": True,
        },
        "codex": {
            "model": "gpt-5.4-mini",
            "model_reasoning_effort": "medium",
            "sandbox_mode": "workspace-write",
            "nickname_candidates": ["Verifier", "Probe", "Check"],
        },
    },
    "adk-doc-writer": {
        "description": (
            "Write or review technical documentation from code evidence. "
            "Use when changes require docs, release notes, onboarding updates, or architecture notes."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "maxTurns": 20,
            "skills": ["adk-write-docs", "adk-review-docs"],
            "effort": "medium",
            "background": True,
            "color": "blue",
            "memory": "local",
        },
        "cursor": {
            "model": "fast",
            "readonly": False,
            "is_background": True,
        },
        "codex": {
            "model": "gpt-5.4-mini",
            "model_reasoning_effort": "medium",
            "sandbox_mode": "workspace-write",
            "nickname_candidates": ["Quill", "Scribe", "Gloss"],
        },
    },
    "adk-research-agent": {
        "description": (
            "Research framework behavior and upstream docs with clear verified versus inferred findings. "
            "Use when external behavior or version-specific guidance matters."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "disallowedTools": ["Write", "Edit"],
            "maxTurns": 25,
            "skills": ["adk-research", "adk-plan"],
            "effort": "high",
            "background": True,
            "color": "purple",
        },
        "cursor": {
            "model": "inherit",
            "readonly": True,
            "is_background": True,
        },
        "codex": {
            "model": "gpt-5.4",
            "model_reasoning_effort": "high",
            "sandbox_mode": "read-only",
            "nickname_candidates": ["Scout", "Beacon", "Index"],
        },
    },
    "adk-brainstorm-facilitator": {
        "description": (
            "Drive iterative brainstorming to narrow options, question assumptions, "
            "and route work into the right spec, plan, docs, or implementation path."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "maxTurns": 20,
            "skills": ["adk-brainstorm", "adk-plan", "adk-spec"],
            "effort": "high",
            "background": False,
            "color": "teal",
            "memory": "local",
        },
        "cursor": {
            "model": "inherit",
            "readonly": False,
            "is_background": False,
        },
        "codex": {
            "model": "gpt-5.4",
            "model_reasoning_effort": "high",
            "sandbox_mode": "workspace-write",
            "nickname_candidates": ["Northstar", "Mapper", "Triage"],
        },
    },
    "adk-plan-reviewer": {
        "description": (
            "Critique implementation plans for completeness, risk, and validation gaps. "
            "Use after a plan is drafted and before execution begins."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "disallowedTools": ["Write", "Edit"],
            "maxTurns": 15,
            "skills": ["adk-plan"],
            "effort": "high",
            "background": False,
            "color": "orange",
        },
        "cursor": {
            "model": "inherit",
            "readonly": True,
            "is_background": False,
        },
        "codex": {
            "model": "gpt-5.4",
            "model_reasoning_effort": "high",
            "sandbox_mode": "read-only",
            "nickname_candidates": ["Compass", "Ledger", "Scope"],
        },
    },
    "adk-implementer": {
        "description": (
            "Implement the smallest correct change from an approved plan. "
            "Use for multi-file changes, targeted fixes, and parallel implementation work."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "maxTurns": 30,
            "skills": ["adk-build", "adk-refactor", "adk-migrate"],
            "effort": "medium",
            "background": False,
            "isolation": "worktree",
            "color": "cyan",
            "memory": "local",
        },
        "cursor": {
            "model": "inherit",
            "readonly": False,
            "is_background": False,
        },
        "codex": {
            "model": "gpt-5.3-codex-spark",
            "model_reasoning_effort": "medium",
            "sandbox_mode": "workspace-write",
            "nickname_candidates": ["Builder", "Patch", "Forge"],
        },
    },
    "adk-debugger": {
        "description": (
            "Investigate failures systematically, isolate root cause, and verify fixes. "
            "Use for failing tests, runtime errors, and flaky behavior."
        ),
        "claude": {
            "model": "claude-sonnet-4-6",
            "maxTurns": 30,
            "skills": ["adk-build", "adk-test"],
            "effort": "high",
            "background": False,
            "isolation": "worktree",
            "color": "pink",
            "memory": "local",
        },
        "cursor": {
            "model": "inherit",
            "readonly": False,
            "is_background": False,
        },
        "codex": {
            "model": "gpt-5.4",
            "model_reasoning_effort": "high",
            "sandbox_mode": "workspace-write",
            "nickname_candidates": ["Trace", "Breakpoint", "Rootcause"],
        },
    },
}


RUNTIME_DIRS = {
    "claude": CLAUDE_AGENTS_DIR,
    "cursor": CURSOR_AGENTS_DIR,
    "codex": CODEX_AGENTS_DIR,
}


def discover_canonical_agents() -> list[str]:
    return sorted(
        directory.name
        for directory in CANONICAL_AGENTS_DIR.iterdir()
        if directory.is_dir() and (directory / "AGENT.md").exists()
    )


def quote_yaml_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def render_yaml_scalar(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return quote_yaml_string(value)
    raise TypeError(f"Unsupported YAML scalar type: {type(value).__name__}")


def render_yaml_frontmatter(items: list[tuple[str, object]]) -> str:
    lines = ["---"]
    for key, value in items:
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {render_yaml_scalar(item)}")
        else:
            lines.append(f"{key}: {render_yaml_scalar(value)}")
    lines.append("---")
    return "\n".join(lines)


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def render_toml_array(values: list[str]) -> str:
    rendered = ", ".join(f'"{toml_escape(value)}"' for value in values)
    return f"[{rendered}]"


def render_toml_string(key: str, value: str) -> str:
    return f'{key} = "{toml_escape(value)}"'


def render_toml_multiline(key: str, value: str) -> str:
    sanitized = value.replace('"""', '\\"\\"\\"').rstrip() + "\n"
    return f'{key} = """\n{sanitized}"""'


def runtime_filename(runtime: str, agent_name: str) -> str:
    suffix = ".toml" if runtime == "codex" else ".md"
    return f"{agent_name}{suffix}"


def render_claude_agent(agent_name: str, config: dict[str, object], body: str) -> str:
    frontmatter = [("name", agent_name), ("description", config["description"])]
    for key in (
        "model",
        "tools",
        "disallowedTools",
        "maxTurns",
        "skills",
        "memory",
        "effort",
        "background",
        "isolation",
        "color",
    ):
        if key in config:
            frontmatter.append((key, config[key]))
    return render_yaml_frontmatter(frontmatter) + "\n\n" + body.rstrip() + "\n"


def render_cursor_agent(agent_name: str, config: dict[str, object], body: str) -> str:
    frontmatter = [("name", agent_name), ("description", config["description"])]
    for key in ("model", "readonly", "is_background"):
        if key in config:
            frontmatter.append((key, config[key]))
    return render_yaml_frontmatter(frontmatter) + "\n\n" + body.rstrip() + "\n"


def render_codex_agent(agent_name: str, config: dict[str, object], body: str) -> str:
    lines = [
        render_toml_string("name", agent_name),
        render_toml_string("description", str(config["description"])),
    ]
    for key in ("model", "model_reasoning_effort", "sandbox_mode"):
        if key in config:
            lines.append(render_toml_string(key, str(config[key])))
    if "nickname_candidates" in config:
        lines.append(f"nickname_candidates = {render_toml_array(list(config['nickname_candidates']))}")
    lines.append(render_toml_multiline("developer_instructions", body))
    return "\n".join(lines) + "\n"


def build_outputs() -> dict[Path, str]:
    canonical_agents = discover_canonical_agents()
    configured_agents = sorted(AGENT_CONFIGS.keys())
    if canonical_agents != configured_agents:
        raise SystemExit(
            "Canonical agents and runtime config drifted.\n"
            f"Canonical: {canonical_agents}\n"
            f"Configured: {configured_agents}"
        )

    outputs: dict[Path, str] = {}
    for agent_name in canonical_agents:
        body = (CANONICAL_AGENTS_DIR / agent_name / "AGENT.md").read_text(encoding="utf-8")
        config = AGENT_CONFIGS[agent_name]
        outputs[CLAUDE_AGENTS_DIR / runtime_filename("claude", agent_name)] = render_claude_agent(
            agent_name, {"description": config["description"], **config["claude"]}, body
        )
        outputs[CURSOR_AGENTS_DIR / runtime_filename("cursor", agent_name)] = render_cursor_agent(
            agent_name, {"description": config["description"], **config["cursor"]}, body
        )
        outputs[CODEX_AGENTS_DIR / runtime_filename("codex", agent_name)] = render_codex_agent(
            agent_name, {"description": config["description"], **config["codex"]}, body
        )
    return outputs


def stale_runtime_files(outputs: dict[Path, str]) -> list[Path]:
    expected_by_dir: dict[Path, set[str]] = {
        runtime_dir: {
            path.name
            for path in outputs
            if path.parent == runtime_dir
        }
        for runtime_dir in RUNTIME_DIRS.values()
    }

    stale: list[Path] = []
    for runtime_dir, expected_names in expected_by_dir.items():
        if not runtime_dir.exists():
            continue
        for path in runtime_dir.glob("adk-*"):
            if path.is_file() and path.name not in expected_names:
                stale.append(path)
    return sorted(stale)


def check_outputs(outputs: dict[Path, str]) -> int:
    failures: list[str] = []

    for path, expected in sorted(outputs.items()):
        if not path.exists():
            failures.append(f"missing: {path.relative_to(ROOT)}")
            continue
        current = path.read_text(encoding="utf-8")
        if current != expected:
            failures.append(f"out of date: {path.relative_to(ROOT)}")

    for stale in stale_runtime_files(outputs):
        failures.append(f"stale: {stale.relative_to(ROOT)}")

    if failures:
        print("✗ Agent projections are out of date:")
        for failure in failures:
            print(f"  - {failure}")
        print("Regenerate with: python3 scripts/generate_agent_projections.py")
        return 1

    print(f"✓ Agent projections are up to date ({len(outputs)} files)")
    return 0


def write_outputs(outputs: dict[Path, str]) -> int:
    for runtime_dir in RUNTIME_DIRS.values():
        runtime_dir.mkdir(parents=True, exist_ok=True)

    for stale in stale_runtime_files(outputs):
        stale.unlink()

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    print(f"✓ Generated {len(outputs)} runtime agent files")
    return 0


def main() -> int:
    outputs = build_outputs()
    if "--check" in sys.argv:
        return check_outputs(outputs)
    return write_outputs(outputs)


if __name__ == "__main__":
    raise SystemExit(main())
