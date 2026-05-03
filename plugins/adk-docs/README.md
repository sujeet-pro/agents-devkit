# adk-docs

> Documentation authoring, review, and publishing for the `adk` marketplace.
> Eight single-verb skills, two persona agents, zero shipped MCPs.

`adk-docs` covers the prose side of the Principal Engineer workflow: writing
markdown docs grounded in real code, reviewing existing docs against the
source of truth, drafting PR descriptions and commit messages, appending
changelog entries, authoring Mermaid diagrams, and publishing markdown to
Confluence / Google Drive without duplicating pages.

## What it ships

| Component | What |
| --- | --- |
| **Skills (8)** | `docs-write`, `docs-review`, `docs-pr-description`, `docs-commit-message`, `docs-changelog`, `docs-diagram`, `docs-publish-confluence`, `docs-publish-gdrive` |
| **Agents (2)** | `doc-writer`, `doc-reviewer` |
| **Templates (4)** | `readme.md`, `adr.md`, `runbook.md`, `migration-guide.md` (under `skills/docs-write/references/templates/`) |
| **MCPs shipped** | none |
| **Hooks** | none (inherits `adk-core` `PreToolUse:Bash` safety + `SessionStart` banner) |
| **Bin scripts** | none (inherits `adk-core`'s `adk-info`, `adk-task-slug`, `adk-mcp-health`) |

## Skills

### `docs-write` — author or refresh a markdown doc

Write README / runbook / ADR / migration guide / API reference / onboarding
guide / design doc, grounded in actual repo files (not training data). Cites
every claim to a repo path. `--fix` writes to the canonical path (e.g.
`README.md`, `docs/adr/0007-*.md`) and stages the change. Never commits,
never pushes.

```text
/adk-docs:docs-write "README for the checkout service"
/adk-docs:docs-write "ADR for the auth migration" --audience eng -i
/adk-docs:docs-write "runbook for on-call rotation" --fix
```

### `docs-review` — audit an existing doc against the source

Review markdown files, fetched URLs, Confluence pages (via the workspace
Atlassian connector), or Google Docs (via the workspace Google Drive
connector). Severity-tiered findings (Blocker / Critical / Should-Have /
May-Have / Nitpick). `--fix` applies non-controversial corrections in place;
does NOT rewrite voice.

```text
/adk-docs:docs-review docs/runbooks/oncall.md
/adk-docs:docs-review "https://acme.atlassian.net/wiki/spaces/ENG/pages/42" -i
/adk-docs:docs-review README.md --fix
```

### `docs-pr-description` — draft a PR description from the diff

Reads `git log <base>..HEAD` and `git diff <base>...HEAD`; loads
`.github/pull_request_template.md` if present; drafts Title, Summary, Test
plan, Risks, Linked tickets. `--fix` updates the PR body via `gh pr edit`.

```text
/adk-docs:docs-pr-description
/adk-docs:docs-pr-description main -i
/adk-docs:docs-pr-description main --auto --fix
```

### `docs-commit-message` — draft a commit message from staged diff

Detects the repo's existing convention (Conventional Commits, semantic-
release, free-form) from `git log -10 --pretty=format:%s`. Drafts subject
(≤72 chars) + body explaining the WHY. `--fix` runs `git commit -m "..."`
after one explicit confirmation. Never amends.

```text
/adk-docs:docs-commit-message
/adk-docs:docs-commit-message --style conventional -i
/adk-docs:docs-commit-message --fix
```

### `docs-changelog` — append a changelog entry

Reads `git log <from>..<to>`; groups by type (feat / fix / chore / breaking);
matches existing changelog style (Keep a Changelog, semantic-release, free-
form). Calls out breaking changes prominently. Never invents entries.

```text
/adk-docs:docs-changelog v1.2.0 HEAD
/adk-docs:docs-changelog v1.1.0 v1.2.0 --fix
```

### `docs-diagram` — author a Mermaid diagram

Supports flowchart, sequence, class, state, ER, gantt, gitgraph, mindmap,
timeline, C4. Keeps diagrams under 15 nodes (splits larger concepts).
Renders to SVG (light + dark) via the diagramkit npx tool. Never produces
ASCII art when Mermaid is what's asked.

```text
/adk-docs:docs-diagram sequence "auth login flow"
/adk-docs:docs-diagram ER "orders schema" --scope db/schema.sql
```

### `docs-publish-confluence` — publish markdown to Confluence

Via the **workspace Atlassian connector** (no MCP shipped). Match-by-title-
and-parent before creating so retries are idempotent. Never overwrites a
page authored by a human (warns on non-bot author).

```text
/adk-docs:docs-publish-confluence docs/design/auth.md --space ENG
/adk-docs:docs-publish-confluence .temp/task-readme/draft.md --parent "Engineering Home" -i
```

### `docs-publish-gdrive` — publish markdown to Google Drive

Via the **workspace Google Drive connector** (no MCP shipped). GDoc / md /
PDF output formats. Folder placement per `docs.md`. **Never** changes
sharing permissions automatically — sharing is a human action.

```text
/adk-docs:docs-publish-gdrive .temp/task-<slug>/draft.md --format gdoc
/adk-docs:docs-publish-gdrive README.md --folder "1AbC..." -i
```

## Agents

| Agent | Persona | Used by |
| --- | --- | --- |
| `doc-writer` | "Write for the reader. Concrete > abstract. Show, don't tell. Cite every claim to a repo path." | `docs-write`, `docs-pr-description`, `docs-commit-message`, `docs-changelog` |
| `doc-reviewer` | "Audit against the actual code. Distinguish stale from wrong from incomplete. Tier findings by severity." | `docs-review` |

Agents hold persona + hard rules; the skill holds the workflow.

## MCP strategy — no MCP shipped

`adk-docs` ships **no `.mcp.json`**. Read + write to Confluence and Google
Drive goes through the **claude.ai workspace connectors** (Atlassian and
Google Drive) that the operator already has enabled — so `adk-docs` never
duplicates auth state.

| Capability | Source | Skills that use it |
| --- | --- | --- |
| Confluence read + write | claude.ai Atlassian workspace connector | `docs-publish-confluence`, `docs-review` (when target is a Confluence URL) |
| Google Drive read + write | claude.ai Google Drive workspace connector | `docs-publish-gdrive`, `docs-review` (when target is a GDoc URL) |
| GitHub (PR body edit, PR diff fetch) | `gh` CLI by default; `adk-review`'s `github` MCP if both plugins are installed | `docs-pr-description` |
| Git (diff, log, commit) | local `git` via the Bash tool | `docs-pr-description`, `docs-commit-message`, `docs-changelog` |

Skills detect the workspace connector via `claude mcp list` in Phase 1
preflight and stop with a `connector missing` message if the required one
isn't connected.

## Installation

```text
/plugin install adk-docs@adk
/reload-plugins
```

`adk-core` is a dependency and is auto-installed. Optional: install
`adk-review` as well so `docs-pr-description` can use the `github` MCP
instead of the `gh` CLI fallback.

## Meta-info consumed

| File | Topics used |
| --- | --- |
| `~/.config/adk/info.md` | operator name + email (signs PR descriptions and commits) |
| `~/.config/adk/repos.md` | repo → local folder mapping, default base branch, primary language |
| `~/.config/adk/github.md` | PR template path, default reviewers, default merge method (docs-pr-description only) |
| `~/.config/adk/docs.md` | default Confluence space + parent, default GDrive folder id, ADR / runbook / changelog paths, audience default |

If a required field is missing, skills stop with a copy-paste-able
suggestion and offer `/adk-core:setup --target <topic>`.

## Repo layout

```
adk-docs/
├── .claude-plugin/plugin.json
├── README.md                          # this file
├── agents/
│   ├── doc-writer.md
│   └── doc-reviewer.md
└── skills/
    ├── docs-write/{SKILL.md, references/*.md, references/templates/*.md}
    ├── docs-review/{SKILL.md, references/*.md}
    ├── docs-pr-description/{SKILL.md, references/*.md}
    ├── docs-commit-message/{SKILL.md, references/*.md}
    ├── docs-changelog/{SKILL.md, references/*.md}
    ├── docs-diagram/{SKILL.md, references/*.md}
    ├── docs-publish-confluence/{SKILL.md, references/*.md}
    └── docs-publish-gdrive/{SKILL.md, references/*.md}
```

See `plan/13-adk-docs.md` (in the repo root) for the authoritative per-skill
spec.
