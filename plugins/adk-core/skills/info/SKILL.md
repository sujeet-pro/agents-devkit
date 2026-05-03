---
name: info
description: |
  Read and merge ~/.config/adk/*.md into a single structured JSON view that other skills consume. Use when an outer skill needs current operator/repo/MCP context, when debugging "why did the skill pick service X?", or when the user asks "what does adk know about me?". Three sub-modes: dump-all (the full merged JSON), single-topic (just one ~/.config/adk/<topic>.md), single-key (one dotted-path value). Wraps the bin/adk-info script. Do NOT use to write or modify the meta-info files (use /adk-core:setup for that). Do NOT use to print env-var values (this skill never prints secrets — it shows present/missing only).
metadata:
  category: meta
  kind: task
  modes: [auto, interactive]
  layer: 0
argument-hint: "[<topic>] [<key>] [--check] [--missing] [--resolve-env]"
---

# info — read & merge meta-info

Read-only wrapper around the `bin/adk-info` script. Skills shell out to this to fetch operator / repo / MCP context.

## When to use

- An outer skill is gathering inputs (e.g. `investigate-datadog` needs `datadog.md.site`).
- Debugging "why did adk pick service X?" — dump `datadog.md.service_aliases`.
- The user asks `/adk-core:info` to see what's loaded.

## When NOT to use

- Need to write meta-info → `/adk-core:setup`.
- Need to print actual env-var values — this skill never prints secrets, only their presence.

## Common prompts

- "what does adk know?"
- "show config"
- "show datadog config"
- "what service alias is `checkout`?"

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<topic>` | optional | dump all topics |
| `<key>` | optional (with topic) | dump just that key (dotted path) |
| `--check` | optional | validate every file's schema; exit non-zero on errors |
| `--missing` | optional | list keys that skills want but aren't set |
| `--resolve-env` | optional | substitute `${ENV_VAR}` placeholders (won't print missing) |

## Workflow

```
Phase 1 — preflight
  - Verify `bin/adk-info` exists and is executable.
  - Verify `~/.config/adk/` exists when reading real topics.
  - If --resolve-env is set, report missing env vars but never print values.

Phase 2 — execute
  - Shell out to `bin/adk-info` with the right args.
```

The skill is a thin documentation wrapper; the script does the work.

| User invocation | Shell-out |
| --- | --- |
| `/adk-core:info` | `adk-info` |
| `/adk-core:info datadog` | `adk-info datadog` |
| `/adk-core:info datadog site` | `adk-info datadog site` |
| `/adk-core:info --check` | `adk-info --check` |
| `/adk-core:info --missing` | `adk-info --missing` |

## Persona

> Read-only librarian. Surface facts; don't invent them.

See `references/persona.md`.

## Constitution

**Must do:**

1. Flag fields with `${ENV_VAR}` placeholders that don't resolve (when `--resolve-env`).
2. Always preserve the file's literal content unless `--resolve-env`.
3. Validate via `adk-info --check` if asked.

**Must not do:**

1. Modify any file.
2. Print env-var VALUES — only their presence/absence.
3. Cache data across invocations (always read fresh).

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Printing env-var values (they're secrets).
- Inventing fields that don't exist in the file.
- Treating an unset field as an error (fields are optional unless explicitly required).

## Output

JSON on stdout (or markdown summary if invoked interactively).

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | The librarian persona |
| `references/workflow.md` | Shell-out matrix |
| `references/output-format.md` | JSON schema per topic |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked invocations |
| `references/modes.md` | Mode contract |
| `references/interaction-contract.md` | Canonical interaction contract |
