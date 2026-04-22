# `setup` — clarifying questions

Per missing tool / per missing env var:

1. **Install `<tool>` via Homebrew now?** — _How to pick:_ Default yes (it is required by adk). No only if you have a non-default version managed by another tool (asdf, mise, nvm).
2. **Add the suggested `export <VAR>="..."` line to your `~/.zshenv` yourself?** — _How to pick:_ We do not auto-edit your zshenv. Add the line manually, then re-run `bin/adk-setup` to pick it up.
3. **Enable MCP server `<name>`?** — _How to pick:_ Default yes if its env vars are present. Skip if you do not use that integration.
