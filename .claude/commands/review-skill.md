---
description: "Deep review of a single ADK skill with open-source comparison and improvement recommendations"
---

# Review Single Skill

Deep-dive review of one skill with research into similar open-source skills and specific improvement recommendations.

## Arguments

`$ARGUMENTS` should be the skill name (directory name under `skills/`), e.g. `code-review-pr`, `diagram-mermaid`, `docs-write`.

## Workflow

### 1. Read the Skill

- Read `skills/$ARGUMENTS/SKILL.md` in full
- Read all files in `skills/$ARGUMENTS/references/` if they exist
- Read all files in `skills/$ARGUMENTS/stages/` if they exist
- Read `skills/$ARGUMENTS/scripts/preflight.py` if it exists
- Count total lines across all skill files

### 2. Run Quality Checks

Apply all checks from the `review-skills` command to this single skill:
- Naming convention
- Token efficiency (line count, conditional loading, reference splitting)
- Upstream alignment (from manifest.json)
- Completeness (required files and sections)
- Structural consistency (frontmatter, tables, sections)
- Cross-reference integrity

### 3. Research Similar Skills

Search for similar open-source skills:

1. Check `manifest.json` `open_source_refs` for this skill's known references
2. Search skills.sh for skills with similar functionality:
   - Use WebSearch: `site:skills.sh OR site:agentskill.sh <skill-function-keywords>`
3. Search GitHub for similar agent skills:
   - Use WebSearch: `github claude agent skill <skill-function-keywords> 2026`
4. For each found alternative:
   - Note the repo/skill name
   - Summarize its approach and key features
   - Compare token efficiency (if visible)
   - Identify features ADK skill is missing
   - Identify features ADK skill has that alternatives lack

### 4. Check Tool Documentation (if tool-based)

If the skill is built on a specific tool (check manifest.json `docs` field):
1. Fetch the tool's `llms.txt` if available
2. Compare documented features against the skill's coverage
3. Flag any tool features not covered by the skill
4. Flag any skill content that contradicts current tool docs

### 5. Generate Improvement Report

## Output Format

```markdown
## Skill Review: $ARGUMENTS

### Quality Report Card

| Check | Status | Details |
|-------|--------|---------|
| Naming | PASS/WARN/FAIL | ... |
| Token Efficiency | PASS/WARN/FAIL | <line-count> lines, <conditional/eager> loading |
| Upstream | PASS/WARN/FAIL | last sync <date>, <stale/fresh> |
| Completeness | PASS/WARN/FAIL | ... |
| Structure | PASS/WARN/FAIL | ... |
| Cross-Refs | PASS/WARN/FAIL | ... |

### Open-Source Comparison

| Alternative | Source | Approach | ADK Advantage | ADK Gap |
|-------------|--------|----------|---------------|---------|
| <skill-name> | <repo> | <summary> | <what ADK does better> | <what ADK is missing> |

### Tool Documentation Alignment (if applicable)

| Feature | In Tool Docs | In ADK Skill | Status |
|---------|-------------|-------------|--------|
| <feature> | yes/no | yes/no | covered/missing/outdated |

### Recommendations

Priority-ordered list of specific improvements:

1. **[HIGH]** <specific actionable recommendation>
2. **[MEDIUM]** <specific actionable recommendation>
3. **[LOW]** <specific actionable recommendation>

### Token Efficiency Analysis

- Current load: <N> lines (<N> SKILL.md + <N> references + <N> stages)
- Per-invocation estimate: <N> lines (after conditional loading)
- Recommendation: <split/merge/keep>
```

## Notes

- Write the report to `.temp/skill-review-<name>.md`
- If the skill has upstream references in manifest.json, prioritize checking those
- Focus recommendations on actionable changes, not theoretical improvements
