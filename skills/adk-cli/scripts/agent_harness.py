"""Shared helpers for spawning ADK skills in external agent harnesses."""
from __future__ import annotations

import os
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
REPO_ROOT = THIS_DIR.parent.parent.parent

# These are the CLI-facing model identifiers for each harness.
RUNNER_MODEL_DEFAULTS = {
    "claude": {
        "standard": "sonnet",
        "deep": "opus",
        "planning": "sonnet",
    },
    "cursor": {
        "standard": "composer-2.5-fast",
        "deep": "gpt-5.5-extra-high",
        "planning": "gpt-5.5-extra-high",
    },
    "codex": {
        "standard": None,
        "deep": "gpt-5.5-extra-high",
        "planning": "gpt-5.5-extra-high",
    },
    "custom": {
        "standard": None,
        "deep": None,
        "planning": None,
    },
}


def resolve_runner_model(
    *,
    runner: str,
    explicit_model: str | None = None,
    deep: bool = False,
    planning: bool = False,
) -> str | None:
    """Return the model to pass to a harness CLI for the requested depth."""
    if explicit_model and explicit_model != "inherit":
        return explicit_model
    if explicit_model == "inherit":
        return None
    profile = RUNNER_MODEL_DEFAULTS.get(runner, RUNNER_MODEL_DEFAULTS["custom"])
    if deep:
        return profile.get("deep")
    if planning:
        return profile.get("planning") or profile.get("deep")
    return profile.get("standard")


def build_agent_cmd(
    prompt: str,
    *,
    runner: str,
    agent: str | None = None,
    model: str | None = None,
    workspace: Path | None = None,
) -> list[str]:
    """Build a CLI command for one skill prompt in the selected harness."""
    workspace = workspace or REPO_ROOT
    if runner == "claude":
        binary = agent or "claude"
        cmd = [binary, "-p", prompt]
        if model:
            cmd += ["--model", model]
        return cmd
    if runner == "cursor":
        binary = agent or "cursor"
        cmd = [
            binary, "agent",
            "--print",
            "--output-format", "text",
            "--force",
            "--trust",
            "--approve-mcps",
            "--sandbox", "disabled",
            "--workspace", str(workspace),
        ]
        if model:
            cmd += ["--model", model]
        cmd.append(prompt)
        return cmd
    if runner == "codex":
        binary = agent or "codex"
        cmd = [
            binary, "exec",
            "--dangerously-bypass-approvals-and-sandbox",
            "-C", str(workspace),
        ]
        if model:
            cmd += ["--model", model]
        cmd.append(prompt)
        return cmd
    if runner == "custom":
        if not agent:
            raise ValueError("--runner custom requires --agent <binary>")
        return [agent, "-p", prompt]
    raise ValueError(f"unsupported --runner {runner!r}")


def env_flag(name: str) -> bool:
    """Parse an opt-in environment flag used by shell wrappers/tests."""
    return (os.environ.get(name) or "").strip().lower() in {"1", "true", "yes", "on"}
