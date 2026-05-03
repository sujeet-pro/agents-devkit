# `setup` — required CLI tools

Source-of-truth list. Order matters: tools earlier in the list are dependencies of later ones.

## Required (errors if missing)

| Tool | Min version | Why adk needs it | macOS install | Linux install |
| --- | --- | --- | --- | --- |
| `gh` | 2.50 | GitHub CLI; fallback when GitHub MCP isn't available | `brew install gh` | vendor instructions at https://cli.github.com |
| `jq` | 1.6 | JSON wrangling in shell; used by `bin/adk-info`, `bin/adk-mcp-health` | `brew install jq` | `sudo apt install jq` |
| `node` | 18.0 | `bin/adk-info` runs in Node | `brew install node` | nvm-recommended; otherwise `sudo apt install nodejs` |

## Recommended (warnings if missing)

| Tool | Min version | Why adk needs it | macOS install | Linux install |
| --- | --- | --- | --- | --- |
| `fd` | 9.0 | Fast file finding; faster than `find` | `brew install fd` | `sudo apt install fd-find` (binary may be `fdfind`) |
| `ripgrep` (`rg`) | 14.0 | Fast in-file search; faster than `grep` | `brew install ripgrep` | `sudo apt install ripgrep` |
| `fzf` | 0.50 | Optional interactive picker for `setup` | `brew install fzf` | `sudo apt install fzf` |
| `docker` | 24.0 | Required by the GitHub MCP (Docker container). Optional if you use `gh` CLI fallback only | `brew install --cask docker` | `sudo apt install docker.io` |

## Notes

- `brew` itself: assume present on macOS; the `setup` skill will surface `brew --version` and prompt the install command if missing.
- `node` is only required by `bin/adk-info` (the meta-info reader). If you want to skip Node, you can re-implement `adk-info` in any language; the rest of adk doesn't require Node.
- `docker` is technically optional — every adk skill that uses the GitHub MCP also supports `gh` CLI as a fallback. But Docker is recommended because it gives equal-priority access to the GitHub MCP toolset.
