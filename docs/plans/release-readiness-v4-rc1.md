# Release readiness — v4.0.0-rc1

Scope: bring the repo to a state where an external contributor can open it cold, understand it, install it, run the test suite, find a contribution guide, file an issue against a template, and watch CI gate every PR. Then tag `v4.0.0-rc1`.

These were Session 2's "Phase 4 — OSS hardening" and "Phase 7 — Release readiness report + tag" recommendations, deferred until P8 (TUI) shipped. P8 is now complete (commit `9798375`); this is the next track.

## Current state (2026-05-22)

Already in repo:
- `README.md` — 336 lines, dense, covers install + skills + supported agents.
- `LICENSE` — MIT, dated 2026.
- `SETUP.md` — install + env-var prereqs.
- `.github/workflows/docs.yml` — docs build workflow.
- `.github/workflows/version-bump.yml` — version-bump automation.
- `install.sh` / `install.py` — primary install path.
- `571` tests passing across `tui/`, `skills/adk-cli/scripts/`, `skills/adk-pr-review/scripts/`.

Missing for OSS-ready:
- `CONTRIBUTING.md` — no contributor guide.
- `CODE_OF_CONDUCT.md` — no community covenant.
- `.github/ISSUE_TEMPLATE/` — no bug/feature templates.
- `.github/PULL_REQUEST_TEMPLATE.md` — no PR template.
- `.github/workflows/test.yml` — CI does not currently run the test suite on PRs.
- `pyproject.toml` — no Python package metadata.
- `CHANGELOG.md` — no release-notes file.
- Screenshot / GIF demo of the TUI in the README.
- `SECURITY.md` — vulnerability-reporting policy.
- A badges row at the top of the README (CI status, license, Python version).

## Plan — 5 tracks, mostly parallel

### Track A — README polish (1-2 hours)

Goals:
1. Add a badges row at the top: CI status (once test.yml lands), license, Python ≥ 3.12.
2. Add an embedded `.gif` / asciicast of the TUI in action (`adk` no-args → press `r` on a queued PR → recap modal). Lives at `docs/assets/tui-demo.gif`.
3. Reorder for a fresh-reader: TL;DR (2-3 sentences) → install → `/adk-*` skill list → the TUI → architecture → contributing.
4. Cross-link to `SETUP.md`, `CONTRIBUTING.md` (when it lands), `docs/plans/adk-v4-overhaul.md`, `docs/plans/progress/P8.md` (TUI), and the `docs/plans/archive/session-4/` history.

Files: `README.md` (rewrite), `docs/assets/tui-demo.gif` (new).

### Track B — Community files (30 min)

Goals:
1. `CONTRIBUTING.md` — covers: dev setup (`./install.sh`, then `pytest`), branch naming, commit message style (look at `git log --oneline -20` for the de facto style), code review expectations, the constitution + decision-log rules, the question-first contract.
2. `CODE_OF_CONDUCT.md` — Contributor Covenant 2.1 verbatim; enforcement contact set to the repo owner (`sujeet@onequince.com`).
3. `SECURITY.md` — pin a contact email; reference §VII of `shared/constitution.md` for the credential-safety posture.

Files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md` (all new, root-level).

### Track C — GitHub templates (15 min)

Goals:
1. `.github/ISSUE_TEMPLATE/bug.yml` — structured: skill (`/adk-*` dropdown), expected, actual, repro steps, environment (`./install.sh --check` output).
2. `.github/ISSUE_TEMPLATE/feature.yml` — short: motivation, proposed change, alternatives considered.
3. `.github/ISSUE_TEMPLATE/config.yml` — link to GH Discussions for Q&A; block bare-empty issues.
4. `.github/PULL_REQUEST_TEMPLATE.md` — summary / test plan / Co-Authored-By note + the constitution-§I checklist (no force-push, no merge-protected-branch, no shared-state writes without confirmation).

Files: 4 new files under `.github/`.

### Track D — CI test workflow (30 min)

Goals:
1. `.github/workflows/test.yml` — pytest on push/PR. Matrix on `ubuntu-latest` × Python 3.12 only (the repo's known-good interpreter). Cache pip + pytest. Install repo's existing requirements (`skills/adk-cli/scripts/requirements.txt`, `skills/adk-pr-review/scripts/requirements.txt`). Skip Pilot-tests on CI if Textual's Pilot dev-requirement isn't available (or pin it).
2. Add a status badge to the README once green.
3. Consider keeping `docs.yml` + `version-bump.yml` untouched.

Files: `.github/workflows/test.yml` (new), `README.md` (badge addition).

### Track E — Package metadata + changelog (30 min)

Goals:
1. `pyproject.toml` — declare `name = "adk-agents-devkit"`, `version = "4.0.0rc1"`, `requires-python = ">=3.12"`, the runtime deps (textual ≥ 0.86 + whatever else `requirements.txt` lists). This makes the repo `pip install -e .`-able even if we never publish to PyPI.
2. `CHANGELOG.md` — Keep-a-Changelog format. Backfill the 25 commits since `e4b4bd3` (Session 4) as one "v4.0.0-rc1" entry under three headings: TUI (α–λ), CLI install (statusline), tests (1 fix). Older sessions get one-line "v3.x → v4 migration" rollup at the bottom.
3. Pin the v4.0.0-rc1 tag at the end (Track F).

Files: `pyproject.toml` (new), `CHANGELOG.md` (new).

### Track F — Release tag (5 min, after A–E green)

Goals:
1. Verify: `pytest` green, `./install.sh --check` clean, README renders on GH, ISSUE_TEMPLATE shows up in GH UI.
2. Annotate the tag: `git tag -a v4.0.0-rc1 -m "v4.0.0-rc1 — first release candidate"`.
3. Push the tag: `git push origin v4.0.0-rc1` (after explicit confirmation per constitution §I.4).
4. Draft a GH Release with the relevant CHANGELOG section + a TUI demo gif.

## Order of operations

Recommended sequence (some tracks are parallel-safe):

```
1. Track B + Track C            (parallel, low risk; no code dependencies)
2. Track D                      (CI gate ready before opening up)
3. Track A README polish        (use Track D's badge URL)
4. Track E pyproject + CHANGELOG
5. Track F tag                  (after `git status` clean + tests green + user confirmation)
```

A single agent can sweep through 1–5 in ~3-4 hours; or fan out tracks B, C, D to parallel implementer agents (B and C don't touch the same files; D is on its own).

## Acceptance — done when…

- A GitHub stranger can clone, run `./install.sh`, run `pytest`, and have a passing build.
- A first-time contributor can open `CONTRIBUTING.md` and know which test to run for their change.
- A bug report includes (via the issue template) the agent name, skill name, and the `--check` output without us asking.
- CI red-flags a regression on every PR (test.yml).
- `git tag` shows `v4.0.0-rc1` and the tag is pushed to origin (last step, gated).

## Out of scope (defer to v4.0.0 GA)

- PyPI publishing (the install path stays `./install.sh`; pyproject is for `pip install -e .` dev convenience).
- Homebrew formula.
- A separate `adk` Python entry point (`bin/adk` already exists as a shell shim).
- A multi-OS CI matrix — keep Linux only for rc1.
- A `docs/site/` static site (the existing `docs.yml` workflow can stay; we'll iterate on it later).

## Follow-ups already tracked in P8.md

- Stabilise `test_batch_run.py` flake (the next concrete code task — see `docs/plans/progress/P8.md` § Next steps).
- η-M-2: `RepoScreen._spawn_subprocess` truncates multi-line errors.
- θ-S-1: SIGTERM can't cancel in-flight `_run_streamed` subprocess inside the worker.
- κ-S-1: `action_pick_agent` race window (shared with η's `action_add_pr`).
- ι: single-`r` doesn't push a recap; long error messages get clipped in the recap modal.

These don't block rc1, but should land before v4.0.0 GA.
