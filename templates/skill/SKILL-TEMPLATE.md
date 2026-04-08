---

## name: 
description: "adk - [tier] [area] Use when "
user-invocable: true
argument-hint: " [--flag1] [--flag2]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
workflow-tier: full
maturity: stable
workflow-family: <family>
dependencies:
  commands: [git]

# 



## Shared Skills

This skill **invokes helper skills** for shared behavior (workflow, tone, preflight, output shape, interaction, etc.). Do **not** treat other skills as loose folders of markdown to copy from; delegate by invoking the helper skill, which stays self-contained.

If a **required** helper is unavailable in the user’s environment, print a short warning that names the missing skill and both invocation forms, then **continue** using the **inline fallback** summary in the table below (do not block the task on missing helpers).

| Helper skill | Invoke (Claude plugin) | Invoke (Codex / skills.sh) | When | Inline fallback (1–2 lines) |
|--------------|------------------------|------------------------------|------|----------------------------|
| workflow | `/adk:workflow --family <family>` | `/workflow --family <family>` | always | <Family> workflow: <shape>. `--auto` skips confirmations. |
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

## Workflow

<!-- Replace <family> with the actual family: quick-action, standard-task, complex-build, or investigative-loop -->
<!-- Then replace these placeholder steps with the family-appropriate steps -->

### 1. Confirm

<Intent confirmation — what the skill confirms before starting>

### 2. Research

<Research step — what the skill investigates (omit for quick-action)>

### 3. Execute

<Execution step — the core work the skill performs>

### 4. Validate

<Validation — how the skill verifies its output>

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

