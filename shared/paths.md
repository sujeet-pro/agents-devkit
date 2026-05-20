# shared/paths.md — canonical task-folder layout

> Where artifacts go. Loaded by every skill. Higher priority than any SKILL.md path string. Superseded only by an explicit `--out` flag the user passes on this invocation.

## Two roots, one rule

A skill writes its artifacts to **exactly one** of two roots:

| Root | When | Reason |
|---|---|---|
| `<repo>/.temp/adk/<skill-stem>/<task>/` | The skill operates **on the cwd repo** (reads or writes files in this checkout). | Artifacts live next to the code they describe; gitignored; a human can `cd` to them. |
| `~/.agents-devkit/<area>/<task>/` | The skill operates **without a cwd repo** — its inputs are URLs, IDs, dashboards, MCPs; or its working copy is an isolated clone/worktree it owns. | A user can invoke from anywhere (`~`, `/tmp`, an unrelated repo) and the skill still works. No pollution of the user's current project. |

**The rule**: if running the skill requires the user's cwd to be inside a specific repo, the root is `<repo>/.temp/adk/`. Otherwise, it's `~/.agents-devkit/`.

## Per-skill anchoring

| Skill | Root | Layout | Notes |
|---|---|---|---|
| `/adk-implement` | repo-bound | `<repo>/.temp/adk/implement/<task>/` | Writes code into the cwd repo. Always repo-bound. |
| `/adk-document` | repo-bound | `<repo>/.temp/adk/document/<task>/` | Draft path. `--write-to <path>` overrides to a canonical repo path (e.g. `docs/adr/...`). |
| `/adk-review` | hybrid | `<repo>/.temp/adk/review/<task>/` for `.` / local-changes / `--audit`; `~/.agents-devkit/reviews/<task>/` for a PR URL where the cwd is unrelated | Light review. No worktree, no embeddings. |
| `/adk-pr-review` | **global, always** | `~/.agents-devkit/pr-reviews/<repo>_pr-<n>/` | Heavy review. Owns a worktree in `~/.agents-devkit/repos/<repo>/`. Never touches cwd. |
| `/adk-investigate` | global | `~/.agents-devkit/investigations/<task>/` | Queries DD / Slack / Statsig / Mixpanel / Snowflake / Looker. No repo. |
| `/adk-sync` | hybrid | `<repo>/.temp/adk/sync/<task>/` when invoked from a repo and the synced doc belongs to that repo; `~/.agents-devkit/sync/<task>/` otherwise | Bridge for 3P docs. |
| `/adk-setup` | global | `~/.agents-devkit/setup/<ts>/` | Configures `~/.agents-devkit/config/`. |
| `/adk-improve` | global | `~/.agents-devkit/improve/<ts>/` | Reads decision logs. |
| `/adk-explain` | global | `~/.agents-devkit/explain/<ts>/` (only if an artifact is produced; usually ephemeral) | Advisor, mostly transient. |

`<skill-stem>` = the skill name with the leading `adk-` stripped. `<task>` = the task discriminator (Jira key, PR number, slug from the prompt). `<ts>` = a UTC timestamp `YYYYMMDDTHHMMSSZ` when no natural discriminator exists.

## ~/.agents-devkit/ skeleton (v4)

```
~/.agents-devkit/
├── memory/                      # user-managed cross-session memory
├── config/                      # user-owned settings
│   ├── core.yaml                # user, workspaces, defaults, rag, learning_state, enriched
│   ├── repos.md                 # frontmatter: repo defs. body: per-repo notes
│   ├── links.json5              # cross-connector entity graph (see below)
│   ├── settings.json5           # session-level settings
│   ├── connectors/              # one .md per data source — frontmatter is config, body is notes
│   │   ├── datadog.md mixpanel.md statsig.md snowflake.md
│   │   ├── slack.md             # absorbs pr_reviews: section (was pr-reviews-slack.json5)
│   │   └── atlassian.md github.md bitbucket.md
│   └── .legacy/                 # archived v3 files (overrides.yaml, *.md) — kept for rollback
├── improve/                     # data the /adk-improve skill reads/writes
│   ├── learning/{decisions.jsonl, sessions/, archive/, proposals/}
│   └── metadata/<source>.json   # MCP introspection cache
├── repos/<repo-name>/.git/      # checkouts; the base for PR-review worktrees
├── pr-reviews/
│   ├── queue.json5              # /adk-pr-reviews batch queue (JSON5)
│   └── <repo>_pr-<n>/{code/, pr.json, diff.patch, docs/, code-index/, findings.{json,md}, report.md, state.json}
├── investigations/<task>/
├── reviews/<task>/              # lightweight /adk-review on remote PRs
├── sync/<task>/synced/
├── setup/<ts>/  explain/<ts>/
```

**Why this layout.** `memory/` and `improve/` are top-level because their lifecycle is independent of config (memory is per-session, improve is auto-managed by `/adk-improve`). `config/` is user-owned, with `connectors/<source>.md` as the canonical per-source config — the YAML frontmatter is what scripts read; the markdown body is the human-authored cheatsheet the agent reads as context.

## The connector file shape

```markdown
---
# YAML frontmatter — the machine-read config.
auth:
  token_env: SLACK_BOT_TOKEN_CRED
channels:
  - "#sf-web-pr-reviews"
pr_reviews:                       # /adk-pr-reviews's slice of this connector
  url_patterns: [...]
  status_emoji: { ... }
---

# Notes (markdown body — read by the agent as context)
Conventions, queries, dashboards, on-call list, gotchas.
```

Scripts read frontmatter via `scripts/config_io.py.load_connector(name)` → `(frontmatter: dict, body: str)`.

## The entity graph (`links.json5`)

Cross-connector relationships live in one file:

```json5
[
  { from: "repo:ecomm-ssr",  to: "datadog.apm:quince-site",  relation: "observed_by" },
  { from: "repo:ecomm-ssr",  to: "statsig.project:quince",   relation: "uses_flags_from" },
  { from: "repo:ecomm-ssr",  to: "mixpanel.project:3292013", relation: "emits_events_to" },
]
```

Entity keys: `<kind>:<id>`. Common kinds: `repo`, `datadog.apm`, `datadog.service`, `statsig.gate`, `statsig.experiment`, `statsig.dynamic_config`, `statsig.project`, `mixpanel.project`, `mixpanel.event`, `snowflake.table`, `atlassian.confluence.space`, `atlassian.jira.project`, `github.repo`, `bitbucket.repo`, `slack.channel`.

Common relations: `observed_by`, `observes`, `uses_flags_from`, `emits_events_to`, `gates_feature`, `stored_in`, `documents`, `tracks`.

Skills query the graph via `config_io.neighbors(...)` / `config_io.expand(key, depth=N)` — irrespective of where you enter (a PR, a Datadog incident, a Statsig gate), you can walk to the linked entities.

The folder is created lazily on first use by each skill. `install.py` may create it eagerly, but a skill that finds it missing creates whatever it needs.

## <repo>/.temp/adk/ skeleton

```
<repo>/.temp/
└── adk/
    ├── implement/<task>/
    │   ├── context.md
    │   ├── plan.md
    │   ├── diffs/applied.jsonl
    │   └── report.md
    ├── document/<task>/
    │   ├── draft.md
    │   └── report.md
    ├── review/<task>/
    │   ├── context.md
    │   ├── findings/<dimension>.md
    │   └── report.md
    └── sync/<task>/
        └── synced/
```

`<repo>/.temp/` should be in `.gitignore`. Skills do not enforce this; they refuse to write if the user has `<repo>/.temp/` tracked.

## Migration from the v3.x layout

Before this change: `<repo>/.temp/<task-slug>/` (skill prefixed into the slug). After: `<repo>/.temp/adk/<skill-stem>/<task>/`. Existing in-flight work in the old path is left alone; new tasks use the new path. There is no automatic mover — the user can delete `<repo>/.temp/<old-slugs>/` whenever convenient.

## Anti-patterns

- Writing to `<repo>/` (uncontained). Always under `<repo>/.temp/adk/` or under a canonical destination the user named with `--write-to`.
- Writing to `~/` outside `~/.agents-devkit/` and `~/.agents-devkit/config/`. Those are the only two roots adk owns.
- Writing to `/tmp/`. Lost on reboot, not gitignored, not inspectable later.
- Mixing the two roots in one task. A single invocation picks one and stays there.
- Hard-coding `task-slug` into a path string. Use the stem-folder layout so a `find <repo>/.temp/adk/implement/ -mindepth 1 -maxdepth 1` lists all implement tasks cleanly.

## Tooling

`scripts/adk_task_slug.py` resolves the right path given `(skill, input)`:

```bash
python3 scripts/adk_task_slug.py --skill implement --input "SF-1234"
# repo-bound  → /Users/sujeet/code/storefront-bff/.temp/adk/implement/SF-1234/

python3 scripts/adk_task_slug.py --skill pr-review --input https://github.com/acme/foo/pull/42
# global      → /Users/sujeet/.agents-devkit/pr-reviews/foo_pr-42/

python3 scripts/adk_task_slug.py --skill investigate --input "checkout 500s"
# global      → /Users/sujeet/.agents-devkit/investigations/checkout-500s/
```

Pass `--create` to mkdir the resolved path; `--json` for structured output.
