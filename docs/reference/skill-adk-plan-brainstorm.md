---
title: 'adk-plan-brainstorm'
description: 'Run iterative brainstorming to close ambiguity, weigh 2-3 viable options, choose blast radius and confidence target, and route into the right next skill (spec, design, roadmap, build, write-docs). Use when a task has real ambiguity about goal, scope, or approach and the user wants help picking a direction before any code or doc is written. Do not use for trivial decisions with one obvious path.'
skill_name: adk-plan-brainstorm
category: task
---
# ADK Plan / Brainstorm

Standalone task skill under the `adk-plan` category router. Closes design ambiguity by capturing current state, target state, blast radius, and confidence target, surfacing 2-3 options, and recommending the next route.

## When to use

- The request still has direction-changing ambiguity.
- Multiple valid approaches exist with real trade-offs.
- The acceptable blast radius (`surgical` / `bounded` / `transformative`) is not yet chosen.
- The user wants an iterative question-answer loop before locking direction.

## When NOT to use

- Pure fact-finding with no decision -> `adk-plan-research`
- Direction is already locked, just write the artifact -> `adk-plan-spec` / `adk-plan-design` / `adk-plan-roadmap`
- Implementation -> `adk-build-feature`
- One obvious path with low risk

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task>` | yes | What needs to be decided |
| `<downstream skill>` | optional | Where this brainstorm hands off (`spec`, `design`, `roadmap`, `build`, `write-docs`) |
| `<confidence target>` | optional | 80 / 90 / 95 - finalize threshold |
| `<change tolerance>` | optional | `surgical` / `bounded` / `transformative` |
| `<artifact>` | optional | `none` / `proposal` / `prd` / `rfc` / `hld` / `lld` / `tdd` / `plan` |
| `<scope>` | optional | Path to limit repo inspection |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate the task, the downstream skill, the confidence target, the change tolerance, and the artifact preference. Approval gate unless `--auto`.
2. **Capture state** - record `currentState` (what is true now, with file/URL evidence) and `targetState` (what should be true after the work).
3. **Research unknowns** - for each direction-changing unknown, gather repo evidence first, then primary external sources. Mark each finding `Verified` / `Inferred` / `Open`.
4. **Surface options** - present 2-3 viable paths with one-line trade-offs each. Approval gate unless `--auto`.
5. **Iterate questions** - ask follow-up questions until remaining ambiguity is no longer direction-changing.
6. **Validate (per `plan-brainstorm-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/plan-brainstorm-<slug>-validator.md` before the final report.
7. **Finalize direction** - check confidence against the target. Either finalize or explicitly accept the gap with the user.
7. **Recommend route** - name the next skill (`adk-plan-spec`, `adk-plan-design`, `adk-plan-roadmap`, `adk-build-feature`, `adk-build-refactor`, `adk-build-migrate`, `adk-frontend-design`, `adk-docs-write`).

## Required state

By the end of the brainstorm, every one of these must have a concrete value:

- `currentState`
- `targetState`
- `changeTolerance`
- `desiredConfidence`
- `currentConfidence`
- `chosenDirection` (or explicit "still open" with reason)
- `openQuestions`
- `nextRoute`

## Option presentation

Each option block should be 3-5 lines:

```
### Option A: <short label>
- Approach: <one sentence>
- Pros: <2-3 bullets>
- Cons: <2-3 bullets>
- Blast radius: <surgical | bounded | transformative>
- Confidence we can deliver: <low | medium | high>
```

## Output format

```
## Brainstorm: <task summary>

## Direction
<recommended path and why> (or "still open: <reason>")

## Current State
<what exists today, with evidence>

## Target State
<what should be true after the work>

## Options
### Option A: <label>
...
### Option B: <label>
...

## Confidence
- Current: <score>
- Target: <score>
- Gap accepted? <yes/no with rationale>

## Open Questions
- <question>

## Recommended Route
-> <next skill>

Need more detail on any option or trade-off?
```

## MCP enhancement (optional)

If a `brainstorming` MCP server is configured, prefer it as the session store - it gives structured iteration support and a cleaner handoff. If absent, run the workflow above manually and announce once:

`Note: brainstorming MCP server not configured. Running the manual workflow.`

## Anti-patterns

- Producing one option dressed as three. Make options meaningfully different.
- Locking direction below the confidence target without explicit user acceptance.
- Skipping `currentState` / `targetState` capture and jumping to options.
- Drifting into implementation. Hand off to a build skill instead.
- Asking >3 questions at once - iterate one or two at a time.

## Examples

| User says | Reframe |
| --- | --- |
| "Should we use TanStack Router or React Router?" | currentState = today's router setup; targetState = chosen router with rationale; options A/B; route to `adk-plan-design` if architectural impact is high, else `adk-plan-roadmap`. |
| "Refactor the auth module" | Real question is *what* about auth. Capture pain points, target invariants, blast radius; surface 2-3 refactor scopes; route to `adk-build-refactor`. |

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-brainstorm-clarifying-questions.md`) and reports the choices.

1. **What is the current state today, with one piece of evidence?** — _How to pick:_ Cite a file path, URL, command output, or screenshot. Without evidence the brainstorm is speculative.
2. **What change tolerance is acceptable: surgical, bounded, or transformative?** — _How to pick:_ Surgical = touch only what must change; reversible in <1h. Bounded = touch one subsystem; reversible in <1d. Transformative = touch many subsystems; reversibility hard. Pick the smallest that still meets the goal.
3. **What confidence threshold do you want before locking the direction (80/90/95)?** — _How to pick:_ Production-safe surgical = 95. Standard feature/refactor = 90. Exploratory or personal = 85.
4. **What artifact should this brainstorm produce: none, proposal, PRD, RFC, HLD, LLD, TDD, or plan?** — _How to pick:_ None = continue inside the calling skill. Proposal/RFC/HLD/LLD/TDD = adk-docs-write. PRD = adk-plan-spec. Plan = adk-plan-roadmap.

**Default report:** Recommended direction + 2-3 option blocks (Pros/Cons/BlastRadius/Reversibility), confidence status, recommended next skill.

**Detailed report (on request or `--verbose`):** Add: full currentState/targetState narratives, list of unknowns each option resolves, decision matrix scoring options against constraints, dropped options with reason.

**Artifact:** `brainstorm-summary` — Markdown report. Sections: Direction, Current State, Target State, Options (A/B/C with the standard option block), Confidence, Open Questions, Recommended Route.

**Artifact path:** .temp/plans/brainstorm-<slug>.md (also keep raw notes in .temp/notes/brainstorm-<slug>-notes.md)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-brainstorm-clarifying-questions.md`) and reports the choices.

1. **What is the current state today, with one piece of evidence?** — _How to pick:_ Cite a file path, URL, command output, or screenshot. Without evidence the brainstorm is speculative.
2. **What change tolerance is acceptable: surgical, bounded, or transformative?** — _How to pick:_ Surgical = touch only what must change; reversible in <1h. Bounded = touch one subsystem; reversible in <1d. Transformative = touch many subsystems; reversibility hard. Pick the smallest that still meets the goal.
3. **What confidence threshold do you want before locking the direction (80/90/95)?** — _How to pick:_ Production-safe surgical = 95. Standard feature/refactor = 90. Exploratory or personal = 85.
4. **What artifact should this brainstorm produce: none, proposal, PRD, RFC, HLD, LLD, TDD, or plan?** — _How to pick:_ None = continue inside the calling skill. Proposal/RFC/HLD/LLD/TDD = adk-docs-write. PRD = adk-plan-spec. Plan = adk-plan-roadmap.

## Default vs detailed output

**Default report:** Recommended direction + 2-3 option blocks (Pros/Cons/BlastRadius/Reversibility), confidence status, recommended next skill.

**Detailed report (on request or `--verbose`):** Add: full currentState/targetState narratives, list of unknowns each option resolves, decision matrix scoring options against constraints, dropped options with reason.

**Artifact:** `brainstorm-summary` — Markdown report. Sections: Direction, Current State, Target State, Options (A/B/C with the standard option block), Confidence, Open Questions, Recommended Route.

**Artifact path:** .temp/plans/brainstorm-<slug>.md (also keep raw notes in .temp/notes/brainstorm-<slug>-notes.md)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/plan-brainstorm-anti-patterns.md` | Things to avoid when running this skill. |
| `references/plan-brainstorm-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/plan-brainstorm-brainstorming-workflow.md` | Required inputs, confidence defaults, iteration loop, artifact routing. |
| `references/plan-brainstorm-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/plan-brainstorm-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/plan-brainstorm-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/plan-brainstorm-mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/plan-brainstorm-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/plan-brainstorm-persona.md` | The agent persona that drives this skill. |
| `references/plan-brainstorm-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/plan-brainstorm-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/plan-brainstorm-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
