---
name: <skill-name>
description: "Use when <trigger description>"
user-invocable: true
argument-hint: "<primary-arg> [--flag1] [--flag2]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
workflow-tier: full
dependencies:
  commands: [git]
---

# <Skill Title>

<One-paragraph description of what this skill does and when to use it.>

Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`.

## Preflight

```
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}
```

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|---------------------|
| 0. Intent Expansion | yes | <what to confirm with user> |
| 1. Research & Options | yes | <what to research for this skill> |
| 2. Approach Selection | yes | <what to select> |
| 3. Planning | yes | <how to decompose> |
| 4. Execute | yes | <execution specifics> |
| 5. Validate & Learn | yes | <validation criteria> |

## Phase 0: Intent Expansion

<Skill-specific intent confirmation steps>

## Phase 1: Research & Options

<Skill-specific research and options discovery>

## Phase 2: Approach Selection

<Skill-specific approach selection guidance>

## Phase 3: Planning

<Skill-specific planning and task decomposition>

## Phase 4: Execute

<Execution-specific instructions>

## Phase 5: Validate & Learn

<Skill-specific validation criteria, checks, and "what to know" guidance>

## Output Format

<Define the markdown output structure for this skill>

```markdown
## <Title>

### Summary
<brief overview>

### <Section 1>
<content>

### <Section N>
<content>

### Next Steps
<actionable items>
```

## Adjacent Skills

- `/related-skill` — when to use instead or in combination
