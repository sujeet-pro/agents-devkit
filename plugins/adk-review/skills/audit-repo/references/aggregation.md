# `audit-repo` — aggregation rules

How Phase 4 turns per-dimension findings into the Top-10 + per-dimension grouping + "what's healthy" + recommendations.

## Inputs

From Phase 3:

```
.temp/reports/audit-<slug>-evidence/security.md       # per-dimension findings
.temp/reports/audit-<slug>-evidence/performance.md
.temp/reports/audit-<slug>-evidence/quality.md
.temp/reports/audit-<slug>-evidence/deps.md
.temp/reports/audit-<slug>-evidence/test-coverage.md
.temp/reports/audit-<slug>-evidence/architecture.md
```

Each has a `## Findings` table + a `## What's healthy in this dimension` table.

## Step 1: collate

Read every per-dimension `.md`. Extract:

```python
findings = []
healthy = []
for dim in dimensions:
    findings.extend(read_findings(f"{dim}.md"))    # each: {severity, file, line, dim, confidence, issue, action, effort}
    healthy.extend(read_healthy(f"{dim}.md"))      # each: {item, evidence, dim}
```

## Step 2: apply overrides

```python
# Severity-bar overrides
for f in findings:
    if f.category in review_md.severity_bar.blocker:
        f.severity = max(f.severity, "Blocker")
    if f.category in review_md.severity_bar.critical:
        f.severity = max(f.severity, "Critical")
    if f.category in review_md.severity_bar.should_have:
        f.severity = max(f.severity, "Should-Have")

# Ignore filter for this repo
findings = [f for f in findings if f.category not in review_md.ignore_in_repos.get(repo, [])]
```

## Step 3: sort

Primary: severity (Blocker > Critical > Should-Have > May-Have > Nitpick > Question).

Secondary: impact-area breadth (5 endpoints affected > 1 endpoint affected). Computed as the count of distinct files/services touched by the finding.

Tertiary: confidence (high > med > low).

```python
def sort_key(f):
    severity_rank = {"Blocker": 0, "Critical": 1, "Should-Have": 2,
                     "May-Have": 3, "Nitpick": 4, "Question": 5}
    breadth_rank = -f.impact_area_count   # negative because higher breadth ranks higher
    confidence_rank = {"high": 0, "med": 1, "low": 2}[f.confidence]
    return (severity_rank[f.severity], breadth_rank, confidence_rank[f.confidence])

findings.sort(key=sort_key)
```

## Step 4: pick Top-N

```python
top_n = min(int(args.top or 10), len(findings))
top = findings[:top_n]
remaining = findings[top_n:]
```

**Important: NO PADDING.** If there are fewer than `top_n` real findings, surface fewer. The report says "5 of 5 findings (no Top-10 to surface)" — and surfaces "the repo is in good shape" instead.

## Step 5: group remaining per dimension

```python
per_dimension_remaining = defaultdict(list)
for f in remaining:
    per_dimension_remaining[f.dim].append(f)
```

Each dimension's per-dimension report (Section 3 of the full report) lists its top findings + the remaining findings + healthy.

## Step 6: assemble "what's healthy"

```python
# Pick top 5 healthy items across dimensions
# Priority: items with the broadest "what NOT to break" impact
healthy.sort(key=lambda h: -h.impact_breadth)
top_healthy = healthy[:5]
```

What COUNTS as "healthy":

- **Concrete + measurable.** "0 secrets in repo" beats "code is well-organized".
- **Substantive.** "CI green and fast (3.5min)" beats "uses semicolons consistently".
- **Cross-dimension.** "Coverage >80% on critical paths" cuts across test-coverage + architecture.
- **Counter-balance to the findings.** If security has 1 Blocker, the healthy item from security would be "no other security issues found" — explicit contrast.

What does NOT count:

- Padding ("uses TypeScript", "has a README"). Default expectations, not noteworthy.
- Speculative ("seems readable"). Without evidence, it's not a finding (positive or negative).
- Dimension-specific micro-wins ("eslint config has 47 rules"). The reader doesn't care.

## Step 7: build recommendations

For each Top-N finding, build a recommendation:

```python
recommendations = []
for f in top_n_findings:
    rec = {
        "priority": severity_to_priority[f.severity],
        "description": f.issue,
        "skill": map_to_skill(f),    # see mapping table
        "scope": f.scope_filter,
        "effort": f.effort_estimate,
        "severity_addressed": f.severity,
    }
    recommendations.append(rec)

# Sort: severity (high to low) AND effort (low to high — low-effort high-impact first)
def rec_sort_key(r):
    sev_rank = {"P1": 0, "P2": 1, "P3": 2, "P4": 3, "P5": 4}
    eff_rank = {"1 hour": 0, "1 day": 1, "1 week": 2, "1 quarter": 3, "1 year": 4}
    return (sev_rank[r.priority], eff_rank.get(r.effort, 5))

recommendations.sort(key=rec_sort_key)
```

### Severity → priority mapping

| Severity | Priority |
| --- | --- |
| Blocker | P1 |
| Critical | P2 |
| Should-Have | P3 |
| May-Have | P4 |
| Nitpick | P5 |
| Question | (no priority — included as "discuss with team") |

### Finding → skill mapping

| Finding category | Recommended skill (with scope filter) |
| --- | --- |
| Auth bypass / missing auth check | `/adk-code:code-security --scope <auth-path>` |
| Missing input validation | `/adk-code:code-security --scope <api-path>` |
| Secret in code | (manual: rotate + remove from history; never auto-fix) |
| n+1 query / unbounded loop | `/adk-code:code-perf --scope <path>` |
| Missing tests on critical path | `/adk-code:code-test --scope <path>` |
| God-class / long function | `/adk-code:code-refactor --scope <path>` |
| Boundary violation | `/adk-code:code-refactor --scope <path>` |
| Cyclic deps | `/adk-code:code-refactor --scope <path>` |
| Outdated major dep (e.g. React 18 → 19) | `/adk-code:code-migrate --target <dep>@<version>` |
| Outdated minor / patch dep | `/adk-code:code-migrate --target <dep>` (smaller) |
| Disallowed license | `/adk-code:code-migrate --target <dep>` (replacement) |
| CVE in dep | `/adk-code:code-migrate --target <dep>` (security upgrade) |
| Missing CHANGELOG / runbook | `/adk-docs:docs-write --type runbook` OR `/adk-docs:docs-changelog` |
| Suspected perf regression in prod | `/adk-investigate:investigate-datadog --service <name>` |
| Architecture drift | (manual: update ADR / docs/architecture.md) OR `/adk-code:code-refactor` |

### Effort estimates

Per-finding-type ballparks:

| Effort | Examples |
| --- | --- |
| 1 hour | secret rotation; lint auto-fix; config tweak; missing role check on 1 endpoint |
| 1 day | n+1 fix + test; missing-validator on 1-3 endpoints; CHANGELOG backfill |
| 1 week | major version dep upgrade (react 18 → 19); refactor a single god-class |
| 1 quarter | architecture refactor (e.g. introduce service layer); migrate to a new framework |

The agent picks based on the finding's blast radius + the file count touched + complexity.

## Step 8: write `healthy.md`

```markdown
# What's healthy

Top 5 across dimensions:

| Item | Evidence | Dimension |
| --- | --- | --- |
| 0 secrets in repo | regex + entropy clean | security |
| 0 npm vulns (production deps) | `npm audit --omit=dev` clean | security |
| CI green and fast (3.5min) | `gh run list --limit 10` all green | quality |
| Coverage healthy on Python side (81%) | `pytest --cov` | test-coverage |
| 0 disallowed licenses | `npm-license-checker` + `pip-licenses` | deps |
```

## Step 9: hand off to Phase 6 (write report)

Phase 6 reads:
- Top-N findings → Section 2 (Top-10).
- Per-dimension remaining → Section 3 (Per-dimension detail).
- `healthy.md` → Section 4 (What's healthy).
- Recommendations → Section 5 (Recommendations).
- `methodology.md` (built in Phase 6 itself from the dimension passes' coverage notes) → Section 6.

## Edge cases

### All findings are Question / Nitpick

Verdict: "the repo is in good shape; only Question / Nitpick findings". Surface as such; explicitly note "no Blocker / Critical / Should-Have findings".

### Zero healthy items

Suspicious. Re-check that dimension passes ran. Even rough repos usually have at least 1-2 healthy items (a clean lint, a passing CI, etc.). If 0, surface a `validator.md` warning and continue.

### One dimension's tool failed entirely

Mark that dimension's coverage as `partial` in `methodology.md`. Findings from heuristics still surface; healthy items from that dimension may be sparse.

### Scope filter shrinks scope to 0 files

Refuse the audit; surface "no files match `--scope <path>`; check the path or remove the filter".

### `--top <n>` larger than the actual finding count

Surface what we have; note "<n> requested, <m> real findings to surface".

## Anti-patterns

- **Padding to hit Top-10.** Don't fabricate. Surface fewer if fewer real findings.
- **Sorting only by severity.** Within a tier, breadth matters; don't surface a localized Blocker over a widespread Critical.
- **Building recommendations without effort estimates.** The reader can't prioritize without effort.
- **Mapping every finding to the same skill.** Be specific (with scope filter); don't always say `/adk-code:code-refactor`.
- **Hiding "Question" findings.** They're surfaced too — they're prompts for team discussion, not noise.
