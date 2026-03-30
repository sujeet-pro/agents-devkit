---
name: use
description: "[orchestrator] [pipeline] Use when starting any task to expand intent, identify the right DevKit skills, confirm the plan early with the user, and then execute the approved workflow"
user-invocable: true
argument-hint: "<task description> [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: orchestrator
---

<CHILD-AGENT-STOP>
If you were launched as a child agent for a focused task, skip this skill.
</CHILD-AGENT-STOP>

# DevKit Orchestrator

`/use` is the default entry point for DevKit. Start here unless the user explicitly names a specific skill and clearly wants to bypass routing.

This skill must make the workflow human-in-the-loop as early as possible:

1. expand the user's intent before doing real work
2. show concise visible reasoning
3. identify skills, scripts, tools, and MCPs
4. confirm the approach and plan with the user
5. execute without asking for more information unless reality changes

Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`, `references/intent-expansion.md`.

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<task description>` | free-text | required | Describe what you want to accomplish |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level for all downstream skills |

### Behavior Variations

- **Trivial tasks**: inline intent confirmation, abbreviated plan, direct execution, quick validation
- **Small tasks**: inline or lightweight confirmation, light research, brief plan approval, execution, verification
- **Medium tasks**: full intent review, research/options, interactive approach selection, approved implementation plan, tracked execution
- **Large tasks**: same as medium plus Principal Engineer check, stronger questioning, phased execution, and progress dashboard
- **Explicit skill invocation by the user**: keep that skill in the pipeline, but still run Phase 0 and plan-before-execute
- **Direct `/review`, `/develop`, `/write`, etc.**: those skills may still be called directly, but this orchestrator should be the preferred route for general prompts

### Examples

```text
/use review this PR: https://github.com/org/repo/pull/42
/use implement user authentication with OAuth2
/use write an ADR for our caching strategy
/use debug the failing CI pipeline
/use audit this codebase for security and performance
```

## Core Rules

1. Run **Phase 0: Intent Expansion** before selecting the final pipeline.
2. Make reasoning visible, but concise and decision-oriented.
   Never dump hidden chain-of-thought or a long internal monologue.
3. For Medium and Large work, challenge the approach like a Principal Engineer:
   do we need this, what is the simplest version, what are the alternatives, and what is the maintenance cost?
4. The user must approve the direction before execution starts.
5. For non-trivial work, execution starts only after an approved plan exists.
6. Every downstream skill invocation must be explainable from the confirmed intent.

## Phase 0: Intent Expansion

Start by expanding the prompt using `references/intent-expansion.md`.

For Medium and Large work, use `intent-analyst` to pressure-test the prompt expansion before presenting it to the user.

### What to Produce

Create a compact intent summary with:

- one-line goal
- 2-4 reasoning bullets
- assumptions and ambiguities
- required skills in order
- required tools, scripts, and MCPs with status
- complexity and rationale
- PE check for Medium or Large work

### Visible Reasoning Format

Use this style:

```text
Intent:
- Goal: <one line>
- Why this pipeline: <reasoning bullet>
- Skills: <skill list with short why>
- Tools/MCPs: <available / missing / optional>
- Complexity: <level> because <brief rationale>
```

### Confirmation

- **Trivial / Small**: inline confirmation is enough
- **Medium / Large**: write `intent.json`, launch `python3 ${CLAUDE_SKILL_DIR}/scripts/tui/intent_confirm.py <session_dir>`, and wait for approval or edits

If the user simplifies or edits the intent, re-run the expansion and only then continue.

## Skill Routing

Load `references/routing-patterns.md` for the full routing table and parameter resolution rules.

Pick the smallest useful pipeline that covers the confirmed intent. Resolve parameters by reading each skill's `argument-hint` and `Parameters` section, inferring what the prompt provides, and marking the rest as defaults or needing confirmation.

## Complexity and Phase Use

Use `references/workflow-6phase.md` as the source of truth.

- **Trivial**: inline intent confirm, no separate options phase, direct execution
- **Small**: inline intent confirm, light research, brief planning, direct execution
- **Medium**: full Phase 0-5
- **Large**: full Phase 0-5 plus PE check and phased execution

When uncertain, classify as Medium.

## Approach Selection

For Medium and Large work, do not lock the pipeline silently.

1. research enough to present 2-3 viable options
2. call out the simplest option explicitly
3. explain pros, cons, effort, and risk
4. let the user pick, mix, or simplify

Use `python3 ${CLAUDE_SKILL_DIR}/scripts/tui/approach_select.py <session_dir>` when a TUI is appropriate.

## Planning Gate

Execution must follow an approved plan.

### Plan Expectations

The approved plan must include:

- tasks or waves
- affected files or deliverables
- verification steps
- explicit sequencing when dependencies exist

For Medium and Large work:

1. draft the plan
2. review it with `plan-reviewer`
3. let the user approve it
4. only then execute it

Use `python3 ${CLAUDE_SKILL_DIR}/scripts/tui/plan_approve.py <session_dir>` for Medium and Large tasks.

## Execution

Once the user approves the plan:

1. invoke the selected downstream skills in order
2. keep progress visible at natural checkpoints
3. avoid asking for more information unless the approved assumptions are broken by reality
4. for Medium and Large execution, write progress updates, use `progress-tracker` to summarize status, and optionally launch `python3 ${CLAUDE_SKILL_DIR}/scripts/tui/progress_dashboard.py <session_dir>`

## Validation and Learning

End every `/use` run with:

- what was done
- what was verified
- what changed from the initial idea, if anything
- a short “what to know” note so the user learns why the chosen path made sense

## Output Format

Adapt output to `--verbosity`, but keep it concise.

- **short**: one-line summary + next action
- **standard**: intent, approved pipeline, progress, outcome
- **detailed**: standard output plus decision notes and artifact paths

## Adjacent Skills

- `/plan` — use directly when the user explicitly asks to brainstorm, write, execute, or track a plan
- `/team` — use when the user explicitly wants multi-model or multi-agent orchestration as the primary task
