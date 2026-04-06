---

## name: adk-
description: "Use when "
user-invocable: true
argument-hint: " [--flag1] [--flag2]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
workflow-tier: full
dependencies:
  commands: [git]

# 



## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

## Reference Loading

Load reference files conditionally to minimize token usage:

| Reference | Load When |
|-----------|-----------|
| `workflow-6phase.md` | always (read only the section for the current phase) |
| `communication-style.md` | always |
| `preflight.md` | before preflight check |
| `output-formats.md` | when producing final output |
| `output-format-modes.md` | when producing final output |
| `principal-engineer.md` | Phase 0, complexity >= medium |
| `agentic-teams.md` | Phase 4, when launching child agents |
| `inline-interaction.md` | interactive phases, NOT --auto |
| `help-format.md` | when --help is passed |
| `project-guidelines.md` | Phase 1, when scanning project |
| `review-pipeline.md` | review skills only |
| `review-comment-template.md` | when posting review comments |
| `source-routing.md` | when target is external (PR, Confluence, Google Docs) |

## Preflight

```
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}
```

## Phase Applicability


| Phase                 | Applies | Skill-Specific Notes |
| --------------------- | ------- | -------------------- |
| 0. Intent Expansion   | yes     |                      |
| 1. Research & Options | yes     |                      |
| 2. Approach Selection | yes     |                      |
| 3. Planning           | yes     |                      |
| 4. Execute            | yes     |                      |
| 5. Validate & Learn   | yes     |                      |


## Phase 0: Intent Expansion



## Phase 1: Research & Options



## Phase 2: Approach Selection



## Phase 3: Planning



## Phase 4: Execute



## Phase 5: Validate & Learn

<Skill-specific validation criteria, checks, and "what to know" guidance>

## Output Format



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

