from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentSpec:
    """One row in the agent registry. Knows how to invoke a slash command
    against this agent's binary."""
    name: str            # registry key, lower-case (e.g. "claude")
    bin: str             # binary name on PATH (e.g. "claude") or absolute path
    description: str     # one-line human label for the picker


# The default registry. Ordered as it appears in the picker.
DEFAULT_AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec(
        name="claude",
        bin="claude",
        description="Anthropic Claude (recommended for /adk-pr-review)",
    ),
    AgentSpec(
        name="codex",
        bin="codex",
        description="OpenAI Codex CLI",
    ),
    AgentSpec(
        name="cursor",
        bin="cursor-agent",
        description="Cursor agent CLI",
    ),
    AgentSpec(
        name="opencode",
        bin="opencode",
        description="OpenCode CLI",
    ),
    AgentSpec(
        name="headless",
        bin="__headless__",
        description="No-op stub (for testing the worker without an agent)",
    ),
)


def list_agents() -> tuple[AgentSpec, ...]:
    return DEFAULT_AGENTS


def get_agent(name: str | None) -> AgentSpec | None:
    """Look up an agent by name (case-insensitive). Returns None if not found."""
    needle = (name or "").strip().lower()
    if not needle:
        return None
    for spec in DEFAULT_AGENTS:
        if spec.name == needle:
            return spec
    return None


def default_agent() -> AgentSpec:
    """The agent used when no `--agent` is passed. Always `claude` today."""
    return DEFAULT_AGENTS[0]
