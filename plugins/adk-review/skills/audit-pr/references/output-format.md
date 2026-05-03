# `audit-pr` — output format

## Per-turn status (each turn opens with this)

```
[adk-review:audit-pr] task=<slug> pr=<repo>#<num> phase=<0|1|2|3|4|5|6> mode=<auto|interactive>[+fix] mcp=<github-docker|gh-cli> checks=<n-of-10> verdict=<pending|pass|warn|fail|mixed>
```

## Final report

Written to `.temp/task-<slug>/report.md`:

```markdown
# audit-pr report — <slug>

## Result
<one sentence — overall verdict + actionable next step>

## PR snapshot
- Repo: <owner>/<repo>
- PR: #<num> — <title>
- Head SHA: <sha>
- Files changed: +<add>/-<del> across <n> files
- Existing CI: <green|yellow|red>

## Verdict
**Overall: <PASS | WARN | FAIL | MIXED>**

| # | Check | Verdict | Notes |
| --- | --- | --- | --- |
| 1 | lint-clean | PASS | 0 errors, 0 warnings |
| 2 | typecheck-clean | PASS | 0 errors |
| 3 | tests-added | PASS | tests-LOC=44 vs prod-LOC=80; ratio 0.55 |
| 4 | secrets-in-diff | PASS | no secrets detected |
| 5 | license-headers | PASS | 3 new .tsx files all have header |
| 6 | dep-licenses | PASS | no new deps |
| 7 | doc-updated | PASS | small change |
| 8 | a11y-regression | PASS | 0 violations on touched components |
| 9 | perf-regression | N/A | no hot-path files touched |
| 10 | bundle-size | PASS | within budget (delta +1.2KB; budget +5KB) |

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | mcp client | gh-cli | both available; gh has faster cold start |
| 0 | checks subset | all 10 | default; no --checks override |
| 1 | tool detection | all present | npm, tsc, eslint, axe-core, npm-license-checker, markdown-toc |
| 3 | parallel groups | 4 at a time | dispatcher rule |
| 5 | comment posting | NO | no --post-comment flag |

## --fix log (when --fix was set)
| Check | Fix applied | Validation |
| --- | --- | --- |
| lint-clean (was WARN) | npm run lint -- --fix | re-run lint: 0 warnings (PASS) |

## Validation evidence
- Local checkout: <path> (head=<sha>)
- MCP health: <github-docker|gh-cli> reachable
- Tool versions: node v22.7, eslint 9.x, tsc 5.x, axe-core 4.x

## Residual risk / follow-ups
<bulleted list, prioritized>
- (empty when overall is PASS)
- For Warns / Fails / N/As, list with the suggested next skill (`/adk-code:code-test`, `/adk-docs:docs-changelog`, install command, etc.)

## Artifact index
.temp/task-<slug>/
  prompt.txt              verbatim user prompt + ISO ts
  audit/
    results.md            verdict + per-check table
    per-check/
      lint-clean.md
      typecheck-clean.md
      ... (one per check)
    fix-log.md            (--fix only) per-fix evidence
    postback.md           (if --post-comment) PR comment receipt
  validation/
    per-skill/audit-pr.md
  report.md               this file
```

## `results.md` shape

```markdown
# audit-pr results — <slug>

## Overall verdict: <PASS | WARN | FAIL | MIXED>

## Per-check
| # | Check | Verdict | Tool | Time | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | lint-clean | PASS | eslint 9.x | 8s | 0 errors, 0 warnings |
| 2 | typecheck-clean | PASS | tsc 5.x | 14s | 0 errors |
| ... |

## Verdict counts
- PASS: 9
- WARN: 0
- FAIL: 0
- N/A: 1

## Total time: 42s (parallelized; serial would have been ~120s)
```

## `per-check/<name>.md` shape

```markdown
# <check-name>

## Verdict: <PASS | WARN | FAIL | N/A | INCONCLUSIVE>

## Command
```
<the exact command that ran>
```

## Output (truncated to 100 lines)
```
<stdout/stderr; truncated>
```

## Exit code: <code>

## Reason
<one or two sentences explaining the verdict>

## Files affected
- <file1>
- <file2>

## Mitigation (for WARN / FAIL)
<one or two sentences on how to address; OR "not auto-fixable" with the suggested next skill>
```

## `fix-log.md` shape (`--fix` only)

```markdown
# Fix log

## lint-clean (was WARN; now PASS)
- Strategy: npm run lint -- --fix
- Files changed:
  - components/ProductCard.tsx (-2)
  - utils/format.ts (-1)
- Validation: re-ran `npm run lint` → 0 warnings, 0 errors (PASS)
- Commit: <sha> (or "uncommitted; awaiting user push")

## license-headers (was FAIL; now PASS)
- Strategy: prepended header to 3 new .tsx files (header from .github/license-header.txt)
- Files changed:
  - components/NewWidget.tsx (+5)
  - components/NewWidget.test.tsx (+5)
  - utils/newhelper.ts (+5)
- Validation: re-ran license-headers check → all new files have header (PASS)
- Commit: <sha>
```

## `postback.md` shape (only when `--post-comment` set)

```markdown
# Postback

## Posted
| Comment URL | Receipt ID | Confirmed at |
| --- | --- | --- |
| <url> | c-7891 | 5s |

## Post-confirmation timeline
- t=0s   : posted via gh pr comment
- t=5s   : re-fetch → c-7891 visible (confirmed).

## Comment body (verbatim)
<the exact body posted>
```

## PR comment template (when `--post-comment` is used)

The comment body posted to the PR (see Example 8 in `references/examples.md`):

```markdown
**audit-pr summary** (from /adk-review:audit-pr)

| # | Check | Verdict |
| --- | --- | --- |
| 1 | lint-clean | PASS |
| 2 | typecheck-clean | PASS |
| 3 | tests-added | PASS |
| 4 | secrets-in-diff | PASS |
| 5 | license-headers | PASS |
| 6 | dep-licenses | PASS |
| 7 | doc-updated | PASS |
| 8 | a11y-regression | PASS |
| 9 | perf-regression | N/A (no hot-path) |
| 10 | bundle-size | PASS |

Overall: <PASS | WARN | FAIL | MIXED> (<n> Pass, <n> Warn, <n> Fail, <n> N/A).

<optional: 1-line "next step" if overall != PASS>

— /adk-review:audit-pr
```

Terse by design. Full per-check details remain in `.temp/task-<slug>/audit/per-check/`; the comment links to the run rather than dumping output.

## Verdict transitions (after `--fix`)

When `--fix` runs and re-runs the affected checks, `results.md` is REWRITTEN with the new verdicts. The pre-fix verdicts are preserved in `audit/results.pre-fix.md` so the user can diff:

```bash
diff .temp/task-<slug>/audit/results.pre-fix.md .temp/task-<slug>/audit/results.md
```

This shows exactly which checks moved (e.g. `lint-clean: WARN → PASS`).
