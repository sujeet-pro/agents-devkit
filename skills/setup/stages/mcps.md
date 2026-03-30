# Stage: MCP Server Setup & Validation

This stage idempotently configures, validates, and updates MCP servers used by DevKit skills. It processes each server one by one:

1. **Check** -- Is the server configured in `~/.claude.json`?
2. **Configure** -- If not, add the config using tokens from `~/.zshenv`
3. **Update packages** -- Pull latest Docker images, npm packages, or Python packages
4. **Sync tokens** -- Compare `~/.zshenv` values against config; update if they differ

## Execution

Run the setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-mcps.sh <args>
```

Where `<args>` are the arguments passed to this skill (e.g. `--check-only`, `--server github`).

## Supported Servers

| Server | Key in config | Env vars from `~/.zshenv` |
|---|---|---|
| GitHub | `github` | `GITHUB_PAT` |
| Bitbucket | `bitbucket` | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `atlassian-confluence` | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Google Drive | `google-drive` | `GOOGLE_DRIVE_OAUTH_CREDENTIALS` |

## Post-Setup Validation

After the script completes, report the results to the user. If any servers were skipped due to missing env vars, list what needs to be added to `~/.zshenv`.

If the user asks to validate a specific skill's MCP dependencies, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py <skill-dir>
```
