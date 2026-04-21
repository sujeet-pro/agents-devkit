# ADK Hooks

Flat layout — one file per runtime. Each file is the full hook config for that runtime; nothing is generated.

## Layout

| File | Runtime | Install target |
| --- | --- | --- |
| `claude.json` | Claude Code | `~/.claude/settings.json` (global install) or `<project>/.claude/settings.json` (project install) |
| `cursor.json` | Cursor | `~/.cursor/hooks.json` or `<project>/.cursor/hooks.json` |
| `codex.json` | Codex CLI | `~/.codex/hooks.json` or `<project>/.codex/hooks.json` |

The CLI symlinks each file in via `cli/lib/hooks.mjs` when the user opts into the "Hook configs" surface during `adk-install`.

## Codex hooks (experimental)

Codex hooks additionally require the feature flag in `~/.codex/config.toml` (or `<project>/.codex/config.toml`):

```toml
[features]
codex_hooks = true
```

Without that flag, the symlinked `hooks.json` is ignored by Codex.

## Editing

Edit the relevant `.json` file directly. There is no projection script.

## Validation

```bash
npm run validate
```

This parses each file as JSON and fails the run if any of them is malformed.
