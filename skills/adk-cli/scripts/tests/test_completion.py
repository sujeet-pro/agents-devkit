"""Smoke tests for completion.py — make sure each shell variant emits a
non-empty script that at least mentions every top-level subcommand.
"""
from __future__ import annotations

import pytest

from completion import emit_bash, emit_zsh, emit_fish, SUBCMDS


@pytest.mark.parametrize("shell,emit", [
    ("bash", emit_bash),
    ("zsh", emit_zsh),
    ("fish", emit_fish),
])
def test_emits_every_top_level_subcommand(shell, emit):
    out = emit()
    assert out.strip()
    for cmd in SUBCMDS:
        assert cmd in out, f"{shell} completion missing {cmd}"


def test_bash_completion_function_present():
    assert "_adk_complete" in emit_bash()
    assert "complete -F _adk_complete adk" in emit_bash()


def test_zsh_has_compdef():
    out = emit_zsh()
    assert "#compdef adk" in out
    assert "_adk" in out


def test_fish_uses_native_completion():
    out = emit_fish()
    assert "complete -c adk" in out
    assert "__fish_use_subcommand" in out


def test_nested_subcommands_present_in_each_shell():
    # pr-queue has the most nested subcommands; verify each appears in each shell.
    expected = SUBCMDS["pr-queue"]
    for emit in (emit_bash, emit_zsh, emit_fish):
        out = emit()
        for sub in expected:
            assert sub in out


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
