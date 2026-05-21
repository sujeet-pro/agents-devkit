"""_verbose.py — v4 §6.x cross-cutting verbose-mode helper.

Every CLI verb's main() can call `setup_verbose(verb_name, enabled=args.verbose)`
to wire structured DEBUG logging into a JSON-lines file at
`~/.agents-devkit/logs/<verb>-<utc-ts>-<pid>.log`. Off by default; stderr
keeps the human-friendly INFO output.

Off (default):
  - root logger at INFO.
  - stderr handler with the existing "ts level [name] msg" formatter.
  - No log file.

On (`--verbose` / `-v`):
  - root logger at DEBUG.
  - stderr handler unchanged (human-friendly).
  - File handler at DEBUG, JSON-lines, scrubbed of credential-pattern env-var
    values (constitution §VII).
  - First record: a manifest with verb, argv (scrubbed), pid, started_at.
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import time
from pathlib import Path

ADK_HOME = Path(os.environ.get("ADK_HOME", Path.home() / ".agents-devkit"))
LOGS_DIR = ADK_HOME / "logs"

# Env-var name patterns that signal a secret. We never log the VALUE of any
# var whose name ends in one of these suffixes. Constitution §VII.
SECRET_SUFFIXES = ("_TOKEN", "_KEY", "_SECRET", "_CRED", "_CREDS",
                   "_PASSWORD", "_PAT", "_API_KEY")
_SECRET_RE = re.compile(
    r"(?<=[\s=])([A-Za-z0-9_]+(?:" + "|".join(s[1:] for s in SECRET_SUFFIXES) + r"))"
    r"\s*[:=]\s*\S+",
    re.IGNORECASE,
)


def _is_secret_name(name: str) -> bool:
    n = name.upper()
    return any(n.endswith(suf) for suf in SECRET_SUFFIXES)


def _scrub_argv(argv: list[str]) -> list[str]:
    """Mask values that look like inline secrets in argv.
    Pattern: --foo-token=VALUE or --foo-token VALUE for any flag matching
    the secret-name patterns. Conservative; matches only after =.
    """
    out: list[str] = []
    skip_next = False
    for i, a in enumerate(argv):
        if skip_next:
            out.append("<redacted>")
            skip_next = False
            continue
        if "=" in a and a.startswith("--"):
            name, _, val = a.partition("=")
            stripped = name.lstrip("-").replace("-", "_")
            if _is_secret_name(stripped):
                out.append(f"{name}=<redacted>")
                continue
        if a.startswith("--"):
            stripped = a.lstrip("-").replace("-", "_")
            if _is_secret_name(stripped):
                out.append(a)
                skip_next = True
                continue
        out.append(a)
    return out


class _JsonLinesFormatter(logging.Formatter):
    """One JSON record per log line. Scrubs anything that looks like a
    secret pattern in the message body.
    """

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        # Light scrub — anything matching <NAME>_TOKEN=value / <NAME>_KEY=value.
        msg = _SECRET_RE.sub(lambda m: m.group(1) + "=<redacted>", msg)
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "name": record.name,
            "msg": msg,
        }
        return json.dumps(payload, ensure_ascii=False)


def setup_verbose(verb_name: str, *, enabled: bool, argv: list[str] | None = None) -> Path | None:
    """Wire the verbose file handler if enabled. Idempotent; returns the
    log file path (or None when disabled).
    """
    if not enabled:
        # Nothing to do — caller's existing INFO logging is preserved.
        return None
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    log_path = LOGS_DIR / f"{verb_name}-{ts}-{os.getpid()}.log"

    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_JsonLinesFormatter())
    # Tag the handler so a second call doesn't double-wire.
    if not any(getattr(h, "_adk_verbose", False) for h in root.handlers):
        setattr(fh, "_adk_verbose", True)
        root.addHandler(fh)

    # Manifest record at the top of the file.
    logging.getLogger("adk-verbose").info(
        "verb=%s pid=%d started_at=%s argv=%s",
        verb_name, os.getpid(), ts, _scrub_argv(argv or sys.argv[1:]),
    )
    return log_path
