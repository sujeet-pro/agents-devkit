"""Tests for repo._repo_name_from_url — the URL → repo-name derivation that
shows up everywhere downstream (clone path, index task dir).
"""
from __future__ import annotations

import pytest

from repo import _repo_name_from_url


@pytest.mark.parametrize("url,expected", [
    ("https://github.com/acme/foo.git", "foo"),
    ("https://github.com/acme/foo", "foo"),
    ("https://github.com/acme/foo/", "foo"),
    ("git@github.com:acme/foo.git", "foo"),
    ("git@github.com:acme/foo", "foo"),
    ("https://bitbucket.org/team/my-repo.git", "my-repo"),
    ("/home/user/repos/myproject", "myproject"),
    ("ssh://git@gitea.example.com/acme/zoo.git", "zoo"),
])
def test_repo_name_derivation(url, expected):
    assert _repo_name_from_url(url) == expected


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
