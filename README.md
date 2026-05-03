# adk marketplace

A Claude Code plugin marketplace for a **Principal Engineer** workflow: code writing, code review (self / others), doc writing & review, and production investigations across Datadog, Mixpanel, Statsig, Snowflake, GitHub, and the workspace's managed connectors.

> **Marketplace name:** `adk`
> **Repository:** [sujeet-pro/agents-devkit](https://github.com/sujeet-pro/agents-devkit)
> **Audience:** A Principal Engineer (single operator) doing code writing, code review, doc writing/review, and production investigations.

The marketplace ships **5 audience-focused plugins** with a total of **37 single-action skills**, **3 custom MCPs** (GitHub Docker, Datadog hosted, Statsig hosted), and **10 per-user meta-info files** at `~/.config/adk/*.md` that the skills read for company- and repo-specific facts.

---

## What is `adk`?

A 5-plugin marketplace, opinionated and optimized for one operator (a Principal Engineer):

```
adk-core            required by all; ships auto-router, setup, meta-info reader,
                    mode contract, .temp/ layout, Bash safety hook
  ├── adk-code        write / fix / refactor / migrate / test / perf / api / security
  ├── adk-review      review-pr / review-code-changes / review-feedback /
  │                   review-handoff / audit-pr / audit-repo
  ├── adk-docs        docs-write / docs-review / docs-pr-description /
  │                   docs-commit-message / docs-changelog / docs-diagram /
  │                   docs-publish-confluence / docs-publish-gdrive
  └── adk-investigate datadog / mixpanel / statsig / snowflake / deploy /
                      incident / experiment / rca
```

Every skill follows the same `--auto / -i / --fix` mode contract and the same Phase 0–3 workflow (prompt-expand → preflight → execute → validate-and-report).

---

## Installation

### Step 1 — Make the marketplace reachable

Pick whichever path matches how you authenticate to GitHub. **You only need ONE of Paths A–D.**

#### Path A — Local clone (simplest; works regardless of auth method)

Clone the repo once, then point Claude Code at the local path. Lets you `git pull` to refresh.

```bash
git clone git@github.com:sujeet-pro/agents-devkit.git ~/code/claude-marketplace
# or
gh repo clone sujeet-pro/agents-devkit ~/code/claude-marketplace
# or
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/claude-marketplace
```

Then in Claude Code (covered in Step 2):

```text
/plugin marketplace add ~/code/claude-marketplace
```

#### Path B — SSH URL (no clone; uses your existing SSH key)

```text
/plugin marketplace add git@github.com:sujeet-pro/agents-devkit.git
```

#### Path C — HTTPS URL via `gh` CLI auth

If you've already run `gh auth login`, git's credential helper picks up the `gh` token automatically. You can use either:

```text
/plugin marketplace add sujeet-pro/agents-devkit
```

or the explicit HTTPS URL:

```text
/plugin marketplace add https://github.com/sujeet-pro/agents-devkit.git
```

Verify auth first with `gh auth status`.

#### Path D — HTTPS URL with a Personal Access Token (CI / non-interactive)

Set a token in your shell rc file before launching Claude Code:

```bash
# Mint at https://github.com/settings/personal-access-tokens/new
export GITHUB_TOKEN="github_pat_..."
export GH_TOKEN="$GITHUB_TOKEN"
```

Reload your shell (`source ~/.zshenv`), then:

```text
/plugin marketplace add sujeet-pro/agents-devkit
```

> All four paths produce the same registered marketplace named `adk`. Only Path A keeps the upstream copy on disk for inspection or `git pull`; Paths B–D let Claude Code manage its own internal cache.

### Step 2 — Add the marketplace inside Claude Code

Inside any Claude Code session, run the one `/plugin marketplace add` command from the path you picked above. It registers the marketplace under the name `adk`.

To refresh later when new commits land upstream:

- **Path A (local clone):**

  ```bash
  cd ~/code/claude-marketplace && git pull
  ```

  ```text
  /plugin marketplace update adk
  /reload-plugins
  ```

- **Paths B / C / D (remote URL):**

  ```text
  /plugin marketplace update adk
  /reload-plugins
  ```

### Step 3 — Install the plugins you need

```text
/plugin install adk-core@adk
/plugin install adk-code@adk
/plugin install adk-review@adk
/plugin install adk-docs@adk
/plugin install adk-investigate@adk
/reload-plugins
```

`adk-core` is auto-installed as a dependency of every other plugin, so you can skip it explicitly if you're already installing something else.

### Step 4 — Bootstrap your meta-info + env vars

Run the one-time setup skill — it walks you through the 10 `~/.config/adk/*.md` topic files and reports which env vars referenced by the shipped MCPs are missing from your shell.

```text
/adk-core:setup
```

Or per topic (also shows missing env vars):

```text
/adk-core:setup --target datadog
```

See [`SETUP.md`](./SETUP.md) for the env-var walkthrough per MCP.

---

## Plugins at a glance

| Plugin | Purpose | Setup needed |
| --- | --- | --- |
| [`adk-core`](./plugins/adk-core/README.md) | Prompt routing (auto), setup of `~/.config/adk/*.md`, meta-info reader, mode contract, `.temp/` layout, the universal Bash safety hook. **Required by every other adk plugin.** | Yes — `~/.config/adk/info.md` + `repos.md` (via `adk-core:setup`) |
| [`adk-code`](./plugins/adk-code/README.md) | Write features, fix bugs (with reproducer + regression test), refactor without behavior change, migrate frameworks, write/expand tests, diagnose perf, design APIs, harden security. | No |
| [`adk-review`](./plugins/adk-review/README.md) | Review someone else's PR, review your local changes, address PR feedback, capture handoff, run quick / whole-repo audits. Ships GitHub MCP (Docker) with `gh` CLI fallback. | Yes — `GITHUB_PAT` env var (for the GitHub MCP / `gh` CLI) |
| [`adk-docs`](./plugins/adk-docs/README.md) | Write/review prose docs, draft PR descriptions and commit messages, append changelog entries, author Mermaid diagrams, publish to Confluence / Google Drive (via workspace connectors). | No (requires workspace Atlassian + Google Drive connectors) |
| [`adk-investigate`](./plugins/adk-investigate/README.md) | Query Datadog, Mixpanel, Statsig, Snowflake, GitHub deploys, Slack incident discussions. Composite incident / experiment / RCA workflows. Ships custom MCPs for Datadog and Statsig. | Yes — `DD_API_KEY`, `DD_APP_KEY`, `STATSIG_CONSOLE_API_KEY` |

---

## MCP strategy at a glance

The marketplace prefers **claude.ai workspace connectors** wherever they exist (no local setup, no token rotation, automatic auth via Okta SSO). Custom MCPs ship only when no workspace alternative exists.

Claude Code can load the plugin-local `.mcp.json` files shipped by `adk-review` and `adk-investigate`. Claude Desktop does not obey plugin-local `.mcp.json`, so skills that need those MCPs stop in Phase 1 and ask the user to configure the equivalent custom connector in Desktop or the required workspace connector before continuing. The user can explicitly skip a dependency check only when the selected mode does not need that capability, such as a dry-run flow that drafts output but does not post or publish.

| Capability | Source | Plugins consuming |
| --- | --- | --- |
| GitHub | Custom MCP (`ghcr.io/github/github-mcp-server` via Docker, pinned to `v1.0.3`) + `gh` CLI fallback | `adk-review`, `adk-docs` |
| Datadog | Custom MCP — Datadog hosted at `mcp.datadoghq.com` (Preview) | `adk-investigate` |
| Statsig | Custom MCP — Statsig hosted at `api.statsig.com/v1/mcp` | `adk-investigate` |
| Atlassian (Jira + Confluence) | Workspace connector (Rovo) | `adk-docs`, `adk-investigate` |
| Google Drive | Workspace connector | `adk-docs`, `adk-investigate` |
| Gmail | Workspace connector | `adk-investigate` |
| Google Calendar | Workspace connector | `adk-investigate` |
| Slack | Workspace connector | `adk-investigate` |
| Mixpanel | Workspace connector | `adk-investigate` |
| Snowflake | Workspace connector (e.g. `QDP_SNOWFLAKE_MCP_SERVER`) | `adk-investigate` |

If a workspace doesn't have a particular connector enabled, the depending skills stop with a clear error and tell you what to enable. Ask your Claude admin to turn on the missing connector, or run `bin/adk-mcp-health` (shipped by `adk-core`) for a one-shot diagnostic.

See [`SETUP.md`](./SETUP.md) for env-var setup and the verifier curl one-liners per MCP, and [`plugins/adk-investigate/.mcp.json`](./plugins/adk-investigate/.mcp.json) / [`plugins/adk-review/.mcp.json`](./plugins/adk-review/.mcp.json) for the canonical config blocks.

---

## Universal contracts (every adk skill follows these)

### Mode contract — `--auto`, `-i`, `--fix`

| Mode | Trigger | Behavior |
| --- | --- | --- |
| `--auto` | default | Run end-to-end without per-phase approval gates. Still **stops** before destructive or shared-state actions (push, post, delete). |
| `-i` / `--interactive` | explicit | Show the plan, ask for approval at each phase boundary, allow edits. Mutually exclusive with `--auto`. |
| `--fix` | explicit | Apply optional local/remote mutation for skills that declare it, such as review-fix flows, docs update/commit/PR-description flows, changelog updates, and safe audit fixes. Code-authoring skills mutate by default and do not need `--fix`. |

`--auto` and `--fix` compose. They never auto-merge a PR, never force-push to a protected branch, never delete a branch.

### Phase contract — every skill has 4 phases

```
Phase 0 — Prompt expansion
Phase 1 — Preflight (deps, MCP, meta-info, git state)
Phase 2 — Execute (the actual work; artifacts under .temp/task-<slug>/)
Phase 3 — Validate + Report
```

### Meta-info contract — `~/.config/adk/`

Skills that need company- or repo-specific facts read them from `~/.config/adk/<topic>.md`. The `adk-core:setup` skill scaffolds these from templates the first time you run adk on a machine.

Topics: `info`, `repos`, `github`, `datadog`, `mixpanel`, `statsig`, `snowflake`, `slack`, `review`, `docs`.

### Working-artifact layout — `.temp/task-<slug>/`

Every adk skill writes intermediate artifacts under `.temp/task-<slug>/` (gitignored). The `adk-core:temp-folder` skill is the convention authority.

---

## Plugin dependencies

```
adk-core ──┬── adk-code
           ├── adk-review
           ├── adk-docs
           └── adk-investigate
```

Hard deps (in each plugin's `plugin.json`) are auto-installed by Claude Code when you install the parent.

---

## Repo layout

```
.
├── .claude-plugin/marketplace.json     # marketplace manifest (5 plugins)
├── plugins/
│   ├── adk-core/                       # auto, setup, info, temp-folder, mode-contract,
│   │   │                                 prompt-expand, context-gather + hooks + bin
│   │   ├── .claude-plugin/plugin.json
│   │   ├── hooks/                      # PreToolUse:Bash safety, SessionStart banner
│   │   ├── bin/                        # adk-info, adk-task-slug, adk-mcp-health
│   │   ├── agents/                     # dispatcher, prompt-expander, context-gatherer
│   │   └── skills/                     # 7 skills
│   ├── adk-code/                       # 8 skills (build/fix/refactor/migrate/test/perf/api/security)
│   ├── adk-review/                     # 6 skills + GitHub MCP
│   ├── adk-docs/                       # 8 skills (write/review/pr-desc/commit/changelog/diagram/publish×2)
│   └── adk-investigate/                # 8 skills + Datadog + Statsig MCPs
├── plan/                               # detailed plan files (10 docs; the "spec")
├── scripts/verify_marketplace.py       # marketplace + SKILL.md validator
├── README.md                           # this file
├── SETUP.md                            # env-var setup walkthrough
├── CHANGELOG.md
├── LICENSE
└── PLAN.md                             # entry point for the design plan
```

Each plugin directory has its own `README.md` describing its skills and any setup requirements. Each skill directory has a `SKILL.md` (frontmatter + behavior contract) and a `references/` folder containing the persona, anti-patterns, examples, etc. — every skill is self-contained.

---

## How `adk` decides which skill to run

Two layers, designed so you never have to memorize skill names:

1. **Top-level dispatcher — `adk-core:auto`.** When you give a free-form prompt that doesn't name a specific skill, `auto` runs Phase 0 prompt expansion (restate, classify the verb, resolve entities against meta-info, identify links → context-gather), matches against the dispatch matrix, and dispatches the chosen skill chain.
2. **Per-skill auto-routing.** Every SKILL.md description is engineered to be "pushy" so Claude's own skill matcher picks it up when the prompt matches its trigger patterns. The "Common prompts" section in each SKILL.md is the auto-route trigger list.

Result: you can either name a skill explicitly (`/adk-review:review-pr <url>`) or just talk naturally ("review the PR") and `auto` (or Claude's matcher) picks the right skill.

---

## Updating skills

If you contribute to a plugin or skill:

- Skill folder name uses kebab-case and matches the YAML `name:` field in `SKILL.md`.
- Cross-plugin references use `/<plugin>:<skill>` form (e.g. `/adk-review:review-pr`).
- The plugin's `dependencies` field in `plugin.json` declares hard deps. Soft deps go in skill descriptions / references.
- Don't add MCPs unless absolutely required — prefer claude.ai workspace connectors and built-in tools (`WebSearch`, `WebFetch`, `Bash` with the safety hook).
- Run `python3 scripts/verify_marketplace.py` from repo root before committing.
- See each plugin's README for any plugin-specific contribution rules.

## License

MIT — see [LICENSE](./LICENSE).
