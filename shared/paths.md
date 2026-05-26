# shared/paths.md — canonical task-folder layout

> Where artifacts go. Loaded by every skill. Higher priority than any SKILL.md path string. Superseded only by an explicit `--out` flag the user passes on this invocation.

## Two roots, one rule

A skill writes its artifacts to **exactly one** of two roots:

| Root | When | Reason |
|---|---|---|
| `<repo>/.temp/adk/<skill-stem>/<task>/` | The skill operates **on the cwd repo** (reads or writes files in this checkout). | Artifacts live next to the code they describe; gitignored; a human can `cd` to them. |
| `$ADK_DATA_HOME/<area>/<task>/` | The skill operates **without a cwd repo** — its inputs are URLs, IDs, dashboards, MCPs; or its working copy is an isolated clone/worktree it owns. | A user can invoke from anywhere (`~`, `/tmp`, an unrelated repo) and the skill still works. No pollution of the user's current project. |

**The rule**: if running the skill requires the user's cwd to be inside a specific repo, the root is `<repo>/.temp/adk/`. Otherwise, it's `$ADK_DATA_HOME/`.

## Per-skill anchoring

| Skill | Root | Layout | Notes |
|---|---|---|---|
| `/adk-implement` | repo-bound | `<repo>/.temp/adk/implement/<task>/` | Writes code into the cwd repo. Always repo-bound. |
| `/adk-document` | repo-bound | `<repo>/.temp/adk/document/<task>/` | Draft path. `--write-to <path>` overrides to a canonical repo path (e.g. `docs/adr/...`). |
| `/adk-review` | hybrid | `<repo>/.temp/adk/review/<task>/` for `.` / local-changes / `--audit`; `$ADK_DATA_HOME/skill-review/<task>/` for a PR URL where the cwd is unrelated | Light review. No worktree, no embeddings. |
| `/adk-pr-review` | **global, always** | `$ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/` | Heavy review. Owns a worktree in `$ADK_DATA_HOME/repos/<repo>/`. Never touches cwd. |
| `/adk-investigate` | global | `$ADK_DATA_HOME/skill-investigate/<task>/` | Queries DD / Slack / Statsig / Mixpanel / Snowflake / Looker. No repo. |
| `/adk-sync` | hybrid | `<repo>/.temp/adk/sync/<task>/` when invoked from a repo and the synced doc belongs to that repo; `$ADK_DATA_HOME/skill-sync/<task>/` otherwise | Bridge for 3P docs. |
| `/adk-setup` | global | `$ADK_DATA_HOME/skill-setup/<ts>/` | Configures `$ADK_CONFIG_HOME/`. |
| `/adk-improve` | global | `$ADK_DATA_HOME/skill-improve/<ts>/` (top-level `improve/` keeps the shared learning data) | Reads decision logs. |
| `/adk-explain` | global | `$ADK_DATA_HOME/skill-explain/<ts>/` (only if an artifact is produced; usually ephemeral) | Advisor, mostly transient. |

`<skill-stem>` = the skill name with the leading `adk-` stripped. `<task>` = the task discriminator (Jira key, PR number, slug from the prompt). `<ts>` = a UTC timestamp `YYYYMMDDTHHMMSSZ` when no natural discriminator exists.

## $ADK_DATA_HOME/ skeleton (v4)

```
$ADK_DATA_HOME/
├── memory/                      # user-managed cross-session memory
├── config/                      # user-owned settings
│   ├── core.yaml                # user, workspaces, defaults, rag, learning_state, enriched
│   ├── repos.md                 # frontmatter: repo defs. body: per-repo notes
│   ├── links.json5              # cross-connector entity graph (see below)
│   ├── settings.json5           # session-level settings
│   ├── adk-cli.json5            # CLI behaviour knobs (pr_sync / pr_scan / pr_review_all)
│   ├── pr-queue.json5           # PR review queue — curated by `adk pr-scan`, drained by /adk-pr-review
│   ├── pr-queue.json5.lock      # fcntl sidecar for atomic queue writes
│   ├── connectors/              # one .md per data source — frontmatter is config, body is notes
│   │   ├── datadog.md mixpanel.md statsig.md snowflake.md
│   │   ├── slack.md             # absorbs pr_reviews: section (was pr-reviews-slack.json5)
│   │   └── atlassian.md github.md bitbucket.md
│   └── .legacy/                 # archived v3 files (overrides.yaml, *.md) — kept for rollback
├── improve/                     # data the /adk-improve skill reads/writes
│   ├── learning/{decisions.jsonl, sessions/, archive/, proposals/, summary.md}
│   └── metadata/{archive/<ts>/, <source>.json}   # MCP introspection cache + archive
├── repos/<repo-name>/           # one folder per tracked repo
│   ├── .clone-lock              # per-repo lock used during fetch/worktree-add
│   ├── original-clone/          # bare clone (.git/ only) — source for every worktree
│   ├── docs/                    # supporting docs (lazy, optional)
│   ├── repo-meta.json           # url, default_branch, tracked_branches[]
│   └── branch-<slug>/           # one per tracked branch (default + extras)
│       ├── branch-meta.json     # branch, slug, last_indexed_oid, embed_model
│       ├── code/                # `git worktree add` from original-clone
│       └── code-index/          # chunks.jsonl + chunks.lance/ + scip/ + meta.json
│                                # consumed by /adk-pr-review (seed-and-overlay) and
│                                # by /adk-implement, /adk-investigate, /adk-document
│                                # via scripts/lib/code_index/query.py
├── skill-pr-review/
│   └── <repo>_pr-<n>/           # one folder per PR being reviewed
│       ├── code/                # PR-head worktree (git worktree add from repos/<n>/original-clone)
│       ├── code-index/          # per-PR seed-and-overlay index over the worktree
│       ├── docs/                # supporting docs pulled from queue-context.json (lazy)
│       ├── state.json           # {phases, task_dir}
│       ├── review.log           # streaming log of the review run
│       ├── narration.log        # append-only live phase narration (tail -f during a run)
│       ├── agent.log            # stdout/stderr of the spawned review agent (pr-review-all)
│       ├── .adk-pr-lock         # per-PR fcntl lock (held during a live review)
│       └── pr-review/           # per-run artifacts (separates "review output" from "code + index + state")
│           ├── pr.json          # PR metadata (host, head_sha, title, body, …)
│           ├── diff.patch       # unified diff (head vs base)
│           ├── precis.md        # short LLM précis of the diff (Phase-1 input)
│           ├── queue-context.json  # slack permalink + supporting_docs from the queue row
│           ├── findings.json    # structured findings (machine-readable)
│           ├── findings.md      # human-readable findings rendering
│           ├── pr-comments.json # prior PR comments fetched for resolve-comments
│           ├── posting-plan.json # what we plan to post (pre-confirmation)
│           └── report.md        # final review report
# The queue itself lives under config/ (see above): config/pr-queue.json5.
├── skill-investigate/<task>/
├── skill-review/<task>/         # lightweight /adk-review on remote PRs
├── skill-sync/<task>/synced/
├── skill-setup/                 # /adk-setup outputs
│   └── auto-runs/<ts>/          # one folder per --check or --init run
├── skill-explain/<ts>/  skill-improve/<ts>/  skill-document/<ts>/  skill-implement/<ts>/
├── tui/                         # state shared between the TUI and background workers
│   ├── runs/                    # one <run-id>.json per active or recent multi-PR run
│   ├── workers/                 # one <worker-id>.json heartbeat per live worker process
│   └── workers/sync-plan.json   # current sync plan (written by pr-sync, read by TUI)
└── logs/                        # CLI log output — `adk pr-sync`, `adk pr-queue`, etc.
                                 # One file per command invocation. Rotated by hand for now.
    └── pr-review-all-runs/<ts>/ # one folder per `adk pr-review-all` / `adk pr-review` run
        ├── report.md            # aggregate result: per-PR status, exit codes, elapsed times
        └── pr-sync.log          # stdout of the pre-flight `adk pr-sync` step
                                 # Per-PR agent stdout lives in the PR's own task dir: agent.log
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
pr_reviews:                       # used by `adk pr-scan` + /adk-pr-review queue mode
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
  { from: "repo:ecomm-ssr",  to: "datadog.apm:acme-site",    relation: "observed_by" },
  { from: "repo:ecomm-ssr",  to: "statsig.project:acme",     relation: "uses_flags_from" },
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
- Writing to `~/` outside `$ADK_DATA_HOME/` and `$ADK_CONFIG_HOME/`. Those are the only two roots adk owns.
- Writing to `/tmp/`. Lost on reboot, not gitignored, not inspectable later.
- Mixing the two roots in one task. A single invocation picks one and stays there.
- Hard-coding `task-slug` into a path string. Use the stem-folder layout so a `find <repo>/.temp/adk/implement/ -mindepth 1 -maxdepth 1` lists all implement tasks cleanly.

## Tooling

`scripts/adk_task_slug.py` resolves the right path given `(skill, input)`:

```bash
python3 scripts/adk_task_slug.py --skill implement --input "SF-1234"
# repo-bound  → /Users/sujeet/code/storefront-bff/.temp/adk/implement/SF-1234/

python3 scripts/adk_task_slug.py --skill pr-review --input https://github.com/acme/foo/pull/42
# global      → /Users/sujeet/.agents-devkit/skill-pr-review/foo_pr-42/

python3 scripts/adk_task_slug.py --skill investigate --input "checkout 500s"
# global      → /Users/sujeet/.agents-devkit/skill-investigate/checkout-500s/
```

Pass `--create` to mkdir the resolved path; `--json` for structured output.
