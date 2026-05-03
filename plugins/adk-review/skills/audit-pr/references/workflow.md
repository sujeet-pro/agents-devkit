# `audit-pr` — workflow detail

Detailed phase-by-phase stage list. Logs to `.temp/task-<slug>/validation/per-skill/audit-pr.md`.

## Phase 0 — prompt expand

1. **Resolve PR.** URL, `<owner>/<repo>#<num>`, or bare `#<num>`. If no arg, current branch's open PR.
2. **Locate local checkout** via `~/.config/adk/repos.md`. If not found, `git worktree add .temp/task-<slug>/audit-checkout/ <head-sha>`.
3. **Slug.** Derive from PR title with `audit-` prefix (e.g. `audit-checkout-pr-2841`). Disambiguates from `review-pr` runs.
4. **Mode + checks subset.** Parse `--checks` if set; else default to all 10.

## Phase 1 — preflight

1. **MCP / CLI selection.** Same as `review-pr`: prefer `gh` if both available.
2. **Auth scope check.** `gh api /user`.
3. **Local repo state.** Working tree clean for `--fix`.
4. **Meta-info.** `bin/adk-info github --check` AND `bin/adk-info repos --check`.
5. **Tool detection per `references/check-catalog.md`:**
   - For each check, run `command -v <tool>` to confirm presence.
   - Record which checks will be `executable` vs `N/A (missing tool: <name>; install: <command>)`.

## Phase 2 — fetch context

| Call | Output |
| --- | --- |
| PR metadata | `gh pr view <num> --json title,body,baseRefName,headRefOid,additions,deletions,files,statusCheckRollup` |
| Diff | `gh pr diff <num> --patch` |
| Existing CI status | `gh pr checks <num> --json status,name,conclusion,startedAt,completedAt` |

Surfaced in the audit report (don't re-run what CI already ran; reference its result).

## Phase 3 — fixed-set checks (parallel)

Per `references/check-catalog.md`, run each of the 10 checks. Independent checks run in parallel (max 4 at once).

### Always-run checks

| # | Check | What it does | Tool | Pass condition | Warn | Fail |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | lint-clean | repo-native lint on changed files | `npm run lint` / `golangci-lint` / `ruff` / `cargo clippy` / etc. | 0 errors, 0 warnings | warnings only | errors |
| 2 | typecheck-clean | repo-native type-check | `tsc --noEmit` / `mypy` / `go build` / etc. | 0 errors | (no warn tier) | errors |
| 3 | tests-added | heuristic on test-LOC vs prod-LOC delta | git diff stat | tests-LOC ≥ 0.3 × prod-LOC OR no prod-LOC change | tests-LOC > 0 but < 0.3 × prod-LOC | prod-LOC > 50 AND tests-LOC = 0 |
| 4 | secrets-in-diff | regex + entropy + delegate to security-reviewer agent | regex/entropy + agent | no secrets detected | (no warn tier) | secret detected (any) |
| 5 | license-headers | new source files have repo-required header | `head -n 5 <file>` + repo's license-header pattern | all new source files have header | (no warn tier) | any new source file without header |
| 6 | dep-licenses | new deps have repo-compatible licenses | `npm-license-checker` / `pip-licenses` / `go-licenses` / `cargo-license` | all new deps in allow-list | new dep with `unknown` | new dep with disallowed (e.g. AGPL when repo policy disallows) |
| 7 | doc-updated | behavior change implies CHANGELOG/README touch | heuristic: prod-LOC > 100 AND no CHANGELOG.md / README.md / docs/ change | docs touched OR small change | small change with no docs | large change (>100 LOC) with no docs |

### Conditional checks (run if relevant)

| # | Check | Run when | Tool | Pass | Warn | Fail |
| --- | --- | --- | --- | --- | --- | --- |
| 8 | a11y-regression | UI files touched (extensions: .tsx/.jsx/.vue/.svelte/.html) | `axe-core` (via repo's a11y test); else `pa11y` | 0 a11y violations on touched components | warnings only | errors |
| 9 | perf-regression | hot-path files touched (per `~/.config/adk/datadog.md.slo_thresholds` repo→service mapping) | repo's perf budget script (e.g. `npm run perf-budget`) | within budget | within 10% over budget | >10% over budget |
| 10 | bundle-size | frontend repo with bundle-budget config | `npm run build:bundle-stats` + repo's budget config | within budget | within 5% over budget | >5% over budget |

### Per-check execution

```
for each check in (selected subset):
  spawn parallel subagent:
    - load /adk-review:audit-pr
    - run the check's command
    - capture stdout + stderr + exit code
    - write per-check/<name>.md with: command, exit code, output (truncated to 100 lines), verdict
    - return verdict (Pass / Warn / Fail / N/A)
```

Aggregate verdicts → overall verdict per `references/pass-warn-fail.md`.

## Phase 4 — propose

1. **Show check results.** Per-check verdict table + overall verdict.
2. **Mode branch:**
   - `-i`: walk each `Warn` and `Fail`; ask user how to proceed (suggest fix? Open follow-up? Override?).
   - `--auto`: keep results as-is.
3. **Approval gate** (unless `--auto`): user confirms before any post or fix.

## Phase 5 — report / fix / postback

### Phase 5a — report (no `--fix`, no `--post-comment`)

Write `.temp/task-<slug>/audit/results.md`. Surface verdict + per-check.

### Phase 5b — fix (`--fix` only)

For the safely-fixable subset:

| Check | Fix strategy |
| --- | --- |
| lint-clean | Run the lint tool's auto-fix mode (`npm run lint -- --fix`, `golangci-lint run --fix`, `ruff --fix`, etc.). Re-run the check; expect Pass. |
| license-headers | Prepend the repo-required header (read from `~/.config/adk/review.md.license_header_template` or detect from existing files). Re-run the check; expect Pass. |
| docs-toc | Regenerate the doc TOC (`npm run docs:toc`, `markdown-toc -i`, etc.). Re-run the check; expect Pass. |

For non-fixable checks (tests-added, secrets-in-diff, perf-regression, etc.), do NOT attempt to fix. Surface in the report as "not auto-fixable".

If `--fix` is set AND the user wants to push the fixes:

- PUSH-GATE: ask before the first push (even under `--auto --fix`).
- Push to PR head branch. NEVER `--force`. NEVER protected branches.
- Else: leave dirty for user to commit + push manually.

### Phase 5c — postback (only if `--post-comment`)

Optional. Post a Pass/Warn/Fail summary as a top-level PR comment.

- Use `gh pr comment <num> --body-file <summary>`.
- Apply POST-CONFIRMATION per `/adk-review:review-pr` `references/post-confirmation.md`.
- Capture receipt; write `audit/postback.md`.

DEFAULT IS NOT TO POST. Audit-pr is informational; comment-posting is `review-pr`'s job. The `--post-comment` flag is explicit opt-in for cases where the user wants the audit signal in the PR thread.

## Phase 6 — final report

1. Write `report.md` per `references/output-format.md`.
2. Surface the verdict + per-check counts.
3. Suggest natural follow-up:
   - Verdict `pass` → "ready to merge (per the audit; review-pr separately if depth needed)".
   - Verdict `warn` → "consider the warnings; safe to merge".
   - Verdict `fail` → "address the failures; re-run audit; OR use review-pr for depth".
   - Verdict `mixed` (some N/A) → "audit covered <n>/10 checks; install missing tools (listed) for full coverage".

## Loop control

- **Same check fails 3 times in this session.** Stop and surface (likely a tool config issue).
- **A subagent doesn't return.** Surface as `Inconclusive`; the overall verdict notes it.
- **More than 4 parallel subagents.** Refuse — coordination overhead grows past 4.
- **Repo-native tool times out.** Mark the check as `Inconclusive (timeout)` with the timeout duration. Suggest re-run with `--no-timeout` (if added).

## Key differences from `review-pr`

| Concern | `review-pr` | `audit-pr` |
| --- | --- | --- |
| Verdict model | severity-tiered (B/C/S/M/N/Q) | Pass / Warn / Fail / N/A |
| Depth | semantic / architectural | fixed checklist; no semantics |
| Default post-to-PR | yes (under `--auto`) | NO (use `--post-comment`) |
| `--fix` scope | applies all accepted findings | only safely-fixable subset |
| Speed | thorough; can take minutes | fast; ~1-2 min target |
| Severity overrides | honors `review.md.severity_bar` | honors `review.md.ignore_in_repos[<repo>]` only |
| Reconciliation phase | yes (existing comments) | no (fresh checks every run) |
