"""Tests for install.py helper behavior."""
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


def test_cursor_http_url_defaults_expand_without_touching_secret_headers(monkeypatch):
    install = _load_install_module()
    monkeypatch.delenv("DATADOG_MCP_URL", raising=False)
    cfg = {
        "url": "${DATADOG_MCP_URL:-https://mcp.datadoghq.com/api/unstable/mcp-server/mcp}?toolsets=core",
        "headers": {
            "DD_API_KEY": "${DATADOG_API_KEY_CRED}",
            "DD_APPLICATION_KEY": "${DATADOG_APP_KEY_CRED}",
        },
    }

    translated = install._translate_mcp_entry_generic(cfg)

    assert translated["url"] == "https://mcp.datadoghq.com/api/unstable/mcp-server/mcp?toolsets=core"
    assert translated["headers"] == cfg["headers"]


def test_cursor_http_url_defaults_prefer_environment_override(monkeypatch):
    install = _load_install_module()
    monkeypatch.setenv("DATADOG_MCP_URL", "https://mcp.datadoghq.eu/api/unstable/mcp-server/mcp")
    cfg = {
        "url": "${DATADOG_MCP_URL:-https://mcp.datadoghq.com/api/unstable/mcp-server/mcp}?toolsets=core",
    }

    translated = install._translate_mcp_entry_generic(cfg)

    assert translated["url"] == "https://mcp.datadoghq.eu/api/unstable/mcp-server/mcp?toolsets=core"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
