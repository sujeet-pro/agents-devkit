# ADK Hooks

Runtime-specific hook source files live here and are installed into tool-specific
config locations via symlink.

## Layout

- `settings.json` -- Claude Code hook source
- `hooks-cursor/hooks.json` -- Cursor native hook source
- `hooks-codex/hooks.json` -- Codex native hook source

These files are generated from `scripts/generate_hook_projections.py`.

## Install Targets

- Claude Code: `~/.claude/settings.json` or `.claude/settings.json`
- Cursor: `~/.cursor/hooks.json` or `.cursor/hooks.json`
- Codex: `~/.codex/hooks.json` or `.codex/hooks.json`

Codex hooks are experimental and also require:

```toml
[features]
codex_hooks = true
```

Regenerate hook sources with:

```bash
python3 scripts/generate_hook_projections.py
```
