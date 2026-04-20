# ADK Hooks

Flat layout — one file per runtime. Each file is generated from
`scripts/generate_hook_projections.py` and installed via `scripts/install.sh`.

## Layout

| File | Runtime | Install target |
| --- | --- | --- |
| `claude.json` | Claude Code | `~/.claude/settings.json` or `.claude/settings.json` |
| `cursor.json` | Cursor | `~/.cursor/hooks.json` or `.cursor/hooks.json` |
| `codex.json` | Codex | `~/.codex/hooks.json` or `.codex/hooks.json` |

Codex hooks are experimental and additionally require the feature flag in
`~/.codex/config.toml` or `.codex/config.toml`:

```toml
[features]
codex_hooks = true
```

## Regenerate

```bash
python3 scripts/generate_hook_projections.py
```

## Validate

```bash
python3 scripts/generate_hook_projections.py --check
python3 tests/test_hooks.py
```
