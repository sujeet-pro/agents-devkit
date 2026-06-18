"""Result type, env-var presence check, and the terminal renderer."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Iterable

# ── result states ────────────────────────────────────────────────────────────
OK = "OK"                       # probed the live API, credential works
FAIL = "FAIL"                   # credential present but rejected / endpoint error
MISCONFIGURED = "MISCONFIGURED"  # required env vars unset or still placeholders
LOGIN = "LOGIN"                 # needs an interactive login the script can't do
SKIPPED = "SKIPPED"             # not applicable

# Values that count as "not really set" — see required_env().
_PLACEHOLDERS = ("", "ADD_VALUE")


def _is_placeholder(value: str) -> bool:
    v = value.strip()
    return (
        v in _PLACEHOLDERS
        or v.upper().startswith("PLACEHOLDER")
        or (v.startswith("<") and v.endswith(">"))
    )


@dataclass
class Result:
    connector: str
    state: str
    message: str = ""
    sample: str = ""              # e.g. a sample resource name proving access
    missing: list[str] = field(default_factory=list)


def required_env(*names: str) -> tuple[dict[str, str], list[str]]:
    """Split env var names into (present, missing).

    A var is "missing" when it is unset, empty, or still a placeholder
    (``ADD_VALUE``, ``PLACEHOLDER...``, ``<...>``).
    """
    present: dict[str, str] = {}
    missing: list[str] = []
    for name in names:
        value = os.environ.get(name)
        if value and not _is_placeholder(value):
            present[name] = value
        else:
            missing.append(name)
    return present, missing


# ── rendering ────────────────────────────────────────────────────────────────
_COLORS = {
    OK: "\033[32m",            # green
    FAIL: "\033[31m",          # red
    MISCONFIGURED: "\033[33m",  # yellow
    LOGIN: "\033[36m",         # cyan
    SKIPPED: "\033[90m",       # grey
}
_RESET = "\033[0m"
_ICON = {OK: "✓", FAIL: "✗", MISCONFIGURED: "•", LOGIN: "→", SKIPPED: "–"}


def _color(state: str, text: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{_COLORS.get(state, '')}{text}{_RESET}"


def render(results: Iterable[Result]) -> int:
    """Print a table of results and return a process exit code.

    Exit codes: 1 if any FAIL, else 2 if any MISCONFIGURED, else 0
    (OK / LOGIN / SKIPPED are all non-fatal).
    """
    results = list(results)
    if not results:
        print("no connectors to report")
        return 0

    width = max(len(r.connector) for r in results)
    has_fail = has_misconfig = False
    for r in results:
        if r.state == FAIL:
            has_fail = True
        elif r.state == MISCONFIGURED:
            has_misconfig = True

        icon = _ICON.get(r.state, "?")
        head = f"  {icon} {r.connector.ljust(width)}  {r.state.ljust(13)}"
        detail = r.message
        if r.missing:
            detail = f"{detail} (set: {', '.join(r.missing)})".strip()
        if r.sample:
            detail = f"{detail}  ⟨{r.sample}⟩"
        print(_color(r.state, head) + " " + detail)

    if has_fail:
        return 1
    if has_misconfig:
        return 2
    return 0
