# Agent Development Kit (ADK)

Self-contained engineering skills, runtime-specific custom subagents, hooks, and MCP server configurations for coding agents. Works with Claude Code, Claude Desktop, Cursor (App + CLI), Codex CLI, Codex Desktop, Gemini CLI, Antigravity, and Junie.

## Install

The Node CLI is the only installer. It is fully idempotent — re-runs converge every target to the current state.

### Option 1 — global npm (most users)

```bash
npm install -g agents-devkit
adk-install                 # interactive setup, writes into $HOME
adk-install --dry-run       # preview, writes nothing
```

Skills and runtime mirrors land under your home directory: `~/.agents/skills/`, `~/.claude/skills/`, `~/.cursor/skills/`, `~/.codex/skills/`, etc.

### Option 2 — per-project npm

```bash
cd <your-project>
npm install --save-dev agents-devkit
npx adk-install             # auto-detects project mode
```

Writes into the project's dot-dirs: `<your-project>/.agents/skills/`, `<your-project>/.claude/skills/`, etc. Use this when you want a pinned, versioned skill bundle inside one repo.

### Option 3 — git clone (contributors / hackers)

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
npm install
npm run setup               # interactive (alias for adk-install)
npm run setup:dry           # preview only
```

Symlinks point at the clone, so edits to skills show up in your runtimes immediately.

## What the installer does

```
<root>/.agents/skills/<name>            # hub (symlinks for adk-* + your own dirs)
<root>/.claude/skills/<name>            # symlink → ../.agents/skills/<name>
<root>/.cursor/skills/<name>            # symlink
<root>/.codex/skills/<name>             # symlink
<root>/.antigravity/skills/<name>       # symlink
<root>/.junie/skills/<name>             # symlink
<root>/.claude/agents/<name>.md         # symlink to <pkg>/agents-claude/<name>.md
<root>/.cursor/agents/<name>.md         # symlink to <pkg>/agents-cursor/<name>.md
<root>/.codex/agents/<name>.toml        # symlink to <pkg>/agents-codex/<name>.toml
<root>/.<runtime>/{settings,hooks,mcp}.json  # symlinked / merged
```

`<root>` is `$HOME` for global installs and the project root for project installs.

Every run does the following, in order, idempotently:

1. **Detects** the runtimes on this machine (Claude Code, Claude Desktop, Cursor, Codex CLI, Codex Desktop, Antigravity, Junie, Gemini CLI).
2. **Stage A — sync the hub.** Prunes every symlink in `<root>/.agents/skills/` whose target lives inside any package install path the CLI has ever seen (current install + paths persisted in `~/.config/adk/settings.json5`), then re-creates one symlink per chosen `adk-*`. Plain dirs you created yourself are preserved.
3. **Stage B — mirror the hub** into each chosen runtime's skills dir. Stale hub-pointing symlinks are pruned and recreated to match.
4. Symlinks runtime-specific custom subagents (Claude / Cursor / Codex) into the runtime's `agents/` folder.
5. Merges chosen MCP servers into each runtime's `mcp.json`. For each required env var: reads from `~/.zshenv`, prompts for missing ones with a "how to get this" hint, and (with confirmation) appends new exports to `~/.zshenv`.
6. Maintains an `<!-- adk:global-prompts:start/end -->` block in each runtime's memory file (`CLAUDE.md` / `AGENTS.md` / `GEMINI.md`).
7. Writes user choices to `~/.config/adk/settings.json5` (and to `<project>/.adk/settings.json5` when `--mode project`).

### Adding personal / project skills

There is no separate `user-skills/` folder. Just create a regular skill directory inside the hub:

```bash
mkdir -p ~/.agents/skills/my-skill           # global install
mkdir -p ./.agents/skills/my-skill           # project install
```

Add a `SKILL.md` (with the standard frontmatter) and re-run `adk-install`. The hub picks it up and mirrors it into every selected runtime automatically.

### Useful flags

```bash
adk-install --dry-run                # preview, write nothing
adk-install --mode global            # force install into $HOME
adk-install --mode project           # force install into cwd / detected project root
adk-install --root <path>            # override the install root entirely
adk-install --yes                    # skip the final "apply this plan?" confirmation
```

## Repository structure

```
agents-devkit/
├── skills/                    # 37 self-contained adk-* skills (SKILL.md + flat references/)
├── agents-claude/             # self-contained Claude custom subagents (Markdown)
├── agents-cursor/             # self-contained Cursor custom subagents (Markdown)
├── agents-codex/              # self-contained Codex custom agents (TOML)
├── hooks/                     # claude.json, cursor.json, codex.json
├── mcp-config/servers/        # one JSON per server, env vars resolved from ~/.zshenv
├── global-prompts/            # always-on prompts, injected into runtime memory files
├── workflows/                 # composable multi-skill YAML pipelines
├── cli/                       # Node installer (only install path)
├── docs/                      # pagesmith source for the public docs site
├── gh-pages/                  # built site
└── README.md AGENTS.md CLAUDE.md LICENSE REFERENCE.md llms.txt
```

## Skill catalog

37 public skills: 1 top router (`adk`) + 8 category routers + 28 task skills. Activate `adk` first for any non-trivial task; it routes to a category and then to a specific task skill.

| Category | Use when | Task skills |
| --- | --- | --- |
| `adk-plan` | Close ambiguity, research, write spec / design / roadmap | `adk-plan-brainstorm`, `adk-plan-research`, `adk-plan-spec`, `adk-plan-design`, `adk-plan-roadmap` |
| `adk-build` | Implement a feature or fix, refactor, migrate, write tests, manage deps | `adk-build-feature`, `adk-build-refactor`, `adk-build-migrate`, `adk-build-test`, `adk-build-deps` |
| `adk-review` | Review PR, review local changes, address feedback, capture handoff | `adk-review-pr`, `adk-review-local`, `adk-review-feedback`, `adk-review-handoff` |
| `adk-docs` | Write or review a technical document | `adk-docs-write`, `adk-docs-review` |
| `adk-audit` | Multi-dimensional audit of a repo or site | `adk-audit-repo`, `adk-audit-site` |
| `adk-publish` | Commit messages, PRs on GitHub / Bitbucket, Confluence / Google Drive | `adk-publish-commit`, `adk-publish-github`, `adk-publish-bitbucket`, `adk-publish-confluence`, `adk-publish-gdrive` |
| `adk-visualize` | Diagrams or charts | `adk-visualize-diagram`, `adk-visualize-chart` |
| `adk-frontend` | UI design, frontend feature work, React 19 client-side sample apps | `adk-frontend-design`, `adk-frontend-feature`, `adk-frontend-react-csr` |

Every skill is fully standalone: a single folder with `SKILL.md` and a flat `references/` carrying its own copy of the persona, workflow, output format, constitution subset, and any other supporting material. There is no `_shared/`, no auto-propagation, no cross-skill file references.

## Custom subagents (per provider)

Each provider's agent files are independent and self-contained — different runtimes have different config formats and supported features:

| Provider | Folder | Format | Notes |
| --- | --- | --- | --- |
| Claude | [agents-claude/](agents-claude/) | Markdown + YAML frontmatter | Rich frontmatter (model, isolation, color, tools) |
| Cursor | [agents-cursor/](agents-cursor/) | Markdown + Cursor frontmatter | Smaller frontmatter surface |
| Codex | [agents-codex/](agents-codex/) | TOML | `developer_instructions = """..."""` body |

Lists may differ per provider. There is no shared persona source; each file is hand-authored for its runtime.

## Hooks

`hooks/claude.json`, `hooks/cursor.json`, `hooks/codex.json` are independent per runtime. The CLI symlinks each one into the runtime's hooks file when you opt in.

## MCP servers

`mcp-config/servers/<server>.json` carries one JSON per server with `${ENV_VAR}` placeholders. The CLI:

- Reads existing values from `~/.zshenv`.
- Prompts for any missing ones with a one-line "how to get this" hint.
- Appends new exports to `~/.zshenv` (with confirmation).
- Merges the server config into each chosen runtime's `mcp.json`, preserving the user's pre-existing entries.

## Maintenance commands

```bash
npm run validate          # validate skills, agents, hooks
npm run skills:manifest   # regenerate skills-manifest.json
npm run setup             # interactive installer (alias: adk-install)
npm run setup:dry         # preview only
npm run docs:build        # build gh-pages/ from docs/
```

## Philosophy

- **Plan first** — every non-trivial task has a phased workflow with approval gates.
- **Self-sufficient skills** — each skill works alone with inline references; no shared sources.
- **Concise by default** — short version first; offer to elaborate.
- **Auto mode** — pass `--auto` to skip confirmations and run end-to-end.
- **Working artifacts to `.temp/`** — never write scratch outside `.temp/` in the host repo.

## License

[MIT](LICENSE).
