---

## name: 
description: "adk - [tier] [area] Use when "
user-invocable: true
argument-hint: " [--flag1] [--flag2]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
workflow-tier: full
dependencies:
  commands: [git]

# 



## Shared Skills

This skill **invokes helper skills** for shared behavior (workflow, tone, preflight, output shape, interaction, etc.). Do **not** treat other skills as loose folders of markdown to copy from; delegate by invoking the helper skill, which stays self-contained.

If a **required** helper is unavailable in the user’s environment, print a short warning that names the missing skill and both invocation forms, then **continue** using the **inline fallback** summary in the table below (do not block the task on missing helpers).

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback (1–2 lines) |
|--------------|------------------------|------------------------------|------|----------------------------|
| workflow | `/adk:workflow` | `/workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| communication | `/adk:communication` | `/communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| preflight-check | `/adk:preflight-check` | `/preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| output-format | `/adk:output-format` | `/output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. |
| principal-engineer | `/adk:principal-engineer` | `/principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| agentic-teams | `/adk:agentic-teams` | `/agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| interaction | `/adk:interaction` | `/interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |

## Helper skills instead of copied reference packs

Use the **Shared Skills** table above: call the helper skill when installed; otherwise warn once and use the inline fallback. Skill-specific material for *this* task belongs under this skill’s own `references/` or `stages/` only.

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

- `/adk:<related>` / `/<related>` — when to use instead or in combination (ensure the named skill exists in `skills/<related>/` or treat as optional).

