---
description: "Review all ADK skills for quality, token efficiency, upstream alignment, naming, and completeness"
---

# Review All Skills

Audit every skill in the `skills/` directory against quality standards. Produce a per-skill report card and aggregate summary.

## Checks

Run these checks against every `skills/*/SKILL.md`:

### 1. Naming Convention

- Directory name matches one of:
  - `[category]-[task]` for task skills in a category (e.g., `code-review-pr`, `docs-write`)
  - `[category]` for routing skills (e.g., `code-review`, `docs`, `dev`, `diagram`)
  - `[name]` for standalone tasks or helpers (e.g., `plan`, `audit`, `workflow`)
- Frontmatter `name` field is `adk-<directory-name>`
- Description starts with `adk -` followed by bracket tags

### 2. Token Efficiency

- Measure SKILL.md line count. Flag if > 300 lines.
- Check the "Shared Skills" section says "Load each skill's reference file ONLY when the condition" (conditional loading) not "loaded automatically" (eager loading)
- Check for a "Reference Loading" section with conditional gates
- Flag skills that inline large content that should be in `references/` or `stages/`
- For diagram-mermaid: verify type content is in `references/types/`, not inline

### 3. Upstream Alignment

Read `manifest.json` at the repo root:
- For `type=copy` sources: check `last_sync` age. Flag if > 30 days stale.
- For `type=ref` sources: check `last_sync` age. Flag if > 30 days stale.
- For `docs` entries: check `last_checked` field. Flag if null or > 30 days.
- Cross-check `ref_skills` arrays against actual skill directories.

### 4. Completeness

For each skill, check based on `workflow-tier`:
- **full**: requires SKILL.md, `references/` directory, `scripts/preflight.py`
- **abbreviated**: requires SKILL.md, `scripts/preflight.py`
- **helper**: requires SKILL.md
- **orchestrator**: requires SKILL.md

Additional checks:
- Every documented `--mode` or stage has a corresponding `stages/*.md` file
- Every skill referenced in "Shared Skills" table exists
- Every skill in "Adjacent Skills" section exists
- Connector skills have `references/routing.md`

### 5. Structural Consistency

Required SKILL.md sections by tier:

**full/abbreviated**:
- YAML frontmatter with: `name`, `description`, `user-invocable`, `argument-hint`, `allowed-tools`, `dependencies`, `workflow-tier`
- Shared Skills table
- Reference Loading section
- Help section (Parameters table, Behavior Variations, Examples)
- Preflight section
- Workflow section
- Output Format section
- Adjacent Skills section

**helper**:
- YAML frontmatter with: `name`, `description`, `user-invocable: false`, `workflow-tier: helper`
- Content-specific sections

**orchestrator**:
- YAML frontmatter with: `name`, `description`, `user-invocable: true`, `workflow-tier: orchestrator`
- Routing table
- Sub-Skills section

### 6. Cross-Reference Integrity

- Grep all SKILL.md files for `/adk:` references. Every reference must match an existing `skills/<name>/SKILL.md`.
- The `use` skill's routing table must include every `user-invocable: true` skill.
- `manifest.json` `ref_skills` must match actual skill directories.
- `CLAUDE.md` cross-skill update table must be accurate.

### 7. Open-Source Alignment (optional, with `--deep`)

For each skill listed in `manifest.json` `open_source_refs`:
- Fetch the referenced repo's README or skill files
- Compare feature coverage
- Flag gaps where ADK skill is missing features from the reference

## Output Format

```markdown
## Skill Review Summary

Date: <timestamp>
Skills reviewed: <count>

### Results by Category

#### code-review (3 skills + router)
| Skill | Lines | Naming | Tokens | Upstream | Complete | Structure | Refs |
|-------|-------|--------|--------|----------|----------|-----------|------|
| code-review | 74 | PASS | PASS | n/a | PASS | PASS | PASS |
| code-review-pr | 308 | PASS | WARN | stale | PASS | PASS | PASS |
| code-review-repo | 150 | PASS | PASS | n/a | PASS | PASS | PASS |
| code-review-fix | 120 | PASS | PASS | n/a | PASS | WARN | PASS |

(repeat for each category)

### Aggregate

| Check | Pass | Warn | Fail |
|-------|------|------|------|
| Naming | 45 | 2 | 0 |
| Token Efficiency | 40 | 5 | 2 |
| Upstream Alignment | 35 | 8 | 4 |
| Completeness | 42 | 3 | 2 |
| Structure | 38 | 7 | 2 |
| Cross-References | 45 | 1 | 1 |

### Top Issues
1. <highest priority issue>
2. <second>
3. <third>
```

## Execution

1. Read `manifest.json` to get upstream tracking data
2. List all `skills/*/` directories
3. For each skill, run all 6 checks (parallelize with child agents for speed)
4. Consolidate results into the output format
5. Write results to `.temp/skill-review-report.md`
