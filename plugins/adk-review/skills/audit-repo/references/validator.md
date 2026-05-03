# `audit-repo` — per-phase validator

Run at every phase boundary. Log to `.temp/reports/audit-<slug>-evidence/validator.md`.

## Phase 0 — pre-execution

- [ ] Repo path resolved (arg or CWD walk-up to `.git`).
- [ ] Slug derived: `audit-<repo-name>-<YYYY-MM-DD>`.
- [ ] `.temp/reports/audit-<slug>(-evidence)/` directories created (or prior moved to `.archive/<iso-ts>/` for same-day re-run).
- [ ] Mode parsed (`auto` | `interactive`); incompatible combos refused.
- [ ] `--dimensions <list>` and `--scope <path>` parsed if set.

## Phase 1 — preflight

- [ ] `git rev-parse --is-inside-work-tree` returns true.
- [ ] `bin/adk-info repos --check` returns 0.
- [ ] Tool detection per `references/dimension-passes.md`: each dimension marked `executable` (with tool list) or `partial (some tools missing)` (with install commands).
- [ ] Repo's meta-docs read (`README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `docs/architecture.md`, `docs/adr/`).

## Phase 2 — inventory

- [ ] `inventory.md` written with: languages (LOC), frameworks, dep manager, test framework, lint tool, type-check tool, CI provider, deployment, observability stack.
- [ ] Top-20 largest files captured.
- [ ] Top-20 most-changed files (last 6 months) captured.
- [ ] Repo metadata captured (commit count, contributor count, open PRs, open issues, last release tag).

## Phase 3 — dimension passes

- [ ] All requested dimensions ran (or are explicitly skipped with reason in `<dimension>.md`).
- [ ] Each dimension's repo-native tools ran FIRST (before heuristics); tool output captured.
- [ ] Heuristics ran ONLY where no tool is available or applicable.
- [ ] Each finding has: severity, file:line, dimension, confidence, evidence (≤15 words), issue, impact, recommended action, effort estimate.
- [ ] No untiered findings.
- [ ] No findings without evidence.
- [ ] `~/.config/adk/review.md.severity_bar` overrides applied.
- [ ] `~/.config/adk/review.md.ignore_in_repos[<repo>]` filter applied.
- [ ] Each dimension wrote a "What's healthy in this dimension" sub-section.
- [ ] Each dimension wrote a "Coverage" sub-section (what was checked / NOT checked).
- [ ] Per-dimension files written to `audit-<slug>-evidence/<dimension>.md`.
- [ ] No dimension exceeded its time budget (default: no per-dimension cap; `--time-budget <minutes>` is the global cap).

## Phase 4 — aggregate

- [ ] All findings collated from per-dimension reports.
- [ ] Sorted by severity (Blocker → Critical → Should-Have → May-Have → Nitpick → Question).
- [ ] Within severity, sorted by impact-area breadth.
- [ ] Top-10 selected (or fewer if fewer real findings; **NO PADDING**).
- [ ] Remaining findings grouped per dimension.
- [ ] "What's healthy" section assembled from per-dimension sub-sections; top-5 across dimensions.
- [ ] Recommendations sorted by severity AND effort (low-effort high-impact first).
- [ ] Each recommendation references the appropriate `/adk-code:*` (or other) skill with scope filter.
- [ ] `healthy.md` written.

## Phase 5 — propose

- [ ] Top-10 surfaced to user.
- [ ] Under `-i`: each Top-10 finding walked; user re-tier / discard / merge captured.
- [ ] Under `--auto`: aggregation kept as-is.
- [ ] Approval gate (unless `--auto`): user confirms before writing the full report.

## Phase 6 — write report

- [ ] `audit-<slug>.md` written with all 7 sections:
  - [ ] 1. Executive summary (≤30 lines; verdict-led)
  - [ ] 2. Top-10 (severity-sorted; file-anchored cards)
  - [ ] 3. Per-dimension detail (one section per active dimension)
  - [ ] 4. What's healthy (top 5 across dimensions)
  - [ ] 5. Recommendations (sorted by severity AND effort; each with skill + scope + effort estimate)
  - [ ] 6. Methodology (tools, scope, time, what was/wasn't covered)
  - [ ] 7. Artifact index
- [ ] Length within budget (~600-800 lines target; warn user if >1200).
- [ ] No emojis.
- [ ] No secrets quoted verbatim.
- [ ] No customer data / PII unredacted.
- [ ] Per-finding evidence files written for findings warranting deeper exhibits.

## Phase 7 — pre-handoff

- [ ] Surfaced to user: report path + verdict + Top-3.
- [ ] Suggested follow-ups: each Top-10 finding mapped to a `/adk-code:*` (or other) skill with scope.
- [ ] No remote write happened (assert: zero `gh ` / `git push` / `Edit` / `Write` outside `.temp/reports/`).
- [ ] No file written outside `.temp/reports/audit-<slug>(-evidence)/` (assert).
- [ ] No PR opened, no comment posted, no commit made.
- [ ] Final status banner printed.

## On any check failure

- Log the failure to `validator.md` with the failing check + remediation.
- Block the next phase until the failure is resolved.
- If the same check fails 3 times in this session, stop and surface to the user.
- If a dimension's tool fails (timeout, crash), mark that dimension as `PARTIAL` in methodology; continue with other dimensions.
- If the heuristic-derived "Files NOT touched" or healthy items look wrong, surface in Phase 5 for user verification.

## Invariants

- This skill never modifies code. Read-only.
- This skill never `git push` / `git commit` / `gh pr *`.
- This skill never modifies any artifact written by another skill.
- This skill never modifies `~/.config/adk/*.md`.
- This skill writes ONLY to `.temp/reports/audit-<slug>(-evidence)/`.
- This skill never pads findings to hit Top-10.
- This skill never quotes secrets verbatim.
- This skill never posts publicly.
