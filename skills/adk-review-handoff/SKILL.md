---
name: adk-review-handoff
description: Capture a structured session-handoff document so a paused or transferred task can resume without information loss - covering task summary, decisions with rationale, work completed, remaining work, blockers, key files, git state, and environment. Use when pausing long-running work, switching contexts, transferring to another developer or session, or preparing async collaboration. Do not use for project documentation (use adk-docs-write) or commit messages (use adk-publish-commit).
---

# ADK Review / Handoff

Standalone task skill under the `adk-review` category router. Produces a self-contained handoff document that any session or person can resume without consulting the original chat.

## When to use

- Pausing a long-running task mid-stream.
- Switching to a higher-priority item with intent to resume later.
- Handing off in-progress work to a teammate.
- Resuming after a break or new session (use `resume` action to verify state).
- Documenting session progress for async collaboration.

## When NOT to use

- Project documentation -> `adk-docs-write`
- Commit messages or PR text -> `adk-publish-commit`
- Planning new work from scratch -> `adk-plan-roadmap`
- Retrospectives or post-mortems

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `create` (default) / `resume` / `status` |
| `<task>` | optional | Description of the task being handed off; inferred from context if absent |
| `<output path>` | optional | Defaults to `.handoff/handoff-YYYY-MM-DD-HHMM.md` |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate action and task. Approval gate unless `--auto`.
2. **Capture state** - snapshot:
   - `git` state: branch, uncommitted changes, staged files, recent commits, dirty tree summary.
   - Modified files (touched in this session).
   - Conversation decisions (each with rationale and the alternative considered).
   - Open questions still unresolved.
3. **Structure** - place the captured state into the handoff template below.
4. **Preview** - show the document summary to the user for confirmation. Skip when `--auto`.
5. **Deliver** - write the handoff file; print the file path, progress summary, and the recommended next step.

For `resume`:

1. Read the handoff document.
2. Verify git state matches; surface any mismatch (different branch, uncommitted changes that were not in the handoff, deleted files).
3. Recap task, decisions, and remaining work; recommend the immediate next action.

For `status`:

1. List existing handoff files in `.handoff/` (or configured directory).
2. For the latest, show task / progress / blockers / next.

## Handoff template

```markdown
# Handoff: <task summary>

## Created
<ISO timestamp> - <session id or git user>

## Task
<one paragraph - what we are trying to do and why>

## Progress
<percent or N/M phases complete>

## Decisions Made
- <decision> - rationale: <one sentence> - alternative rejected: <one phrase>
- <decision> - rationale: <one sentence>

## Work Completed
- <bullet> - commit: <sha if applicable>
- <bullet>

## Remaining Work
- [ ] <actionable step> - file: `<path>` if known
- [ ] <actionable step>

## Blockers
- <blocker> - waiting on: <person / system> - mitigation: <if any>

## Key Files
- `path/to/file.ts` - <why it matters>
- `path/to/other.ts` - <why it matters>

## Git State
- Branch: <name>
- Base: <ref>
- Uncommitted changes: <yes/no, with file count>
- Staged files: <count or list>
- Recent commits:
  - <sha> <subject>
  - <sha> <subject>

## Environment
- Node / Python / runtime version: <value>
- Required env vars set: <list or "see .env.example">
- External services: <up / degraded / unknown>

## Open Questions
- <question> - direction so far: <if any>

## Resume Instructions
1. <first concrete step to pick this up>
2. <second step>

## Out of Scope
- <items intentionally not in this task>
```

## Output format (create)

```
**Handoff**: <path>
**Task**: <task summary>
**Progress**: <percent / phases>
**Blockers**: <count>
**Next**: <one-line next action>

Open the handoff file for the full context.
```

## Output format (resume)

```
**Resumed from**: <path>
**Task**: <task summary>
**Git state match**: <YES | NO - <mismatch>>
**Progress**: <percent / phases>
**Blockers (still open)**: <count>
**Next**: <one-line next action>
```

## Output format (status)

```
**Latest handoff**: <path> (created <timestamp>)
**Task**: <task summary>
**Progress**: <percent / phases>
**Other handoffs**: <count>
```

## Hard rules

- Remaining-work items must be actionable, not vague ("finish the feature" is not actionable).
- Decisions include rationale; otherwise the next session re-debates them.
- Git state is captured even if "clean".
- The document stands alone; do not assume the original chat is available.
- Blockers list a recipient or mitigation, not just "waiting".

## Anti-patterns

- Vague remaining-work items.
- Missing decision rationale.
- Skipping git state capture.
- Documents that read like personal notes ("I think we agreed...").
- Handoffs without a recommended `Resume Instructions` section.

## Examples

```
adk-review-handoff --action create --task "Implementing OAuth2 flow for the API gateway"
```

```
adk-review-handoff --action resume --output .handoff/handoff-2026-04-14-1030.md
```

```
adk-review-handoff --action status
```

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/working-artifacts.md` | The .temp/ rule for intermediate artifacts. |

<!-- adk:references:end -->
