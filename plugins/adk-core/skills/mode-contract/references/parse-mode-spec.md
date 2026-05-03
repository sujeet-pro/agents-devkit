# `parse-mode.sh` — specification

## Sourcing

```bash
source "${CLAUDE_PLUGIN_ROOT}/skills/mode-contract/scripts/parse-mode.sh"
parse_mode "$@"
```

After `parse_mode` returns 0:

| Env var | Value |
| --- | --- |
| `ADK_MODE` | `auto` (default) or `interactive` |
| `ADK_FIX` | `0` (default) or `1` |
| `ADK_REMAINING` | bash array of args that weren't consumed |

## Behavior

- `--auto` → `ADK_MODE=auto`, sets `saw_auto=1`.
- `-i` or `--interactive` → `ADK_MODE=interactive`, sets `saw_interactive=1`.
- `--fix` → `ADK_FIX=1`.
- `--` → terminates flag parsing; everything after is collected into `ADK_REMAINING`.
- Anything else → collected into `ADK_REMAINING` for the calling skill to handle.

## Errors

If both `saw_auto=1` and `saw_interactive=1`:

```
ERROR: --auto and -i / --interactive are mutually exclusive
```

→ `parse_mode` returns 2; the calling skill should propagate the failure.

## Edge cases

- `parse_mode` (with no args) → `ADK_MODE=auto`, `ADK_FIX=0`, empty remaining.
- `parse_mode --fix` → `ADK_MODE=auto`, `ADK_FIX=1`. (`--fix` alone implies `--auto` for the apply step.)
- `parse_mode -i --fix` → `ADK_MODE=interactive`, `ADK_FIX=1`. Per-phase gates AND auto-apply.
- `parse_mode --auto --fix` → `ADK_MODE=auto`, `ADK_FIX=1`. End-to-end with auto-apply.

## Calling skill responsibilities

- Verify `ADK_FIX=1` is allowed for this skill (per `metadata.modes`). If not, refuse with a helpful message.
- Use `ADK_REMAINING` for skill-specific positional args (e.g. PR URL, prompt).
- Surface the active mode in the skill's status banner: `mode=$ADK_MODE fix=$ADK_FIX`.

## Why a shell helper, not a Node parser

- Skills are markdown + shell. Adding Node as a hard dep just for flag parsing is overkill.
- Bash is universal; `parse-mode.sh` is ~30 lines.
- Skills that DO use Node (`bin/adk-info`) re-implement the same logic in Node — see that script for parity.
