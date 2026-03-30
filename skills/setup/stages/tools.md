# Stage: CLI Tool Setup & Validation

This stage idempotently installs, validates, and updates CLI tools used by DevKit skills. It processes each tool one by one:

1. **Check** -- Is the tool installed and on PATH?
2. **Install** -- If not, install via Homebrew (or curl for uv)
3. **Update** -- Check for newer versions and upgrade (unless `--skip-update`)

## Execution

Run the setup script:

```bash
bash ${CLAUDE_SKILL_DIR}/scripts/setup-tools.sh <args>
```

Where `<args>` are the arguments passed to this skill (e.g. `--check-only`, `--tool node`, `--skip-update`).

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

## Post-Setup

After the script completes, report results to the user. If Homebrew is not installed, the script will provide installation instructions and exit.

## Prerequisites

- **macOS**: Homebrew must be installed (the script checks and provides install instructions if missing)
- All brew installations require an internet connection
