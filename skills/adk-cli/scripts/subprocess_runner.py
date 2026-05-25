"""SubprocessRunner — ReviewRunner backed by the existing CLI/subprocess flow.

This module wraps the current agent-spawning approach (build a CLI command via
``agent_harness.build_agent_cmd``, ``subprocess.Popen``, parse phase markers
from stdout) into the ``ReviewRunner`` protocol without changing
``auto_run._spawn_review`` or any other existing path.

The key difference from ``auto_run._spawn_review``
--------------------------------------------------
``_spawn_review`` is the production batch path: it manages worker-state JSON
files, queue-entry updates, run-state files, and the context-refresh step.
``SubprocessRunner`` is a focused event-emitting adapter — it does not write
worker state, does not update the queue, and does not run context-refresh.
Its job is purely to drive one subprocess and yield structured ``ReviewEvent``
objects that callers (TUI workers, targeted CLI tools, tests) can consume.

For automated batch runs that need the full queue-side-effect machinery,
``auto_run._spawn_review`` remains the authoritative path.

Phase label parsing
-------------------
The phase regex mirrors ``auto_run._PHASE_RE`` and ``auto_run._parse_phase_marker``.
It is kept local here to avoid importing the full ``auto_run`` module (which
pulls in ``_common``, ``adk_log``, and several other heavy imports from the
``adk-pr-review`` skill tree).

opts accepted by start()
------------------------
deep (bool)            — override deep flag; falls back to constructor default
detailed (bool)        — override detailed flag; falls back to constructor default
comments_only (bool)   — pass --comments-only to the skill; default False
log_path (Path|None)   — write raw subprocess stdout+stderr here; default None
"""
from __future__ import annotations

import re
import selectors
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterator

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))

from agent_harness import build_agent_cmd, resolve_runner_model  # noqa: E402
from review_runner import ReviewEvent, ReviewRunner  # noqa: E402

# Phase marker regex — mirrors auto_run._PHASE_RE.  Both patterns must be kept
# in sync if one changes.  The duplication avoids importing the full auto_run
# module with its heavy skill-tree import chain.
_PHASE_RE = re.compile(
    r"^[\s\-#*>]*"
    r"(?:\[[^\]]+\]\s*)?"
    r"[Pp]hase\s+"
    r"([0-9]+[a-zA-Z]?)"
    r"(?:\s*[:—\-]\s*([^.\n*:]{1,60}))?"
)


def _parse_phase_label(text: str) -> str | None:
    """Return a normalized phase label from a stdout line, or None."""
    m = _PHASE_RE.match(text)
    if m is None:
        return None
    num = m.group(1)
    desc = (m.group(2) or "").strip().rstrip("- ").rstrip()
    label = f"phase {num}: {desc}" if desc else f"phase {num}"
    return label[:80]


class SubprocessRunner:
    """Concrete ReviewRunner backed by subprocess agent invocations.

    Constructs the agent CLI command via ``agent_harness.build_agent_cmd``,
    spawns it as a subprocess, reads its stdout line-by-line, and yields
    ``ReviewEvent`` objects for each significant state change.

    Parameters
    ----------
    runner:    Agent harness name ("claude", "cursor", "codex", "custom").
    agent:     Override runner binary path.
    model:     Explicit model string, or None to use the harness default.
    deep:      Default deep-mode flag for this runner instance.
    detailed:  Default detailed-mode flag.
    workspace: Workspace path passed to harnesses that require it (Cursor/Codex).
    """

    def __init__(
        self,
        *,
        runner: str = "claude",
        agent: str | None = None,
        model: str | None = None,
        deep: bool = False,
        detailed: bool = False,
        workspace: Path | None = None,
    ) -> None:
        self._runner = runner
        self._agent = agent
        self._model = model
        self._deep = deep
        self._detailed = detailed
        self._workspace = workspace

    # ------------------------------------------------------------------
    # ReviewRunner protocol
    # ------------------------------------------------------------------

    def start(
        self,
        pr_url: str,
        **opts: object,
    ) -> Iterator[ReviewEvent]:
        """Yield ReviewEvents for one PR review subprocess.

        Accepted opts
        -------------
        deep (bool)         — per-invocation deep override
        detailed (bool)     — per-invocation detailed override
        comments_only (bool)— forward --comments-only to the skill
        log_path (Path)     — write subprocess stdout+stderr to this path
        """
        deep = bool(opts.get("deep", self._deep))
        detailed = bool(opts.get("detailed", self._detailed))
        comments_only = bool(opts.get("comments_only", False))
        log_path: Path | None = opts.get("log_path")  # type: ignore[assignment]

        resolved_model = resolve_runner_model(
            runner=self._runner,
            explicit_model=self._model,
            deep=deep,
        )

        flags: list[str] = []
        if detailed:
            flags.append("--detailed")
        if deep:
            flags.append("--deep")
        if comments_only:
            flags.append("--comments-only")
        prompt = " ".join(["/adk-pr-review", pr_url] + flags)

        try:
            cmd = build_agent_cmd(
                prompt,
                runner=self._runner,
                agent=self._agent,
                model=resolved_model,
                workspace=self._workspace,
            )
        except ValueError as exc:
            yield ReviewEvent(
                kind="failed",
                label="build command failed",
                detail=str(exc),
                links={"pr": pr_url},
            )
            return

        started_ms = int(time.monotonic() * 1000)

        def _elapsed() -> int:
            return int(time.monotonic() * 1000) - started_ms

        yield ReviewEvent(
            kind="started",
            label="spawning review agent",
            detail=f"runner={self._runner} model={resolved_model or 'default'}",
            elapsed_ms=0,
            links={"pr": pr_url},
        )

        fh = None
        try:
            if log_path is not None:
                log_path.parent.mkdir(parents=True, exist_ok=True)
                fh = open(log_path, "w", encoding="utf-8")

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                )
            except FileNotFoundError:
                yield ReviewEvent(
                    kind="failed",
                    label="agent binary not found",
                    detail=f"binary '{cmd[0]}' not on PATH",
                    elapsed_ms=_elapsed(),
                    links={"pr": pr_url},
                )
                return

            yield ReviewEvent(
                kind="phase",
                label="review agent running",
                elapsed_ms=_elapsed(),
                links={"pr": pr_url},
            )

            current_phase = "review agent running"
            sel = selectors.DefaultSelector()
            if proc.stdout is not None:
                # Non-selectable objects (e.g. test fakes) are silently
                # bypassed; the trailing drain loop reads remaining output.
                try:
                    sel.register(proc.stdout, selectors.EVENT_READ)
                except (ValueError, OSError):
                    pass

            while proc.poll() is None:
                for key, _ in sel.select(timeout=0.2):
                    line = key.fileobj.readline()
                    if not line:
                        continue
                    if fh is not None:
                        fh.write(line)
                        fh.flush()
                    phase = _parse_phase_label(line)
                    if phase is not None and phase != current_phase:
                        current_phase = phase
                        yield ReviewEvent(
                            kind="phase",
                            label=phase,
                            elapsed_ms=_elapsed(),
                            links={"pr": pr_url},
                        )

            # Drain any remaining output after the process exits.
            if proc.stdout is not None:
                for line in proc.stdout:
                    if fh is not None:
                        fh.write(line)
                        if hasattr(fh, "flush"):
                            fh.flush()
                    phase = _parse_phase_label(line)
                    if phase is not None and phase != current_phase:
                        current_phase = phase
                        yield ReviewEvent(
                            kind="phase",
                            label=phase,
                            elapsed_ms=_elapsed(),
                            links={"pr": pr_url},
                        )

            sel.close()
            rc = proc.returncode

        finally:
            if fh is not None:
                fh.close()

        if rc == 0:
            yield ReviewEvent(
                kind="completed",
                label="review completed",
                detail=f"rc={rc}",
                elapsed_ms=_elapsed(),
                links={"pr": pr_url},
            )
        else:
            yield ReviewEvent(
                kind="failed",
                label="review failed",
                detail=f"rc={rc}",
                elapsed_ms=_elapsed(),
                links={"pr": pr_url},
            )


# Runtime check: confirm SubprocessRunner is structurally compatible with
# ReviewRunner before callers discover it at runtime.
def _assert_protocol_conformance() -> None:
    assert isinstance(
        SubprocessRunner(), ReviewRunner
    ), "SubprocessRunner must satisfy ReviewRunner protocol"


_assert_protocol_conformance()
