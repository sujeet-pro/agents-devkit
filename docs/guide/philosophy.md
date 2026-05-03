---
title: Philosophy
description: The operating principles behind the adk marketplace.
order: 1
---

# Philosophy

`adk` is shaped for a Principal Engineer using Claude as a working partner, not
as an unchecked automation runner. The marketplace optimizes for accuracy,
small correct changes, reviewability, and explicit approval before shared-state
actions.

## Core Principles

### Verify Before Claiming

Skills should read the file, inspect the diff, run the command, or query the
metric before stating a fact. When evidence is missing, the skill should say so.

### Smallest Correct Change

Implementation skills prefer the smallest change that satisfies the request and
fits the repo. No drive-by refactors, speculative abstractions, or cleanup mixed
into unrelated work.

### Prompt Expansion First

Natural language prompts are often fuzzy. `adk-core:auto` and each direct skill
start by restating the request, resolving entities from `~/.config/adk/*.md`,
and choosing the smallest skill chain that matches the job.

### Preflight Before Work

Skills check required CLI tools, MCP servers, workspace connectors, env vars,
meta-info files, and git state before the main work begins. Missing required
dependencies stop the run with a concrete fix.

### Auto Mode Skips Pauses, Not Safety

`--auto` removes per-phase approval pauses. It does not skip validation, does
not hide failures, and does not allow automatic merges, protected force-pushes,
branch deletion, rollbacks, or connector writes without explicit approval.

### One Skill, One Action

Each skill has a narrow job. Composite workflows are explicit chains, such as
incident investigation followed by bugfix followed by local review.

### Local Meta-Info, No Secrets In Docs

Company and repo specifics live in `~/.config/adk/*.md`. Those files can
reference env vars by name, but raw tokens stay in the shell environment or a
future `userConfig` secret store.

## What This Means In Practice

- Code changes are planned, scoped, edited, validated, and reported.
- Reviews lead with severity and evidence, not volume.
- Documentation claims are checked against source files before being written.
- Investigations pin windows, environments, sources, and confidence.
- Generated working artifacts live under `.temp/task-<slug>/`, not in the repo.

## Next

- [Installation](./getting-started/installation.md)
- [Getting Started](./getting-started/)
- [Reference](../reference/)
