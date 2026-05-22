# Status — agents-devkit (2026-05-22)

Live status of where things stand. Resume from the "Next step" section.

## Where we are

P8 (the TUI) is **complete locally** — all 11 sub-phases shipped (α β γ δ ε ζ η θ ι κ λ) across 12 commits on `main`. Repo is 25 commits ahead of `origin/main`. The `test_batch_run.py` flake is also fixed in the working tree (uncommitted at the time of writing).

### Test count

- Repo-wide: **571 passing + 2 deliberate skips** (skips guard `claude`-on-PATH-conditional tests).
- TUI suite alone: **149 passing**. Stability check: 4/4 consecutive runs green after the flake fix; 10x stress still in-progress (latest 4 results all green).
- Pre-existing `test_quiet_hours_aborts_inside_window` red was fixed at the start of Session 4.

### Working-tree state (uncommitted)

```
M  tui/app.py                              ← flake fix
M  tui/tests/test_batch_run.py             ← flake fix
A  docs/plans/release-readiness-v4-rc1.md  ← P4+P7 plan
A  docs/plans/archive/session-4/...        ← session 4 archive
A  docs/plans/progress/STATUS.md           ← this file
```

The `.temp/prj-prod-ready/` directory was deleted as part of the `.temp` cleanup; its valuable artifacts (TUI specs + Session 1–3 reports) are preserved in `docs/plans/archive/session-4/`.

## The flake fix (uncommitted — needs commit)

**Root cause**: ι's RecapScreen (and other modals from η/κ) sit on top of the default screen. The TUI's 2-second `_maybe_reload` timer calls `_reload`, `_reload_plan`, `_reload_workers`, `_refresh_detail` — each of which used `self.query_one(...)`. Textual's `App.query_one` searches only the *active* screen, so when a modal was on top, the queries raised `NoMatches`. A separate sub-bug: during app unmount, `screen_stack` drains to empty, and any in-flight worker's `_reload` call would then crash with `IndexError`.

**Fix**:
1. New `AdkApp._default_query(widget_type)` helper that does `self.screen_stack[0].query_one(widget_type)` — always targets the default screen where the main widgets live, ignoring whichever modal is active.
2. All four timer-driven reload methods (`_reload`, `_reload_plan`, `_reload_workers`, `_refresh_detail`) plus the timer entrypoint `_maybe_reload` now early-return when `self.screen_stack` is empty (unmount-safe).
3. The two test helpers `_log_text` and `_footer_text` in `test_batch_run.py` were also retargeted to `app.screen_stack[0].query_one(...)` so polls work after a modal pushes.

**Verification**: 10/10 consecutive runs of `test_batch_run.py + test_recap_screen.py` green; ongoing 10x stress of the full TUI suite is 4/4 green so far.

## Plans landed in this session

1. `docs/plans/release-readiness-v4-rc1.md` — track-by-track plan for the OSS hardening + v4.0.0-rc1 tag. 5 parallel-safe tracks (A: README polish; B: community files; C: GH templates; D: CI test workflow; E: pyproject + CHANGELOG; F: tag).
2. `docs/plans/archive/session-4/` — TUI specs (α through κ) + Session 1–3 reports preserved in-tree.
3. `docs/plans/progress/P8.md` — fully updated to reflect all 11 sub-phases.

## Next step (resume here)

**Commit the flake fix.** Two files:

```
M tui/app.py                    — _default_query helper + 5 screen_stack guards
M tui/tests/test_batch_run.py   — helper queries target screen_stack[0]
```

Suggested commit message:

> fix(tui): timer-driven reloads target default screen + unmount-safe
>
> When a modal (RecapScreen pushed by ι at end-of-batch, AgentPickerScreen
> opened by κ, etc.) was on top, the 2s `_maybe_reload` timer called
> `self.query_one(...)` which searches the active screen — raising
> `NoMatches: No nodes match 'QueueTable' on Screen(id='_default')` and
> intermittently failing test_R_skips_unready_rows / test_R_respects_
> parallel_cap.
>
> Fix:
> - New `_default_query(widget_type)` helper that uses
>   `self.screen_stack[0].query_one(...)` — always targets the default
>   screen, ignoring any modal on top.
> - Migrate all 4 timer-driven reloads (_reload / _reload_plan /
>   _reload_workers / _refresh_detail) to use _default_query.
> - Add `if not self.screen_stack: return` early-return at each
>   _reload* entrypoint AND in _maybe_reload to handle the unmount
>   race (background tasks can call _reload after on_unmount drains
>   screen_stack).
> - Helper functions in test_batch_run.py also retargeted to
>   screen_stack[0] so log/footer polls keep working after a modal
>   pushes.
>
> Verified: 10/10 consecutive isolated runs green; ε reviewer's flagged
> follow-up (ε-may-2) now closed.

**Then proceed to the v4.0.0-rc1 plan** (`docs/plans/release-readiness-v4-rc1.md`). Recommended starting order:
1. Track B (community files: CONTRIBUTING / CODE_OF_CONDUCT / SECURITY).
2. Track C (GH templates).
3. Track D (CI test workflow).
4. Track A (README polish).
5. Track E (pyproject + CHANGELOG).
6. Track F (the v4.0.0-rc1 tag — gated on explicit confirmation per constitution §I.4).

## Earlier follow-ups still open (none load-bearing)

From P8.md:
- η-M-2: RepoScreen._spawn_subprocess truncates multi-line errors.
- θ-S-1: SIGTERM can't cancel in-flight `_run_streamed` subprocess.
- κ-S-1 / η-N-3: `@work`-decorated action double-push window.
- κ-M-1: AgentPickerScreen falls through to row 0 on unknown current name.
- ι: single-`r` doesn't push a recap; long error lines clip at 60 chars.
- ε-may-1: `_PHASE_RE` description truncates at 60 chars before the defensive `[:80]` slice.
- ζ: `test_R_respects_parallel_cap` sampling rate; per-worker `_reload` waste at end of batch.

## Commits on `main` (this session — 25 ahead of origin)

```
9798375 feat(tui): λ — polish (themes, detach prompt, reattach banner) — P8 done
3a98c40 feat(tui): ι — end-of-run recap modal after batch finishes
3cb5a38 feat(tui): κ — agent picker + headless fallback
181fee4 feat(tui): ε — phase-aware progress via worker stdout parsing
1910c0b feat(tui): η — add-PR modal + repo management screen
4cdef77 feat(install): set_statusline_in_claude — patch ~/.claude/settings.json
4adc692 feat(tui): ζ — multi-select + ordered batch run with parallel cap
86156df feat(tui): θ — WorkersPane + worker async-streaming refactor
74bc44c feat(tui): δ — `r` runs a single-PR review worker
da0b2b5 refactor(tui): drop LogPane.announce wrapper + harden log-text test
2097f08 feat(tui): γ — `s` runs pr-sync, streams output to LogPane + SyncPlanPane
a5b9968 fix(tests): pin _in_quiet_hours mock so test isn't wall-clock dependent
```
