# TUI sub-phase ζ — binding interface SPEC

Status: **frozen**, parallel build. Companion to SPEC.md / SPEC-gamma.md / SPEC-delta.md / SPEC-theta.md.

δ ships a single-PR review via `r`. θ shows every active worker in the WorkersPane. ζ adds:

1. **Multi-select** rows in the QueueTable. `space` toggles the highlighted row's URL in/out of the selection. Selected rows show a `[N]` prefix indicating run order (1-based, 9-cap for display).
2. **`R` (capital) — batch run** all selected rows in FIFO selection order, respecting a parallel cap. As each worker finishes, the next URL in the queue starts.
3. **`p` — cycle parallel cap** through 1 → 2 → 4 → 8 → 1.
4. **Refactor**: `_review_proc` (single slot) → `_review_workers: dict[pr_url → Process]` so multiple workers run concurrently. `_review_tasks` mirrors.
5. **Selection survives reloads**: a URL in `_selection_order` that vanishes from the queue (e.g., PR merged) is dropped from selection automatically.
6. **Mutex rules preserved**: `s` still blocks while any review is in flight; `R` is blocked while sync is running OR any review is running (current batch must finish first). A single `r` is blocked while a batch is running.

All α+β+γ+δ+θ behavior keeps working. The existing 487 tests stay green.

---

## 1. File ownership (strict)

| Agent | Role | Owns | Reads (no write) |
|---|---|---|---|
| **A** | `adk-agent-implementer` | `tui/app.py` (MODIFIED — selection state, R/space/p actions, batch runner, mutex refactor), `tui/widgets/queue_table.py` (MODIFIED — column widening, [N] prefix), `tui/widgets/footer_bar.py` (MODIFIED — selected_count + parallel_n kwargs), `tui/widgets/help_screen.py` (MODIFIED — new bindings text) | all α–θ files |
| **B** | `adk-agent-test-engineer` | `tui/tests/test_selection.py` (NEW — selection state + space/R/p bindings), `tui/tests/test_batch_run.py` (NEW — Pilot tests for batch concurrency), `tui/tests/conftest.py` (MODIFIED — possibly add an `eligible_multi_queue` fixture with ≥3 eligible rows) | everything |

**Hard rule**: A does not touch tests. B does not write production code.

---

## 2. State changes in `AdkApp`

### 2.1 New attributes (in `__init__`)

```python
self._selection_order: list[str] = []           # ordered pr_urls; preserves insertion order
self._review_workers: dict[str, asyncio.subprocess.Process] = {}  # pr_url → process
self._review_tasks: dict[str, asyncio.Task] = {}                  # pr_url → task
self._parallel_n: int = 4                       # batch concurrency cap
self._batch_task: asyncio.Task | None = None    # the active batch driver, if any
```

The old `self._review_proc` and `self._review_task` are **removed**. All call sites in α–θ that referenced them must be migrated.

### 2.2 New constants

```python
_PARALLEL_CYCLE: tuple[int, ...] = (1, 2, 4, 8)
```

### 2.3 Removed / refactored

- `self._review_proc` → deleted.
- `self._review_task` → deleted.
- `_busy()` → renamed to `_busy_label()` and tightened:
  ```python
  def _busy_label(self) -> str | None:
      if self._sync_proc is not None and self._sync_proc.returncode is None:
          return "sync"
      if self._batch_task is not None and not self._batch_task.done():
          return "batch"
      if self._review_workers:
          # singular review is just a 1-worker batch from the user's perspective
          return "review"
      return None
  ```

---

## 3. New / changed bindings

| Key | Action | Behavior |
|---|---|---|
| `space` | `toggle_select` | If highlighted row's pr_url is in `_selection_order`, remove it. Else append. No-op when no row highlighted or row's url is None. Triggers a queue re-render so the `[N]` marker updates. |
| `R` (capital) | `run_selected` | If `_busy_label() is not None` → write `(can't start batch — X already running)` and return. If `_selection_order` is empty → write `(no rows selected — press `space` on rows to select)` and return. Otherwise spawn the batch runner task. |
| `p` | `cycle_parallel` | Cycle `_parallel_n` through `_PARALLEL_CYCLE`. Always allowed (no mutex). Triggers footer redraw. |
| `r` (existing) | `review` | Updated mutex: blocked when `_busy_label() is not None` OR `len(self._review_workers) >= self._parallel_n`. Otherwise spawn one worker outside the batch (single-PR review still works). |
| `s` (existing) | `sync` | Updated mutex: same as today — blocked when `_busy_label() == "sync"` (legacy text) or any review/batch is running (cross-process collision text). |

**Add to `BINDINGS`** at the appropriate position (after `r`):

```python
Binding("R", "run_selected", "run-selected"),
Binding("space", "toggle_select", "select"),
Binding("p", "cycle_parallel", "parallel"),
```

The `R` binding is uppercase. Textual key names for shifted letters are `"R"` not `"shift+r"`.

---

## 4. Selection model

### 4.1 `action_toggle_select`

```python
def action_toggle_select(self) -> None:
    table = self.query_one(QueueTable)
    pr_url = table.selected_pr_url()
    if not pr_url:
        return
    if pr_url in self._selection_order:
        self._selection_order.remove(pr_url)
    else:
        self._selection_order.append(pr_url)
    self._reload(force=True)
```

### 4.2 Selection pruning on reload

Each time `_reload` runs, prune selections whose URLs are no longer in the current snapshot:

```python
def _reload(self, *, force: bool = False) -> None:
    if self._model is None:
        return
    if not force and not self._model.has_changed():
        return
    snapshot = self._model.snapshot(
        filter_mode=self._filter_mode,
        sort_mode=self._sort_mode,
    )
    self._rows_by_url = {row.pr_url: row for row in snapshot.rows}
    # Prune disappeared URLs from selection.
    self._selection_order = [u for u in self._selection_order if u in self._rows_by_url]
    self.query_one(HeaderBar).update_snapshot(snapshot)
    self.query_one(QueueTable).load(
        snapshot, ascii_only=self._ascii_only,
        selected_order=list(self._selection_order),
    )
    self.query_one(FooterBar).update_status(
        self._filter_mode, self._sort_mode,
        sync_running=(self._sync_proc is not None and self._sync_proc.returncode is None),
        review_running=bool(self._review_workers),
        selected_count=len(self._selection_order),
        parallel_n=self._parallel_n,
    )
    self._refresh_detail()
```

### 4.3 `QueueTable.load` signature change

```python
def load(
    self,
    snapshot: QueueSnapshot,
    *,
    ascii_only: bool = False,
    selected_order: list[str] | None = None,
) -> None:
```

Default `selected_order=None` is treated as empty (so the test_queue_render existing tests still pass without modification).

The icon column is widened from 2 chars to **5 chars**. The renderer becomes:

```python
selected_order = selected_order or []
sel_pos: dict[str, int] = {url: i + 1 for i, url in enumerate(selected_order)}

for row in snapshot.rows:
    state = derive(row, ascii_only=ascii_only, now=snapshot.now)
    pos = sel_pos.get(row.pr_url)
    if pos is not None:
        marker_label = f"[{min(pos, 9)}]"
        icon_cell = f"{marker_label}{state.icon}"
    else:
        icon_cell = f"   {state.icon}"  # 3 leading spaces to align under the 4-char marker prefix
    ...
```

Width adjustment in `_COLUMNS`:

```python
_COLUMNS: tuple[tuple[str, int], ...] = (
    ("", 5),                  # was 2
    ("#", 8),
    ("repo", 24),
    ("title", 40),
    ("branch", 18),
    ("age", 8),
)
```

### 4.4 Empty-state row

Keep the existing empty-state behaviour (`— · — · no PRs · ...`); selected_order is irrelevant in that case.

---

## 5. Batch runner

### 5.1 `action_run_selected`

```python
def action_run_selected(self) -> None:
    busy = self._busy_label()
    if busy is not None:
        self.query_one(LogPane).write(f"(can't start batch — {busy} already running)")
        return
    if not self._selection_order:
        self.query_one(LogPane).write("(no rows selected — press `space` on rows to select)")
        return
    # Filter selection to only ready rows; emit warnings for the rest.
    ready: list[str] = []
    log_pane = self.query_one(LogPane)
    for url in list(self._selection_order):
        row = self._rows_by_url.get(url)
        if row is None or not row.ready_for_review:
            log_pane.write(f"(skipping {url} — not ready)")
            continue
        ready.append(url)
    if not ready:
        log_pane.write("(no eligible rows in selection)")
        return
    log_pane.write(f"(batch start — {len(ready)} rows, parallel={self._parallel_n})")
    self._batch_task = asyncio.create_task(self._run_batch(ready))
    self._batch_task.add_done_callback(self._on_batch_task_done)
```

### 5.2 `_run_batch(urls)`

```python
async def _run_batch(self, urls: list[str]) -> None:
    queue: list[str] = list(urls)
    inflight: set[asyncio.Task] = set()

    def _start_next() -> None:
        while queue and len(inflight) < self._parallel_n:
            url = queue.pop(0)
            t = asyncio.create_task(self._run_review(url))
            inflight.add(t)

    _start_next()
    while inflight:
        done, _ = await asyncio.wait(inflight, return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            inflight.discard(t)
        _start_next()

    log_pane = self.query_one(LogPane)
    log_pane.write(f"(batch done — {len(urls)} rows)")
    # Refresh footer + queue once at the end.
    self.query_one(FooterBar).update_status(
        self._filter_mode, self._sort_mode,
        sync_running=False, review_running=False,
        selected_count=len(self._selection_order), parallel_n=self._parallel_n,
    )
    self._reload(force=True)
```

### 5.3 `_run_review` migration (each call manages its own slot)

The existing `_run_review(pr_url)` already streams output and updates the footer. **Modifications**:

- Replace `self._review_proc = ...` with `self._review_workers[pr_url] = ...`.
- On completion: `self._review_workers.pop(pr_url, None)`.
- Footer's `review_running` becomes True whenever `bool(self._review_workers)` is True. Update at the start AND end of each `_run_review` call:
  ```python
  self.query_one(FooterBar).update_status(
      self._filter_mode, self._sort_mode,
      sync_running=False,
      review_running=bool(self._review_workers),
      selected_count=len(self._selection_order),
      parallel_n=self._parallel_n,
  )
  ```

`_on_review_task_done(task)` is preserved but no longer references `_review_proc` — it relies on `_review_workers` being kept in sync by `_run_review`.

### 5.4 `_on_batch_task_done`

```python
def _on_batch_task_done(self, task: asyncio.Task) -> None:
    try:
        exc = task.exception()
    except (asyncio.CancelledError, asyncio.InvalidStateError):
        return
    if exc is not None:
        try:
            self.query_one(LogPane).write(f"(batch crashed: {exc!r})")
        except Exception:
            pass
    self._batch_task = None
```

### 5.5 `on_unmount` extension

`on_unmount` already kills `_sync_proc` and `_review_proc`. After the refactor: iterate over `self._review_workers.values()` instead:

```python
async def on_unmount(self) -> None:
    procs = [self._sync_proc, *self._review_workers.values()]
    for proc in procs:
        if proc is not None and proc.returncode is None:
            try:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2.0)
                except asyncio.TimeoutError:
                    proc.kill()
            except ProcessLookupError:
                pass
```

---

## 6. `action_cycle_parallel`

```python
def action_cycle_parallel(self) -> None:
    try:
        idx = _PARALLEL_CYCLE.index(self._parallel_n)
    except ValueError:
        idx = 0
    self._parallel_n = _PARALLEL_CYCLE[(idx + 1) % len(_PARALLEL_CYCLE)]
    self.query_one(FooterBar).update_status(
        self._filter_mode, self._sort_mode,
        sync_running=(self._sync_proc is not None and self._sync_proc.returncode is None),
        review_running=bool(self._review_workers),
        selected_count=len(self._selection_order),
        parallel_n=self._parallel_n,
    )
```

Changing `_parallel_n` mid-batch DOES NOT immediately spawn more workers — the change takes effect on the next `_start_next()` tick of the batch loop. That's the natural behavior of reading `self._parallel_n` inside the closure.

---

## 7. FooterBar update

### 7.1 New signature

```python
def update_status(
    self,
    filter_mode: str,
    sort_mode: str,
    *,
    sync_running: bool = False,
    review_running: bool = False,
    selected_count: int = 0,
    parallel_n: int = 4,
) -> None:
    sync_label = "[s] sync (running…)" if sync_running else "[s] sync"
    review_label = "[r] review (running…)" if review_running else "[r] review"
    sel_label = f"sel:{selected_count}" if selected_count else "sel:0"
    par_label = f"par:{parallel_n}"
    text = (
        f"[?] help  [f] filter:{filter_mode}  [S] sort:{sort_mode}"
        f"  [j/k] nav  [q] quit"
        f"  ·  {sync_label}  {review_label}  [R] run-sel  [space] sel  [p] par"
        f"  ·  {sel_label}  {par_label}"
    )
    self.update(text)
```

The new kwargs default to safe values so existing call sites that haven't migrated still work.

### 7.2 Existing call sites

All existing `update_status(...)` callers (about 6 in `tui/app.py`) need to also pass `selected_count` + `parallel_n`. Add them as named kwargs.

---

## 8. HelpScreen text

Insert the three new bindings under the existing `r` line:

```
  q              quit
  ?              this help
  f              cycle filter
  S              cycle sort
  s              start `adk pr-sync` (streams into log pane)
  r              start a review on the highlighted row (claim+prepare+claude)
  R              run all selected rows as a batch (parallel cap)
  space          toggle selection on the highlighted row
  p              cycle parallel cap (1 → 2 → 4 → 8)
  j / down       move cursor down
  k / up         move cursor up
  g / home       jump to first row
  G / end        jump to last row
  enter          (read-only — no action yet)
  escape         close this help
```

---

## 9. Tests (Agent B)

### 9.1 `tui/tests/test_selection.py`

Pilot tests:
1. `test_space_toggles_selection`: launch app with eligible queue (≥3 ready rows); press `space` → cursor row's URL is added to `_selection_order`; QueueTable renders `[1]` prefix in icon column. Press `space` again → URL removed.
2. `test_selection_survives_filter_cycle`: select two rows, then press `f` to cycle filter; visible rows that are still in queue keep their `[N]` markers, with N indices unchanged.
3. `test_selection_pruned_when_url_disappears`: select a row, then artificially mutate the queue file (write a version with that URL removed), trigger reload, the selection list drops that URL.
4. `test_p_cycles_parallel`: press `p` four times; `_parallel_n` cycles 4 → 8 → 1 → 2 → 4. Footer text reflects `par:N`.
5. `test_footer_shows_selected_count`: select 2 rows; footer text contains `sel:2`.

### 9.2 `tui/tests/test_batch_run.py`

Pilot tests:
1. `test_R_with_no_selection_logs_no_rows`: press `R` with empty selection → LogPane `(no rows selected — ...)`.
2. `test_R_with_one_eligible_row_spawns_one_worker`: select the eligible row, press `R`, wait for `(batch done — 1 rows)`. Footer flips through `review_running=True` then back.
3. `test_R_respects_parallel_cap`: requires an `eligible_multi_queue` fixture with ≥3 ready rows. Set `parallel_n=1` (press `p` to cycle to 1). Select all 3, press `R`. Use a slow fake_claude (sleeps 0.4s) and slow fake_adk (sleeps 0.1s per call). Poll the WorkersPane and assert at most 1 active worker at any sampled tick.
4. `test_R_skips_unready_rows`: queue with 1 ready + 1 not-ready row, select both, press `R`. LogPane shows `(skipping <url> — not ready)` then `(batch start — 1 rows, ...)`.
5. `test_R_while_sync_running_blocked`: start sync, then press `R` → `(can't start batch — sync already running)`.

### 9.3 `tui/tests/conftest.py` additions

```python
@pytest.fixture
def eligible_multi_queue(tmp_path: Path) -> Path:
    """A queue with 3 rows, all ready_for_review=True (mirrors eligible_queue.json5
    but with 3 distinct URLs)."""
    src = Path(__file__).resolve().parent / "fixtures" / "eligible_multi_queue.json5"
    dst = tmp_path / "eligible-multi.json5"
    shutil.copyfile(src, dst)
    return dst
```

And the corresponding `tui/tests/fixtures/eligible_multi_queue.json5` with 3 rows.

---

## 10. Definition of done

- `space` toggles selection; selected rows show `[N]` marker in QueueTable.
- `R` runs all selected rows; logs `(batch start — N rows, parallel=M)` and `(batch done — N rows)`.
- `p` cycles parallel cap.
- `r` (single) still works for highlighted row; mutex prevents overlap with sync OR batch.
- Footer shows `sel:N par:M`.
- All 487 baseline tests stay green.
- ≥ 8 net-new tests.

---

## 11. Spec deviations — explicit policy

Same as δ/θ. Small, named deviations OK; surface in completion message.
