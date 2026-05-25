"""Tests for install.py shell-completion wiring helpers."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[4]
INSTALL_PY = ROOT / "install.py"


def _load_install_module():
    spec = importlib.util.spec_from_file_location("adk_install_for_tests", INSTALL_PY)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_zsh_completion_block_inserts_before_compinit():
    install = _load_install_module()
    original = "export PATH=\"$HOME/bin:$PATH\"\nautoload -Uz compinit\ncompinit\n"

    updated, line_no, status = install._zsh_completion_insert(original)

    assert status == "inserted-before-compinit"
    assert line_no == 2
    assert install.ADK_ZSH_COMPLETION_START in updated
    assert updated.index(install.ADK_ZSH_COMPLETION_START) < updated.index("compinit")


def test_zsh_completion_block_is_idempotent():
    install = _load_install_module()
    original = install.ADK_ZSH_COMPLETION_BLOCK + "\nautoload -Uz compinit\ncompinit\n"

    updated, line_no, status = install._zsh_completion_insert(original)

    assert updated == original
    assert line_no is None
    assert status == "present"


def test_zsh_completion_diff_redacts_existing_shell_content():
    install = _load_install_module()
    diff = install._zsh_completion_diff(Path("/Users/example/.zshrc"), 7, "inserted")

    assert "context redacted" in diff
    assert install.ADK_ZSH_COMPLETION_START in diff
    assert "export SECRET" not in diff


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
