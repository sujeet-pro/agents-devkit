# Agent Development Kit (ADK)

Self-contained engineering skills, runtime-specific custom subagents, hooks, MCP server configurations, and global prompts for coding agents. Works with Claude Code, Claude Desktop, Cursor (App + CLI), Codex CLI, Codex Desktop, Gemini CLI, Antigravity, and Junie.

**38 self-contained skills** covering planning, building, reviewing, documenting, auditing, publishing, visualization, and frontend work — every skill ships its own complete `references/` (no shared sources, no cross-skill file refs). Every skill is **highly interactive by default** and supports `--auto` for fully unattended runs.

## Install

There are three install paths, ordered from most-recommended to most-minimal. The Node CLI (`adk-install` / `adk`) is the installer used by paths 1 and 2; it is idempotent — re-runs converge every target to the current state. Path 3 uses the third-party [`skills`](https://skills.sh) loader and lands only the skills (no agents / hooks / MCP / global prompts).

### 1. Clone + install script — **suggested**

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
npm install
npm run setup            # interactive; same as `adk-install`
```

This is the recommended path for almost everyone. Symlinks resolve back into the clone, so:

- `git pull` gives you the latest skills with no re-install step.
- Local edits to `skills/`, `agents-claude/`, `hooks/`, `mcp-config/`, etc. show up immediately in every linked runtime.
- You pick the install scope at run time (`--mode global` writes into `$HOME`, `--mode project` writes into the current project).
- All five surfaces are wired up: skills, custom subagents, hooks, MCP servers, and global prompts.

Trade-off: you manage the clone and the `git pull` cadence yourself.

### 2. npm modules — pinned / CI-reproducible

Use this when you want a version pinned in `package.json`, or you'd rather not maintain a clone.

```bash
# Global: one toolkit shared across every project on the machine.
npm install -g agents-devkit
adk-install

# Per-project: pinned in your repo's package.json, reproducible in CI.
cd <your-project>
npm install --save-dev agents-devkit
npx adk-install
```

| Sub-mode | Where the package lives | Where the CLI links into | Best for |
| --- | --- | --- | --- |
| Global npm | `$(npm prefix -g)/lib/node_modules/agents-devkit` | `$HOME/.{agents,claude,cursor,codex,antigravity,junie,gemini}/...` | One shared toolkit across every project on the machine |
| Per-project npm | `<project>/node_modules/agents-devkit` | `<project>/.{agents,claude,cursor,codex,antigravity,junie}/...` | A pinned, versioned skill bundle inside one repo |

Same five surfaces are installed (skills, agents, hooks, MCP, global prompts). Trade-off vs. the clone path: you can't edit skills in place — `npm update` is the only way to refresh.

### 3. `npx skills add` — for non-tech folks (skills only)

If you do not have (or want) a Node toolchain set up and just want the skills landed in your coding agent, use the third-party [`skills`](https://skills.sh) loader:

```bash
npx skills add sujeet-pro/agents-devkit
```

This drops every `SKILL.md` into your agent's skills folder (Claude Code, Cursor, etc., depending on what `skills` supports) with a single command. **Heads up — only the skills install via this path. Custom subagents, hooks, MCP server configs, and global prompts are NOT applied.** Use this when:

- You're a non-developer who just wants the playbooks in Claude Code / Cursor with minimum fuss.
- You want to try ADK skills without committing to a clone or an `npm install`.

If you later want hooks / MCP / custom subagents / global prompts, switch to path 1 or 2.

### Auto-detection and overrides

For paths 1 and 2, `adk-install` auto-detects which scenario you launched it from. Override with `--mode global|project` or with `--root <path>`.

### Useful flags

```bash
adk-install --dry-run              # preview the plan, write nothing
adk-install --mode global          # force install into $HOME
adk-install --mode project         # force install into cwd / detected project root
adk-install --root <path>          # override the install root entirely
adk-install --yes                  # skip the final "apply this plan?" confirmation
adk-install --help                 # full flag list
```

The plan summary lists exactly which runtimes will receive symlinks, which MCP servers will be merged, and which env vars need values before anything is written.

## What the installer lays down

```
<root>/.agents/skills/<name>            # hub: single source of truth (managed adk-* symlinks + your own dirs)
<root>/.claude/skills/<name>            # symlink → ../.agents/skills/<name>
<root>/.cursor/skills/<name>            # symlink → ../.agents/skills/<name>
<root>/.codex/skills/<name>             # symlink
<root>/.antigravity/skills/<name>       # symlink
<root>/.junie/skills/<name>             # symlink
<root>/.claude/agents/<name>.md         # symlink → <pkg>/agents-claude/<name>.md
<root>/.cursor/agents/<name>.md         # symlink → <pkg>/agents-cursor/<name>.md
<root>/.codex/agents/<name>.toml        # symlink → <pkg>/agents-codex/<name>.toml
<root>/.<runtime>/{settings,hooks,mcp}.json  # symlinked / merged
<root>/<MEMORY>.md                      # managed <!-- adk:global-prompts:start/end --> block
```

`<root>` is `$HOME` for global installs and the project root for project installs.

Every run does the following, in order, idempotently:

1. **Detects** the runtimes on this machine (Claude Code, Claude Desktop, Cursor, Codex CLI, Codex Desktop, Antigravity, Junie, Gemini CLI).
2. **Stage A — sync the hub.** Prunes every symlink in `<root>/.agents/skills/` whose target lives inside any package install path the CLI has ever seen (current install + paths persisted in `~/.config/adk/settings.json5`), then re-creates one symlink per chosen `adk-*` skill. Plain dirs you created yourself are preserved.
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

## Interaction model — interactive by default, `--auto` for unattended

Every skill ships `references/interaction-contract.md`. The contract is short and identical across the catalog:

- **Default mode.** At every meaningful decision the skill restates the question in one sentence, presents 2-3 options with `Pros / Cons / Best when / Blast radius / Reversibility`, marks one option `(default)`, asks one question, and waits for the user. Trivial reversible actions (e.g. creating `.temp/`) are taken without asking.
- **`--auto` mode.** Pass `--auto` anywhere in the request to suppress every approval gate. The skill picks the documented `(default)` at every fork, still validates after meaningful changes, and still ends with a final report listing what it auto-decided.
- **Always.** Every run ends with a structured report: result, decisions auto-picked, validation evidence, residual risk, and an offer of more depth.
- **Never auto.** Even under `--auto`, skills refuse irreversible destructive ops they explicitly mark "never auto" (`pr-merge`, force-push, schema drop, prod deploy, billing actions, account writes for other users).

The same contract is mirrored as a global prompt (`global-prompts/interaction-contract.md`) so it lands in every runtime's memory file and applies even outside skill activations.

## Repository structure

```
agents-devkit/
├── skills/                    # 38 self-contained adk-* skills (SKILL.md + flat references/)
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

38 public skills: 1 top router (`adk`) + 8 category routers + 29 task skills. Activate `adk` first for any non-trivial task; it routes to a category and then to a specific task skill.

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

Plus one standalone setup skill that does not belong to a category router:

| Skill | Purpose |
| --- | --- |
| `adk-doc-site-setup` | Bootstrap a `@pagesmith/docs` + `diagramkit` documentation site in any repo and install `prj-doc-site-*` project skills so future agents can keep extending it |

Every skill is fully standalone: a single folder with `SKILL.md` and a flat `references/` carrying its own copy of the persona, workflow, output format, constitution subset, interaction contract, and any other supporting material. There is no `_shared/`, no auto-propagation, no cross-skill file references.

## Custom subagents (per provider)

Each provider's agent files are independent and self-contained — different runtimes have different config formats and supported features:

| Provider | Folder | Format | Notes |
| --- | --- | --- | --- |
| Claude | [agents-claude/](agents-claude/) | Markdown + YAML frontmatter | Rich frontmatter (model, isolation, color, tools) |
| Cursor | [agents-cursor/](agents-cursor/) | Markdown + Cursor frontmatter | Smaller frontmatter surface |
| Codex | [agents-codex/](agents-codex/) | TOML | `developer_instructions = """..."""` body |

The current set is `adk-brainstorm-facilitator`, `adk-code-reviewer`, `adk-debugger`, `adk-doc-writer`, `adk-implementer`, `adk-plan-reviewer`, `adk-research-agent`, `adk-security-reviewer`, `adk-test-engineer`. Each provider has its own copy; lists may differ.

## Hooks

`hooks/claude.json`, `hooks/cursor.json`, `hooks/codex.json` are independent per runtime. The CLI symlinks each one into the runtime's hooks file when you opt in. Codex hooks are experimental and require `[features] codex_hooks = true` in `~/.codex/config.toml`.

## MCP servers

`mcp-config/servers/<server>.json` carries one JSON per server with `${ENV_VAR}` placeholders. Available servers: `github`, `bitbucket`, `confluence`, `jira`, `google-drive`, `brainstorming`. The CLI:

- Reads existing values from `~/.zshenv`.
- Prompts for any missing ones with a one-line "how to get this" hint.
- Appends new exports to `~/.zshenv` (with confirmation).
- Merges the server config into each chosen runtime's `mcp.json`, preserving the user's pre-existing entries.

## Maintenance commands

```bash
npm run validate          # validate skills, agents, hooks
npm run skills:manifest   # regenerate skills-manifest.json
npm run setup             # interactive installer (alias for adk-install)
npm run setup:dry         # preview only
npm run docs:build        # build gh-pages/ from docs/
```

## Philosophy

- **Plan first** — every non-trivial task has a phased workflow with approval gates.
- **Self-sufficient skills** — each skill works alone with inline references; no shared sources at runtime.
- **Concise by default** — short version first; offer to elaborate.
- **Interactive by default, `--auto` for unattended** — every skill is identical-shape across modes.
- **Working artifacts to `.temp/`** — never write scratch outside `.temp/` in the host repo.

## License

[MIT](LICENSE).
