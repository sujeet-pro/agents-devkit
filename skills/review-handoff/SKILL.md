---
name: review-handoff
description: Capture a structured session-handoff document so a paused or transferred task can resume without information loss - covering task summary, decisions with rationale, work completed, remaining work, blockers, key files, git state, and environment. Use when pausing long-running work, switching contexts, transferring to another developer or session, or preparing async collaboration. Do not use for project documentation (use adk-docs-write) or commit messages (use adk-publish-commit).
metadata:
  category: review
  kind: task
  layer: 5
  modes: [auto]
---

# ADK Review / Handoff

Standalone task skill under the `@adk:review` (a.k.a. `adk-review`) category router. Produces a self-contained handoff document that any session or person can resume without consulting the original chat.

## When to use

- Pausing a long-running task mid-stream.
- Switching to a higher-priority item with intent to resume later.
- Handing off in-progress work to a teammate.
- Resuming after a break or new session (use `resume` action to verify state).
- Documenting session progress for async collaboration.

## When NOT to use

- Project documentation -> `@adk:docs-write` (a.k.a. `adk-docs-write`)
- Commit messages or PR text -> `@adk:publish-commit` (a.k.a. `adk-publish-commit`)
- Planning new work from scratch -> `@adk:plan-roadmap` (a.k.a. `adk-plan-roadmap`)
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
5. **Validate (per `review-handoff-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/review-handoff-<slug>-validator.md` before the final report.
6. **Deliver** - write the handoff file; print the file path, progress summary, and the recommended next step.

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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/review-handoff-clarifying-questions.md`) and reports the choices.

1. **What is the next intended owner (yourself later, another agent, a human)?** — _How to pick:_ Adjust verbosity: terse for self, full context for stranger handoff.
2. **Should the handoff include suggested commands to resume, or only state?** — _How to pick:_ Include commands when the next owner is an agent or a junior dev. State-only when the owner already knows the workflow.

**Default report:** Status block (done / in-flight / blocked) + open questions + artifact map + recommended next step.

**Detailed report (on request or `--verbose`):** Add: chronological session log, every decision made and its rationale, environment snapshot (branch, dirty files, env vars set).

**Artifact:** `handoff-document` — Markdown handoff. Sections: Context, Status (Done / In-Flight / Blocked), Artifacts (paths + purpose), Open Questions, Recommended Next Step (skill + inputs), Environment Snapshot.

**Artifact path:** .temp/reports/handoff-<date>-<slug>.md

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/review-handoff-clarifying-questions.md`) and reports the choices.

1. **What is the next intended owner (yourself later, another agent, a human)?** — _How to pick:_ Adjust verbosity: terse for self, full context for stranger handoff.
2. **Should the handoff include suggested commands to resume, or only state?** — _How to pick:_ Include commands when the next owner is an agent or a junior dev. State-only when the owner already knows the workflow.

## Default vs detailed output

**Default report:** Status block (done / in-flight / blocked) + open questions + artifact map + recommended next step.

**Detailed report (on request or `--verbose`):** Add: chronological session log, every decision made and its rationale, environment snapshot (branch, dirty files, env vars set).

**Artifact:** `handoff-document` — Markdown handoff. Sections: Context, Status (Done / In-Flight / Blocked), Artifacts (paths + purpose), Open Questions, Recommended Next Step (skill + inputs), Environment Snapshot.

**Artifact path:** .temp/reports/handoff-<date>-<slug>.md

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/review-handoff-anti-patterns.md` | Things to avoid when running this skill. |
| `references/review-handoff-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/review-handoff-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/review-handoff-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/review-handoff-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/review-handoff-persona.md` | The agent persona that drives this skill. |
| `references/review-handoff-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/review-handoff-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
