# Session 1 — Production-Readiness Pass

Date: 2026-05-21.
Branch: `main`. Start HEAD: `3902989`. End HEAD: `9b91965`.
Tests: **412 passing** (unchanged count throughout — every commit verified green).

## TL;DR

Phases 0–3 of the 7-phase plan complete. Eight clean commits removed 2400+ LOC of dead/duplicate code, brought all docs to v4 layout, added the missing Karpathy framework templates, and tightened narration.md. The big helper consolidation (F-009/F-010) is the only "structural" item deferred to Session 2 — it needs careful test work that wouldn't fit cleanly in the remaining context. Phases 4–7 (open-source hardening / TUI build / real-PR validation / final report) are also Session 2+.

## Risk / Blockers / Follow-ups

- **F-009 / F-010 (helper consolidation)** — deferred. Three parallel `_common.py` files still exist (`skills/adk-pr-review/scripts/_common.py`, `scripts/lib/code_index/_lib_common.py`, `scripts/config_io.py`). The right fix is to hoist shared helpers (get_logger, run, write_json, file_lock, sha256_hex, …) into `scripts/lib/adk_common.py` and shrink the three current files to per-domain helpers + re-export shims. Needs careful test verification at each step.
- **F-012 (slack_helpers → config_io.load_core)** — explored, reverted. `config_io.py` binds `ADK_HOME`/`CORE_YAML` at module import time, which silently breaks tests that monkeypatch `ADK_HOME` after first import. Proper fix is to make `config_io`'s paths dynamic — wider blast radius, deferred. Inline comment added documenting the constraint.
- **D-014 (1.85 GB ecomm-ssr worktree bloat)** — flagged. 7 PR-review folders each carry their own 265 MB worktree of ecomm-ssr. Worktrees ARE cheap (just files, not history), and parallel review needs them, but stale terminal-status PR folders should be swept. Not addressed this session (it's a runtime data concern, not a code concern).
- **D-001 (`~/.agents-devkit/memory/` missing)** — user-side. Will be created next time `install.sh` (re-)runs `bootstrap_user_dir()` (the v4 skeleton includes it).
- **D-007 (3 empty connector frontmatters: atlassian / bitbucket / github)** — user-side. `/adk-setup --init` will scaffold them.

## What got done — by phase

### Phase 0 — Stabilize WIP (2 commits)

| Commit | Subject |
|---|---|
| `d0efd6d` | chore(v4): drop migration scaffolding now that v4 layout is canonical |
| `a7de9aa` | refactor(v4): simplify post-migration code paths + rename `adk auto` → `pr-review-all` |

40+ in-flight files committed as two logical chunks. Migration code removed (no longer needed); post-v4 code paths simplified.

### Phase 1 — Parallel discovery (3 forked agents, 0 commits)

Three audit reports written under `.temp/prj-prod-ready/`:
- `phase1a-consolidation-worksheet.md` — 28 findings: 6 BLOCKER, 10 HIGH, 8 MEDIUM, 3 LOW.
- `phase1b-karpathy-gaps.md` — coverage matrix vs `.temp/x.md`: 19 covered, 4 partial, 3 gap, 0 conflicts. 3 minimal patches proposed.
- `phase1c-data-folder-drift.md` — 14 drift items vs `shared/paths.md` v4 spec. 6 concrete cleanup commands.

### Phase 2 — Consolidation (6 commits)

| Commit | Subject | Findings cleared |
|---|---|---|
| `bb08971` | chore: drop ghost adk-pr-reviews references + refresh llms.txt for v4 | F-001, F-002 |
| `6dbd209` | chore: delete orphan / dead-code targets surfaced by Phase 1A | F-005, F-006, F-007, F-008, F-013, F-014, F-020 |
| `a6b57fd` | fix(v4): delete dead adk_info.py + rename enrich_overrides.py → enrich_metadata.py | F-003, F-004 |
| `5f8aa11` | docs: v3→v4 path sweep across SKILL.md / shared / README / SETUP / AGENTS | F-015, F-016, F-027 |
| `b12acda` | cleanup: empty-skill-dirs, install_tui SUPPORTED dedup, paths.md v4 doc | F-017, F-022, F-023, D-002, D-003, D-004, D-010 |
| `b1a5a32` | refactor(cli): repo.py imports _now_iso/_parse_iso from queue_io (F-011) | F-011 |

**Deleted (8 entries):**
- `skills/build/` (orphan category-router skill — 13 files)
- `scripts/migrate_v2_to_v3.py` (v2→v3 migration; v4 dropped overrides.yaml entirely)
- `scripts/adk_narrate.py` (listed in narration.md as option 2 but no skill used it)
- `scripts/sync-to-personal.sh` (author-private tooling)
- `scripts/adk_info.py` (read from dead overrides.yaml)
- `docs/reference/scripts/{adk_info,enrich_overrides,migrate_v2_to_v3,adk_narrate}.md` (autogen docs for deleted scripts)
- 8 empty `skills/adk-*/scripts/` dirs + 4 empty `skills/adk-*/references/` dirs

**Renamed:**
- `scripts/enrich_overrides.py` → `scripts/enrich_metadata.py` (matches what it actually does)

**v3→v4 path/reference sweep across 33 files:**
- `~/.agents-devkit/pr-reviews/` → `~/.agents-devkit/skill-pr-review/`
- `~/.agents-devkit/config/overrides.yaml` (general) → `~/.agents-devkit/config/core.yaml`
- `overrides.yaml.defaults.*` → `core.yaml.defaults.*`
- `overrides.yaml.repos[*]` → `repos.md` frontmatter `repos[*]`
- `overrides.yaml.data_sources.<src>.pii_columns` → `connectors/<src>.md` frontmatter `pii_columns`
- Preserved: `<repo>/.adk/overrides.yaml` (repo-local override file — name unchanged in v4).

**Code consolidations:**
- `install_tui.py` no longer duplicates `SUPPORTED = [...]` — reads `install.SUPPORTED` via a new `supported_targets(repo_root)` helper.
- `repo.py` imports `_now_iso` / `_parse_iso` from `queue_io` instead of redeclaring them locally.
- `hooks/banner.sh` v3→v4: checks `core.yaml` not `overrides.yaml`; tagline retagged to v4; skill list updated to current 9 slash skills.
- `hooks/hooks.json` v3→v4: post-write secret-detection regex now matches `core.yaml` + `connectors/*.md` frontmatter + `adk-cli.json5`.

**Spec updates in `shared/paths.md`:**
- Documented `config/adk-cli.json5` (CLI behavior knobs).
- Documented top-level `logs/` for CLI command output.
- Documented `skill-setup/auto-runs/<ts>/` subfolder pattern.
- Spelled out the `<repo>_pr-<n>/{code, code-index, docs, state.json, review.log, .adk-pr-lock, pr-review/{...}}` split for PR-review artifacts.
- Added `pr-queue.json5.lock`, `improve/learning/summary.md`, `improve/metadata/archive/<ts>/` to the documented skeleton.

### Phase 3 — Karpathy patches (1 commit)

| Commit | Subject | Patches |
|---|---|---|
| `9b91965` | docs: apply Karpathy framework patches (Phase 1B P-002/P-003/P-004) | P-002, P-003, P-004 |

- **P-002** — `shared/narration.md` end-of-run summary template gains "Files touched" and "Files intentionally not touched" sections (x.md §S4 transparency).
- **P-003** — new `shared/templates/MEMORY.md.template` + `shared/templates/ERRORS.md.template` for per-project drop-in (x.md §6).
- **P-004** — `AGENTS.md` §3a documents sub-agent inheritance: what propagates (constitution / narration / decision-log / shared-state gate / project context) and what doesn't (parent's tool list / scope) when a skill spawns a child agent (x.md §7).
- `AGENTS.md` §1.2a pointer added so MEMORY.md/ERRORS.md are loaded if present.

## Files touched

Eight commits, 60+ files. Highlights:
- `install.py` · drop NON_SLASH_SKILLS ghost, remove 3 stale comment blocks, update final-step message
- `install_tui.py` · dedup SUPPORTED, route through install.SUPPORTED
- `bin/adk` · (Phase 0) `adk auto` → `adk pr-review-all`
- `llms.txt` · full v4 refresh
- `hooks/{banner.sh,hooks.json}` · v3→v4
- `scripts/enrich_metadata.py` (renamed from enrich_overrides.py)
- `scripts/metadata_introspector.py` · call new name
- `scripts/config_io.py` (Phase 0 only)
- `skills/adk-cli/scripts/{repo,slack_helpers}.py` · dedup, doc comment
- `skills/adk-cli/scripts/queue_io.py` (Phase 0)
- `skills/adk-pr-review/scripts/*.py` (Phase 0)
- All 10 `skills/*/SKILL.md` (v4 path sweep)
- `shared/{paths.md,narration.md,advisor.md,question-first.md,decision-log-schema.md}`
- `shared/guidelines/{data-modeling,frontend-design,observability,prompt-handling}.md`
- `shared/personas/{context-gatherer,implementer,investigator}.md`
- `shared/workflows/{phase-0-context-gather,phase-1-advise}.md`
- `shared/templates/{MEMORY,ERRORS}.md.template` (new)
- `AGENTS.md`, `README.md`, `SETUP.md`

## Files intentionally not touched

- `shared/constitution.md` — §VIII forbids programmatic edits.
- `docs/plans/**.md` and `docs/plans/progress/*.md` — historical planning docs; v3 references preserved as a record of when migrations happened.
- `docs/reference/scripts/*.md` — autogen reference docs; will refresh when the regenerator runs.
- `agents-codex/codex-config.toml.append` — already long gone (only references in install.py comments remained).
- `~/.agents-devkit/` user data folder — read-only audit only (per Phase 1C prompt).
- Test files in `skills/*/scripts/tests/` — no code-shape change required them.

## What got skipped (and why)

- **F-009 / F-010 (big helper consolidation)** — defer to Session 2; needs careful test verification at each helper extraction step.
- **F-012 (slack_helpers → config_io)** — proper fix needs config_io paths to be dynamic; cross-cutting test impact. Documented inline comment instead.
- **F-018 (present_only env-var helper)** — depends on F-009 (the shared adk_common module).
- **F-019 (doctor.py uses ensure_ollama helpers)** — minor; defer.
- **F-021 (rewrite scripts/verify_repo.py for v4 + CI gate)** — fits naturally in Phase 4 (open-source hardening).
- **F-024 (audit agents-codex/junie READMEs)** — fits in Phase 4.
- **F-025 (decision_logger.py coverage)** — analysis question; deferred.
- **F-028 (query_index.py vs query.py)** — needs read-and-decide; deferred.
- **D-005 (suspicious pr-queue.json5.lock content)** — user-side investigation; documented for next session.
- **D-006, D-007 (improve/metadata empty, 3 connectors empty frontmatter)** — both fixed by user-side `/adk-setup --init` + `--enrich`.
- **D-008, D-009, D-014 (repo cleanup, worktree bloat)** — runtime data concerns, not code concerns.

## Decisions made this run

| Fork | Choice | Type | Reason |
|---|---|---|---|
| Scope | "Tackle Phases 0–3 this session; defer 4–7" | inferred | Realistic for context budget; each phase is independently shippable. |
| WIP handling | Split 40+ in-flight files into 2 logical commits | user-answered | Cleanest history per user's pick. |
| Test target | Real PRs in the queue (Phase 6, not yet reached) | user-answered | User's pick. |
| F-009 / F-010 deferral | Skip the big helper hoist this session | inferred | High risk; needs careful test work that doesn't fit cleanly in remaining context. |
| F-012 revert | Keep slack_helpers's direct read; document the constraint | inferred | Tests broke; root cause is config_io's import-time path binding; proper fix is broader. |
| F-008 disposal | Delete skills/build/ outright (vs preserving for future) | inferred | Phase 1A confidence was high; routing-table check confirmed no callers. |
| Connector-only sweep | Run sed across all SKILL.md / shared/ files at once | inferred | Substitutions were mechanical; one bulk pass + spot-fix safer than per-file edits. |

## Evidence (where to look)

- Audit reports: `.temp/prj-prod-ready/phase1{a,b,c}-*.md`.
- Commit list: `git log --oneline a7de9aa..9b91965` (or `git log --oneline 3902989..HEAD`).
- Test status: `python3 -m pytest skills/adk-cli/scripts/tests/ skills/adk-pr-review/scripts/tests/ -q` → 412 passed.
- Per-commit diff: standard git tooling.

## Next-best actions (Session 2)

**Recommended order:**

1. **Phase 5 — TUI build** *(if you want momentum)* — Layered textual TUI with three tabs (setup wizard / queue dashboard / skill runner). Quick visible win; doesn't depend on the helper consolidation.

2. **Phase 6 — Real-PR validation** *(highest user-visible value)* — Pick a non-terminal row from your queue, run `/adk-pr-review --verbose -i`, capture issues, fix. One round of `/adk-sync` round-trip against a sandbox doc.

3. **Phase 2 continuation** — F-009 (hoist shared helpers to `scripts/lib/adk_common.py`), F-010 (repo.py uses `_common` path helpers). Best done as a single careful refactor pass with test verification after each helper move.

4. **Phase 4 — Open-source hardening** — README polish, CONTRIBUTING.md, CODE_OF_CONDUCT.md, .github/ISSUE_TEMPLATE, CI workflow, pyproject.toml. Parallelizable across 3 agents.

5. **Phase 7 — Release readiness report + v4.0.0-rc1 tag**.

**User-side actions (independent of next session):**
- Run `./install.sh` to refresh hooks (banner.sh + hooks.json now v4) and recreate `~/.agents-devkit/memory/`.
- Run `/adk-setup --init` to scaffold missing connector frontmatters (atlassian, bitbucket, github).
- Optionally run `/adk-setup --enrich` to populate `improve/metadata/<source>.json`.
- Optionally drop a `MEMORY.md` / `ERRORS.md` (from `shared/templates/`) into a working repo to try the per-project context feature.
