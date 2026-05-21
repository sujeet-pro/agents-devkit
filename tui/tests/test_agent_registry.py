"""Unit tests for `tui/agent_registry.py` — κ §8.1.

Pure functions over the in-memory registry. No subprocess, no Pilot.
"""
from __future__ import annotations

from tui.agent_registry import (
    AgentSpec,
    DEFAULT_AGENTS,
    default_agent,
    get_agent,
    list_agents,
)


def test_list_agents_returns_at_least_five_specs() -> None:
    specs = list_agents()
    assert len(specs) >= 5, f"expected >=5 specs, got {len(specs)}"
    names = {s.name for s in specs}
    expected = {"claude", "codex", "cursor", "opencode", "headless"}
    missing = expected - names
    assert not missing, f"missing expected agents: {missing}"


def test_get_agent_claude_returns_spec() -> None:
    spec = get_agent("claude")
    assert spec is not None
    assert isinstance(spec, AgentSpec)
    assert spec.name == "claude"
    assert spec.bin == "claude"


def test_get_agent_is_case_insensitive() -> None:
    upper = get_agent("CLAUDE")
    mixed = get_agent("ClAuDe")
    assert upper is not None and upper.name == "claude"
    assert mixed is not None and mixed.name == "claude"
    # Surrounding whitespace also tolerated per impl.
    spaced = get_agent("  codex  ")
    assert spaced is not None and spaced.name == "codex"


def test_get_agent_unknown_returns_none() -> None:
    assert get_agent("ghost") is None
    assert get_agent("not-a-real-agent") is None


def test_get_agent_empty_and_none_return_none() -> None:
    assert get_agent("") is None
    assert get_agent(None) is None  # type: ignore[arg-type]
    assert get_agent("   ") is None


def test_default_agent_is_claude() -> None:
    spec = default_agent()
    assert spec.name == "claude"
    assert spec.bin == "claude"


def test_every_spec_has_non_empty_bin() -> None:
    for spec in list_agents():
        assert isinstance(spec.bin, str), f"{spec.name}: bin is not a str"
        assert spec.bin, f"{spec.name}: bin is empty"
        assert isinstance(spec.name, str) and spec.name, f"name empty for {spec}"
        assert isinstance(spec.description, str) and spec.description, (
            f"description empty for {spec.name}"
        )


def test_headless_spec_has_sentinel_bin() -> None:
    spec = get_agent("headless")
    assert spec is not None
    assert spec.bin == "__headless__"
    # And it shows up in DEFAULT_AGENTS too (not just via get_agent).
    assert any(s.name == "headless" and s.bin == "__headless__"
               for s in DEFAULT_AGENTS)
