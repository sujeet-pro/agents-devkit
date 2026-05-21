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


def test_dynamic_repo_name_completion_present():
    """All three shells should hook `adk repo list --names-only` so that
    `adk repo update <TAB>` suggests actual repo names."""
    for emit in (emit_bash, emit_zsh, emit_fish):
        out = emit()
        assert "adk repo list --names-only" in out, \
            f"{emit.__name__} missing dynamic repo-name completion"
        assert "--all" in out, \
            f"{emit.__name__} missing `--all` suggestion alongside repo names"


def test_dynamic_pr_url_completion_present():
    """All three shells should hook `adk pr-queue list --urls-only` so that
    `adk pr-queue {show,update,release} <TAB>` suggests actual PR URLs."""
    for emit in (emit_bash, emit_zsh, emit_fish):
        out = emit()
        assert "adk pr-queue list --urls-only" in out, \
            f"{emit.__name__} missing dynamic pr-queue URL completion"


def test_pr_task_present_in_completion_map():
    """pr-task is a new top-level subcommand. Both its nested verbs and the
    dynamic URL completion (for prepare + info) must show up in each shell."""
    assert "pr-task" in SUBCMDS
    assert set(SUBCMDS["pr-task"]) == {"prepare", "info", "list", "validate", "clean-orphans"}
    for emit in (emit_bash, emit_zsh, emit_fish):
        out = emit()
        assert "pr-task" in out
        for verb in ("prepare", "info", "list", "validate", "clean-orphans"):
            assert verb in out, f"{emit.__name__} missing pr-task {verb}"


def test_pr_sync_present_in_completion_map():
    """pr-sync is the new top-level sync entry point. Every shell should
    include it in the first-level subcommand list."""
    assert "pr-sync" in SUBCMDS
    for emit in (emit_bash, emit_zsh, emit_fish):
        assert "pr-sync" in emit(), f"{emit.__name__} missing pr-sync"


def test_pr_update_dropped_full_flag():
    """`--full` was removed from `pr-queue update` (one-way principle:
    update = metadata, prepare = task folder). It must not appear in any
    pr-queue-update completion suggestion."""
    for emit in (emit_bash, emit_zsh, emit_fish):
        out = emit()
        # The orphan-clean / pr-task-prepare slots may still reference flags,
        # so scope the check to whether `--full` is suggested for pr-queue update.
        # Conservative check: --full shouldn't appear in any shell completion
        # output now that it's no longer a valid flag anywhere.
        assert "--full" not in out, \
            f"{emit.__name__} still suggests --full (should have been removed)"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
