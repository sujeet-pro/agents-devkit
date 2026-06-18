"""Read and rewrite ``export KEY=...`` lines in ~/.zshenv.

``set_value`` is how rotation persists freshly-minted secrets: it replaces
the value of an existing ``export`` line in place (atomic write, original
file mode preserved) and never echoes the secret. It only updates keys that
already exist in the file — it will not append new ones, so the file's shape
stays under your control.
"""

from __future__ import annotations

import os
import re
import shlex
import tempfile
from pathlib import Path

_LINE_RE = re.compile(
    r"^(?P<lead>\s*)export\s+(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<val>.*)$"
)


def zshenv_path() -> Path:
    return Path(os.environ.get("ZSHENV_FILE", os.path.expanduser("~/.zshenv")))


def _dequote(value: str) -> str:
    value = value.strip()
    # Drop a trailing inline comment only when the value is unquoted.
    if value and value[0] not in "\"'":
        value = value.split(" #", 1)[0].rstrip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def get_value(key: str, path: Path | None = None) -> str | None:
    """Return the (de-quoted) value of an ``export KEY=`` line, or None."""
    p = path or zshenv_path()
    if not p.exists():
        return None
    for raw in p.read_text(encoding="utf-8").splitlines():
        m = _LINE_RE.match(raw)
        if m and m.group("key") == key:
            return _dequote(m.group("val"))
    return None


def set_value(key: str, value: str, path: Path | None = None) -> bool:
    """Replace the value of an existing ``export KEY=`` line.

    Returns True if the key was found and updated, False otherwise. The
    write is atomic and preserves the file's permission bits. The new value
    is shell-quoted; the secret is never printed.
    """
    p = path or zshenv_path()
    if not p.exists():
        return False

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    quoted = shlex.quote(value)
    found = False
    for i, line in enumerate(lines):
        m = _LINE_RE.match(line.rstrip("\n"))
        if m and m.group("key") == key:
            nl = "\n" if line.endswith("\n") else ""
            lines[i] = f"{m.group('lead')}export {key}={quoted}{nl}"
            found = True
            break
    if not found:
        return False

    mode = p.stat().st_mode & 0o777
    fd, tmp = tempfile.mkstemp(dir=str(p.parent), prefix=".zshenv.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("".join(lines))
        os.chmod(tmp, mode)
        os.replace(tmp, p)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return True
