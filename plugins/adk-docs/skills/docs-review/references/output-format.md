# `docs-review` — output format

## Per-turn status

```
[adk-docs:docs-review] task=<slug> phase=<0|1|2|3|4|5> target=<md|confluence|gdoc|url> findings=<b/c/s/m/n> mode=<auto|interactive|fix>
```

## Severity rubric

| Severity | Short label | Trigger |
| --- | --- | --- |
| Blocker | B | Doc actively contradicts current code on a load-bearing topic (install, auth, rollback, payment, on-call step) |
| Critical | C | Stale-and-wrong on a moderately load-bearing topic (deprecated API still documented as current; env var removed but still listed) |
| Should-Have | S | Missing context a reader needs (no rollback in a runbook; no examples in an API ref) |
| May-Have | M | Polish / clarity that isn't wrong (mixed heading depths; ambiguous pronoun) |
| Nitpick | N | Taste (trailing period in a heading; oxford-comma style) |

## `review.md` shape

```markdown
# docs-review — <slug>

**Target:** <path-or-URL>
**Target kind:** md | confluence | gdoc | url
**Last-modified:** YYYY-MM-DD
**Last-editor:** <name or bot>
**Repo audited against:** <owner>/<repo>

## Summary

| Severity | Count |
| --- | --- |
| Blocker | 2 |
| Critical | 1 |
| Should-Have | 3 |
| May-Have | 2 |
| Nitpick | 5 |

## Findings

### 1. [Blocker] <short title>
- **Doc**: `<path>:<line>` — "<quoted claim, ≤15 words>"
- **Code**: `<file>:<lines>` — <actual behavior>
- **Evidence**: <command or file path the reader can re-run>
- **Severity**: Blocker — <reason load-bearing>
- **Fix (if non-controversial)**: <exact diff or replacement string>

### 2. [Blocker] ...

### 3. [Critical] ...

### N. [Should-Have] ...

## Overall assessment

1-2 sentences. Is this doc mostly right, mostly stale, or actively
misleading? Recommend one next action.
```

## `fixes-applied.md` (under `--fix`)

```markdown
# Fixes applied — <slug>

Target: <path-or-URL>
Backup: .temp/task-<slug>/backup/<basename>

## 1. Replaced `npm install` with `pnpm install`
- Location: `README.md:22`
- Finding: §1 (Blocker)
- Diff:
  ```diff
  - Run `npm install` to fetch dependencies.
  + Run `pnpm install` to fetch dependencies.
  ```

## 2. ...

## Re-validation

- Fetched target after write; diff applied cleanly.
- All fixed findings re-checked against code; now `OK`.
```

## `fixes-deferred.md` (under `--fix`)

```markdown
# Fixes deferred (controversial) — <slug>

These were labeled controversial per `references/modes.md`. Decide
and apply manually or re-run with explicit opt-in.

## 1. [Should-Have] Add a "Rollback" section
- Rationale: reader can't recover from the mitigation procedure.
- Proposed content: (sketched in the review)
- Why deferred: new section, not a factual correction.
```

## Final report

`.temp/task-<slug>/report.md` follows the standard auto report shape
(Result / Decisions / Validation / Residual risk / Artifact index).
