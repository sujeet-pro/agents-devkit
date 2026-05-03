# `review-code-changes` — per-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/review-code-changes.md`.

## Phase 0 — pre-execution

- [ ] In a git repo (CWD walk found `.git`).
- [ ] Branch resolved (or `detached-<sha>` if HEAD is detached).
- [ ] Baseline resolved per documented order (`@{upstream}` → `origin/<branch>` → `main` → `master` → first-parent → `<arg>`); source recorded.
- [ ] Slug derived from branch.
- [ ] `.temp/task-<slug>/` created.
- [ ] `prompt.txt` written (verbatim user prompt + ISO ts + repo + branch + baseline + source).
- [ ] Mode parsed (`auto` | `interactive` | + `fix`); incompatible combos refused.

## Phase 1 — preflight

- [ ] `git status --porcelain` captured.
- [ ] For `--fix`: working tree is writeable.
- [ ] `bin/adk-info repos --check` returned 0.
- [ ] `bin/adk-info review --check` returned 0.
- [ ] Repo conventions read from `AGENTS.md` / `CLAUDE.md` / `.cursorrules` if present; written to `repo-conventions.md`.
- [ ] Cheap lint pre-pass attempted (or skipped with reason); output captured to `lint-output.txt` if ran.

## Phase 2 — gather scope

- [ ] Branch-vs-baseline diff captured: `git diff <baseline>...HEAD --name-status` and full diff.
- [ ] Staged captured: `git diff --cached`.
- [ ] Unstaged captured: `git diff`.
- [ ] Untracked listed: `git ls-files --others --exclude-standard`; full content of each read.
- [ ] Unified scope map built; each file tagged with kind ∈ {branch, staged, unstaged, untracked}.
- [ ] `--scope <path>` filter applied if provided.
- [ ] Each in-scope file's mtime recorded at `mtime_t0`.
- [ ] `scope.md` written with per-source counts + file table.

## Phase 3 — full-scope review

- [ ] All requested dimension passes ran (or are explicitly skipped with reason).
- [ ] Each finding has: severity, file:line, scope source, dimension, confidence, evidence (≤15 words), issue, fix, impact.
- [ ] No untiered findings.
- [ ] No findings without evidence.
- [ ] `~/.config/adk/review.md.severity_bar` overrides applied.
- [ ] `~/.config/adk/review.md.ignore_in_repos[<repo>]` filter applied.
- [ ] Same-root-cause de-noise applied.
- [ ] Each finding tagged with its scope source (branch / staged / unstaged / untracked).
- [ ] mtime check at phase end: any in-scope file with `mtime > mtime_t0` flagged as `dirty_during_review`; affected findings annotated.
- [ ] `raw-findings.md` written.

## Phase 4 — propose

- [ ] `findings.md` exists, severity-sorted (Blocker first), scope-source-tagged.
- [ ] Under `-i`: walked every finding; recorded each user decision.
- [ ] Under `--auto`: all validated findings kept.
- [ ] Approval gate (unless `--auto`): user said "show full report?".

## Phase 5a — report (no `--fix`)

- [ ] `findings.md` final.
- [ ] Next-step suggestion present in `report.md`.
- [ ] No remote calls in the session log.

## Phase 5b — fix (`--fix` mode)

- [ ] Fix queue built (accepted findings, severity-prioritized).
- [ ] For each fix: applied (inline or via `/adk-code:code-bugfix`).
- [ ] Repo-native validation ran after each fix (or once at end if scope is small): tests + typecheck + lint.
- [ ] **NO `git push`** in the session log (assert).
- [ ] **NO `gh pr create` / `gh pr edit` / `gh pr merge` / `gh pr comment`** in the session log (assert).
- [ ] **NO `git commit`** automatically (working tree left dirty).
- [ ] If validation failed mid-queue: stopped applying further fixes; surfaced.
- [ ] `fix-log.md` written.

## Phase 6 — pre-handoff

- [ ] `report.md` covers: Result, Repo snapshot, Findings, Per-source breakdown, Decisions, Fix log (if --fix), Validation, Next step, Artifact index.
- [ ] Every artifact referenced in `report.md` actually exists at the cited path.
- [ ] No remote write happened (assert: zero `gh ` / `git push` / `git fetch` / MCP calls in the session log).
- [ ] No file written outside `.temp/task-<slug>/` UNLESS `--fix` was set (in which case writes to the working tree are expected).
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validation/per-skill/review-code-changes.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, stop and surface to the user.
- If `--fix` validation fails, stop applying further fixes — do NOT try to "fix the fix".
