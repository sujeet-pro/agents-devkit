# TUI sub-phase ε — binding interface SPEC

Status: **frozen**, parallel build.

ε makes the existing `current_phase` heartbeat field actually move during a review. Today the worker writes `current_phase="review"` once when entering the agent stream and never updates it; the WorkersPane row stays static at `review/review`. After ε, the worker parses the agent's stdout for phase markers and rewrites the heartbeat file as the review progresses through Phases 0 → 6.

UX surface: the **WorkersPane** (θ) already renders `current_phase` — it just becomes more granular. ε also adds a `Phase:` line to the **DetailPane** when the highlighted row has a live worker.

No QueueTable changes — the icon column stays at `⚙↻` for in-review rows. The phase is surfaced in the two text panes (WorkersPane row + DetailPane).

All α–η behavior keeps working. The existing 517 tests stay green.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `tui/worker.py` (MODIFIED — phase parser), `tui/widgets/detail_pane.py` (MODIFIED — `Phase:` line), `tui/app.py` (MODIFIED — pass `worker=...` to DetailPane.show) | all α–η files |
| **B** | `adk-agent-test-engineer` | `tui/tests/test_worker_phase.py` (NEW), `tui/tests/test_detail_pane_phase.py` (NEW), `tui/tests/conftest.py` (MODIFIED — add `_phase_emitting_agent_script` fixture if needed) | everything |

---

## 2. Worker phase parser

### 2.1 Where it lives

`tui/worker.py` already has `_stream_proc(agent_proc)` which reads the agent's stdout line-by-line and writes each line to OUR stdout. Extend that loop to ALSO match each line against a phase-marker regex and update the heartbeat file when one matches.

### 2.2 Phase-marker regex

Match any of these line shapes (from `prepare_task.py` log output, claude markdown headings, and conversational text):

- `--- Phase 0: prereq ---` (from `prepare_task.py:388`)
- `--- Phase 2a: fetch PR (always; gets fresh head_sha) ---`
- `## Phase 4: Triage`
- `**Phase 5: Post**`
- `Phase 3 validate:` 
- `Phase 6 disposition`

The unified regex:

```python
import re
_PHASE_RE = re.compile(
    r"(?:^|\W)"                     # word boundary or start of line
    r"[Pp]hase\s+"                  # "Phase " or "phase "
    r"([0-9]+[a-zA-Z]?)"            # phase number + optional suffix letter ("2a", "4")
    r"(?:\s*[:—\-]\s*([^.\n*]{1,60}))?"  # optional sub-task description
)
```

The capture groups:
1. Phase number string ("0", "2a", "4", "6")
2. Optional sub-task description (e.g., "Triage", "fetch PR")

When a line matches, compose the new phase string:
- If group 2 exists: `f"phase {group1}: {group2.strip()}"` (e.g., `"phase 4: Triage"`)
- Else: `f"phase {group1}"` (e.g., `"phase 6"`)

Truncate the final string at 80 chars (defensive).

### 2.3 Heartbeat update

The existing `_file_loop` (in worker.py) periodically rewrites the heartbeat file with `last_heartbeat=now`. ε adds the side effect of updating `payload["current_phase"]` whenever a phase-marker is seen.

Implementation: modify `_stream_proc(proc)` to take a `payload: dict` parameter. Pass `payload` from `_drive` when calling `_stream_proc`. On each agent line, after writing it to our stdout, check the regex; if it matches, update `payload["current_phase"]` (the `_file_loop` task will pick this up on its next tick and re-persist).

```python
async def _stream_proc(proc: asyncio.subprocess.Process, payload: dict) -> None:
    assert proc.stdout is not None
    while True:
        line = await proc.stdout.readline()
        if not line:
            break
        decoded = line.decode(errors="replace")
        sys.stdout.write(decoded)
        sys.stdout.flush()
        new_phase = _parse_phase_marker(decoded)
        if new_phase is not None:
            payload["current_phase"] = new_phase
```

And:
```python
def _parse_phase_marker(text: str) -> str | None:
    m = _PHASE_RE.search(text)
    if m is None:
        return None
    num = m.group(1)
    desc = (m.group(2) or "").strip()
    label = f"phase {num}: {desc}" if desc else f"phase {num}"
    return label[:80]
```

### 2.4 Initial phase

When the worker starts the agent (after claim + prepare), set `payload["current_phase"] = "phase 0"` (instead of the current `"review"`). The regex parser then advances it as phase markers stream by.

### 2.5 Constraints

- The phase parser must NOT slow down `_stream_proc`. Use `re.search` (which is C-level fast); regex is precompiled at module level.
- The parser must handle `\r\n`, `\n`, and bare `\r` line endings (claude sometimes uses CR).
- False-positive avoidance: the regex MUST NOT match the literal substring `phase` in PR titles, file names, or other prose. The `\W` prefix + bounded sub-task description (`[^.\n*]{1,60}`) limits this. Word boundaries handle `multiphase`, `rephase`, etc.

---

## 3. DetailPane integration

### 3.1 New signature

```python
class DetailPane(Static):
    def __init__(self) -> None:
        super().__init__("(no row selected)", markup=False)

    def show(self, row: QueueRow | None, *, worker: WorkerRow | None = None) -> None:
        ...
```

### 3.2 New line

Append a `Phase:` line to the existing 8-line block when `worker is not None`. Place it between the existing `Status:` line and `Lock:` line.

```
acme/sf-bff#1234
Title:   feat: coupon engine
Author:  sujeet
Branch:  a4f2c1ab → main
Status:  in_review  ·  prep: ready
Phase:   phase 4: Triage              <-- NEW (only when worker is not None)
Lock:    2026-05-22T14:32:15Z
Slack:   #eng-prs (1 thread)
Last reviewed: 1d ago at b7d8e2 (stale)
```

If `worker` is None (no active worker for this row), omit the Phase line entirely. Don't render a blank "Phase: —" placeholder.

### 3.3 Caller side

`AdkApp._refresh_detail()` needs to look up the worker row for the highlighted URL and pass it to `DetailPane.show(row, worker=worker)`.

```python
def _refresh_detail(self) -> None:
    table = self.query_one(QueueTable)
    url = table.selected_pr_url()
    row = self._rows_by_url.get(url) if url else None
    worker = self._workers_by_url.get(url) if url else None
    self.query_one(DetailPane).show(row, worker=worker)
```

`self._workers_by_url: dict[str, WorkerRow]` is a new attribute populated in `_reload_workers`:

```python
def _reload_workers(self, *, force: bool = False) -> None:
    if self._workers_model is None:
        return
    if not force and not self._workers_model.has_changed():
        return
    rows = self._workers_model.snapshot()
    self._workers_by_url = {w.pr_url: w for w in rows if not w.is_stale}
    self.query_one(WorkersPane).update_workers(rows, ascii_only=self._ascii_only)
    # Refresh detail in case the highlighted row's worker phase changed.
    self._refresh_detail()
```

Initialize `self._workers_by_url: dict[str, "WorkerRow"] = {}` in `__init__`.

---

## 4. Tests (Agent B)

### 4.1 `tui/tests/test_worker_phase.py`

Unit tests for `_parse_phase_marker`:
- `"--- Phase 0: prereq ---"` → `"phase 0: prereq"`
- `"--- Phase 2a: fetch PR ---"` → `"phase 2a: fetch PR"`
- `"## Phase 4: Triage"` → `"phase 4: Triage"`
- `"**Phase 5: Post**"` → `"phase 5: Post"`
- `"Phase 6 disposition"` → `"phase 6: disposition"` (or `"phase 6"`, accept either since the boundary regex needs `:` or `-`)
- `"phase 3"` → `"phase 3"`
- `"some unrelated text"` → `None`
- `"multiphase code"` → `None` (no false positive — `multiphase` not matched at word boundary)
- `"see phaserator.py for"` → `None`

Integration:
- Spawn the real `tui/worker.py` with a fake_claude that emits phase lines:
  ```sh
  #!/bin/sh
  echo "--- Phase 0: prereq ---"
  sleep 0.1
  echo "[claude] thinking..."
  sleep 0.1
  echo "## Phase 4: Triage"
  sleep 0.1
  echo "Phase 5: Post"
  exit 0
  ```
- Read the heartbeat file at intervals. Assert it transitions through `phase 0` → `phase 4: Triage` → `phase 5: Post`. (Use a small `--heartbeat-file-interval-s` like 0.05 to catch transitions.)

### 4.2 `tui/tests/test_detail_pane_phase.py`

- `pane.show(row, worker=None)` → render contains `"Phase:"` absent.
- `pane.show(row, worker=WorkerRow(current_phase="phase 4: Triage", ...))` → render contains `"Phase:   phase 4: Triage"`.
- `pane.show(None)` → unchanged: `"(no row selected)"`.

### 4.3 Optional `_workers_by_url` integration test

Pilot test:
- Construct AdkApp with eligible_queue + a pre-populated heartbeat file for the queue's row.
- Wait for the workers poll to pick up the heartbeat.
- Assert DetailPane render contains `"Phase: phase 4: Triage"` (or whatever the heartbeat file has).

---

## 5. Definition of done

- `_parse_phase_marker` returns the right label for all 6 markers above; no false positives on `multiphase` / `phaserator`.
- The worker's heartbeat file's `current_phase` updates live as phase markers stream from the agent.
- DetailPane shows `Phase: ...` line when the highlighted row has an active worker.
- 517 baseline tests stay green.
- ≥ 8 net-new tests.

---

## 6. Spec deviations — explicit policy

Same as δ/θ/η. Small named deviations OK; surface in completion message.
