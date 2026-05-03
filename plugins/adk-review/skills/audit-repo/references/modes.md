# `audit-repo` — mode contract

`audit-repo` supports `--auto` (default) and `-i` / `--interactive`. It does **not** support `--fix` (the skill is read-only; recommendations point to `/adk-code:*` skills instead).

| Mode | Effect |
| --- | --- |
| `--auto` (default) | Inventory → dimension passes (parallel) → aggregate → write report. No per-phase gating. |
| `-i` / `--interactive` | Per-phase approval + walks each Top-10 finding before writing the report. |
| `--auto -i` | Invalid; refused at parse. |

## `--auto` (default mode)

- Skips per-phase approval gates.
- Picks the documented dimension set (all 6 by default).
- Runs all dimension passes in parallel (max 4 at once).
- Writes the full report to `.temp/reports/audit-<slug>.md`.
- Does NOT post anywhere; does NOT modify code.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates: inventory → propose dimensions → propose Top-10 → write.
- For each Top-10 finding: shows + asks "accept | edit | discard | re-tier".
- Allows the user to add findings the heuristic missed.

## Why `audit-repo` doesn't support `--fix`

The skill's deliverable is a REPORT. Auditing is an evaluation activity; fixing is a change activity. Mixing them dilutes both:

- Auditing well requires a top-down strategic view; fixing requires a bottom-up tactical depth.
- A report that's also fixing things creates churn that invalidates the report.
- The right "fix" for a Top-10 finding is often a multi-PR program of work, not a one-shot edit.

Recommendations in the report point to the right `/adk-code:*` skill for each finding (with scope filters where applicable):

| Finding category | Recommended skill |
| --- | --- |
| Auth bypass / missing input validation | `/adk-code:code-security --scope src/auth/` |
| n+1 / unbounded loop | `/adk-code:code-perf --scope src/billing/` |
| Missing tests on critical path | `/adk-code:code-test --scope src/checkout/` |
| God class / boundary violation | `/adk-code:code-refactor --scope src/legacy/` |
| Outdated major-version dep | `/adk-code:code-migrate --target react@19` |
| Missing CHANGELOG / runbook | `/adk-docs:docs-write --type runbook` |
| Suspected perf regression in prod | `/adk-investigate:investigate-datadog --service <name>` |

Users execute these as separate engagements after digesting the audit.

## What `audit-repo` will NOT do, ever

1. Modify code. Read-only.
2. `git push`, `git commit`, `git stash`, `git merge`, `git rebase`. Read-only.
3. `gh pr create`, `gh pr merge`, `gh pr comment`, `gh pr close`. Read-only.
4. Open a Jira ticket for findings (that's the user's call).
5. Modify `~/.config/adk/*.md`.
6. Modify any artifact written by another skill.
7. Quote env-var values verbatim (anonymize).
8. Quote secrets verbatim (security findings name the type / file:line; never the bytes).
9. Auto-install missing tools (surface install command instead).

## Subset / specialized flags

- `--dimensions <comma-list>` — restrict to a subset (e.g. `--dimensions security,deps`).
- `--scope <path>` — restrict to a sub-path (e.g. `--scope src/auth/`).
- `--no-healthy` — skip the "what's healthy" section. Default: include. (RARELY a good idea — the section is the morale check.)
- `--top <n>` — change the Top-N count (default: 10). Useful for very large repos (`--top 20`) or very small ones (`--top 5`).
- `--no-tools` — force heuristics-only (skip repo-native tool runs). Default: tools first.
- `--time-budget <minutes>` — soft cap on total runtime; if exceeded, surface what was completed and what was skipped.

## Default vs override

| Decision | Default | Override |
| --- | --- | --- |
| Dimensions | all 6 | `--dimensions <list>` |
| Scope | whole repo | `--scope <path>` |
| Tool-first vs heuristic-first | tool-first | `--no-tools` (rare) |
| Top-N | 10 | `--top <n>` |
| Healthy section | include | `--no-healthy` (rare) |
| Time budget | none (run to completion) | `--time-budget <minutes>` |
| Report location | `.temp/reports/audit-<slug>.md` | (not user-overrideable; consistent across runs) |

## Composability

`audit-repo` is the natural starting point for a multi-PR hardening program:

```
/adk-review:audit-repo .                              # baseline audit
# ... read the report ...
/adk-code:code-security --scope src/auth/             # address security findings
/adk-code:code-test --scope src/checkout/             # address test-coverage findings
/adk-review:audit-repo . --dimensions security,test-coverage  # confirm progress
```

For M&A or open-source readiness, the typical flow is:

```
/adk-review:audit-repo .                              # full audit
# ... share with stakeholders ...
# ... iterate via /adk-code:* over weeks ...
/adk-review:audit-repo .                              # delta audit
# ... ship / open-source ...
```

The skill itself doesn't track progress across runs; the user (or a future `audit-tracker` skill) does that by diffing successive `.temp/reports/audit-<slug>.md` files.
