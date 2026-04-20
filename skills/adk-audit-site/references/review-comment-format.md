# Review Comment Format

Standard format for all review and audit findings.

## Comment structure
```
F<n> [Type][Severity]: Comment Title
Confidence: <low | medium | high> | Dimension: <dimension> | Scope: <file:line>

Issue Summary:
Briefly explain the issue. Include minimal, relevant code or doc excerpts.

Why This Matters:
Explain potential impact (maintainability, security, architecture, performance).

Suggested Fix:
A focused resolution path or alternative approach.

Verify / Clarify (optional):
Mention if external validation or product / platform input is required.
```

## Type
| Value | Meaning |
| --- | --- |
| `Question` | Seeks clarification |
| `Praise` | Highlights well-executed code or design |
| `Issue` | Points out a bug or violation of expectations |
| `Suggestion` | Proposes improvement, not mandatory |
| `NitPick` | Minor cosmetic tweak |

## Severity
| Value | Merge impact |
| --- | --- |
| `Critical` | Must fix before merge |
| `Blocker` | Blocks merge |
| `Must Have` | Fix recommended before approval |
| `Should Have` | Not merge-blocking |
| `Nice to Have` | No merge impact |

## Dimensions
`security`, `architecture`, `patterns`, `code-quality`, `performance`, `documentation`,
`accessibility`, `readability`, `correctness`, `completeness`, `consistency`, `seo`, `content`.

## Stable IDs
- Sequential within a session: `F1`, `F2`, `F3`.
- IDs are stable; do not renumber when reordering.
- User accepts / rejects / edits by ID: `a-1,3`, `r-2`, `e-4`.

## Consolidation
1. Group related findings affecting the same location under one F-ID.
2. Use the highest severity in the group.
3. List each sub-issue as a bullet under the consolidated finding.
4. Keep the finding actionable.

## Summary
```
---
Summary: N findings (X critical, Y must-have, Z suggestions)
Praise: N positive observations
Questions: N items needing clarification
```
