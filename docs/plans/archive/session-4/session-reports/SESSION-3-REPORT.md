# Session 3 — Production-Readiness Pass

Date: 2026-05-21 → 2026-05-22.
Branch: `main`. Start HEAD: `2e74c91`. End HEAD: `e4b4bd3`.
Tests: **430 total, 429 passing** (412 baseline + 18 net-new TUI tests; 1 pre-existing local-clock bug unrelated to this slice).
Session 2 close: see `SESSION-2-REPORT.md` (Phases 0–6 done; Phase 4 OSS hardening and Phase 5 TUI deferred).

## TL;DR

One commit this session — the α + β slice of the TUI (P8 from the v4 plan). `adk` (no args) now launches a Textual read-only queue viewer with filter, sort, detail pane, help modal, and live mtime-gated polling. Implemented by a 3-agent parallel team (widgets / model / tests) against a binding interface spec, then re-tightened by an independent code-review pass that landed 12 specific findings. Sub-phases γ (live sync stream) and δ (run review from the TUI) are deferred to a future session.

## Risk / Blockers / Follow-ups

- **One pre-existing test now fails on this machine**: `test_quiet_hours_aborts_inside_window` in `skills/adk-cli/scripts/tests/test_auto_run_guards.py`. The test passes `--quiet-hours 0-23` expecting "always inside the window", but `_in_quiet_hours` in `auto_run.py:81` treats the range half-open (`a ≤ h < b`), so wall-clock hour 23 lies OUTSIDE [0, 23). Local clock here was 23:42 when Session 3 ran; pre-Session-3 reproduction (`git stash + pytest`) shows the same failure. **Not introduced by this session.** Owner: whoever wrote auto_run's quiet-hours. One-line fix in either the test (use `1-0` wrap-around for "always inside") or the code (decide whether `b` should be inclusive).
- **TUI shipped α+β only**. `s` sync, `r` review, `n` next — all show as `(disabled)` in the footer until sub-phases γ and δ land. Visible to the user but explicitly scoped.
- **From Session 1 still open**: F-018 (env-var presence helper), F-019 (doctor.py uses ensure_ollama), F-021 (scripts/verify_repo.py rewrite + CI gate), F-024 (agents-codex/junie READMEs), F-025 (decision_logger.py coverage), F-028 (query_index.py vs query.py).
- **From Session 2 still open**: SKILL.md / `adk pr-task prepare` workflow cleanup; Bitbucket MCP signature audit on a real Bitbucket PR; `validate_findings.py --strict` mode.

## What got done — by phase

### Phase 5 — TUI α + β (1 commit)

| Commit | Subject |
|---|---|
| `e4b4bd3` | feat(tui): α+β — Textual read-only queue viewer (P8 sub-phases α+β) |

**Layout** (one full-window app):
- Docked header — `adk · queue: N · ready: M · in-review: K/4 · platform: {github,bitbucket,github+bitbucket}`.
- DataTable queue (icon / # / repo / title / branch / age) with cursor preservation across mtime reloads (cursor saved by `pr_url`, restored after replacing rows).
- Detail pane updates as the cursor moves (repo#N, title, author, branch, status+prep, lock, slack, last-reviewed).
- Docked footer — `[?] help  [f] filter:X  [S] sort:Y  [j/k] nav  [q] quit  ·  [s] sync (disabled)  [r] run (disabled)`.

**Bindings**: `q` quit, `?` help (modal with `escape` dismiss), `f` cycle filter (all → open → ready → reviewed → terminal), `S` cycle sort (fifo → newest → repo), `j/k` nav (and ↑/↓), `g/G` jump first/last.

**State icons** (`tui/model/row_state.py:derive`): a 13-icon unicode set (🌱 ⚙ ✓ ⚙↻ 📝 ✅ 🚫 🔒 ⚠ ⏰ …) with a parallel ASCII fallback (`adk --ascii`). Precedence chain: merged/closed → prep_failed → in_review (lock fresh) → approved → reviewed → preparing → waiting_for_base → pending → ready → queued.

**Polling**: 2 s `set_interval`. Queue file is only re-read when its `stat().st_mtime` changes — the steady-state cost is one stat per tick.

**Empty state**: when the queue file doesn't exist, a single `— · — · no PRs · (queue: <path>) · — · —` row renders so the user can read where the missing path is.

**`bin/adk` integration**: no-args (and `--queue-path X` / `--ascii` / `--poll-interval N` alone) lazy-imports `tui.app:main`. Any other first token still dispatches to the existing CLI verbs. `-h` / `--help` / `help` short-circuits to the CLI USAGE block before the TUI detector runs. ImportError on `tui.app` exits 2 with the install hint.

### Build approach — three-agent parallel team

A binding interface spec was written first (`.temp/prj-prod-ready/tui-spec/SPEC.md`, ~13 KB) pinning every public symbol's signature, the queue row → state icon precedence, and the file-ownership boundaries between agents. Then three subagents fanned out:

- **Agent A** (`adk-agent-implementer`) — `tui/app.py`, `tui/styles.tcss`, every file under `tui/widgets/`.
- **Agent B** (`adk-agent-implementer`) — `tui/model/queue_model.py`, `tui/model/row_state.py`.
- **Agent C** (`adk-agent-test-engineer`) — `tui/tests/*`, `bin/adk`, `skills/adk-cli/scripts/requirements.txt`.

Net build time wall-clock: ~13 min from fan-out to last completion (B finished in ~2 min, A in ~3 min, C in ~12.5 min). No file collisions; strict ownership held. Two interface deviations were surfaced explicitly by Agent A and accepted by the leader:

1. `HeaderBar.update()` / `FooterBar.update()` (per spec) → renamed to `update_snapshot()` / `update_status()` to avoid clobbering `Static.update`.
2. `?` binding key name → `question_mark` (Textual's canonical key identifier).

### Validation pass — observable bug + independent reviewer

**Manual smoke** (headless via `app.run_test()`) caught one Rich-markup bug: `Static.update(text)` parses Rich markup by default, so `[f]` / `[S]` / `[q]` / `[s]` / `[r]` got eaten as malformed style tags. Wrong fix attempted first (`self.update(text, markup=False)` — `update()` doesn't accept that kwarg in Textual 8.x); correct fix landed via constructor-level `Static.__init__(..., markup=False)` on HeaderBar, FooterBar, DetailPane, and HelpScreen's inner Static.

**Independent code-review** (`adk-agent-code-reviewer`, read-only) flagged 18 issues across blocker / critical / should / may / nit tiers. Findings landed in the same commit:

| Tier | Finding | Outcome |
|---|---|---|
| Blocker | B-1 — header_bar `update(markup=False)` invalid kwarg | Already fixed by the markup pass before review |
| Critical | C-1 — `row_state._is_locked_fresh` ignored the model's injectable clock | Threaded `now` through `derive()` via `QueueSnapshot.now`; new field on the dataclass |
| Critical | C-2 — `QueueTable.on_mount` + `_ensure_columns` was a brittle double-guard | Dropped `on_mount`; `load()`'s guard is sufficient |
| Should | S-1 — `HelpScreen.action_dismiss` override unnecessary | Removed; `ModalScreen` inherits the right one |
| Should | S-2 — help text said "escape / clear filter" but `action_escape` was a no-op | Trimmed the help text |
| Should | S-3 — duplicate `sys.path` mutation in `row_state.py` | Dropped (`queue_model.py` imported first installs it) |
| Should | S-4 — try/except ValueError around `.index()` | Replaced with `in` check |
| Should | S-5/S-6 — `# type: ignore` smells | Properly typed `_model: QueueModel \| None`, `_filter_mode: FilterMode`, `_sort_mode: SortMode`, `_FILTER_CYCLE: tuple[FilterMode, ...]` |
| Should | S-7 — `head_branch` variable held `target_branch` | Renamed to `branch` |
| May | M-1 — `DEFAULT_CSS` duplicated `styles.tcss` content | Dropped from header / footer / queue / detail; kept on HelpScreen since modal-specific |
| May | M-2 — dead try/except FileNotFoundError + post-read existence check | Collapsed to single existence check |
| May | M-3 — verbose comment on `_sort_key_newest` | Removed |
| May | M-4 — bare `except Exception` around `cursor_row` | Dropped |
| May | M-5 — `sys.path.insert(REPO_ROOT)` unconditional | Moved inside the TUI branch in `bin/adk` |
| Nit | N-2 — chained ternary on `now_fn` default | Refactored to `if now_fn is None: ...` |

Findings N-1 (subsumed by S-5) and N-3 (test cell-reading style) were left as-is.

## Files touched

| File | Change |
|---|---|
| `tui/__init__.py` | NEW (version stub) |
| `tui/app.py` | NEW (~160 LOC) — `AdkApp(App)` + `main()`, 9 bindings, filter/sort cycles, mtime-gated poll loop |
| `tui/styles.tcss` | NEW (~40 lines) — header docks top, footer docks bottom, queue 2fr / detail 1fr split |
| `tui/widgets/__init__.py` | NEW — re-exports |
| `tui/widgets/header_bar.py` | NEW — `HeaderBar(Static, markup=False).update_snapshot(snapshot)` |
| `tui/widgets/queue_table.py` | NEW (~115 LOC) — `QueueTable(DataTable).load(snapshot, *, ascii_only)`, cursor preserved by pr_url, empty-state row, `_format_age` helper |
| `tui/widgets/detail_pane.py` | NEW — `DetailPane(Static, markup=False).show(row)` |
| `tui/widgets/footer_bar.py` | NEW — `FooterBar(Static, markup=False).update_status(filter, sort)` |
| `tui/widgets/help_screen.py` | NEW — `HelpScreen(ModalScreen[None])` |
| `tui/model/__init__.py` | NEW — re-exports |
| `tui/model/queue_model.py` | NEW (~255 LOC) — `QueueModel` + `QueueRow` + `QueueSnapshot` + 5 filter modes + 3 sort modes + mtime-gated `has_changed()`; injectable clock via `now_fn`, surfaced on `QueueSnapshot.now` |
| `tui/model/row_state.py` | NEW (~135 LOC) — `derive(row, *, ascii_only, now)` with 13-state precedence chain |
| `tui/tests/__init__.py` | NEW (pragma marker) |
| `tui/tests/conftest.py` | NEW — `frozen_now` / `fake_queue_path` / `missing_queue_path` / `tui_app` fixtures |
| `tui/tests/fixtures/sample_queue.json5` | NEW — 6-row fixture spanning ready / preparing / merged / failed / locked × GH+BB |
| `tui/tests/test_model.py` | NEW (9 tests) |
| `tui/tests/test_app_launch.py` | NEW (3 Pilot tests) |
| `tui/tests/test_queue_render.py` | NEW (3 Pilot tests) |
| `tui/tests/test_keybindings.py` | NEW (3 Pilot tests) |
| `bin/adk` | Modified — no-args + TUI-only-flag detection → lazy-import `tui.app:main`; `-h` / `--help` short-circuits; `sys.path.insert(REPO_ROOT)` scoped to the TUI branch |
| `skills/adk-cli/scripts/requirements.txt` | Modified — appended `textual>=0.86` |
| `docs/plans/progress/P8.md` | NEW — progress note for the v4 plan |

Total: ~1170 LOC across `tui/` + small surgical edits to `bin/adk` + 1 requirements line + 1 progress doc.

## Files intentionally not touched

- `docs/plans/adk-v4-overhaul.md` — §8 placement of `worker.py` is "skills/adk-cli/scripts/tui/worker.py" but the user chose top-level `tui/`. When sub-phase δ lands, the worker driver will go to `tui/worker.py` and the plan §8 reference will be updated at that point.
- `skills/adk-cli/scripts/auto_run.py:81` — the `_in_quiet_hours` half-open semantics that caused `test_quiet_hours_aborts_inside_window` to fail at hour 23. Pre-existing; out of scope.
- `shared/constitution.md` — §VIII forbids programmatic edits.

## What got skipped (and why)

- **Phase 4 (OSS hardening)** — deferred to a future session per the user's explicit pick of "TUI build" for Session 3.
- **Sub-phases γ through λ of the TUI** — γ (run sync from TUI), δ (run review), ε (progress bars), ζ (multi-select batch), η (add-PR + repo screen), θ (external-worker monitoring), ι (recap modal), κ (agent picker), λ (polish/themes). Multi-session shipping path explicitly agreed; α + β was the e2e slice for today.
- **Session 1 follow-ups** (F-018, F-019, F-021, F-024, F-025, F-028) — not in this session's scope.

## Decisions made this run

| Fork | Choice | Type | Reason |
|---|---|---|---|
| Session 3 first track | Phase 5 (TUI build) | user-answered | Explicit pick over Phase 4 (OSS hardening) / cleanups / release tag. |
| TUI mode | `-i` interactive | user-answered | User wanted to shape style decisions before they landed. |
| TUI scope this session | α + β only, e2e | user-answered | Multi-session shipping path; complete the slice today rather than rush through more sub-phases. |
| TUI directory location | top-level `tui/` | user-answered | "Since this is an app, why not top-level". Departure from v4 plan §8.5's sketch of `skills/adk-cli/scripts/tui/worker.py`. |
| Build approach | 3-agent parallel team with strict file-ownership | user-answered | "Use agentic team to finish it today + ensure highest quality DX". |
| Testing strategy | Textual Pilot via `asyncio.run()` wrappers | inferred | pytest-asyncio not installed; sync wrappers keep tests in the existing pytest invocation pattern. |
| Spec authorship | single binding `SPEC.md` (~13 KB) before fan-out | inferred | Cheapest way to keep three parallel agents from interface-drifting. |
| Spec deviation: `update` rename | accepted Agent A's `update_snapshot` / `update_status` | inferred | Clobbering `Static.update`'s signature was the worse alternative. |
| Markup-eating bug fix | constructor `markup=False`, NOT `update(... markup=...)` | corrected after a smoke failure | First fix attempt used wrong API (`update()` kwarg); constructor-time `markup=False` is the working Textual 8.x pattern. |
| Reviewer findings — apply or punt | apply all Blocker/Critical/Should + most May, punt N-1/N-3 | inferred | "Highest quality DX" + small surgical edits make the ratio worth landing now. |
| Clock injection design | thread `now` through `QueueSnapshot.now`, not a free-standing arg | inferred | Single source of truth for the model's clock; downstream callers (`derive`, `_format_age`) consume it without each needing their own `now_fn`. |

## Evidence (where to look)

- Commit list: `git log --oneline 2e74c91..HEAD` (1 commit).
- Per-commit diff: standard git tooling.
- Test status:
  - `python3 -m pytest tui/tests/ -q` → 18 passed.
  - `python3 -m pytest tui/tests/ skills/adk-cli/scripts/tests/ skills/adk-pr-review/scripts/tests/ -q` → 429 passed, 1 pre-existing failure (`test_quiet_hours_aborts_inside_window`).
- Manual smoke: `python3 /tmp/tui_smoke.py` covered real queue, ASCII mode, missing queue.
- Live launch: `adk` (no args) renders the real `~/.agents-devkit/config/pr-queue.json5` — 10 rows, 7 ready, github+bitbucket.
- Build artifacts:
  - Spec: `.temp/prj-prod-ready/tui-spec/SPEC.md`.
  - Reviewer findings (in this report).
  - Progress note: `docs/plans/progress/P8.md`.
- Session 1 baseline: `SESSION-1-REPORT.md` · Session 2 baseline: `SESSION-2-REPORT.md`.

## Next-best actions (Session 4)

**Recommended order:**

1. **Fix the pre-existing local-clock test** (`test_quiet_hours_aborts_inside_window`). One-line: switch the test to use `1-0` (wrap-around → always inside) and pin a frozen clock; or change `_in_quiet_hours` to treat `b` as inclusive. Removes a flaky red from every test run.
2. **Phase 4 — Open-source hardening** (Session 2's #1 recommendation). README polish, CONTRIBUTING.md, CODE_OF_CONDUCT.md, `.github/ISSUE_TEMPLATE`, CI workflow, `pyproject.toml`. Parallelizable across 3 agents. Prereq for `v4.0.0-rc1`.
3. **TUI sub-phase γ — `s` runs `adk pr-sync` and tails Phase A→E into the log pane**. Needs `pr_sync.py` to write `~/.agents-devkit/tui/workers/sync-plan.json` (the v4 plan §3 sketch; not implemented). Highest visible TUI jump.
4. **TUI sub-phase δ — `r` runs a single PR review**. Worker driver (`tui/worker.py`): claim → spawn agent → heartbeat → release. Sets the seam for ζ (multi-select batch).
5. **SKILL.md / `adk pr-task prepare` workflow cleanup** (Session 2's #3).
6. **Bitbucket MCP signature audit** (Session 2's #4) on `bitbucket.org/lastbrand/ecomm-ssr/pull-requests/5522`.
7. **Phase 7 — Release readiness report + `v4.0.0-rc1` tag** (Session 2's #6).

**User-side actions (independent of next session):**

- `pip install -r skills/adk-cli/scripts/requirements.txt` if you don't have Textual in the active interpreter (system has it via mise already; install only if you switch interpreters).
- Run `adk` against the real queue and try `j/k`, `f`, `S`, `?`, `escape`, `q` to feel the DX.
- Clean stale `terminal-status` PR folders to reclaim disk if Session 1 D-014's ecomm-ssr worktrees haven't been swept yet (~1.85 GB).
