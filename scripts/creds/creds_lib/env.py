"""Best-effort loader for ~/.zshenv into os.environ.

When the toolkit runs inside a normal zsh session the vars are already
exported, so this is a fallback for non-login shells (cron, IDE/GUI
launchers). It only parses simple ``export KEY=VALUE`` lines, expands
``$VAR`` / ``~``, skips command substitutions, and never overwrites a var
that is already set in the environment.
"""

from __future__ import annotations

import os
from pathlib import Path

from .zshenv_io import _LINE_RE, _dequote, zshenv_path


def load_zshenv(path: Path | None = None) -> dict[str, str]:
    """Merge ~/.zshenv exports into os.environ; return the vars newly set."""
    p = path or zshenv_path()
    if not p.exists():
        return {}

    added: dict[str, str] = {}
    for raw in p.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        m = _LINE_RE.match(raw)
        if not m:
            continue
        key, rawval = m.group("key"), m.group("val")
        if "$(" in rawval or "`" in rawval:
            continue  # skip dynamic values we can't safely evaluate

        single_quoted = rawval.strip().startswith("'")
        value = _dequote(rawval)
        if not single_quoted:
            value = os.path.expandvars(os.path.expanduser(value))

        if key not in os.environ:
            os.environ[key] = value
            added[key] = value
    return added
