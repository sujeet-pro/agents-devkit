---
title: Hooks
description: Automatic safety, validation, and session-start checks ADK installs around an agent session via the Claude plugin hook spec.
order: 5
---

# Hooks

Hooks are the non-negotiable safety rails around an agent session. Unlike skills and subagents (which the user or model chooses to invoke), hooks run **automatically** at specific lifecycle events. They cannot be skipped with `--auto`, cannot be turned off by a chatty subagent, and cannot be reasoned around.

The `adk` Claude Code plugin ships **one hook configuration file** at [`hooks/hooks.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/hooks/hooks.json), referenced from `.claude-plugin/plugin.json`. The schema is defined in the [Claude Code plugins reference — Hooks](https://code.claude.com/docs/en/plugins-reference#hooks).

> [!NOTE]
> ADK targets Claude Code and Claude Desktop only. Hooks are managed exclusively through the Claude plugin spec — there is no projection into other harnesses.

## What ADK hooks do

The shipped hooks cover four concerns mapped to four Claude Code lifecycle events:

| Event | Matcher | Type | Concern |
| --- | --- | --- | --- |
| `PreToolUse` | `Bash` | `prompt` | Block dangerous shell ops (force-push to `main`/`master`, `git reset --hard` on `main`/`master`, `rm -rf /`, `git clean -fd` at repo root, deleting `main`/`master`, unprompted `gh pr merge`). |
| `PostToolUse` | `Edit\|Write` | `prompt` | When a `SKILL.md` is written or edited, verify the YAML frontmatter has both `name` and `description`, and that `name` equals the folder basename. |
| `Stop` | (any) | `prompt` | When the agent tries to stop, confirm Phase 4 (post-execution validation) was logged to `.temp/<task-slug>/validation/` or `.temp/notes/` if a four-phase skill ran. |
| `SessionStart` | (any) | `command` | `cat ${CLAUDE_PLUGIN_ROOT}/bin/canonical/system-prompt.md` — injects the canonical ADK primer into every session as a plugin-level "system prompt". |

The four [hook types Claude Code supports](https://code.claude.com/docs/en/plugins-reference#hooks) are `command`, `prompt`, `http`, and `agent`. ADK uses `prompt` for the policy hooks (each is evaluated by an LLM that returns `{decision, reason}` or `{ok, reason}` JSON) and `command` for the SessionStart primer.

## Adding to the system prompt

There is no documented Claude plugin field for "global system prompt." The supported pattern is a **`SessionStart` hook of type `command`** whose stdout is captured and added to the conversation. ADK uses this pattern:

```52:60:hooks/hooks.json
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "cat \"${CLAUDE_PLUGIN_ROOT}/bin/canonical/system-prompt.md\""
          }
        ]
      }
```

The single source of truth is [`bin/canonical/system-prompt.md`](https://github.com/sujeet-pro/agents-devkit/blob/main/bin/canonical/system-prompt.md). Edit that one file, and every session gets the new primer on next start.

## `${CLAUDE_PLUGIN_ROOT}` substitution

Every command in `hooks/hooks.json` references the plugin via the `${CLAUDE_PLUGIN_ROOT}` environment variable, which Claude Code substitutes inline (see [Environment variables](https://code.claude.com/docs/en/plugins-reference#environment-variables)). This is the only correct way to reference plugin-bundled files because plugins are copied to `~/.claude/plugins/cache` at install time — relative paths from CWD will not work.

Hook script processes also receive `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` as environment variables.

## How hooks interact with `--auto`

`--auto` removes *workflow-level* approval pauses inside a skill. It never removes hook-level safety. If the agent tries to force-push in `--auto` mode, the `PreToolUse:Bash` hook still blocks it. If the agent tries to stop without validation in `--auto` mode, the `Stop` hook still sends the turn back.

This is deliberate. Hooks are the layer below the skill. A skill can choose to skip its own confirmations; it cannot ask a hook to ignore `rm -rf /`.

## When to modify a hook

Edit [`hooks/hooks.json`](https://github.com/sujeet-pro/agents-devkit/blob/main/hooks/hooks.json) when:

- You find a new class of dangerous command ADK should block by default — extend the `PreToolUse:Bash` prompt.
- You want to extend the `SKILL.md` frontmatter validation — extend the `PostToolUse:Edit|Write` prompt.
- You want to tighten or loosen the end-of-turn validation signal — extend the `Stop` prompt.
- You want to add or change the plugin-level system prompt — edit `bin/canonical/system-prompt.md` (the `SessionStart` hook stays the same).

After editing, run `npm run validate` then `/reload-plugins` inside Claude.

## Validate

```bash
npm run validate                    # bin/adk-validate parses hooks.json
claude plugin validate .            # full Claude validator: plugin.json, hooks, skill/agent frontmatter
```

The Claude validator catches issues like a malformed `hooks/hooks.json` (which would prevent the entire plugin from loading) and per-skill YAML frontmatter problems. See the full error list in the [marketplace troubleshooting reference](https://code.claude.com/docs/en/plugin-marketplaces#marketplace-validation-errors).

## Related

- [Philosophy](./philosophy.md) — why hooks exist as the layer below `--auto`.
- [Skill Anatomy](./skill-anatomy.md) — how skill validation phases complement hooks.
- [Plugins reference — Hooks](https://code.claude.com/docs/en/plugins-reference#hooks) — Anthropic's authoritative spec.
