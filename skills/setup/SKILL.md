---

## name: setup
description: "adk - [abbreviated] [setup] Use when setting up, validating, or updating CLI tools and MCP server configurations for DevKit skills"
user-invocable: true
argument-hint: "[--type tools|mcps|hooks|config|all] [--check-only] [--skip-update] [--server ] [--tool ] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Read, Bash, Write]
dependencies:
  commands: [python3]
workflow-tier: abbreviated

---

# DevKit Setup & Validation

This skill idempotently installs, validates, and updates CLI tools, MCP servers, hooks, and configuration used by DevKit skills.

**CLI Tools** — processed via `stages/tools.md`:

1. **Check** -- Is the tool installed and on PATH?
2. **Install** -- If not, install via Homebrew (or curl for uv)
3. **Update** -- Check for newer versions and upgrade (unless `--skip-update`)

**MCP Servers** -- processed via `stages/mcps.md`:

1. **Check** -- Is the server configured in `~/.claude.json`?
2. **Configure** -- If not, add the config using tokens from `~/.zshenv`
3. **Update packages** -- Pull latest Docker images, npm packages, or Python packages
4. **Sync tokens** -- Compare `~/.zshenv` values against config; update if they differ

**Hooks** -- SessionStart hook and compaction reminders:

1. **Check** -- Does `~/.claude/settings.json` have the ADK SessionStart hook?
2. **Configure** -- Add a SessionStart hook that reminds about ADK on compaction

**Config** -- User-level settings for `/adk:use` routing:

1. **Check** -- Does `settings.json` set `/adk:use` as the default agent?
2. **Configure** -- Update `settings.json` to set the `use` agent as default

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.


| Skill                | Load When | Inline Fallback                                                             |
| -------------------- | --------- | --------------------------------------------------------------------------- |
| `/adk:workflow`      | always    | 6-phase workflow: intent → research → approach → plan → execute → validate. |
| `/adk:communication` | always    | Lead with conclusion. Bullet points. No preamble. Concrete specifics.       |


## Help

When `--help` is passed, display this reference and stop.

### Parameters


| Parameter       | Values                                                                                   | Default       | Description                                                     |
| --------------- | ---------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------- |
| `--type`        | `tools`, `mcps`, `hooks`, `config`, `all`                                                | `all`         | Which category to set up                                        |
| `--check-only`  | flag                                                                                     | off           | Report status without making changes                            |
| `--tool`        | `git`, `python3`, `node`, `npm`, `jq`, `curl`, `dot`, `uvx`, `docker`, `gh`, `diagramkit`, `pagesmith` | (all tools)   | Only process a specific CLI tool (implies `--type tools`)       |
| `--server`      | `github`, `bitbucket`, `confluence`, `google-drive`                                      | (all servers) | Only process a specific MCP server (implies `--type mcps`)      |
| `--skip-update` | flag                                                                                     | off           | Install/configure missing items but do not update existing ones |
| `--verbosity`   | `short`, `standard`, `detailed`                                                          | `standard`    | Output detail level                                             |


### Type Auto-Detection

- If `--tool` is provided, `--type` is implicitly `tools`
- If `--server` is provided, `--type` is implicitly `mcps`
- If neither `--tool` nor `--server` is provided, `--type` defaults to `all`

### Behavior Variations

- **Full setup** (default): installs missing tools, configures MCP servers, sets up hooks and config, updates everything
- `**--type tools`**: only processes CLI tools, skips MCP servers, hooks, and config
- `**--type mcps**`: only processes MCP servers, skips CLI tools, hooks, and config
- `**--type hooks**`: only processes SessionStart hooks and compaction reminders
- `**--type config**`: only processes user-level settings (default agent, routing)
- `**--check-only**`: reports status without modifications
- `**--tool <name>**`: only processes the specified tool, skips all others
- `**--server <name>**`: only processes the specified MCP server, skips all others
- `**--skip-update**`: installs/configures missing items but leaves existing ones at current version
- `**--verbosity short**`: status table only (installed/missing per item)
- `**--verbosity detailed**`: full config details, token sync results, version info, and package versions

### Examples

```
/adk:setup                                  # Full setup: tools + MCPs + hooks + config
/adk:setup --type tools                     # Only set up CLI tools
/adk:setup --type mcps                      # Only set up MCP servers
/adk:setup --type hooks                     # Only set up SessionStart hooks
/adk:setup --type config                    # Only configure default agent routing
/adk:setup --check-only                     # Report status without changes
/adk:setup --tool git                       # Only process git
/adk:setup --tool diagramkit               # Only process diagramkit
/adk:setup --tool node --verbosity detailed # Only process node with full details
/adk:setup --server github                  # Only process GitHub MCP
/adk:setup --server confluence              # Only process Confluence MCP
/adk:setup --skip-update                    # Install missing but don't update
/adk:setup --type tools --check-only        # Check tool status only
/adk:setup --type mcps --check-only --verbosity short  # Quick MCP status check
```

---

## Phase Applicability


| Phase                 | Applies | Skill-Specific Notes                                                              |
| --------------------- | ------- | --------------------------------------------------------------------------------- |
| 0. Intent Expansion   | yes     | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes     | Analyze requirements and context                                                  |
| 2. Approach Selection | skip    | Direct execution after early confirmation                                         |
| 3. Planning           | skip    | Direct execution                                                                  |
| 4. Execute            | yes     | Execute the main workflow                                                         |
| 5. Validate & Learn   | yes     | Validate output quality and completeness                                          |


## Output Format

All output is markdown by default. Structure varies by deliverable type -- see the skill-specific execution sections above for the exact format.

## Usage

```
/adk:setup                                  # Full setup: install + configure + update all
/adk:setup --type tools                     # Tools only: install + update CLI tools
/adk:setup --type mcps                      # MCPs only: configure + update + sync all servers
/adk:setup --type hooks                     # Hooks only: configure SessionStart hook
/adk:setup --type config                    # Config only: set default agent routing
/adk:setup --check-only                     # Report status without making changes
/adk:setup --tool git                       # Only process git
/adk:setup --server github                  # Only process GitHub MCP
/adk:setup --skip-update                    # Install/configure missing but don't update existing
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

### Hooks Setup

When type is `hooks` or `all`:

1. Read `~/.claude/settings.json`
2. Check if a SessionStart hook exists that reminds about ADK on compaction
3. If missing, add it:
  - Hook type: `SessionStart`
  - Purpose: remind the agent about ADK skill availability after context compaction
  - The hook should include a brief reminder of the `/adk:use` entry point and available skills

### Config Setup

When type is `config` or `all`:

1. Read the project or user `settings.json`
2. Set `/adk:use` as the default agent for general prompts
3. Validate the configuration is syntactically correct

## What Gets Configured

### `~/.claude/settings.json`

- **SessionStart hook**: adds a hook that reminds about ADK on compaction, ensuring the agent retains awareness of available skills across long sessions
- **Default agent**: sets `/adk:use` as the default routing entry point

### MCP Servers


| Server       | Config Key             | Transport | Env vars from `~/.zshenv`                                       |
| ------------ | ---------------------- | --------- | --------------------------------------------------------------- |
| GitHub       | `github`               | HTTP      | `GITHUB_PAT`                                                    |
| Bitbucket    | `bitbucket`            | stdio     | `BITBUCKET_USERNAME`, `BITBUCKET_TOKEN`                         |
| Confluence   | `atlassian-confluence` | stdio     | `CONFLUENCE_URL`, `CONFLUENCE_USERNAME`, `CONFLUENCE_API_TOKEN` |
| Google Drive | `google-drive`         | stdio     | `GOOGLE_DRIVE_OAUTH_CREDENTIALS`                                |


GitHub MCP uses HTTP transport. Bitbucket, Confluence, and Google Drive are optional and configured on request.

### CLI Tools


| Tool       | Command      | Install Method                 | Used By                                                                  |
| ---------- | ------------ | ------------------------------ | ------------------------------------------------------------------------ |
| git        | `git`        | `brew install git`             | Nearly all skills                                                        |
| Python 3   | `python3`    | `brew install python`          | preflight.py, scripts                                                    |
| Node.js    | `node`       | `brew install node`            | Diagram skills, audit-dependency                                         |
| npm        | `npm`        | Bundled with node              | Same as Node.js                                                          |
| jq         | `jq`         | `brew install jq`              | Bitbucket, Confluence, Jira connectors                                   |
| curl       | `curl`       | `brew install curl`            | Bitbucket, Confluence, Jira connectors (pre-installed on macOS)          |
| Graphviz   | `dot`        | `brew install graphviz`        | `/adk:diagram-graphviz`                                                  |
| uv / uvx   | `uvx`        | `curl` installer               | Confluence MCP                                                           |
| Docker     | `docker`     | `brew install --cask docker`   | GitHub MCP (Docker variant)                                              |
| GitHub CLI | `gh`         | `brew install gh`              | PR management (run `gh auth login` after install)                        |
| diagramkit | `diagramkit` | `npm install -g diagramkit`    | `/adk:diagram-mermaid`, `/adk:diagram-excalidraw`, `/adk:diagram-drawio` |
| pagesmith  | `pagesmith`  | `npm install -g @pagesmith/docs` | `/adk:docs-crud`, `/adk:docs-repo`                                       |


Validation: confirm git, node, npm are installed and on PATH. Install diagramkit and pagesmith globally if not present.

### Plugin Validation

- Verify `.claude-plugin/plugin.json` exists and is valid JSON
- Check that the plugin declares the expected skills and entry points
- Report any missing or malformed entries

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Post-Setup Validation

After the scripts complete, report the results to the user:

- **Tools**: If Homebrew is not installed, provide installation instructions. List any tools that could not be installed.
- **MCPs**: If any servers were skipped due to missing env vars, list what needs to be added to `~/.zshenv`.
- **Hooks**: Report whether the SessionStart hook was added or already existed.
- **Config**: Report whether `/adk:use` was set as default or was already configured.

If the user asks to validate a specific skill's MCP dependencies, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py <skill-dir>
```

## Prerequisites

- **macOS**: Homebrew must be installed for tool installations (the script checks and provides install instructions if missing)
- All brew installations require an internet connection
- MCP server configuration requires tokens in `~/.zshenv`

## Adjacent Skills

- `/adk:use` — the orchestrator that routes general prompts to the right skill
- `/adk:project` — for initializing new projects and managing milestones

