# Adopt-AI Validator

The validator gate this skill MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/adopt-ai-<repo-slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before inspecting the target repo.

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Target is a git repo | `git rev-parse --show-toplevel` succeeds | BLOCKER — ask the user to point at a real repo |
| Write permission | Test-write a tempfile in the target's `.git/` parent | BLOCKER — surface the error verbatim |
| No in-progress merge / rebase | `.git/MERGE_HEAD` and `.git/REBASE_HEAD` absent | BLOCKER — ask the user to finish the merge first |
| Refresh-mode preconditions | If `--refresh`: `ai-guidelines/` exists OR markers found in `AGENTS.md` / `CLAUDE.md` | WARN if neither — fall back to fresh-bootstrap and surface the decision |
| `.gitignore` covers `.temp/` | Host repo's `.gitignore` ignores `.temp/` (or contains a glob that does) | WARN — not blocking; the skill writes to `.temp/` and a file appearing in `git status` would be noisy |

## Phase 2: Mid-flow gates (between workflow phases)

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `repo-inspected` | After Inspect repo, before Detect stack | Evidence summary at `.temp/notes/adopt-ai-<repo-slug>-evidence.md` exists with all sections from `repo-analysis-playbook.md` populated | BLOCKER — finish the inspection |
| `stack-detected` | After Detect stack, before Research | Evidence summary's "Detected stack" section is non-empty | BLOCKER — finish detection |
| `research-done` | After Research targeted external sources, before Plan output tree | `ai-guidelines/research/sources.md` draft has ≥ 1 source per dominant detected stack | WARN if zero sources for a minor stack; BLOCKER if zero for the dominant stack |
| `plan-approved` | After Plan output tree, before Generate `ai-guidelines/` | File tree + skill catalog + hook commands shown to user; explicit approval (or `--auto`) | BLOCKER — wait |
| `merge-plan-clean` (refresh only) | After Plan output tree, before Generate `ai-guidelines/` | Merge diff captured in `.temp/notes/adopt-ai-<repo-slug>-merge-diff.md`; no CONFLICT entries unsigned by the user | BLOCKER if conflicts unaddressed under `preserve-and-merge`; OK under `report-conflicts-only` |

## Phase 3: Pre-handoff validation

Run after the final write but before declaring the run complete.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Every linked file exists | Every Markdown link in the generated tree resolves to a real file | List of broken links (should be empty) |
| Every cross-reference resolves | Every `<path>` mentioned in skill wrappers points at a real `ai-guidelines/` file | Cross-reference map |
| Every command in `scripts-and-commands.md` is real | The command's source (manifest script, task runner target, binary on PATH) exists | Per-command verification table |
| Every hook command runs cleanly on a clean tree | `python3 ai-guidelines/scripts/run_project_checks.py <group> --continue-on-error` exits 0 | Captured stdout/stderr per group |
| Hook configs parse | `.cursor/hooks.json` and `.claude/settings.json` parse as valid JSON | JSON parse result |
| Markers present | Every generated file has `<!-- adk:adopt:start -->` / `<!-- adk:adopt:end -->` (or JSON equivalent) | List of files missing markers (should be empty) |
| Idempotency | Re-running the merge in dry-run mode produces zero diff | Diff summary (should be empty) |

## Phase 4: Post-execution validation

Run after Phase 3 passes; finalize the report.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| File tree matches plan | The actual files written match the planned tree from Phase 2 | File-by-file outcome (NEW / UPDATED / etc.) |
| Skill catalog complete | Every wrapper in `.claude/skills/` and `.cursor/skills/` is present | Catalog listing |
| Hook coverage matches plan | If `wire-hooks` was selected, every planned hook is present in the configs | Hook listing |
| Manual follow-up captured | Any check that emitted WARN or any command flagged "expensive / requires-setup" is in the manual follow-up list | Follow-up list |
| `.temp/reports/adopt-ai-<repo-slug>.md` written | Final report file exists with full content | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish inspection) and re-enter the gate.
- **Phase 2 `plan-approved` BLOCKER (default-ask mode)**: present the plan again with the user's feedback incorporated; loop until approved.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Roll back the writes from this run if possible:
  - For `NEW` files: `rm` them.
  - For `UPDATED` files: revert managed sections to the pre-run snapshot (taken at the start of Phase 3 BEFORE writing).
  - For `APPENDED` sections: remove the appended block.
  - Surface the rollback in the report.
- **Phase 4 partial failure**: Record what's wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner (per `adopt-ai-persona.md`):

- `ADOPT-AI-DRAFT (plan only)` — Phases 1-2 passed; user passed `report-conflicts-only` or aborted before write.
- `AWAITING-APPROVAL-FOR-PLAN` — Phase 2 `plan-approved` is pending user input.
- `ADOPT-AI-BOOTSTRAPPED <n files>` — fresh-bootstrap mode; Phases 1-4 OK; `<n>` files written.
- `ADOPT-AI-REFRESHED <n files>` — refresh mode; Phases 1-4 OK; `<n>` files updated.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/adopt-ai-<repo-slug>-validator.md` for audit. Format:

```
## Phase 1
- Target is a git repo: OK (/Users/me/projects/myrepo)
- Write permission: OK
- No in-progress merge: OK
- Refresh-mode preconditions: N/A (fresh-bootstrap)
- .gitignore covers .temp/: OK

## Phase 2
- repo-inspected: OK (.temp/notes/adopt-ai-myrepo-evidence.md, 14 sections)
- stack-detected: OK (Next.js 14, Express 4, pnpm workspace)
- research-done: OK (3 sources for Next.js, 2 for Express)
- plan-approved: OK (user accepted at 2026-04-21T16:42:11Z)
- merge-plan-clean: N/A (fresh-bootstrap)

## Phase 3
- Every linked file exists: OK (47/47)
- Every cross-reference resolves: OK
- Commands real: OK (12/12 verified)
- Hook commands run on clean tree: OK (format-and-lint OK, typecheck-and-test OK)
- Hook configs parse: OK
- Markers present: OK (24/24 files)
- Idempotency: OK (0 diff in second dry-run pass)

## Phase 4
- File tree matches plan: OK (24/24)
- Skill catalog complete: OK (7/7 + 7/7)
- Hook coverage matches plan: OK
- Manual follow-up captured: 2 items
- Final report: .temp/reports/adopt-ai-myrepo.md
```
