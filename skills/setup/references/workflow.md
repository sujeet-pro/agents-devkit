# `setup` — detailed workflow

## Step-by-step

1. `uname -s` → must equal `Darwin`. Else exit 2 with "macOS only".
2. `command -v brew`. If absent, prompt user to run the official install command. Wait until present.
3. For each tool in `references/tool-list.md`:
   - `command -v <tool>`. If present, log `present (<version>)`. Skip.
   - If absent, under `--mode auto` ask "install via `brew install <tool>`?" — under `--mode fix` just install.
4. `gh auth status -h github.com`. If not authed, prompt user to run `gh auth login` (we cannot do it for them — it requires interactive browser auth).
5. `node --version`. If <18, prompt to upgrade.
6. Read `.mcp.json`. Collect every `${VAR}` placeholder. For each, run `(source ~/.zshenv && echo "$VAR")` in a subshell. Bucket: present / missing.
7. For each missing var, output the suggested `export VAR="..."` line. Do not modify `~/.zshenv`.
8. Hand off to `bin/adk-mcp-install` (which uses the now-resolved env vars to register MCP servers via `claude mcp add`).
9. Run `bin/adk-doctor`. Capture its output into the final report.
10. Print final report (see `output-format.md`).
