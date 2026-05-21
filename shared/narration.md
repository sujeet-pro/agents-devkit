# shared/narration.md — narrate progress, end with a summary

> Every adk skill prints its progress in real time and closes with a structured summary. The user should never have to guess what the skill is doing or why it picked a particular path. Loaded by every skill; referenced from `shared/advisor.md` (Phase G) and the constitution §IV.

## Why

`--auto` (the default) means "don't wait for me", not "don't tell me". A skill that runs silently for two minutes and then prints "done" is broken — the user can't intervene, can't catch a wrong assumption, can't trust the output. Narration is the substitute for the question-first wait.

## What to print, when

| Moment | Format | Example |
|---|---|---|
| Skill start | `▶ /adk-<skill> <input>` | `▶ /adk-pr-review https://github.com/acme/foo/pull/42` |
| Phase boundary | `  · <phase-name>` | `  · Phase 1: worktree (serialized)` |
| Auto-defaulted fork | `  → <fork>=<choice>  (reason)` | `  → scope=vertical-slice  (prior 3 tickets in this repo chose vertical-slice)` |
| Non-trivial side effect (running a script, calling an MCP, spawning claude -p) | `  $ <command summary>` | `  $ git fetch --all --prune  (clone-lock held)` |
| Refusal / gap | `  ⚠ <gap>: <reason>` | `  ⚠ statsig: unreachable — feature-flow tracing falls back to grep` |
| Posting / mutation gate | `  ❓ About to <action>. OK?` (in both modes; constitution §I.4) | `  ❓ About to post 4 comments to PR #42. OK to proceed?` |
| Completion | `▣ done in <elapsed>` followed by the summary block | `▣ done in 2m14s` |

Use plain ASCII when the host might not be a UTF-8 terminal:

```
> /adk-pr-review …
  - Phase 1: worktree (serialized)
  > scope=vertical-slice (prior 3 tickets in this repo chose vertical-slice)
  $ git fetch --all --prune  (clone-lock held)
  ! statsig: unreachable — feature-flow tracing falls back to grep
  ? About to post 4 comments to PR #42. OK to proceed?
  # done in 2m14s
```

Skills can pick either glyph set; consistency within a single run is what matters.

## End-of-run summary (mandatory)

Every skill ends by printing AND writing-to-file a structured summary. Path: `<task_dir>/report.md`. Stdout shows the same content (or a 10-line abbreviated version, with a pointer to the full report).

Required sections (in this order):

```markdown
# <skill> — <task-slug>

## TL;DR
<two sentences max. The reader should know if this was a success / partial / failure
without scrolling.>

## Risk / Blockers / Follow-ups
- <any blocker or risk the skill surfaced>  · (none if truly none — say "none" explicitly)

## What got done
- <bullet — concrete, with file:line or URL evidence>

## Files touched
- <relative-path> · <one-line summary of the change>
- (write "none" if the skill made no file changes)

## Files intentionally not touched
- <relative-path> · <why this was out of scope despite being adjacent>
- (write "none" if nothing scope-adjacent was noticed)

## What got skipped (and why)
- <gap>: <reason>
- <e.g. "statsig MCP unreachable; feature-flow used grep fallback (lower confidence)">
- (write "none" if truly none)

## Decisions made this run
- <fork>: <chose X> — [auto-defaulted | user-answered | inferred] (one-line reason)

## Evidence
- <task_dir>/<file>                       # artifacts the user can inspect
- <link to changed file / PR / dashboard>

## Next-best action
- <one or two suggested next skills / commands>
```

Two of those sections are **required even when empty**: *Risk / Blockers / Follow-ups* and *What got skipped*. The absence of a section is ambiguous; an explicit "none" is not.

## How to actually do this in a skill

Two options, increasing in formality:

1. **Print + echo.** The skill's orchestrator script prints to stderr; the host agent passes the same lines to the user-facing chat. Cheapest and current default for everything in `skills/adk-pr-review/scripts/` + `skills/adk-cli/scripts/`.
2. **In-skill flair.** For skills where the model authors the narration (e.g. `/adk-explain` walking the user through tie-breakers), the SKILL.md tells the model: "narrate each step inline, then close with the summary template above".

## Failure modes (when narration goes wrong)

- **Wall of text in auto mode.** Auto narration is one short line per decision. If a phase is going to take more than 30 s without a status update, print a "still working: <step>" tick every 30 s.
- **Hiding the assumption.** Every auto-defaulted choice MUST be narrated. "I assumed X" must appear before X has consequences, not after.
- **Print after action.** Narrate BEFORE the side effect, not after. Mutations and shared-state writes go through the constitution §I.4 gate which always asks.

## Cross-skill dependencies

- Constitution §IV.5 — reports lead with risk, bury bookkeeping. This contract enforces that ordering.
- `shared/question-first.md` — describes when to ask vs auto. This file describes how to TELL the user what auto picked.
- `shared/advisor.md` Phase G — refers back here for the report shape.
