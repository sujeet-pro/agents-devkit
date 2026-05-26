"""Identity cache for TUI authorship attribution.

The TUI marks comments as `OURS` vs `them` when rendering the unified Comments
view. To do that it needs to know who the current user is on each forge host.

Identities are cheap to obtain (`gh api user --jq .login`) but slow enough to
warrant caching to disk. The cache lives at
``$ADK_CONFIG_HOME/identity.json``::

    {
      "github": "sujeet-jaiswal",
      "bitbucket": "{abc123-uuid}",
      "fetched_at": "2026-05-26T14:00Z"
    }

Constitution §VII compliance: login names are not credentials, but the
**verification** command must not surface the token. We use ``gh api ... --jq``
which only prints the requested field; verbose output goes to ``/dev/null``.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

_ADK_REPO_LIB = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_ADK_REPO_LIB) not in sys.path:
    sys.path.insert(0, str(_ADK_REPO_LIB))
from config import load_identity_cache, save_identity_cache  # noqa: E402


def _load_cache() -> dict:
    return load_identity_cache()


def _save_cache(data: dict) -> None:
    save_identity_cache(data)


def _fetch_gh_login() -> str | None:
    """Run `gh api user --jq .login` with stderr suppressed.

    Constitution §VII.3: we exercise the credential implicitly (gh reads
    GITHUB_TOKEN from env) and only let the login field through stdout.
    """
    if os.environ.get("ADK_TUI_SKIP_IDENTITY"):
        return None
    try:
        result = subprocess.run(
            ["gh", "api", "user", "--jq", ".login"],
            capture_output=True,
            text=True,
            timeout=4,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    login = (result.stdout or "").strip()
    return login or None


def get_github_login(*, force: bool = False) -> str | None:
    """Return the current user's github login (cached on disk).

    ``force=True`` bypasses the cache and re-queries. Returns None if gh is
    unavailable, unauthenticated, or returns no login.
    """
    cache = _load_cache()
    if not force:
        cached = cache.get("github")
        if cached:
            return str(cached)

    login = _fetch_gh_login()
    if login is None:
        return None
    cache["github"] = login
    cache["fetched_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    _save_cache(cache)
    return login


def is_ours(author_login: str | None) -> bool:
    """Return True iff ``author_login`` matches the cached github login."""
    if not author_login:
        return False
    me = get_github_login()
    if not me:
        return False
    return author_login.strip().lower() == me.strip().lower()
