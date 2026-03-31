---
name: adk-setup
description: "[abbreviated] [setup] Use when setting up, validating, or updating CLI tools and MCP server configurations for DevKit skills"
user-invocable: true
argument-hint: "[--type tools|mcps|all] [--check-only] [--skip-update] [--server <name>] [--tool <name>] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Read, Bash, Write]
dependencies:
  commands: [python3]
workflow-tier: abbreviated
---

# DevKit Setup & Validation

`references/tool-registry.md`, `references/mcp-registry.md`.

This skill idempotently installs, validates, and updates CLI tools and MCP servers used by DevKit skills.

**CLI Tools** — processed via `stages/tools.md`:

1. **Check** -- Is the tool installed and on PATH?
2. **Install** -- If not, install via Homebrew (or curl for uv)
3. **Update** -- Check for newer versions and upgrade (unless `--skip-update`)

**MCP Servers** -- processed via `stages/mcps.md`:

1. **Check** -- Is the server configured in `~/.claude.json`?
2. **Configure** -- If not, add the config using tokens from `~/.zshenv`
3. **Update packages** -- Pull latest Docker images, npm packages, or Python packages
4. **Sync tokens** -- Compare `~/.zshenv` values against config; update if they differ

---

## Help

When `--help` is passed, display this reference and stop.

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--type` | `tools`, `mcps`, `all` | `all` | Which category to set up |
| `--check-only` | flag | off | Report status without making changes |
| `--tool` | `git`, `python3`, `node`, `npm`, `dot`, `uvx`, `docker`, `gh` | (all tools) | Only process a specific CLI tool (implies `--type tools`) |
| `--server` | `github`, `bitbucket`, `confluence`, `google-drive` | (all servers) | Only process a specific MCP server (implies `--type mcps`) |
| `--skip-update` | flag | off | Install/configure missing items but do not update existing ones |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |

### Type Auto-Detection

- If `--tool` is provided, `--type` is implicitly `tools`
- If `--server` is provided, `--type` is implicitly `mcps`
- If neither `--tool` nor `--server` is provided, `--type` defaults to `all`

### Behavior Variations

- **Full setup** (default): installs missing tools, configures MCP servers, updates everything
- **`--type tools`**: only processes CLI tools, skips MCP servers
- **`--type mcps`**: only processes MCP servers, skips CLI tools
- **`--check-only`**: reports status without modifications
- **`--tool <name>`**: only processes the specified tool, skips all others
- **`--server <name>`**: only processes the specified MCP server, skips all others
- **`--skip-update`**: installs/configures missing items but leaves existing ones at current version
- **`--verbosity short`**: status table only (installed/missing per item)
- **`--verbosity detailed`**: full config details, token sync results, version info, and package versions

### Examples

```
/adk-setup                                  # Full setup: tools + MCPs
/adk-setup --type tools                     # Only set up CLI tools
/adk-setup --type mcps                      # Only set up MCP servers
/adk-setup --check-only                     # Report status without changes
/adk-setup --tool git                       # Only process git
/adk-setup --tool node --verbosity detailed # Only process node with full details
/adk-setup --server github                  # Only process GitHub MCP
/adk-setup --server confluence              # Only process Confluence MCP
/adk-setup --skip-update                    # Install missing but don't update
/adk-setup --type tools --check-only        # Check tool status only
/adk-setup --type mcps --check-only --verbosity short  # Quick MCP status check
```

---



Load references: `references/communication-style.md`, `references/preflight.md`.


## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze requirements and context |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Execute the main workflow |
| 5. Validate & Learn | yes | Validate output quality and completeness |

## Output Format

All output is markdown by default. Structure varies by deliverable type -- see the skill-specific execution sections above for the exact format.

## Usage

```
/adk-setup                                  # Full setup: install + configure + update all
/adk-setup --type tools                     # Tools only: install + update CLI tools
/adk-setup --type mcps                      # MCPs only: configure + update + sync all servers
/adk-setup --check-only                     # Report status without making changes
/adk-setup --tool git                       # Only process git
/adk-setup --server github                  # Only process GitHub MCP
/adk-setup --skip-update                    # Install/configure missing but don't update existing
```

## Execution

Determine the effective type:

- If `--tool` is present: type = `tools`
- If `--server` is present: type = `mcps`
- If `--type` is explicitly set: use that value
- Otherwise: type = `all`

### Tools Setup

When type is `tools` or `all`, run the tools setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-tools.sh <args>
```

Where `<args>` are the relevant arguments (e.g. `--check-only`, `--tool node`, `--skip-update`).

Load stage details: `stages/tools.md`.

### MCP Setup

When type is `mcps` or `all`, run the MCP setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-mcps.sh <args>
```

Where `<args>` are the relevant arguments (e.g. `--check-only`, `--server github`).

Load stage details: `stages/mcps.md`.

## Supported Tools

| Tool | Command | Install Method | Used By |
|---|---|---|---|
| git | `git` | `brew install git` | Nearly all skills |
| Python 3 | `python3` | `brew install python` | preflight.py, scripts |
| Node.js | `node` | `brew install node` | Diagram skills, audit-dependency |
| npm | `npm` | Bundled with node | Same as Node.js |
| Graphviz | `dot` | `brew install graphviz` | diagram-graphviz |
| uv / uvx | `uvx` | `curl` installer | Confluence MCP |
| Docker | `docker` | `brew install --cask docker` | GitHub MCP (Docker variant) |
| GitHub CLI | `gh` | `brew install gh` | PR management |

## Supported MCP Servers

| Server | Key in config | Env vars from `~/.zshenv` |
|---|---|---|
| GitHub | `github` | `GITHUB_PAT` |
| Bitbucket | `bitbucket` | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN` |
| Confluence | `atlassian-confluence` | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Google Drive | `google-drive` | `GOOGLE_DRIVE_OAUTH_CREDENTIALS` |

## Post-Setup Validation

After the scripts complete, report the results to the user:

- **Tools**: If Homebrew is not installed, provide installation instructions. List any tools that could not be installed.
- **MCPs**: If any servers were skipped due to missing env vars, list what needs to be added to `~/.zshenv`.

If the user asks to validate a specific skill's MCP dependencies, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py <skill-dir>
```

## Prerequisites

- **macOS**: Homebrew must be installed for tool installations (the script checks and provides install instructions if missing)
- All brew installations require an internet connection
- MCP server configuration requires tokens in `~/.zshenv`

## Adjacent Skills

- See the parent router skill for related skills
