"""adk_log.py — shared human-friendly logging helpers.

The default path is intentionally conservative: agent/non-TTY contexts keep the
plain timestamped format so captured logs stay easy to parse. Interactive TTYs
get a compact modern format with color and status glyphs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Any, Iterable

SECRET_SUFFIXES = ("_TOKEN", "_KEY", "_SECRET", "_CRED", "_CREDS",
                   "_PASSWORD", "_PAT", "_API_KEY")
_SECRET_RE = re.compile(
    r"(?<=[\s=])([A-Za-z0-9_]+(?:" + "|".join(s[1:] for s in SECRET_SUFFIXES) + r"))"
    r"\s*[:=]\s*\S+",
    re.IGNORECASE,
)

_NOISY_LOGGERS = (
    "urllib3",
    "urllib3.connectionpool",
    "requests",
    "requests.packages.urllib3",
    "httpx",
    "httpcore",
    "slack_sdk",
    "slack_sdk.web",
    "slack_sdk.web.base_client",
    "slack_sdk.web.slack_response",
)

_RESET = "\033[0m"
_DIM = "\033[38;5;244m"
_CYAN = "\033[38;5;38m"
_GREEN = "\033[38;5;70m"
_YELLOW = "\033[38;5;178m"
_RED = "\033[38;5;203m"

_OSC8_START = "\033]8;;{url}\033\\"
_OSC8_END = "\033]8;;\033\\"
_GH_PR_RE = re.compile(
    r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<n>\d+)",
    re.IGNORECASE,
)
_BB_PR_RE = re.compile(
    r"bitbucket\.org/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull-requests/(?P<n>\d+)",
    re.IGNORECASE,
)
_EVENT_PREFIX = "ADK_EVENT "


def _scrub(text: str) -> str:
    return _SECRET_RE.sub(lambda m: m.group(1) + "=<redacted>", text)


def _plain_mode(*, no_color: bool = False, stream=None) -> bool:
    stream = stream or sys.stderr
    return (
        os.environ.get("ADK_AGENT_MODE") == "1"
        or no_color
        or "NO_COLOR" in os.environ
        or os.environ.get("TERM") == "dumb"
        or not getattr(stream, "isatty", lambda: False)()
    )


def is_orchestrated() -> bool:
    """True when a parent command owns terminal rendering."""
    return os.environ.get("ADK_ORCHESTRATED") == "1"


def is_verbose() -> bool:
    return os.environ.get("ADK_VERBOSE") == "1"


def supports_hyperlinks(*, stream=None) -> bool:
    """Return True when OSC-8 terminal links are safe to emit."""
    stream = stream or sys.stdout
    if os.environ.get("ADK_NO_LINKS") == "1":
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return getattr(stream, "isatty", lambda: False)()


def terminal_link(label: str, url: str, *, stream=None) -> str:
    """Render `label` as a clickable terminal link when supported.

    When stdout is captured or redirected, returning the plain label keeps log
    files readable and avoids leaking escape sequences into markdown reports.
    """
    if not url or not supports_hyperlinks(stream=stream):
        return label
    return f"{_OSC8_START.format(url=url)}{label}{_OSC8_END}"


def parse_pr_ref(url: str) -> dict[str, object] | None:
    """Parse GitHub / Bitbucket PR URLs into the compact terminal label shape."""
    raw = (url or "").strip().rstrip("/")
    m = _GH_PR_RE.search(raw)
    if m:
        return {
            "host": "github",
            "prefix": "gh",
            "owner": m.group("owner"),
            "repo": m.group("repo"),
            "number": int(m.group("n")),
            "url": raw,
        }
    m = _BB_PR_RE.search(raw)
    if m:
        return {
            "host": "bitbucket",
            "prefix": "bb",
            "owner": m.group("owner"),
            "repo": m.group("repo"),
            "number": int(m.group("n")),
            "url": raw,
        }
    return None


def format_pr_ref(url: str, *, stream=None) -> str:
    """Format a PR as `gh:repo#123` / `bb:repo#123`, linked when possible."""
    ref = parse_pr_ref(url)
    if ref is None:
        return url or "unknown-pr"
    label = f"{ref['prefix']}:{ref['repo']}#{ref['number']}"
    return terminal_link(label, str(ref["url"]), stream=stream)


def format_file_ref(path: str | Path, *, label: str | None = None,
                    stream=None) -> str:
    """Format a local file/path as a clickable `file://` terminal link."""
    p = Path(path).expanduser()
    resolved = p.resolve() if p.exists() else p
    text = label or str(p)
    return terminal_link(text, f"file://{resolved}", stream=stream)


def status_glyph(status: str | None) -> str:
    s = (status or "").lower()
    if s in {"ok", "done", "prepared", "success", "completed"}:
        return "✅"
    if s in {"failed", "error"}:
        return "❌"
    if s in {"warn", "warning"}:
        return "⚠️"
    if s in {"skipped", "noop"}:
        return "⏭️"
    if s in {"running", "in_review", "start"}:
        return "▶️"
    return "•"


@dataclass
class RunEvent:
    kind: str
    name: str = ""
    status: str = ""
    detail: str = ""
    pr_url: str = ""
    stage: str = ""
    reason: str = ""
    next_action: str = ""
    log_path: str = ""
    elapsed_s: float | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        out = {
            "kind": self.kind,
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
            "pr_url": self.pr_url,
            "stage": self.stage,
            "reason": self.reason,
            "next_action": self.next_action,
            "log_path": self.log_path,
            "elapsed_s": self.elapsed_s,
            "data": self.data,
        }
        return {k: v for k, v in out.items() if v not in ("", None, {})}


def encode_event(event: RunEvent | dict[str, Any]) -> str:
    payload = event.to_dict() if isinstance(event, RunEvent) else event
    return _EVENT_PREFIX + json.dumps(payload, ensure_ascii=False, sort_keys=False)


def emit_event(event: RunEvent | dict[str, Any], *, stream=None) -> None:
    print(encode_event(event), file=stream or sys.stdout, flush=True)


def parse_event_line(line: str) -> dict[str, Any] | None:
    if not line.startswith(_EVENT_PREFIX):
        return None
    try:
        data = json.loads(line[len(_EVENT_PREFIX):])
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def compact_path(path: str | Path) -> str:
    p = str(path)
    home = str(Path.home())
    if p.startswith(home + "/"):
        return "~/" + p[len(home) + 1:]
    return p


def summarize_items(items: Iterable[str], *, limit: int = 3) -> str:
    vals = [v for v in items if v]
    if not vals:
        return "none"
    shown = vals[:limit]
    rest = len(vals) - len(shown)
    suffix = f" (+{rest})" if rest > 0 else ""
    return ", ".join(shown) + suffix


_FAILURE_PREFIXES = (
    "RuntimeError:",
    "ValueError:",
    "FileNotFoundError:",
    "PermissionError:",
    "TimeoutError:",
    "AssertionError:",
    "Exception:",
    "Error:",
    "fatal:",
    "error:",
)


def extract_failure_reason(log_path: str | Path, *, max_lines: int = 250) -> str:
    """Return a short actionable reason from the tail of a captured log."""
    path = Path(log_path)
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "could not read child log"
    tail = [ln.strip() for ln in lines[-max_lines:] if ln.strip()]
    if not tail:
        return "child process exited without output"
    for ln in reversed(tail):
        if ln.startswith("step failed (rc="):
            return ln[:240]
    for ln in reversed(tail):
        if any(ln.startswith(prefix) for prefix in _FAILURE_PREFIXES):
            return ln[:240]
    for ln in reversed(tail):
        lower = ln.lower()
        if "error" in lower or "failed" in lower or "exception" in lower:
            return ln[:240]
    return tail[-1][:240]


class RunDashboard:
    """Small stateful terminal renderer for orchestrated PR-review runs."""

    def __init__(self, *, run_id: str, queue: str, runner: str,
                 parallel: int, selected: int = 0, run_dir: str | Path = "",
                 stream=None) -> None:
        self.run_id = run_id
        self.queue = queue
        self.runner = runner
        self.parallel = parallel
        self.selected = selected
        self.run_dir = str(run_dir) if run_dir else ""
        self.stream = stream or sys.stdout
        self.started = time.time()
        self.sync_rows: dict[str, dict[str, Any]] = {}
        self.waiting: dict[str, dict[str, Any]] = {}
        self.active: dict[str, dict[str, Any]] = {}
        self.done: dict[str, dict[str, Any]] = {}
        self.failed: dict[str, dict[str, Any]] = {}
        self.attention: list[dict[str, Any]] = []
        self._last_lines = 0
        self._inline = (
            os.environ.get("ADK_NO_INLINE_DASHBOARD") != "1"
            and getattr(self.stream, "isatty", lambda: False)()
            and os.environ.get("TERM") != "dumb"
        )

    def apply(self, event: dict[str, Any]) -> None:
        kind = event.get("kind")
        if kind in {"step_start", "step_progress", "step_done"}:
            name = event.get("name") or "step"
            row = self.sync_rows.setdefault(name, {"name": name})
            row.update(event)
        elif kind == "pr_wait":
            key = self._pr_key(event)
            self.waiting[key] = event
        elif kind == "pr_active":
            key = self._pr_key(event)
            self.waiting.pop(key, None)
            self.active[key] = event
        elif kind == "pr_done":
            key = self._pr_key(event)
            self.waiting.pop(key, None)
            self.active.pop(key, None)
            self.done[key] = event
        elif kind == "pr_fail":
            key = self._pr_key(event)
            self.waiting.pop(key, None)
            self.active.pop(key, None)
            self.failed[key] = event
            self.attention.append({"kind": "fail", **event})
        elif kind == "attention":
            self.attention.append(event)

    def print_snapshot(self) -> None:
        body = self.render()
        if self._inline and self._last_lines:
            print(f"\033[{self._last_lines}F\033[J", end="", file=self.stream)
        print(body, file=self.stream, flush=True)
        self._last_lines = len(body.splitlines())

    def render(self) -> str:
        elapsed = int(time.time() - self.started)
        lines = [
            f"adk pr-review-all  run {self.run_id}  elapsed {self._fmt_elapsed(elapsed)}",
            f"queue  {compact_path(self.queue)}",
            f"runner {self.runner}  parallel {self.parallel}  selected {self.selected}",
        ]
        if self.run_dir:
            lines.append(f"run dir {compact_path(self.run_dir)}")
        lines += ["", "Sync"]
        if self.sync_rows:
            for row in self.sync_rows.values():
                lines.append(self._render_step(row))
        else:
            lines.append("  wait  sync not started")
        lines += ["", "PRs", "  Active"]
        if self.active:
            for row in self.active.values():
                lines.append(self._render_pr(row, indent="    "))
                if row.get("detail"):
                    lines.append(f"          last: {row['detail']}")
        else:
            lines.append("    wait  none")
        lines.append("")
        lines.append("  Waiting")
        if self.waiting:
            for row in self.waiting.values():
                lines.append(self._render_pr(row, indent="    "))
        else:
            lines.append("    wait  none")
        lines.append("")
        lines.append("  Done")
        combined = list(self.failed.values()) + list(self.done.values())
        if combined:
            for row in combined:
                lines.append(self._render_pr(row, indent="    "))
        else:
            lines.append("    wait  none")
        lines += ["", "Attention"]
        if self.attention:
            for item in self.attention:
                lines.extend(self._render_attention(item))
        else:
            lines.append("  none")
        return "\n".join(lines)

    def _pr_key(self, event: dict[str, Any]) -> str:
        return format_pr_ref(event.get("pr_url") or event.get("name") or "")

    def _render_step(self, row: dict[str, Any]) -> str:
        status = row.get("status") or ("run" if row.get("kind") != "step_done" else "done")
        detail = row.get("detail") or ""
        return f"  {status:<5} {row.get('name', 'step'):<20} {detail}".rstrip()

    def _render_pr(self, row: dict[str, Any], *, indent: str) -> str:
        status = row.get("status") or {"pr_active": "run", "pr_wait": "wait",
                                       "pr_done": "done", "pr_fail": "fail"}.get(row.get("kind"), "")
        ref = format_pr_ref(row.get("pr_url") or row.get("name") or "")
        elapsed = row.get("elapsed_s")
        elapsed_text = f"  {self._fmt_elapsed(float(elapsed))}" if elapsed is not None else ""
        stage = row.get("stage") or ""
        reason = row.get("reason") or ""
        suffix = f"  stage={stage}" if stage else ""
        if status == "fail" and reason:
            suffix += f"  reason={reason[:80]}"
        return f"{indent}{status:<5} {ref:<28}{elapsed_text}{suffix}".rstrip()

    def _render_attention(self, item: dict[str, Any]) -> list[str]:
        level = item.get("level") or item.get("kind") or "warn"
        title = item.get("title") or item.get("name") or item.get("detail") or ""
        if item.get("pr_url"):
            title = f"{format_pr_ref(item['pr_url'])}: {title or item.get('reason', '')}"
        lines = [f"  {level:<5} {title}".rstrip()]
        if item.get("reason") and item.get("reason") not in title:
            lines.append(f"        reason: {item['reason']}")
        if item.get("next_action"):
            lines.append(f"        next: {item['next_action']}")
        if item.get("log_path"):
            lines.append(f"        log: {compact_path(item['log_path'])}")
        return lines

    def _fmt_elapsed(self, seconds: float) -> str:
        seconds = int(seconds)
        if seconds < 60:
            return f"{seconds}s"
        minutes, sec = divmod(seconds, 60)
        if minutes < 60:
            return f"{minutes}m{sec:02d}s"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h{minutes:02d}m"


class _PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = _scrub(record.getMessage())
        ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        head = f"{ts} {record.levelname:<5} [{record.name}]"
        if "\n" in msg:
            first, _, rest = msg.partition("\n")
            msg = f"{first}\n" + "\n".join("  " + ln for ln in rest.splitlines())
        out = f"{head} {msg}"
        if record.exc_info:
            tb = self.formatException(record.exc_info)
            out = f"{out}\n" + "\n".join("  " + ln for ln in tb.splitlines())
        return out


class _ModernFormatter(logging.Formatter):
    def __init__(self, *, color: bool) -> None:
        super().__init__()
        self.color = color

    def _c(self, color: str, text: str) -> str:
        return f"{color}{text}{_RESET}" if self.color else text

    def _glyph(self, record: logging.LogRecord) -> str:
        status = getattr(record, "adk_status", "")
        if status == "start":
            return "◯"
        if status == "ok":
            return "✓"
        if record.levelno >= logging.ERROR:
            return "✗"
        if record.levelno >= logging.WARNING:
            return "⚠"
        if status == "detail":
            return "▸"
        return "›"

    def _glyph_color(self, record: logging.LogRecord) -> str:
        if record.levelno >= logging.ERROR:
            return _RED
        if record.levelno >= logging.WARNING:
            return _YELLOW
        if getattr(record, "adk_status", "") == "ok":
            return _GREEN
        return _CYAN

    def format(self, record: logging.LogRecord) -> str:
        msg = _scrub(record.getMessage())
        ts = self._c(_DIM, time.strftime("%H:%M:%S", time.localtime(record.created)))
        glyph = self._c(self._glyph_color(record), self._glyph(record))
        name = self._c(_CYAN, f"{record.name:<14.14}")
        head = f"{ts}  {glyph}  {name}"
        if "\n" in msg:
            first, _, rest = msg.partition("\n")
            body = f"{head} {first}\n" + "\n".join(f"            ↳ {ln}" for ln in rest.splitlines())
        else:
            body = f"{head} {msg}"
        if record.exc_info:
            tb = self.formatException(record.exc_info)
            body = f"{body}\n" + "\n".join(f"            ↳ {ln}" for ln in tb.splitlines())
        return body


def _pin_noisy_loggers() -> None:
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str, *, task_dir: Path | None = None,
               no_color: bool = False) -> logging.Logger:
    log = logging.getLogger(name)
    if any(getattr(h, "_adk_log", False) for h in log.handlers):
        return log

    log.setLevel(logging.INFO)
    _pin_noisy_loggers()

    plain = _plain_mode(no_color=no_color)
    sh = logging.StreamHandler(sys.stderr)
    sh.setFormatter(_PlainFormatter() if plain else _ModernFormatter(color=True))
    setattr(sh, "_adk_log", True)
    log.addHandler(sh)

    if task_dir:
        task_dir.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(task_dir / "review.log", encoding="utf-8")
        fh.setFormatter(_PlainFormatter())
        setattr(fh, "_adk_log", True)
        log.addHandler(fh)
    return log


def print_summary_box(title: str, kvs: Iterable[tuple[str, object]], *,
                      stream=None) -> None:
    stream = stream or sys.stdout
    rows = [(k, str(v)) for k, v in kvs]
    if _plain_mode(stream=stream):
        print(title, file=stream)
        for k, v in rows:
            print(f"  {k}: {v}", file=stream)
        return

    width = max([len(title) + 4, *(len(k) + len(v) + 7 for k, v in rows)], default=50)
    line = "━" * min(max(width, 48), 80)
    print(line, file=stream)
    print(f"  {title}", file=stream)
    for k, v in rows:
        print(f"  {k:<10}: {v}", file=stream)
    print(line, file=stream)
