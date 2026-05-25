"""Runner protocol and event model for ADK PR reviews.

Provides:
  ReviewEventKind  — the fixed set of event kinds any runner backend emits
  ReviewEvent      — normalized progress/task event for TUI and CLI consumers
  ReviewRunner     — runtime-checkable Protocol every backend must satisfy

Any runner backend satisfies the protocol by implementing ``start()``.
Callers import only this module; they never depend on the concrete backend
module directly.

Current implementors
--------------------
SubprocessRunner (subprocess_runner.py)
    Wraps the existing CLI/subprocess agent flow.  This is the only backend
    until ACP transport is available.

Planned (no dependency today)
------------------------------
AcpRunner
    Future ACP channel backend.  The Protocol signature is intentionally kept
    sync (Iterator, not AsyncIterator) so the current synchronous TUI worker
    loop can consume events without an asyncio rewrite.  An async wrapper can
    be layered on top when needed.

Event ordering contract
-----------------------
Every successful run emits:
    started → phase* → (progress*) → completed

Every failed run emits:
    started → phase* → failed

A run that cannot even build the command (e.g. missing --agent for --runner
custom) emits a single ``failed`` event with no ``started`` preceding it.
"""
from __future__ import annotations

import dataclasses
from typing import Iterator, Literal, Protocol, runtime_checkable

# Exhaustive set of event kinds.  Callers should treat unknown kinds as
# informational and not raise; the set may grow non-breakingly.
ReviewEventKind = Literal[
    "started",               # runner acquired subprocess / connection
    "phase",                 # pipeline phase changed (label = "phase N: desc")
    "progress",              # determinate tick (pct 0-100) or spinner (pct None)
    "waiting_for_confirmation",  # runner paused, awaiting user input
    "completed",             # run finished successfully
    "failed",                # run finished with an error (detail = reason)
    "warning",               # non-fatal issue; run continues
]


@dataclasses.dataclass
class ReviewEvent:
    """Normalized event emitted by any ReviewRunner backend.

    Field semantics follow the ProgressEvent shape from the DX proposal
    (§3.12), mapped to the review-specific lifecycle.

    kind
        See ``ReviewEventKind`` above.
    label
        Short human-readable description.  Examples: "phase 3: embed",
        "spawning agent", "review completed".
    detail
        Optional context string: error message, phase description, or elapsed
        time.  May be ``None``.
    pct
        Progress percentage 0-100 for determinate steps; ``None`` = the
        consumer should render a spinner.
    elapsed_ms
        Milliseconds since the runner was started.  ``None`` if unavailable.
    links
        Stable references for this run: ``{"pr": url, "log": file_path}``.
        Keys are present only when the value is known.
    """

    kind: ReviewEventKind
    label: str
    detail: str | None = None
    pct: int | None = None
    elapsed_ms: int | None = None
    links: dict[str, str] = dataclasses.field(default_factory=dict)


@runtime_checkable
class ReviewRunner(Protocol):
    """Protocol for PR review runner backends.

    Implementors yield ``ReviewEvent`` objects as the review progresses.
    Callers iterate the generator synchronously.

    Example (sync consumer)::

        runner = SubprocessRunner(runner="claude")
        for event in runner.start("https://github.com/org/repo/pull/42"):
            tui_update(event)

    The protocol is ``runtime_checkable`` so ``isinstance(obj, ReviewRunner)``
    confirms structural conformance at runtime without requiring inheritance.
    """

    def start(
        self,
        pr_url: str,
        **opts: object,
    ) -> Iterator[ReviewEvent]:
        """Yield ReviewEvents for one PR review.

        Parameters
        ----------
        pr_url:
            Full pull-request URL understood by /adk-pr-review.
        **opts:
            Backend-specific keyword arguments.  Backends document the keys
            they accept; unknown keys are silently ignored.
        """
        ...
