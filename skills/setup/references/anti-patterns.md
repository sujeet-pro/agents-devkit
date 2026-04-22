# `setup` — anti-patterns

- Auto-modifying `~/.zshenv`. Always show the `export` line and ask the user to add it themselves.
- Re-installing tools that are already present.
- Running on Linux/Windows. Hard fail at Phase 1.
- Skipping the final `bin/adk-doctor` run.
- Installing MCP servers whose env vars are missing (skip them, log "skipped (env missing)").
- Running `gh auth login` non-interactively.
- Forgetting to print the final report under `--auto`.
