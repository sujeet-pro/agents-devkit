"""Repo URL normalisation: user can paste https or ssh; clone goes via ssh."""
from __future__ import annotations

from pathlib import Path
import sys

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR.parent))

import repo


def test_https_github_to_ssh():
    assert repo._normalize_to_ssh("https://github.com/owner/repo") == "git@github.com:owner/repo.git"
    assert repo._normalize_to_ssh("https://github.com/owner/repo.git") == "git@github.com:owner/repo.git"
    assert repo._normalize_to_ssh("https://github.com/owner/repo/") == "git@github.com:owner/repo.git"


def test_https_bitbucket_to_ssh():
    assert (repo._normalize_to_ssh("https://bitbucket.org/ws/repo")
            == "git@bitbucket.org:ws/repo.git")
    assert (repo._normalize_to_ssh("https://bitbucket.org/ws/repo.git")
            == "git@bitbucket.org:ws/repo.git")


def test_https_gitlab_to_ssh():
    assert (repo._normalize_to_ssh("https://gitlab.com/group/sub/repo")
            == "git@gitlab.com:group/sub/repo.git")


def test_ssh_scp_form_passthrough_with_dot_git():
    """git@host:owner/repo.git → unchanged."""
    assert (repo._normalize_to_ssh("git@github.com:owner/repo.git")
            == "git@github.com:owner/repo.git")


def test_ssh_scp_form_adds_dot_git():
    """git@host:owner/repo (no .git) → adds .git."""
    assert (repo._normalize_to_ssh("git@github.com:owner/repo")
            == "git@github.com:owner/repo.git")


def test_ssh_protocol_form_to_scp():
    """ssh://git@host/owner/repo.git → git@host:owner/repo.git"""
    assert (repo._normalize_to_ssh("ssh://git@github.com/owner/repo.git")
            == "git@github.com:owner/repo.git")
    assert (repo._normalize_to_ssh("ssh://git@github.com/owner/repo")
            == "git@github.com:owner/repo.git")


def test_https_with_embedded_credentials_stripped():
    """https://user:token@host/owner/repo → strips creds in the ssh form."""
    out = repo._normalize_to_ssh("https://user:abc123@github.com/owner/repo.git")
    assert out == "git@github.com:owner/repo.git"
    assert "abc123" not in out
    assert "user:" not in out


def test_local_path_unchanged():
    """Local paths and file:// URLs are not rewritten."""
    assert repo._normalize_to_ssh("/Users/me/code/repo") == "/Users/me/code/repo"
    assert repo._normalize_to_ssh("file:///tmp/repo") == "file:///tmp/repo"
    assert repo._normalize_to_ssh("./local-repo") == "./local-repo"


def test_unknown_shape_passthrough():
    """An unrecognised URL shape passes through unchanged (caller decides)."""
    weird = "smb://share/repo"
    assert repo._normalize_to_ssh(weird) == weird


def test_self_hosted_https_to_ssh():
    """Self-hosted (e.g. corporate GHE) https rewrites to ssh on the same host."""
    assert (repo._normalize_to_ssh("https://github.acme.internal/team/repo")
            == "git@github.acme.internal:team/repo.git")


def test_repo_name_from_url_handles_all_forms():
    """_repo_name_from_url returns the bare repo name across input forms."""
    assert repo._repo_name_from_url("https://github.com/acme/foo") == "foo"
    assert repo._repo_name_from_url("https://github.com/acme/foo.git") == "foo"
    assert repo._repo_name_from_url("git@github.com:acme/foo.git") == "foo"
    assert repo._repo_name_from_url("git@github.com:acme/foo") == "foo"
    assert repo._repo_name_from_url("ssh://git@github.com/acme/foo.git") == "foo"
