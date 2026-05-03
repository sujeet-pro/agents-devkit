# `audit-repo` — output format

## Per-turn status (each turn opens with this)

```
[adk-review:audit-repo] task=<slug> repo=<repo-name> phase=<0|1|2|3|4|5|6|7> mode=<auto|interactive> dimensions=<list> findings=B<n>/C<n>/S<n>/M<n>/N<n>/Q<n> healthy=<n>
```

`<healthy>` = count in the "what's healthy" section.

## Final report — `.temp/reports/audit-<slug>.md`

```markdown
# Audit — <repo-name> (<YYYY-MM-DD>)

_Authored <ISO-ts>Z by adk-review:audit-repo for <operator-name>._

## 1. Executive summary

**Verdict:** <one-line verdict suitable for an EM / tech lead to act on>

<one paragraph — repo at a glance: 1 sentence on health, 1 on the most-pressing risk, 1 on the recommended next move>

| Severity | Count | Notes |
| --- | --- | --- |
| Blocker | 1 | requires immediate action |
| Critical | 2 | this PR cycle |
| Should-Have | 7 | next 1-2 sprints |
| May-Have | 3 | backlog |
| Nitpick | 5 | optional cleanup |
| Question | 4 | clarify with team |

| Healthy items | Count |
| --- | --- |
| confirmed healthy | 5 |

## 2. Top-10 findings

(Severity-sorted, file-anchored. Each item is a card.)

### 1. [Blocker] <one-line summary>
- File: <path>:<line-range>
- Dimension: <security|performance|quality|deps|test-coverage|architecture>
- Confidence: <low|med|high>
- Evidence:
  ```
  <≤15-word verbatim quote>
  ```
- Issue: <one sentence>
- Impact: <one sentence — who is affected and how>
- Recommended action: `/<plugin>:<skill> --scope <path>` — <one-line>
- Effort estimate: <e.g. 1 hour | 1 day | 1 week | 1 quarter>
- References: <links to per-finding evidence file>

### 2. [Critical] <next finding>
...

(Up to 10 cards.)

## 3. Per-dimension detail

### 3.1 Security

<one paragraph — what was checked, what was found at high level>

| Severity | File:line | Issue | Confidence | Recommended action |
| --- | --- | --- | --- | --- |
| ...

**Tools run:**
| Tool | Command | Output (link to evidence) |
| --- | --- | --- |
| npm audit | `npm audit --omit=dev` | per-finding/security-001-npm-audit.txt |
| ...

**Coverage:**
- Checked: dep manifest, source files, env files, dot-files
- NOT checked: container images (no Trivy run; install Trivy to enable)

### 3.2 Performance
...

### 3.3 Code quality
...

### 3.4 Dependencies
...

### 3.5 Test coverage
...

### 3.6 Architecture
...

## 4. What's healthy

(Top 5 across dimensions; explicit "what's working".)

| Item | Evidence |
| --- | --- |
| 0 secrets in repo | regex + entropy clean |
| 0 npm vulns (production deps) | `npm audit --omit=dev` clean |
| CI green and fast (3.5min) | `gh run list --limit 10` all green |
| Coverage healthy on Python side (81%) | `pytest --cov` |
| 0 disallowed licenses | `npm-license-checker` + `pip-licenses` |

## 5. Recommendations

(Sorted by severity AND effort. Low-effort high-impact first.)

| Priority | Recommendation | Skill | Effort | Severity addressed |
| --- | --- | --- | --- | --- |
| P1 | Fix admin role check | /adk-code:code-security --scope routes/admin/ | 1 hour | Blocker |
| P2 | Address n+1 query | /adk-code:code-perf --scope db/ | 1 day | Critical |
| P3 | Add tests for 4 admin routes | /adk-code:code-test --scope src/api/admin/ | 1-2 days | Should-Have |
| P4 | Upgrade to React 19 | /adk-code:code-migrate --target react@19 | 1 week | Should-Have |
| P5 | Refactor god-class in calculator.ts | /adk-code:code-refactor --scope src/billing/ | 2-3 weeks | Critical |
| ...

## 6. Methodology

- Tools used:
  - npm audit, pip-audit (security; dep CVE)
  - eslint, ruff, tsc, mypy (quality; type-safety)
  - vitest --coverage, pytest --cov (test-coverage)
  - madge (architecture; cyclic deps)
  - manual sampling (architecture; god-class detection)
- Tools NOT available:
  - gosec (Go isn't the primary language; partial coverage via eslint for embedded Go bits in /scripts/)
  - Trivy (container scanning; install to enable)
- Scope:
  - Whole repo (no --scope filter applied)
  - Top-20 largest files + top-20 most-changed files (for architecture sampling)
  - All 6 dimensions
- Time taken: 6 min 42s (parallelized; serial would have been ~20min)
- Audited at SHA: <sha>
- Working tree state: clean
- Date: 2026-05-03

## 7. Artifact index

`.temp/reports/audit-<slug>.md` — this file
`.temp/reports/audit-<slug>-evidence/` — per-dimension + per-finding evidence
  inventory.md
  security.md
  performance.md
  quality.md
  deps.md
  test-coverage.md
  architecture.md
  healthy.md
  methodology.md
  per-finding/
    sec-001-admin-role-check.md
    perf-001-n-plus-one-orders.md
    quality-001-god-class-calculator.md
    ...
```

## Per-dimension file shape (`audit-<slug>-evidence/<dimension>.md`)

```markdown
# <dimension> — <repo>

## Summary
<one paragraph>

## Findings
| Severity | File:line | Issue | Confidence | Recommended action |
| --- | --- | --- | --- | --- |
| Blocker | routes/admin.go:42 | missing role check | high | /adk-code:code-security |
| Critical | db/orders.go:117 | n+1 query | high | /adk-code:code-perf |
| ... |

## Tool runs
| Tool | Command | Exit code | Output |
| --- | --- | --- | --- |
| npm audit | `npm audit --omit=dev` | 0 | per-finding/security-001-npm-audit.txt |
| pip-audit | `pip-audit` | 1 | per-finding/security-002-pip-audit.txt |

## Heuristics applied
| Heuristic | Found | Notes |
| --- | --- | --- |
| secret regex (24 patterns) | 0 | clean |
| entropy >4.5 in suspicious positions | 0 | clean |

## What's healthy in this dimension
| Item | Evidence |
| --- | --- |
| 0 npm vulns in production | `npm audit --omit=dev` clean |

## Coverage
- Checked: <list>
- NOT checked: <list, with reason>

## Time taken: <e.g. 1 min 12s>
```

## Per-finding file shape (`audit-<slug>-evidence/per-finding/<id>.md`)

For findings warranting deeper exhibits (long tool outputs, dep-tree dumps, code excerpts):

```markdown
# <id> — <one-line summary>

## Severity: <tier>
## Dimension: <dimension>
## Confidence: <low|med|high>

## Evidence
- File: <path>:<line-range>
- Quote: `<≤15-word verbatim>`

## Tool output
```
<full tool output, no truncation>
```

## Code excerpt (if helpful)
```<lang>
<full function or relevant block; cite file:line range>
```

## Issue (extended)
<longer description if warranted; otherwise the Top-10 card's one-liner is enough>

## Recommended fix (extended)
<longer description; otherwise the Top-10 card's "Recommended action" + skill suffices>

## Related findings
- <other finding IDs that share root cause or impact>
```

## Length budget recap

| Section | Target |
| --- | --- |
| 1. Executive summary | ≤30 lines |
| 2. Top-10 | ~100 lines |
| 3. Per-dimension detail (× 6) | ~600 lines (~100 per dimension) |
| 4. What's healthy | ~20 lines |
| 5. Recommendations | ~50 lines |
| 6. Methodology | ~30 lines |
| 7. Artifact index | ~10 lines |
| **Total target** | **600-800 lines** |

Hard upper: 1200 lines. Warn user; suggest `--scope <subdir>` or `--top 5` to focus.

## Status banner status semantics

- `findings=B0/C0/S0/M0/N0/Q0` → in good shape; `What's healthy` is the dominant section.
- `findings=B1+/C2+/...` → urgency in the recommendations.
- `healthy=0` → suspicious; even rough repos usually have at least 1-2 healthy items. If 0, re-check that the dimension passes ran.
