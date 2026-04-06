# Intent Expansion

Use this reference during Phase 0 of `/adk-use`.

The goal is to turn a raw prompt into a compact, reviewable execution brief before any real work starts.

## What to Show the User

Keep it concise. Show:

1. **Goal** — one-line interpretation of what the user wants
2. **Reasoning** — 2-4 short bullets explaining why you picked the route
3. **Skills** — the likely skill pipeline and why each skill is needed
4. **Tools / MCPs** — what will be used, and whether it is available
5. **Complexity** — `Trivial`, `Small`, `Medium`, or `Large`, plus one-line rationale
6. **PE Check** — only for Medium and Large work

## Rules

- Show reasoning, not hidden chain-of-thought.
- Prefer “decision because factor, which means consequence”.
- Surface assumptions explicitly.
- Ask for confirmation early, before deep research or edits.
- When the task is complex, question whether the work should be done as requested or simplified.

## Prompt Expansion Checklist

### Goal

- what outcome is the user trying to reach?
- what artifact or code will change?
- what “done” likely means?

### Hidden Requirements

- tests
- docs
- migrations
- rollout or rollback concerns
- compatibility or version constraints

### Ambiguities

For each meaningful ambiguity, state:

- the question
- your default assumption
- why it matters

### Skills

Pick the minimum useful pipeline.

Common examples:

- PR review -> `/adk-coding`, `/adk-code-review-pr`
- feature implementation -> `/adk-coding`, `/adk-research`, `/adk-plan`, `/adk-dev-build`, `/adk-code-review-pr`
- docs -> `/adk-research`, `/adk-docs-guidelines`, `/adk-docs-write`, `/adk-docs-review`
- audit -> `/adk-coding`, `/adk-audit`, `/adk-docs-write`

### Tools and MCPs

List:

- local code/file tools
- git / shell commands
- web research, if needed
- MCPs or external connectors, if needed

Mark each as:

- `available`
- `missing`
- `optional`

## Complexity Heuristics

- **Trivial**: one obvious change, one file, no real decision
- **Small**: 2-3 files, clear requirements, minimal coordination
- **Medium**: several files, one or two design choices, non-trivial verification
- **Large**: multiple workstreams, architecture choices, unclear boundaries, significant risk

When unsure, choose `Medium`.

## PE Check Format

Use this for Medium and Large tasks:

```text
PE check:
- Need: <yes / maybe / questionable>
- Simplest version: <short description>
- Trade-off: <main trade-off>
- Maintenance cost: <low / medium / high>
```

## Confirmation Prompts

### Inline

```text
This is my read of the task. I’ll use <skills>, start with <first action>, and treat it as <complexity>. Proceed, simplify, or adjust?
```

### Full Confirmation (Medium / Large)

Write `intent.json` to the session directory, then confirm with the user using the Intent Confirmation protocol from `references/inline-interaction.md`. Render the goal, reasoning, skills, tools, and complexity inline. Wait for approve/edit/simplify/cancel.

Use inline confirmation in the agent conversation for all intent approvals.
