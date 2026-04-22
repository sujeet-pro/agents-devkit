# `setup` — tool list (source of truth)

| Tool | Brew formula | Required? | Used by |
| --- | --- | --- | --- |
| `brew` | self | yes | everything |
| `gh` | `gh` | yes | publish-github, cicd-monitor, cicd-fix, audit-pr, review-pr (gh fallback) |
| `jq` | `jq` | yes | many shell helpers |
| `fd` | `fd` | yes | file lookup helpers |
| `ripgrep` | `ripgrep` | yes | content search helpers |
| `fzf` | `fzf` | recommended | interactive picks in shells |
| `claude` | `--cask claude-code` | yes | the runtime itself |
| `node` ≥ 18 | `node` | yes | bin/* scripts and pagesmith / diagramkit deps |
| `docker` | `--cask docker` | recommended | several MCP servers run via Docker |

## Notes

- We never pin a Homebrew version. Always install the latest formula.
- We never install global npm packages — every `npx`-able tool is invoked via `npx`.
- We do not install Python or any Python tooling. The plugin is pure Node.
