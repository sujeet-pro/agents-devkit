---
title: Hooks
description: Automatic safety, validation, and session-start checks ADK installs around an agent session.
order: 5
---

# Hooks

Hooks are the non-negotiable safety rails around an agent session. Unlike skills and subagents (which the user or model chooses to invoke), hooks run **automatically** at specific lifecycle events. They cannot be skipped with `--auto`, cannot be turned off by a chatty subagent, and cannot be reasoned around.

ADK ships **one hand-authored hook file per supported runtime**. There is no shared source — each runtime's hook schema is different, so its file is the source of truth.

## What ADK hooks do

The shipped hooks cover three concerns:

1. **Block dangerous shell commands.** Force-pushing to `main`/`master`, `git reset --hard` on `main`/`master`, `rm -rf /`, `git clean -fd` at the repo root, deleting `main`/`master`. These commands are blocked before the shell runs them.
2. **Validate SKILL.md edits.** When a `SKILL.md` is written or edited, the hook checks the frontmatter follows ADK rules: spec-allowed keys only, `name` matches folder, `description` length under 1024.
3. **Enforce end-of-turn validation.** When the agent tries to stop, the hook checks whether the user's original request was actually addressed and whether the validation phase ran. A session that ends with "done" but no validation evidence is sent back for another turn.

There is also a session-start banner that reminds the agent where the canonical guidance lives (`AGENTS.md`).

## Per-runtime files

| File | Runtime | Install target |
| --- | --- | --- |
| [`hooks/claude.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/hooks/claude.json) | Claude Code | `<root>/.claude/settings.json` |
| [`hooks/cursor.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/hooks/cursor.json) | Cursor | `<root>/.cursor/hooks.json` |
| [`hooks/codex.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/hooks/codex.json) | Codex | `<root>/.codex/hooks.json` (plus a feature flag in `config.toml`) |

Why three files instead of one? The hook event vocabulary and execution model differ per runtime.

### Claude

Claude exposes named hook events (`PreToolUse`, `PostToolUse`, `Stop`, `SessionStart`) and supports two hook types:

- `prompt` — send the matched context to a language model and use its JSON reply to block or allow.
- `command` — run a shell command.

Claude hooks use `matcher` fields to restrict which tool invocations a hook applies to (`"matcher": "Bash"`, `"matcher": "Edit|Write"`).

### Cursor

Cursor uses a smaller event surface (`beforeShellExecution`, `afterFileEdit`, `stop`, `sessionStart`) and requires a `model` hint plus a `timeout` on prompt-type hooks. Cursor hooks return `{ "ok": true }` or `{ "ok": false, "reason": "..." }` instead of Claude's `decision` vocabulary.

### Codex

Codex hooks are still experimental. They require enabling `[features] codex_hooks = true` in `~/.codex/config.toml` before they fire. Codex does not yet support prompt-type hooks, so ADK's Codex hooks are implemented as inline `python3 - <<'PY'` scripts that parse the tool payload from stdin and write a JSON decision to stdout.

## Why the copies are necessary

A single "generic" hook file would not run in any of the three harnesses. Each provider's file is the source of truth for that provider — there is no projection script.

## How to install

`adk-install` symlinks each chosen hook file into the runtime's expected location:

- `hooks/claude.json` → `<root>/.claude/settings.json`
- `hooks/cursor.json` → `<root>/.cursor/hooks.json`
- `hooks/codex.json` → `<root>/.codex/hooks.json`

For Codex, also add to `~/.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

## Validate

`npm run validate` parses each hook JSON and confirms it is structurally sound.

## How hooks interact with `--auto`

`--auto` removes *workflow-level* approval pauses inside a skill. It never removes hook-level safety. If the agent tries to force-push in `--auto` mode, the hook still blocks it. If the agent tries to stop without validation in `--auto` mode, the hook still sends the turn back.

This is deliberate. Hooks are the layer below the skill. A skill can choose to skip its own confirmations; it cannot ask a hook to ignore `rm -rf /`.

## When to modify a hook

Edit a hook when:

- You find a new class of dangerous command ADK should block by default.
- You want to extend the SKILL.md frontmatter validation with a new required field.
- You want to tighten or loosen the end-of-turn validation signal.

Edit the file directly inside `hooks/<runtime>.json`. There is no projection script.

## Related

- [Philosophy](./philosophy.md) — why hooks exist as the layer below `--auto`.
- [Skill Anatomy](./skill-anatomy.md) — how skill validation phases complement hooks.
