#!/usr/bin/env python3
"""
Generate runtime-specific hook projections for Claude, Cursor, and Codex.

Usage:
    python3 scripts/generate_hook_projections.py
    python3 scripts/generate_hook_projections.py --check
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HOOKS_DIR = ROOT / "hooks"

CLAUDE_HOOKS_PATH = HOOKS_DIR / "settings.json"
CURSOR_HOOKS_PATH = HOOKS_DIR / "hooks-cursor" / "hooks.json"
CODEX_HOOKS_PATH = HOOKS_DIR / "hooks-codex" / "hooks.json"


SESSION_START_MESSAGE = (
    "ADK repo loaded. Read AGENTS.md and ai-guidelines/ before repo-maintenance "
    "work. Public skills live in skills/adk-*."
)

SHELL_SAFETY_PROMPT = (
    "Check if the bash command involves any of these dangerous git operations: "
    "'git push --force' or 'git push -f' to main/master, 'git reset --hard' on "
    "main/master, 'git clean -fd' at repo root, or 'git branch -D main' / "
    "'git branch -D master'. Also block 'rm -rf /' or any recursive delete of "
    "the project root. Return {\"decision\": \"block\", \"reason\": \"...\"} "
    "to block, or {\"decision\": \"allow\"} to allow. Only block genuinely "
    "dangerous commands, not normal git operations."
)

SKILL_FRONTMATTER_PROMPT = (
    "Check if the edited file is a SKILL.md. If it is under skills/adk-*, verify "
    "the frontmatter has: name (starts with 'adk-'), description, compatibility, "
    "and maturity (experimental, stable, battle-tested). If it is under "
    ".claude/skills, .cursor/skills, or .agents/skills, require name to start "
    "with 'prj-' and require metadata.internal: true. Return {\"ok\": true} if "
    "valid or not a SKILL.md, {\"ok\": false, \"reason\": \"...\"} if invalid."
)

STOP_VALIDATION_PROMPT = (
    "Check if the user's original request has been fully addressed. If the agent "
    "was following an adk skill workflow, verify the final validation phase was "
    "completed. Return {\"ok\": true} if done, {\"ok\": false, \"reason\": "
    "\"what remains\"} if not."
)


def stable_json(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def build_claude_hooks() -> dict[str, object]:
    return {
        "hooks": {
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "prompt",
                            "prompt": SHELL_SAFETY_PROMPT,
                        }
                    ],
                }
            ],
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [
                        {
                            "type": "prompt",
                            "prompt": SKILL_FRONTMATTER_PROMPT,
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "prompt",
                            "prompt": STOP_VALIDATION_PROMPT,
                        }
                    ],
                }
            ],
            "SessionStart": [
                {
                    "matcher": "compact",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"echo {json.dumps(SESSION_START_MESSAGE)}",
                        }
                    ],
                }
            ],
        }
    }


def build_cursor_hooks() -> dict[str, object]:
    return {
        "version": 1,
        "hooks": {
            "beforeShellExecution": [
                {
                    "type": "prompt",
                    "model": "fast",
                    "timeout": 10,
                    "prompt": (
                        "Check whether the shell command is a dangerous operation such as "
                        "force-pushing to main/master, resetting or cleaning the repo root, "
                        "deleting the project root, or removing the main/master branch. "
                        "Return {\"ok\": false, \"reason\": \"...\"} to block, or "
                        "{\"ok\": true} to allow. Only block genuinely dangerous commands."
                    ),
                }
            ],
            "afterFileEdit": [
                {
                    "type": "prompt",
                    "model": "fast",
                    "timeout": 10,
                    "prompt": (
                        "Check whether the edited file is a SKILL.md with invalid ADK "
                        "frontmatter. Published skills under skills/adk-* must keep an "
                        "adk-* name plus description, compatibility, and maturity. Repo "
                        "maintenance skills under .claude/skills, .cursor/skills, or "
                        ".agents/skills must use a prj-* name and metadata.internal: true. "
                        "Return {\"ok\": true} if valid or irrelevant, or {\"ok\": false, "
                        "\"reason\": \"...\"} if the edit needs correction."
                    ),
                }
            ],
            "stop": [
                {
                    "type": "prompt",
                    "model": "fast",
                    "timeout": 10,
                    "prompt": STOP_VALIDATION_PROMPT,
                }
            ],
            "sessionStart": [
                {
                    "command": f"echo {json.dumps(SESSION_START_MESSAGE)}",
                }
            ],
        },
    }


def build_codex_hooks() -> dict[str, object]:
    pre_tool_command = """python3 - <<'PY'
import json
import sys

payload = json.load(sys.stdin)
command = payload.get("tool_input", {}).get("command", "")
danger_signals = [
    "git push --force origin main",
    "git push --force origin master",
    "git push -f origin main",
    "git push -f origin master",
    "git reset --hard",
    "git clean -fd",
    "git branch -D main",
    "git branch -D master",
    "rm -rf /",
]

should_block = any(signal in command for signal in danger_signals)
if should_block:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "Dangerous shell command blocked by ADK Codex hook."
        }
    }))
else:
    print(json.dumps({"continue": True}))
PY"""

    stop_command = """python3 - <<'PY'
import json
import sys

payload = json.load(sys.stdin)
last = (payload.get("last_assistant_message") or "").lower()
completion_markers = ("done", "complete", "completed", "finished", "fixed", "ready")
validation_markers = ("test", "tests", "validated", "validation", "verify", "verified", "lint", "type-check")

if any(marker in last for marker in completion_markers) and not any(marker in last for marker in validation_markers):
    print(json.dumps({
        "decision": "block",
        "reason": "Before finishing, report validation evidence or explicitly state that validation did not run."
    }))
else:
    print(json.dumps({"continue": True}))
PY"""

    session_start_command = """python3 - <<'PY'
print("ADK repo loaded. Read AGENTS.md and ai-guidelines/ before repo-maintenance work. Public skills live in skills/adk-*.")
PY"""

    return {
        "hooks": {
            "SessionStart": [
                {
                    "matcher": "startup|resume",
                    "hooks": [
                        {
                            "type": "command",
                            "command": session_start_command,
                            "statusMessage": "Loading ADK session guidance",
                        }
                    ],
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "Bash",
                    "hooks": [
                        {
                            "type": "command",
                            "command": pre_tool_command,
                            "statusMessage": "Checking dangerous shell commands",
                        }
                    ],
                }
            ],
            "Stop": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": stop_command,
                            "statusMessage": "Checking completion and validation",
                            "timeout": 30,
                        }
                    ],
                }
            ],
        }
    }


def build_outputs() -> dict[Path, str]:
    return {
        CLAUDE_HOOKS_PATH: stable_json(build_claude_hooks()),
        CURSOR_HOOKS_PATH: stable_json(build_cursor_hooks()),
        CODEX_HOOKS_PATH: stable_json(build_codex_hooks()),
    }


def stale_runtime_files(outputs: dict[Path, str]) -> list[Path]:
    managed = {
        CLAUDE_HOOKS_PATH.parent: {CLAUDE_HOOKS_PATH.name, "README.md"},
        CURSOR_HOOKS_PATH.parent: {CURSOR_HOOKS_PATH.name},
        CODEX_HOOKS_PATH.parent: {CODEX_HOOKS_PATH.name},
    }

    stale: list[Path] = []
    for directory, expected in managed.items():
        if not directory.exists():
            continue
        for path in directory.iterdir():
            if path.is_file() and path.name not in expected:
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
        print("✗ Hook projections are out of date:")
        for failure in failures:
            print(f"  - {failure}")
        print("Regenerate with: python3 scripts/generate_hook_projections.py")
        return 1

    print(f"✓ Hook projections are up to date ({len(outputs)} files)")
    return 0


def write_outputs(outputs: dict[Path, str]) -> int:
    for path in outputs:
        path.parent.mkdir(parents=True, exist_ok=True)

    for stale in stale_runtime_files(outputs):
        stale.unlink()

    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8")

    print(f"✓ Generated {len(outputs)} runtime hook files")
    return 0


def main() -> int:
    outputs = build_outputs()
    if "--check" in sys.argv:
        return check_outputs(outputs)
    return write_outputs(outputs)


if __name__ == "__main__":
    raise SystemExit(main())
