# adk — agents-devkit

A single-repo, multi-agent skill kit for Principal Engineer workflows: implement, review, investigate, document, sync — composed with an advisor-strategy wrapper and a self-improving decision-log loop.

> **Marketplace? No.** v3 installs directly to the active agent(s) at user level via `./install.sh`. No plugin registry, no `/plugin install`. Clone the repo, run install, the skills appear in your agent.

## Supported agents

| Agent | Status | What's installed |
|---|---|---|
| Claude Code | full | skills, agents, slash commands, MCPs, `CLAUDE.md` global pointer |
| Cursor | full | rules (`.mdc`), MCP config, global rules pointer |
| Codex (OpenAI CLI) | partial | prompts, MCP entries in `~/.codex/config.toml`; see `agents-codex/README.md` for gaps |
| Junie (JetBrains AI) | partial | `~/.junie/guidelines.md` append; see `agents-junie/README.md` for gaps |

## Install

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/code/agents-devkit
cd ~/code/agents-devkit
./install.sh                  # autodetects installed agents and wires them up
./install.sh --target claude  # only one
./install.sh --target all     # try every supported agent regardless of detection
./install.sh --uninstall      # removes by marker, leaves your overrides
```

After install, edit the scaffolded config templates at `$ADK_CONFIG_HOME/{core.json5,workspaces.json5,repos.json5,...}` to add your details. See `SETUP.md` for CLI deps + env-var requirements.

## Quick start

```bash
# 1. Verify env, deps, MCPs, ollama, tokens
adk doctor

# 2. Index a repo you'll review PRs in (clones to $ADK_DATA_HOME/repos/<name>/)
adk repo add git@github.com:acme/storefront-bff.git

# 3. Sync the PR review queue end-to-end (scan → metadata refresh → drop merged
#    → clean orphans → pre-warm task folders). One command, idempotent.
adk pr-sync --since-hours 24 -y

# 4. In your agent (Claude Code / Cursor / …), drain the queue:
/adk-pr-review           # claims the next eligible row from the queue
                         # (skips rows already reviewed at the current head_sha)

# Or review one specific PR:
/adk-pr-review https://github.com/acme/storefront-bff/pull/42
/adk-review     https://github.com/acme/storefront-bff/pull/42   # lightweight, no worktree
```

### The canonical sync workflow

`adk pr-sync` runs these five steps in order. The individual subcommands are listed for when you want to do one step at a time.

```bash
# One command does everything — recommended:
adk pr-sync                                 # actual delete + actual reminders; idempotent
adk pr-sync --dry-run                       # preview destructive steps (orphans + reminders)
adk pr-sync --no-scan                       # skip Slack scan (queue is already curated)
adk pr-sync --no-clean-orphans              # keep orphan task folders
adk pr-sync --no-remind                     # skip the stale-review Slack pings
adk pr-sync --no-prepare                    # metadata + cleanup only; no Phase 1 prep
adk pr-sync --remind-threshold-hours 48     # only remind on reviews older than 48h
adk pr-sync --rebuild --detailed            # nuclear: force full re-index + bge-m3 embeddings

# Or step-by-step (these are exactly what pr-sync chains together):
adk pr-scan --since-hours 24                # 1. Slack → queue (upsert PR rows)
adk pr-queue update --all                   # 2. refresh head_sha + merged/closed via origin API
adk pr-queue clean                          # 3. drop merged + closed rows + their task folders
adk pr-task clean-orphans --dry-run         # 4. preview folders with no queue row
adk pr-task clean-orphans -y                #    actually delete them
adk pr-queue remind --dry-run               # 5. preview stale-review Slack pings
adk pr-queue remind                         #    actually post reminders (one per 24h window)
adk pr-task prepare --all                   # 6. create/refresh task folders for remaining rows
                                            #    short-circuits when head_sha hasn't moved
```

**What each step does**

| Step | What happens | Idempotency |
|---|---|---|
| 1 | `pr-scan` walks configured Slack channels; new PR links → new queue rows (status=pending) | Re-scans dedupe by PR URL |
| 2 | `pr-queue update --all` fetches cheap metadata per row via the origin API (GitHub `gh pr view` / Bitbucket REST). The `state` field is interpreted uniformly: `merged_at` set → status=merged; GitHub `CLOSED`-without-merge or Bitbucket `DECLINED` / `SUPERSEDED` → status=closed; otherwise open. | Re-runs are cheap; one call per row |
| 3 | `pr-queue clean` drops every row in a terminal state (merged or closed) AND its `$ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/` task folder | No-op when nothing is terminal |
| 4 | `pr-task clean-orphans` removes any task folder whose PR isn't in the queue (or whose row is in a terminal state) | Always dry-run unless `-y`; safe to repeat |
| 5 | `pr-queue remind` posts a Slack reply in the original thread for every row that: was reviewed >=24h ago, has no new commits since (`head_sha == last_reviewed_head_sha`), isn't terminal, hasn't been reminded in the last 24h, and has `slack.{channel_id,thread_ts}` populated. Stamps `last_reminded_at` so the next pass doesn't re-fire | One reminder per 24h window per row |
| 6 | `pr-task prepare --all` runs Phase 0-4a for every remaining row: fetch PR, sync clone, materialise worktree at the PR head, chunk + embed + SCIP, build precis | Triple-incremental: (a) when `head_sha == last_indexed_head`, Phase 3 skips entirely; (b) when head moved but file delta is computable, only changed files are re-indexed; (c) embed-model is read from the existing `code-index/meta.json` so a re-run without `--detailed` keeps the prior model. Pass `--rebuild` to override and re-index from scratch. |

**Queue acquisition behaviour**

`/adk-pr-review` (no args) drains the queue through `adk pr-queue get-next`, which:

1. Atomically claims the next FIFO row that's not locked, not in a terminal state, and not already reviewed at the current `head_sha` (`last_reviewed_head_sha == head_sha`).
2. **Validates the candidate against the origin API.** If the PR has been merged or closed since the last sync, the row is dropped from the queue (and its on-disk task folder cleaned) — the picker moves on to the next candidate.
3. Refreshes `head_sha` on the row from the API result before handing it back, so the worktree is materialised at the actual head, not a stale snapshot.

```bash
adk pr-queue get-next                       # claim the next eligible row (origin-API validated)
adk pr-queue get-next --no-validate         # skip the API check for already-validated callers
```

Explicit `/adk-pr-review <pr-url>` bypasses queue filters and reviews the PR even if it's merged or closed — useful when re-reviewing for posterity, where any posted comments serve as future-reference material.

### Design principles

**One verb, one purpose.** Each CLI verb does exactly one thing. Composition is via `pr-sync` (and you can always run the pieces yourself).

| Concern | Verb | What it touches |
|---|---|---|
| Slack → queue | `adk pr-scan` | queue rows (upsert, dedupe by URL) |
| Origin API → queue metadata | `adk pr-queue update [--all]` | `head_sha`, `status` (merged/closed detection) |
| Queue → task folder | `adk pr-task prepare [--all] [--rebuild]` | worktree + chunk + embed + SCIP + precis |
| Findings gate | `adk pr-task validate <url>` | drops drifted anchors + no-fix findings |
| Drop terminal rows | `adk pr-queue clean` | merged + closed rows + their folders |
| Drop stranded folders | `adk pr-task clean-orphans` | folders with no queue row |
| Slack-thread nudges | `adk pr-queue remind` | one ping per 24h per stale review |
| Claim next PR | `adk pr-queue get-next` | atomic claim with origin-API validation |
| All of the above | `adk pr-sync` | runs the six steps in order |

**Everything is incremental.** Re-running any verb is idempotent and short-circuits when nothing changed.

- `pr-scan` dedupes by PR URL — re-scans only add genuinely new rows.
- `pr-queue update` is metadata-only — one cheap origin-API call per row.
- `pr-task prepare` skips Phase 3 (chunk + embed + SCIP) when `head_sha == last_indexed_head`; when head moved, only the changed files are re-indexed.
- `pr-queue remind` rate-limits to one ping per 24h via `last_reminded_at`.
- `pr-task clean-orphans` is naturally idempotent.

**One rebuild flag.** `--rebuild` (used by `pr-task prepare` and `repo update`) means "ignore short-circuits and re-index from scratch". There is no separate `--force` or `--full`. Pass `--rebuild` when the index is corrupted, when you switch to a different embedding model, or when you want certainty.

**Embed model is sticky.** `pr-task prepare URL --detailed` records `bge-m3` in `code-index/meta.json`. Subsequent re-runs without `--detailed` read that file and keep using `bge-m3` — you don't get a model-mismatch error. The recorded model is also what `query_index.py` uses to embed the agent's queries against the index, so retrieval is always consistent. To switch models, pass `--rebuild --embed-model <new>` (or `--rebuild --detailed`).

If two terminals run a sync at the same time, the second sees `taken_at` and skips that row. If a sync was interrupted mid-prepare, the next run picks up where it left off — already-indexed PRs short-circuit, the rest finish.

### The `/adk-pr-review` pipeline — 6 phases

Every review goes through this pipeline. Scripts handle every phase except Phase 2 (the actual review), which is the agent running the skill. The full contract is in `skills/adk-pr-review/SKILL.md`.

| # | Phase | Who | CLI entry | Output |
|---|---|---|---|---|
| 0 | Claim — pick next eligible PR (FIFO + origin-API validated; auto-drop merged/closed) | script | `adk pr-queue get-next` | `taken_at` set |
| 1 | Prepare — clone fetch, worktree at PR head, chunk + embed + SCIP, supporting docs, precis. **Does NOT review.** Idempotent. | script | `adk pr-task prepare <url>` | `pr.json`, `code/`, `code-index/`, `precis.md` |
| 2 | Review — agent reads precis + diff + index; may spawn child agents for parallel passes (security, tests, feature-flow); writes findings per `finding.template.json` | **agent** | n/a | `findings.json` |
| 3 | Validate — each finding gated on (a) anchor still resolves in worktree and (b) `suggestion` is non-trivial. Findings without an identifiable fix stay in the audit trail but are NOT posted. `question` and `appreciation` exempt from (b). | script | `adk pr-task validate <url>` | `validated-findings.json` + `initial-findings.json` + `validation-report.json` |
| 4 | Triage — auto (`posted-comments == initial-findings`) or `-i` (user walks accept / reject / edit) | script (+ agent in `-i`) | `triage.py --init --finalize` | `triage.json` |
| 5 | Post — inline review comments via host MCP; resolve / reopen / reply to existing PR threads; Slack summary in the queue thread | script | `post_comments.py` | `posting-plan.json`, posted comments |
| 6 | Disposition — `approve` / `request_changes` / `comment_only`. `--merge-if-approved` prints `MERGEABLE — click to merge: <url>`; the script **never** merges (constitution §I.3) | script | `report.py --merge-if-approved` | `report.md`, `state.json` |

## CLI tools — the `adk` binary

`install.py` symlinks `bin/adk` into `~/.local/bin/adk`. Make sure `~/.local/bin` is on your `PATH`.

Every subcommand accepts `-y` / `--yes` for non-interactive mode (smart defaults, no prompts). Skills shell out with `-y` for headless automation.

```text
adk --help                                  # top-level usage
adk <subcmd> --help                         # per-subcommand options
adk completion zsh >> ~/.zshrc              # shell completion (bash | zsh | fish)
```

### `adk doctor` — environment health check

Validates env vars, CLI deps (`gh`, `jq`, `uv`, `node`, `python`, `ollama`, `scip-*`), MCP reachability, ollama model presence, and credential files.

```bash
adk doctor                  # full check, human-readable
adk doctor --strict         # exit non-zero on any ⚠ (good for CI)
adk doctor --json           # machine-readable
adk doctor --tui            # interactive curses TUI
```

Run this first whenever something's misbehaving — it tells you exactly which env var is missing, which MCP is unreachable, or which ollama model needs pulling.

### `adk repo` — manage indexed checkouts

`/adk-pr-review` runs out of an isolated worktree it owns. The worktree is anchored to a base clone under `$ADK_DATA_HOME/repos/<name>/` with a precomputed code-index (chunks + LanceDB + optional SCIP). `adk repo` builds and refreshes that index.

```bash
adk repo add git@github.com:acme/foo.git              # clone default branch + build full index
adk repo add ./local/path --name foo                  # adopt an existing local checkout
adk repo update foo                                   # fetch + fast-forward + incremental reindex
adk repo update foo --full                            # rebuild index from scratch
adk repo update --all                                 # update every indexed repo (continues past per-repo failures)
adk repo list                                         # show indexed repos + last-indexed OID
adk repo list --names-only                            # one name per line (used by shell completion)
```

The index lives at `$ADK_DATA_HOME/repos/.indices/<repo>/code-index/` and is consumed by `/adk-pr-review` (seed-and-overlay merge with the PR diff) and the other skills via `scripts/lib/code_index/query.py`.

### `adk pr-scan` — populate the review queue from Slack

Walks the channels configured in `$ADK_CONFIG_HOME/connectors/slack.json5` (`pr_reviews.channels`), reads main messages **and** thread replies, extracts every GitHub / Bitbucket PR URL, and upserts rows into `$ADK_CONFIG_HOME/pr-queue.json5`.

```bash
adk pr-scan                              # default window (configured in slack.md)
adk pr-scan --since-hours 24             # last 24 hours
adk pr-scan --since-days 7
adk pr-scan --channels '#eng-prs,#sf-pr-reviews'    # override channel list
adk pr-scan --dry-run                    # show what would change, don't write
adk pr-scan -y                           # non-interactive
```

Run this whenever you want fresh PRs in the queue. `/adk-pr-review` (no arg) drains it FIFO with a 30-min auto-expiring lock per row so two terminals review different PRs.

### `adk pr-queue` — inspect / manage the queue

```bash
adk pr-queue list                        # all entries, with status + last_checked_at
adk pr-queue list --status open          # filter
adk pr-queue list --urls-only            # one URL per line (used by shell completion)
adk pr-queue show <pr-url>               # one entry as JSON (slack threads, supporting docs, lock)
adk pr-queue add <slack-permalink>       # single-shot upsert (accepts a PR URL too)
adk pr-queue update <pr-url>             # metadata only — origin API → head_sha + merged/closed
adk pr-queue update --all                # bulk metadata refresh on every non-terminal row
adk pr-queue ready-to-merge              # approved PRs, grouped by open-comment state
adk pr-queue clean                       # drop merged + closed rows + their skill-pr-review/ folders
adk pr-queue clean --all -y              # nuke everything (queue + per-PR scratch dirs)
adk pr-queue release <pr-url>            # clear a stuck `taken_at` lock
adk pr-queue get-next                    # Phase 0: claim next eligible row (origin-API validated)
adk pr-queue remind [--threshold-hours N] [--dry-run]   # Slack reminders for stale reviews
```

`pr-queue` is read-by-other-skills: when you pass a PR URL to `/adk-pr-review` that already has a queue row, the row's `slack` thread + `supporting_docs` are merged into the review context.

**One verb does one thing.** `pr-queue update` only refreshes the row's metadata via the origin API; it does NOT touch the worktree or the index. To create / refresh the task folder (worktree + chunk + embed + SCIP), use `adk pr-task prepare`. To do both at once, use `adk pr-sync`. This separation is intentional — every operation is composable.

**Queue acquisition skips already-reviewed PRs.** When `/adk-pr-review` is invoked with no URL, it drains the queue FIFO but excludes any row whose `head_sha == last_reviewed_head_sha` (set by the prior review's completion step). New commits push the row back into eligibility automatically. Merged PRs are skipped the same way. Explicit `/adk-pr-review <pr-url>` always reviews — useful for re-reviewing a merged PR for posterity, where comments still post for future reference.

### `adk pr-task` — manage per-PR task folders

The stable CLI surface for the per-PR scratch dir at `$ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/`. `/adk-pr-review` calls these internally so it doesn't depend on script paths.

```bash
adk pr-task prepare <pr-url>             # create or refresh the task folder (phase 0-4a)
                                         # idempotent — unchanged head_sha short-circuits
adk pr-task prepare <pr-url> --rebuild   # force a full index rebuild
adk pr-task prepare <pr-url> --detailed  # use the bge-m3 embedder (higher recall, slower)
adk pr-task info <pr-url>                # JSON: task_dir, head_sha, last_indexed_head, has-findings
adk pr-task list                         # every task folder under $ADK_DATA_HOME/skill-pr-review/
adk pr-task list --names-only            # one folder name per line (used by completion)
adk pr-task list --paths                 # one absolute path per line
```

`prepare` is the same Phase 0-4a work as `pr-queue update <url> --full`, minus the queue metadata write. Use `pr-task prepare` when you only care about the cached worktree + index; use `pr-queue update --full` when you also want the queue's `head_sha` / `status` refreshed.

### `adk completion` — shell completion

```bash
adk completion zsh  >> ~/.zshrc
adk completion bash >> ~/.bashrc
adk completion fish > ~/.config/fish/completions/adk.fish
```

## Review commands

There are two review skills with different cost / depth tradeoffs.

### `/adk-review` — lightweight, polymorphic

No worktree, no embeddings. Reads the diff, applies six review dimensions (correctness → tests → security → performance → readability → consistency), emits severity-tiered findings with `path:line` evidence.

```text
/adk-review                                  # current branch vs main (local working tree)
/adk-review .                                # same — explicit
/adk-review path/to/file.ts                  # one file
/adk-review https://github.com/o/r/pull/42   # remote PR (no checkout)
/adk-review --audit                          # whole-repo audit (heavyweight, but no worktree)
/adk-review docs/runbooks/checkout.md        # markdown file
/adk-review -i                               # interactive walk through findings
/adk-review --fix                            # apply accepted findings + push (never to protected branches)
/adk-review --plan                           # read-only review-and-recommend; no edits
```

Refuses single-pass on diffs > 5000 LOC — for those, use `/adk-pr-review`.

### `/adk-pr-review` — deep, owns a worktree

The default for any real PR review. Builds the full pipeline:

1. **Clone + worktree** at the PR head under `$ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/code/` (uses `$ADK_DATA_HOME/repos/<name>/` as the base if `adk repo add` was run).
2. **Tree-sitter chunker** → **ollama embed** (`nomic-embed-text` default; `bge-m3` with `--detailed`) → **LanceDB** with FTS index. Hybrid retrieval (vector + BM25) at query time.
3. **SCIP cross-file symbols** when `scip-typescript` / `scip-python` / `scip-go` / `scip-java` is on `PATH`. Missing → grep + chunker `parent_symbol` fallback (lower confidence; surfaced in the report).
4. **Feature-flow tracing** through Statsig flags, experiments, and dynamic configs the diff touches.
5. **Optional harness-LLM rerank** of retrieval candidates (JSONL queue contract; the harness picks the model).
6. **findings.json** → **triage step** (in `-i`, walk each finding accept / reject / edit; edits go through an iterative LLM rewrite loop) → **post via the GitHub or Bitbucket MCP** after explicit confirmation.

```text
/adk-pr-review                                            # claim the next queue row (FIFO)
/adk-pr-review https://github.com/acme/foo/pull/42        # specific GitHub PR
/adk-pr-review https://bitbucket.org/acme/foo/pull-requests/7   # specific Bitbucket PR
/adk-pr-review <url> -i                                   # interactive triage before posting
/adk-pr-review <url> --detailed                           # bge-m3 embeddings (slower, better recall)
/adk-pr-review <url> --skip-rerank                        # disable harness rerank
```

**Parallel review**: run `/adk-pr-review` (no arg) in N terminals and each claims a different row via a 30-min auto-expiring `taken_at` lock. Use `adk pr-queue release <url>` to free a stuck lock.

**Isolation**: this skill is global. It never touches your cwd. All scratch state lives under `$ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/` (see `shared/paths.md`).

## All skills

```text
/adk-implement   write code from any input (Jira / GH issue / Slack / TDD / Confluence / freeform)
/adk-review      lightweight review (PR URL / local / doc / comment thread / whole repo)
/adk-pr-review   deep PR review with worktree + embeddings + SCIP + feature-flow tracing
/adk-investigate query 3P data sources (Datadog / Mixpanel / Statsig / Snowflake / Looker / Atlassian)
/adk-document    generate any written artifact (RCA / ADR / runbook / PR body / commit msg / diagram / report)
/adk-sync        bidirectional bridge to 3P (Confluence / Jira / GDoc / GH PR body / Slack)
/adk-setup       bootstrap overrides, enrich metadata, verify env+MCPs
/adk-improve     read decision logs → propose default updates; refresh metadata
/adk-explain     advisor agent for "I don't know which to pick"
```

Each skill is task-based and polymorphic on input. Every skill goes through a mandatory **question-first** phase (auto by default; `-i` for interactive) that doubles as training data for the self-improvement loop.

## Key concepts

- **One source of truth for user data:** `$ADK_CONFIG_HOME/` — `core.json5` (identity / defaults), `workspaces.json5`, `repos.json5`, `services.json5`, `connectors/*.json5` (per-source auth + config), `relations.json5` (cross-connector entity graph).
- **Project-scoped overrides:** `<repo>/.adk/overrides.yaml` + `<repo>/ai-guidelines/` (or `docs/`).
- **Two task-folder roots** (see `shared/paths.md`): repo-bound skills write under `<repo>/.temp/adk/<skill>/<task>/`; global skills (pr-review, investigate, sync, …) write under `$ADK_DATA_HOME/<area>/<task>/`. The latter root is created by `install.sh`.
- **Self-improving:** every Q&A and override is logged to `$ADK_MEMORY_HOME/learning/decisions.jsonl`; `/adk-improve` reads logs and proposes updated defaults that get applied to `$ADK_CONFIG_HOME/core.json5` (or the right connector file) after you confirm.
- **Metadata cache:** `$ADK_DATA_HOME/metadata/<source>.json` — built by `/adk-setup --enrich` and refreshed by `/adk-improve --metadata`. Skills consult it instead of re-introspecting on every run.
- **RAG optional:** drop an `RAG_MCP_URL` into env, set `rag.enabled: true` in overrides, and every skill's context-gather phase pulls company knowledge alongside MCP results.

## Honest limits

- macOS primary; Linux works. Windows unsupported.
- GitHub and Bitbucket Cloud supported (Bitbucket via `adk-mcp-bitbucket` + REST). GitLab and Bitbucket Server are not in scope.
- Codex and Junie are shipped with the gaps documented; full feature parity is Claude + Cursor.
- Slack support requires `SLACK_CREDENTIALS_FILE` to be a shell-sourceable file exporting `SLACK_BOT_TOKEN` and/or `SLACK_USER_TOKEN`.

## Where to read next

- `AGENTS.md` — how prompts get routed (read first if you're an agent).
- `SETUP.md` — env vars + install walkthrough (read first if you're a human).
- `shared/constitution.md` — universal rules.
- `skills/adk-*/SKILL.md` — per-skill specs.
