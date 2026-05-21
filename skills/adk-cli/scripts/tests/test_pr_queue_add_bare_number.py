"""adk pr-queue add 1234 resolves against core.yaml defaults.repo (P1 exit criterion)."""
import argparse
import json
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest


def test_bare_number_resolves_via_defaults_repo(tmp_path, monkeypatch):
    """Bare PR number + defaults.repo=acme/foo + defaults.platform=github → constructs https://github.com/acme/foo/pull/1234."""
    fake_core = tmp_path / "core.yaml"
    fake_core.write_text(
        "schema_version: 4\n"
        "defaults:\n"
        "  platform: github\n"
        "  repo: acme/foo\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("HOME", str(tmp_path))
    (tmp_path / ".agents-devkit" / "config").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".agents-devkit" / "config" / "core.yaml").write_text(fake_core.read_text(), encoding="utf-8")

    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')

    # Mock the cheap_pr_meta call so the test doesn't hit gh.
    import pr_queue
    with patch.object(pr_queue, "_add_from_pr_url") as mock_add:
        mock_add.return_value = 0
        args = argparse.Namespace(url="1234", queue=str(queue_path), yes=True)
        pr_queue.cmd_add(args)
        # Was called with the constructed URL.
        called_url = mock_add.call_args[0][0]
        assert called_url == "https://github.com/acme/foo/pull/1234", f"got: {called_url}"


def test_bare_number_with_hash_prefix(tmp_path, monkeypatch):
    """#1234 (with leading hash) also resolves."""
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = tmp_path / ".agents-devkit" / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "core.yaml").write_text(
        "defaults:\n  platform: github\n  repo: acme/foo\n", encoding="utf-8"
    )
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')
    import pr_queue
    with patch.object(pr_queue, "_add_from_pr_url") as mock_add:
        mock_add.return_value = 0
        args = argparse.Namespace(url="#1234", queue=str(queue_path), yes=True)
        pr_queue.cmd_add(args)
        assert mock_add.call_args[0][0] == "https://github.com/acme/foo/pull/1234"


def test_bare_number_without_defaults_repo_errors_cleanly(tmp_path, monkeypatch):
    """Bare number + no defaults.repo → clear error mentioning core.yaml."""
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = tmp_path / ".agents-devkit" / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "core.yaml").write_text("schema_version: 4\n", encoding="utf-8")
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')
    import pr_queue
    args = argparse.Namespace(url="1234", queue=str(queue_path), yes=True)
    with pytest.raises(SystemExit):
        pr_queue.cmd_add(args)


def test_bare_number_bitbucket_platform(tmp_path, monkeypatch):
    """defaults.platform=bitbucket builds a bitbucket URL."""
    monkeypatch.setenv("HOME", str(tmp_path))
    cfg = tmp_path / ".agents-devkit" / "config"
    cfg.mkdir(parents=True, exist_ok=True)
    (cfg / "core.yaml").write_text(
        "defaults:\n  platform: bitbucket\n  repo: workspace/repo\n", encoding="utf-8"
    )
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')
    import pr_queue
    with patch.object(pr_queue, "_add_from_pr_url") as mock_add:
        mock_add.return_value = 0
        args = argparse.Namespace(url="567", queue=str(queue_path), yes=True)
        pr_queue.cmd_add(args)
        assert "bitbucket.org/workspace/repo/pull-requests/567" in mock_add.call_args[0][0]
