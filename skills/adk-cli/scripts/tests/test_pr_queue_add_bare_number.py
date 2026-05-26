"""adk pr-queue add 1234 resolves against adk-cli.json5 defaults (P1 exit criterion)."""
import argparse
import json
from pathlib import Path
import sys
from unittest.mock import patch, MagicMock

THIS_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = THIS_DIR.parent
_LIB_DIR = THIS_DIR.parent.parent.parent.parent / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

import pytest


def _write_adk_cli(cfg_dir: Path, platform: str, repo: str) -> None:
    """Write a minimal adk-cli.json5 with defaults.platform + defaults.repo."""
    (cfg_dir / "adk-cli.json5").write_text(
        json.dumps({"defaults": {"platform": platform, "repo": repo}}),
        encoding="utf-8",
    )


def test_bare_number_resolves_via_defaults_repo(tmp_path, monkeypatch):
    """Bare PR number + defaults.repo=acme/foo + defaults.platform=github → constructs https://github.com/acme/foo/pull/1234."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    _write_adk_cli(cfg_dir, "github", "acme/foo")
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()

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
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    _write_adk_cli(cfg_dir, "github", "acme/foo")
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')
    import pr_queue
    with patch.object(pr_queue, "_add_from_pr_url") as mock_add:
        mock_add.return_value = 0
        args = argparse.Namespace(url="#1234", queue=str(queue_path), yes=True)
        pr_queue.cmd_add(args)
        assert mock_add.call_args[0][0] == "https://github.com/acme/foo/pull/1234"


def test_bare_number_without_defaults_repo_errors_cleanly(tmp_path, monkeypatch):
    """Bare number + no defaults in adk-cli.json5 → clear error."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    # No adk-cli.json5 written → get_adk_cli returns None → falls back to
    # get_bundle() which fails (no core.json5) → _load_defaults returns {} → die().
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')
    import pr_queue
    args = argparse.Namespace(url="1234", queue=str(queue_path), yes=True)
    with pytest.raises(SystemExit):
        pr_queue.cmd_add(args)


def test_bare_number_bitbucket_platform(tmp_path, monkeypatch):
    """defaults.platform=bitbucket builds a bitbucket URL."""
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    _write_adk_cli(cfg_dir, "bitbucket", "workspace/repo")
    monkeypatch.setenv("ADK_CONFIG_HOME", str(cfg_dir))
    from config import reset_bundle
    reset_bundle()
    queue_path = tmp_path / "pr-queue.json5"
    queue_path.write_text('{"filters": null, "prs": []}\n')
    import pr_queue
    with patch.object(pr_queue, "_add_from_pr_url") as mock_add:
        mock_add.return_value = 0
        args = argparse.Namespace(url="567", queue=str(queue_path), yes=True)
        pr_queue.cmd_add(args)
        assert "bitbucket.org/workspace/repo/pull-requests/567" in mock_add.call_args[0][0]
