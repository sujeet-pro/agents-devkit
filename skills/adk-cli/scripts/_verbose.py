"""_verbose.py — v4 §6.x cross-cutting verbose-mode helper.

Every CLI verb's main() can call `setup_verbose(verb_name, enabled=args.verbose)`
to wire structured DEBUG logging into a plain-text file at
`~/.agents-devkit/logs/<verb>-<utc-ts>-<pid>.log`. Off by default; stderr
keeps the human-friendly INFO output.

Off (default):
  - root logger at INFO.
  - stderr handler with the existing "ts level [name] msg" formatter.
  - No log file.

On (`--verbose` / `-v`):
  - root logger at DEBUG.
  - stderr handler unchanged (human-friendly).
  - File handler at DEBUG, human-readable `[ts] LEVEL [name] msg`, with
    multi-line message bodies indented under the header. Secret-scrubbed
    per constitution §VII.
  - Noisy 3rd-party loggers (urllib3, slack_sdk, requests, httpx, …)
    pinned to WARNING so they don't drown the app-level output.
  - First record: a manifest with verb, argv (scrubbed), pid, started_at.
"""
from __future__ import annotations

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

# 3rd-party loggers that emit one DEBUG line per HTTP header/body chunk.
# Pin these to WARNING in verbose mode so the file stays scannable. App
# loggers ("pr-sync", "pr-task-*", "orchestrator", …) inherit DEBUG from
# the root.
_NOISY_LOGGERS = (
    "urllib3",
    "urllib3.connectionpool",
    "urllib3.util.retry",
    "requests",
    "requests.packages.urllib3",
    "httpx",
    "httpcore",
    "slack_sdk",
    "slack_sdk.web",
    "slack_sdk.web.base_client",
    "slack_sdk.web.slack_response",
    "asyncio",
    "charset_normalizer",
    "filelock",
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


class _HumanFormatter(logging.Formatter):
    """One log record → one or more readable lines.

    Single-line message:
        2026-05-22T09:48:04Z INFO  [pr-sync] === step: auto-base cleanup ===

    Multi-line message body — header on first line, body indented two spaces:
        2026-05-22T09:48:04Z INFO  [orchestrator] stderr:
          Traceback (most recent call last):
            File "create_worktree.py", line 72, in fetch_sha
              raise RuntimeError(...)
    """

    _LEVEL_WIDTH = 5  # "INFO ", "WARN ", "ERROR", "DEBUG"

    def format(self, record: logging.LogRecord) -> str:
        msg = record.getMessage()
        # Light scrub — anything matching <NAME>_TOKEN=value / <NAME>_KEY=value.
        msg = _SECRET_RE.sub(lambda m: m.group(1) + "=<redacted>", msg)
        ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created))
        level = record.levelname.ljust(self._LEVEL_WIDTH)
        head = f"{ts} {level} [{record.name}]"

        # Multi-line bodies: indent every line after the first under the
        # header so a follow-up grep can still pin the header line, but a
        # human can read the structured payload.
        if "\n" in msg:
            first, _, rest = msg.partition("\n")
            indented = "\n".join("  " + ln for ln in rest.splitlines())
            body = f"{head} {first}\n{indented}"
        else:
            body = f"{head} {msg}"

        # Exceptions: append the formatted traceback under the same indent.
        if record.exc_info:
            tb = self.formatException(record.exc_info)
            indented_tb = "\n".join("  " + ln for ln in tb.splitlines())
            body = f"{body}\n{indented_tb}"

        return body


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

    # Pin noisy 3rd-party loggers BEFORE adding our file handler so the
    # flood never reaches the formatter. We also stop them propagating,
    # in case some module installs a NullHandler that masks the level set.
    for name in _NOISY_LOGGERS:
        nlog = logging.getLogger(name)
        nlog.setLevel(logging.WARNING)

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(_HumanFormatter())
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
