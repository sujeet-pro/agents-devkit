from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import LoadingIndicator, Static

_TRIAGE_SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "skills" / "adk-pr-review" / "scripts" / "triage.py"
)


def _run_triage(task_dir: Path, *args: str) -> tuple[int, str]:
    """Run triage.py synchronously. Returns (returncode, combined output)."""
    cmd = [sys.executable, str(_TRIAGE_SCRIPT), "--task-dir", str(task_dir), *args]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        out = (result.stdout or "") + (result.stderr or "")
        return result.returncode, out.strip()
    except Exception as exc:
        return 1, f"error: {exc}"


def _load_findings(findings_path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(findings_path.read_text(encoding="utf-8", errors="replace"))
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "findings" in data:
            return data["findings"]
    except Exception:
        pass
    return []


def _finding_text(finding: dict[str, Any], index: int, total: int) -> str:
    fid = finding.get("id", f"f-{index + 1:03d}")
    severity = finding.get("severity", "unknown")
    dimension = finding.get("dimension", "")
    location = finding.get("location", finding.get("file", ""))
    if not location and finding.get("path"):
        loc_parts = [finding["path"]]
        if finding.get("line"):
            loc_parts.append(str(finding["line"]))
        location = ":".join(loc_parts)
    title = finding.get("title", "(no title)")
    body = finding.get("body", finding.get("description", ""))
    suggestion = finding.get("suggestion", "")

    lines = [
        f"Finding {index + 1} of {total}  [{fid}]",
        "",
        f"  Severity:   {severity}",
        f"  Dimension:  {dimension}",
        f"  Location:   {location}",
        f"  Title:      {title}",
    ]
    if body:
        lines += ["", "  Body:", *[f"    {l}" for l in body.splitlines()]]
    if suggestion:
        lines += ["", "  Suggestion:", *[f"    {l}" for l in suggestion.splitlines()]]
    return "\n".join(lines)


class FindingsWalkScreen(ModalScreen[None]):
    """Walk validated-findings.json one finding at a time.

    Keys:
      A — accept
      R — reject (prompts for reason via PromptScreen)
      E — edit (opens FindingsEditScreen, then rewrites via triage.py)
      right_arrow — skip to next
      Q / Escape — finalize and close
    """

    BINDINGS = [
        Binding("a", "accept", "Accept"),
        Binding("r", "reject", "Reject"),
        Binding("e", "edit", "Edit"),
        Binding("right", "skip", "Skip"),
        Binding("q", "save_quit", "Save+quit"),
        Binding("escape", "save_quit", show=False),
    ]

    DEFAULT_CSS = """
    FindingsWalkScreen {
        align: center middle;
    }
    FindingsWalkScreen > Container {
        width: 95%;
        height: 85%;
        padding: 1 2;
        border: round $accent;
        background: $surface;
    }
    FindingsWalkScreen VerticalScroll {
        width: 100%;
        height: 1fr;
    }
    FindingsWalkScreen #fw-body {
        width: 100%;
    }
    FindingsWalkScreen #fw-status {
        color: $text-muted;
        padding-top: 1;
        width: 100%;
    }
    FindingsWalkScreen #fw-footer {
        padding-top: 1;
        width: 100%;
    }
    FindingsWalkScreen LoadingIndicator {
        height: 3;
        display: none;
    }
    """

    def __init__(self, *, findings_path: Path, task_dir: Path) -> None:
        super().__init__()
        self._findings_path = findings_path
        self._task_dir = task_dir
        self._findings: list[dict[str, Any]] = _load_findings(findings_path)
        self._index: int = 0

    def compose(self) -> ComposeResult:
        with Container():
            with VerticalScroll():
                yield Static("", id="fw-body", markup=False)
                yield LoadingIndicator(id="fw-spinner")
            yield Static("", id="fw-status", markup=False)
            yield Static(
                "[A]ccept  [R]eject  [E]dit  [->]skip  [Q]save+quit",
                id="fw-footer",
                markup=False,
            )

    def on_mount(self) -> None:
        self._render_current()

    def _render_current(self) -> None:
        total = len(self._findings)
        if total == 0:
            self.query_one("#fw-body", Static).update("(no findings to walk)")
            self.query_one("#fw-status", Static).update("")
            return
        if self._index >= total:
            self.query_one("#fw-body", Static).update("(all findings reviewed)")
            self.query_one("#fw-status", Static).update("press Q to finalize and close")
            return
        finding = self._findings[self._index]
        self.query_one("#fw-body", Static).update(_finding_text(finding, self._index, total))
        self.query_one("#fw-status", Static).update("")

    def _current_finding_id(self) -> str | None:
        if 0 <= self._index < len(self._findings):
            f = self._findings[self._index]
            return str(f.get("id", f"f-{self._index + 1:03d}"))
        return None

    def _advance(self) -> None:
        self._index += 1
        self._render_current()

    def action_accept(self) -> None:
        fid = self._current_finding_id()
        if fid is None:
            return
        rc, out = _run_triage(self._task_dir, "--mark", "accept", "--id", fid)
        status = f"accepted {fid}" if rc == 0 else f"accept failed (rc={rc}): {out}"
        self.query_one("#fw-status", Static).update(status)
        self._advance()

    @work
    async def action_reject(self) -> None:
        fid = self._current_finding_id()
        if fid is None:
            return
        from tui.screens.prompt_screen import PromptScreen
        reason = await self.app.push_screen_wait(
            PromptScreen("Reject reason (optional):", "")
        )
        if reason is None:
            return  # cancelled
        args = ["--mark", "reject", "--id", fid]
        if reason.strip():
            args += ["--reason", reason.strip()]
        rc, out = _run_triage(self._task_dir, *args)
        status = f"rejected {fid}" if rc == 0 else f"reject failed (rc={rc}): {out}"
        self.query_one("#fw-status", Static).update(status)
        self._advance()

    @work
    async def action_edit(self) -> None:
        fid = self._current_finding_id()
        if fid is None:
            return
        finding = self._findings[self._index]
        initial_body = finding.get("body", finding.get("description", ""))
        suggestion = finding.get("suggestion", "")
        if suggestion:
            initial_body = initial_body + "\n\n---\n" + suggestion

        from tui.screens.findings_edit_screen import FindingsEditScreen
        new_body = await self.app.push_screen_wait(
            FindingsEditScreen(
                title=str(finding.get("title", fid)),
                body=initial_body,
            )
        )
        if new_body is None:
            return  # cancelled

        spinner = self.query_one("#fw-spinner", LoadingIndicator)
        spinner.display = True
        self.query_one("#fw-body", Static).update("(rewriting via LLM…)")

        rc, out = _run_triage(
            self._task_dir,
            "--rewrite", fid,
            "--fields-json", json.dumps({"body": new_body}),
        )
        spinner.display = False

        if rc == 0:
            self._findings = _load_findings(self._findings_path)
            status = f"rewritten {fid}"
        else:
            status = f"rewrite failed (rc={rc}): {out[:80]}"
        self.query_one("#fw-status", Static).update(status)
        self._render_current()

    def action_skip(self) -> None:
        self._advance()

    def action_save_quit(self) -> None:
        _run_triage(self._task_dir, "--finalize")
        self.dismiss(None)
