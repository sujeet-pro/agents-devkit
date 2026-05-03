# `review-code-changes` — output format

## Per-turn status (each turn opens with this)

```
[adk-review:review-code-changes] task=<slug> repo=<repo-name> baseline=<ref>(<source>) scope=<branch:n staged:n unstaged:n untracked:n> phase=<0|1|2|3|4|5|6> mode=<auto|interactive>[+fix] findings=B<n>/C<n>/S<n>/M<n>/N<n>/Q<n>
```

`<source>` ∈ {`tracking`, `remote`, `main`, `master`, `first-parent`, `arg`}.

## Final report

Written to `.temp/task-<slug>/report.md`:

```markdown
# review-code-changes report — <slug>

## Result
<one sentence on what was found and what to do next>

## Repo snapshot
- Repo: <name>
- Branch: <current-branch>
- Baseline: <ref> (source: <source>)
- Scope sources: branch=<n>, staged=<n>, unstaged=<n>, untracked=<n>
- Lint pre-pass: <PASS / N warnings — see lint-output.txt | not run>

## Findings (severity-sorted)
| Severity | File | Source | Issue |
| --- | --- | --- | --- |
| Critical | src/pricing/types.ts:14-22 | untracked | Missing test variant for discriminated union |
| Should-Have | src/pricing/calc.ts:55 | unstaged | Loop-invariant Math.pow not hoisted |
| Should-Have | src/pricing/utils.ts:12 | untracked | parseFloat without error handling |

## Per-source breakdown
- branch (committed): 0 findings
- staged: 0 findings
- unstaged: 1 Should-Have
- untracked: 1 Critical, 1 Should-Have
- Recommendation: address the Critical in untracked before commit

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 0 | baseline | origin/feature/pricing-rework | tracking branch resolved |
| 0 | scope sources | all four | default; no --no-untracked |
| 1 | lint pre-pass | run | npm run lint < 30s |
| 3 | dimensions | all six | default; no --dimensions override |

## --fix log (when --fix was set)
| Finding | Files changed | Validation | Status |
| --- | --- | --- | --- |
| Critical | src/pricing/calc.test.ts (+36/-0) | npm test → 14/14 PASS | applied |
| Should-Have | src/pricing/calc.ts (+1/-1) | npm test → 14/14 PASS | applied |
| Should-Have | src/pricing/utils.ts (+5/-2) | npm test → 14/14 PASS | applied |

## Validation evidence
- Working tree: <repo-path> (branch: <branch>, dirty: yes)
- Tests: <command> PASS / FAIL (link to log)
- Typecheck: <command> PASS / FAIL
- Lint: <command> PASS / FAIL

## Next step
<one sentence>
- 0 Blockers + 0 Criticals → "Ready to push. Suggested commit message: see /adk-docs:docs-commit-message."
- Blockers / Criticals present + --fix not set → "Re-run with --fix to apply, or address manually."
- Blockers / Criticals present + --fix set + validation green → "Fixes applied; eyeball with `git diff`, commit, push."
- Validation failed during --fix → "Stopped after <n> fixes; <command> failed at <step>. See fix-log.md."

## Artifact index
.temp/task-<slug>/
  prompt.txt           verbatim user prompt + ISO timestamp
  review/
    scope.md           per-source breakdown
    raw-findings.md    pre-de-noise findings (per-dimension)
    findings.md        canonical, severity-sorted
    fix-log.md         (--fix only) per-fix evidence
    lint-output.txt    (if lint pre-pass ran) lint output
  validation/
    per-skill/review-code-changes.md
  report.md            this file
```

## `findings.md` shape

Each finding card. Severity-sorted; tagged with scope source.

```markdown
## Critical

### [Critical] Missing test variant for discriminated union
- File: src/pricing/types.ts:14-22
- Source: untracked
- Dimension: tests
- Confidence: high
- Evidence:
  ```
  type Pricing = StandardPricing | TieredPricing | DynamicPricing
  ```
- Issue: types.ts exports a 3-variant union; calc.test.ts only tests StandardPricing.
- Fix: add tests covering TieredPricing + DynamicPricing branches.
- Impact if unfixed: untested branches likely to break in production on certain product types.

## Should-Have

### [Should-Have] Loop-invariant `Math.pow` not hoisted
- File: src/pricing/calc.ts:55
- Source: unstaged
- Dimension: performance
- Confidence: med
- Evidence:
  ```
  for (const p of prices) { p.tax = p.base * Math.pow(1 + tax, p.years) }
  ```
- Issue: `Math.pow(1 + tax, p.years)` is loop-invariant w.r.t. tax.
- Fix: hoist `const taxFactor = Math.pow(1 + tax, ...)` outside the loop, OR pre-compute per unique p.years.
- Impact if unfixed: ~3x compute on the price-list hot path; visible in profiles >100 prices.
```

## `scope.md` shape

```markdown
# Scope

## Baseline
- Ref: <ref>
- Source: <tracking|remote|main|master|first-parent|arg>
- Resolved at SHA: <baseline-sha>

## Per-source counts
| Source | File count | Lines added | Lines deleted |
| --- | --- | --- | --- |
| branch (committed vs baseline) | 14 | +1240 | -180 |
| staged | 3 | +12 | -4 |
| unstaged | 7 | +84 | -22 |
| untracked | 2 | +120 (new files) | n/a |

## Files in scope
| File | Source | Status |
| --- | --- | --- |
| src/pricing/calc.ts | unstaged | M (modified) |
| src/pricing/calc.test.ts | unstaged | M |
| src/pricing/types.ts | untracked | A (new file) |
| src/pricing/utils.ts | untracked | A |
| ... | | |

## Excluded
- --scope filter: none
- --no-untracked: false (untracked included)
- gitignored: <list of large files / build outputs that were skipped automatically>
```

## `fix-log.md` shape (`--fix` only)

```markdown
# Fix log

## f-001 [Critical] Missing test variant
- Delegated to: /adk-code:code-bugfix
- Files changed:
  - src/pricing/calc.test.ts (+36/-0)
- Validation:
  - `npm test src/pricing/` → 14/14 PASS
- Status: applied (working tree dirty; not committed)

## f-002 [Should-Have] Loop-invariant Math.pow
- Applied: inline edit
- Files changed:
  - src/pricing/calc.ts (+1/-1)
- Validation:
  - `npm test src/pricing/` → 14/14 PASS
- Status: applied
```
