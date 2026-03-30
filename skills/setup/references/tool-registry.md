# CLI Tool Registry

All CLI tools that DevKit skills depend on. Each entry defines the tool, how to check if installed, how to install via Homebrew (macOS), and how to update.

## Core Tools (required by most skills)

### git
- **Check**: `git --version`
- **Install**: `brew install git`
- **Update**: `brew upgrade git`
- **Used by**: Nearly all skills

### python3
- **Check**: `python3 --version`
- **Install**: `brew install python`
- **Update**: `brew upgrade python`
- **Used by**: preflight.py, setup-mcps, various scripts

## Node.js Ecosystem (required by diagram and audit skills)

### node
- **Check**: `node --version`
- **Install**: `brew install node`
- **Update**: `brew upgrade node`
- **Used by**: diagram-mermaid, diagram-drawio, diagram-excalidraw, diagramkit, audit-dependency

### npm
- **Check**: `npm --version`
- **Install**: Included with node
- **Update**: `npm install -g npm@latest`
- **Used by**: Same as node

## Diagram Tools

### dot (Graphviz)
- **Check**: `dot -V`
- **Install**: `brew install graphviz`
- **Update**: `brew upgrade graphviz`
- **Used by**: diagram-graphviz

## Python Package Managers

### uv / uvx
- **Check**: `uvx --version`
- **Install**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Update**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Used by**: atlassian-confluence MCP (via uvx)

## Container Runtime

### docker
- **Check**: `docker --version`
- **Install**: `brew install --cask docker`
- **Update**: `brew upgrade --cask docker`
- **Used by**: github MCP server (Docker variant)
- **Note**: Docker Desktop must be running for MCP servers that use Docker

## GitHub CLI

### gh
- **Check**: `gh --version`
- **Install**: `brew install gh`
- **Update**: `brew upgrade gh`
- **Used by**: PR management, GitHub interactions
