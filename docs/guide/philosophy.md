---
title: Philosophy
description: The operating principles behind adk — accuracy over coverage, advisor strategy, smallest correct change, plan/act tool enforcement, self-improving defaults, and the constitution.
order: 2
---

# Philosophy

`adk` is shaped for a Principal Engineer using AI agents (Claude Code, Cursor, Codex, Junie) as working partners — never as unchecked automation runners. Every skill optimizes for accuracy, smallest correct change, reviewability, and explicit approval before shared-state actions.

## Core principles

### 1. Verify before claiming

Skills read the file, inspect the diff, run the command, or query the metric before stating a fact. When evidence is missing, the skill says so — it doesn't invent. Every non-trivial claim cites `path:line` or a quoted source.

### 2. Smallest correct change

Implementation skills prefer the smallest change that satisfies the request and fits the repo. No drive-by refactors. No speculative abstractions. No cleanup mixed into unrelated work. The constitution forbids this at §V.

### 3. Question-first execution

Every skill starts with `shared/question-first.md`: up to 3 questions about scope, constraints, and (when relevant) scale verification. Even under `--auto`, the agent records the questions it *would* have asked and the defaults it picked. **Every user answer is training data** for the self-improvement loop.

### 4. Advisor strategy

Every skill is wrapped in `shared/advisor.md`: plan → clarify → present 2–4 trade-off options → defer to user → execute → validate → report. When the user says "I don't know" / "you decide", control hands off to `/adk-explain` — which teaches the user how to choose without picking for them.

### 5. Plan/act tool enforcement

`--plan` mode literally restricts the implementer to Read/Grep/Glob/WebFetch — no Edit, no Write, no Bash-mutate. This is enforced at the tool level, not by advisor prose. Inspired by Cline's plan/act modes.

### 6. Self-improving by design

Every non-trivial fork — every default offered, every user override, every question asked — gets one line in `~/.agents-devkit/improve/learning/decisions.jsonl`. `/adk-improve` reads these logs and proposes updates to your `~/.agents-devkit/config/overrides.yaml.defaults.*`. Your skills get more accurate as you use them.

### 7. Auto mode skips pauses, not safety

`--auto` removes per-phase approval pauses. It does NOT skip validation, does NOT hide failures, and does NOT allow auto-merges, protected force-pushes, branch deletion, rollbacks, or connector writes without explicit approval. Shared-state writes remain per-invocation gated.

### 8. One source of user truth

`~/.agents-devkit/config/overrides.yaml` is the single config file you maintain — workspaces, repos, data dictionaries, defaults, RAG config. The skills read it (and any `<repo>/.adk/overrides.yaml` override) at every run. No raw tokens in this file (regex-enforced); secrets live in env vars referenced by `${VAR}` placeholders.

### 9. The constitution is final

`shared/constitution.md` lists universal hard rules: no force-push, no merge from a skill, no monitor / dashboard / gate mutations, no PII queries, no `--no-verify`. Skills cannot override the constitution; `/adk-improve` cannot propose changes to it; only direct human edits to `shared/constitution.md` change it.

## What this means in practice

- Code changes are planned, scoped, edited (via SEARCH/REPLACE blocks), validated, and reported under `<repo>/.temp/<task-slug>/`.
- Reviews lead with severity and quoted evidence (`path:line` + ≤15 words), not opinion volume.
- Documentation claims are checked against source files before being written.
- Investigations pin time windows, name confidence levels per claim, and refuse single-source diagnoses.
- Hooks deterministically block forbidden operations — the safety isn't honor-system.

## Next

- [Installation](./getting-started/installation.md)
- [Multi-agent setup](./usage/multi-agent.md)
- [Reference](../reference/)
