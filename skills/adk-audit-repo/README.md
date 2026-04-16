# adk-audit-repo

Audit a repository for correctness risks, maintainability issues, and validation gaps.

## Quick Start

```
npx adk-audit-repo
```

## What This Skill Does

Audits a repository or scoped area for systemic issues rather than line-by-line diff review. Inspects architecture, code patterns, tests, dependencies, and documentation. Produces a prioritized list of findings grouped by severity and dimension, separated into quick-wins (low effort, high value) and strategic improvements (higher effort, long-term value).

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--scope` | path | none | Limit the audit surface |
| `--focus` | `quality`, `security`, `performance`, `dependencies` | `quality` | Primary audit lens |
| `--auto` | flag | off | Skip confirmations; run end-to-end |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Required | Purpose |
| --- | --- | --- |
| `git` | yes | Read repo structure, history, and patterns |
| `python3` | yes | Run pre-flight checks |

## Skill Layout

```
adk-audit-repo/
  SKILL.md              # Agent-facing skill definition
  README.md             # This file (human-facing docs)
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Skill-specific workflow steps
    persona.md           # Auditor persona and tone
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. **Pre-flight** -- run `scripts/preflight.py` to verify dependencies.
2. **Confirm scope** -- confirm the audit scope, lens, and any exclusions (skipped with `--auto`).
3. **Inspect codebase** -- examine architecture, code patterns, tests, and docs in scope.
4. **Identify patterns** -- look for repeated patterns rather than isolated nits.
5. **Classify findings** -- assign severity (Critical/High/Medium/Low), dimension, and stable F-IDs.
6. **Group findings** -- separate quick-wins from strategic improvements.
7. **Present findings** -- show the prioritized list; wait for user response.
8. **Finalize** -- report blind spots, missing evidence, and recommended next steps.

## Interaction Protocol

### Confirmations

Before starting the audit, the skill confirms:
- The audit scope (full repo or scoped path)
- The primary audit lens
- Any areas to exclude or prioritize

This step is skipped when `--auto` is passed.

### Findings Format

Each finding has a stable ID, severity, dimension, and one-line summary:

```
F-1  [Critical]   [security]      API keys hardcoded in config.py
F-2  [Critical]   [architecture]  Circular dependency between auth and user modules
F-3  [High]       [performance]   N+1 query pattern in user list endpoint
F-4  [Medium]     [quality]       No integration tests for payment flow
F-5  [Low]        [dependencies]  Three unused dependencies in package.json
F-6  [Quick-win]  [quality]       Add type hints to 12 public functions
```

Severity levels: **Critical** > **High** > **Medium** > **Low**
Dimensions: **architecture**, **security**, **performance**, **quality**, **dependencies**, **testing**, **documentation**

Findings are grouped into:
- **Quick-wins** -- low effort, high value; fix first
- **Strategic improvements** -- higher effort, long-term value

### User Response

After seeing findings, respond with any combination of:

| Syntax | Meaning |
| --- | --- |
| `a-N` | Accept finding N |
| `r-N` | Reject finding N |
| `e-N` | Expand finding N (show detail) |
| `all` | Accept all findings |

Example: `a-1, a-3, a-6, r-5, e-2`

## Output Format

The audit output contains six parts:

1. **Summary** -- one-line overview of repository health.
2. **Scope** -- what was audited (full repo, scoped path, focus lens).
3. **Findings** -- prioritized list with stable F-IDs, severity, and dimension, split into quick-wins and strategic improvements.
4. **Validation** -- what was checked with tooling and what relied on pattern analysis.
5. **Risk** -- residual risk and blind spots (areas not audited or not verifiable).
6. **Next steps** -- recommended improvement order, starting with quick-wins.

## Examples

### Full repository audit

```
npx adk-audit-repo
```

Audits the full repository with quality lens, presents prioritized findings split into quick-wins and strategic improvements.

### Security-focused audit

```
npx adk-audit-repo --focus security --scope src/
```

Scoped security audit of the `src/` directory, flags vulnerabilities and risks.

### Auto audit with dependency focus

```
npx adk-audit-repo --focus dependencies --auto
```

Skips confirmation, audits dependency health, reports outdated/unused/vulnerable packages.

## What Success Looks Like

- [ ] Audit scope was fully inspected
- [ ] Findings are prioritized with stable F-IDs, severity, and dimension
- [ ] Repeated patterns are flagged over isolated nits
- [ ] Quick-wins are separated from strategic improvements
- [ ] Each finding references code or tool evidence
- [ ] Blind spots and missing evidence are stated explicitly
- [ ] Recommendations are scoped and actionable
- [ ] User can accept, reject, or expand any finding
