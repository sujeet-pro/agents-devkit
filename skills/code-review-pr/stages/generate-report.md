# Generate Report Stage

Produce a standalone markdown review artifact after a local or branch review. This stage runs when there is no PR context and `--fix` was not specified.

---

## Prerequisites

This stage runs after the primary review stage (`local-review.md` or `branch-review.md`) has produced findings.

---

## Report Structure

Generate a markdown review document at `.temp/adk-code-review-pr/<branch-or-scope>-review.md`:

```md
# Code Review Report

- **Date:** <date>
- **Scope:** <staged | unstaged | branch: <name> vs <base>>
- **Files reviewed:** N
- **Total findings:** N

---

## Executive Summary

<2-3 sentence summary of the overall code quality and key concerns>

---

## Findings

### Must Fix

[findings using canonical comment template format from references/review-comment-template.md]

### Suggestion

[findings]

### Note

[findings]

### Praise

[findings]

---

## Auto-Validation Summary

- **Findings from child agents:** N
- **Validated and kept:** M
- **Discarded (not present in code):** K
- **Line references corrected:** L
- **Suggestions revised:** J

---

## Metrics

- **Files changed:** N
- **Lines added:** N
- **Lines removed:** N
- **Test files changed:** N
- **Must Fix findings:** N
- **Suggestion findings:** N
- **Note findings:** N

---

## Open Questions

- <items needing clarification or discussion>

---

## Action Items

- [ ] **Must Fix:** <description> (<file:line>)
- [ ] **Suggestion:** <description> (<file:line>)
- [ ] **Note:** <description> (<file:line>)

---

## Review Methodology

- **Dimensions:** syntax, correctness, security, performance, design, reliability, testing, documentation [+ ui-ux, spec-compliance when applicable]
- **Review approaches:** diff review + full file context review
- **Auto-validation:** all findings verified against actual code
- **Guidelines:** <loaded guidelines>
```

---

## Verbosity Modes

Adapt the report based on `--verbosity`:

### Short

- Executive summary only
- Must Fix findings only
- Action items checklist
- No metrics or methodology sections

### Standard (default)

- Full report as described above

### Detailed

- Full report plus:
  - Per-file analysis with all findings inline
  - Commit-by-commit review notes
  - Architecture diagram of affected areas
  - Dependency impact analysis
  - Full child agent raw outputs per dimension

---

## Summary

After generating the report, display:

```text
## Review Report Generated

- **Scope:** <scope>
- **Findings:** N (must fix: N, suggestion: N, note: N)
- **Report:** .temp/adk-code-review-pr/<name>-review.md
- **Verbosity:** <short|standard|detailed>
```
