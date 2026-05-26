"""JSON5 I/O helpers — strict load, atomic write."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

import json5


def read_json5(path: Path) -> Any:
    """Read a JSON5 file. Raises FileNotFoundError if missing.

    Returns whatever the file contains (typically a dict).
    """
    text = path.read_text(encoding="utf-8")
    try:
        return json5.loads(text)
    except Exception as e:  # json5 raises various exceptions
        raise ValueError(f"{path}: failed to parse JSON5: {e}") from e


def read_json5_or_none(path: Path) -> Any | None:
    """Read a JSON5 file, returning None if it doesn't exist."""
    if not path.exists():
        return None
    return read_json5(path)


def write_json5(path: Path, data: Any, *, header: str | None = None) -> None:
    """Atomic write of a JSON5 file.

    JSON5 output is just pretty JSON with a leading comment header — the
    json5 library doesn't serialize JSON5 syntax, so we emit valid JSON
    that parses fine under both json5 and json.

    `header` is a multi-line comment block prepended verbatim.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False)
    if header:
        # ensure header is comment-formatted
        text = header.rstrip() + "\n\n" + body + "\n"
    else:
        text = body + "\n"

    # atomic: write to temp file in same dir, fsync, rename
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def comment_header(*lines: str) -> str:
    """Build a `//`-prefixed comment header suitable for JSON5 files."""
    out: list[str] = []
    for line in lines:
        for sub in line.splitlines() or [""]:
            if sub:
                out.append(f"// {sub}")
            else:
                out.append("//")
    return "\n".join(out)


__all__ = ["read_json5", "read_json5_or_none", "write_json5", "comment_header"]
