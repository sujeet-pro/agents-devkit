# stages.md — six-stage taxonomy for adk-pr-review

> Per-stage reference: what each stage does, what it reads/writes, when it skips work, what approach the pipeline picks, and how to invoke or re-run it. See also `shared/decision-log-schema.md` for the `fork_id` semantics that each `pick_approach()` call emits.

## Stage composition

```
Import → Sync → Index → Review → Validate → Post
```

First-pass coupling: when invoked via `adk pr-review <url>` or `adk pr-task review <url>` (without `-i`), Review + Validate + Post run as a single logical step — the user does not confirm between them. Subsequent re-runs may target a single stage. Common patterns:

- **PR pushed a new commit (code changed):** `adk pr-task sync <url>` then `adk pr-task index <url>` then `adk pr-task review <url>`
- **Only PR comments changed:** `adk pr-task sync <url>` then `adk pr-task post <url>`
- **Review is stale but the index is fine:** `adk pr-task review <url>` directly (skips Sync + Index)
- **Validate was wrong; repost from scratch:** `adk pr-task validate <url>` then `adk pr-task post <url>`

---

## Stage 1 — Import

### What it does
Fetches a minimal metadata payload for the PR (title, author, head_sha, target_branch, is_draft, mergeable, additions, deletions, changed_files) and writes it back to the queue row. This is the cheapest stage — one API call, no git, no diff. Its primary purpose is to populate `title` and `author` in the queue before any heavy work starts so the TUI can show them immediately.

### Inputs read
- PR URL (from the queue row or the command line)
- Existing queue row (merged — new fields are upserted, not replaced)

### Outputs written
Queue row fields: `title`, `author`, `head_sha`, `target_branch`, `is_draft`, `mergeable`, `additions`, `deletions`, `changed_files`, `last_imported_at` (UTC ISO).

### Idempotency
Always fast (< 2 s). Re-running overwrites all fields above unconditionally — Import is cheap enough that skipping is not worth the complexity. If the origin API is unreachable, falls back to `local-only` mode (leaves fields at their prior values, does not fail the stage).

### Approach fork — `import-source`

| Option | When selected |
|---|---|
| `origin-api` | Origin API reachable (default) |
| `local-only` | Origin API unreachable; queue row already has `head_sha` from a prior import |

Decision logged to `$ADK_MEMORY_HOME/learning/decisions.jsonl` with `fork_id: import-source`, `fork_type: auto-defaulted` (or `inferred` when falling back due to network failure). See `shared/decision-log-schema.md`.

### CLI entry point
```
adk pr-task import <pr-url>
```
No flags. Runs in < 2 s. Safe to call from a cron or a pre-flight hook.

### Failure modes
- **API rate limit:** retries with exponential back-off (3 attempts). On exhaustion, writes `stage_error` to the queue row and continues with `local-only` fallback.
- **Unknown URL format:** hard-fails with a clear error message; no queue row mutation.

---

## Stage 2 — Sync

### What it does
Fetches the full PR payload (body, comments, diff), runs `git fetch --all --prune` on the bare clone, materialises (or re-uses) a worktree at the PR head, mirrors linked supporting docs (Confluence / Jira / GDoc / markdown URLs from the PR body + comments), and builds `precis.md` (a short LLM-generated summary of the diff). This is the most I/O-intensive stage — expect 5–60 s depending on diff size and doc count.

### Inputs read
- Queue row (`pr_url`, `head_sha`, `last_synced_head_sha`, `slack.supporting_docs`)
- Origin API (PR body, comments, diff)
- Git remote (clone fetch)
- MCP tools for supporting docs (`adk-mcp-atlassian`, `adk-mcp-github`, etc.)

### Outputs written
| Artifact | Path |
|---|---|
| PR metadata | `<task_dir>/pr.json` |
| PR comments | `<task_dir>/pr-comments.json` |
| Unified diff | `<task_dir>/diff.patch` |
| Worktree at PR head | `<task_dir>/code/` |
| Supporting docs | `<task_dir>/docs/<adapter>/<id>.md` |
| Supporting doc index | `<task_dir>/docs/index.json` |
| Diff summary | `<task_dir>/precis.md` |
| Queue context | `<task_dir>/queue-context.json` |

Queue row fields updated: `last_synced_at`, `last_synced_head_sha`.

### Idempotency
When `head_sha == last_synced_head_sha`, Sync skips the diff + worktree steps and only refreshes `pr-comments.json` (comments can change without a new commit). The git fetch still runs (cheap). Supporting docs are re-fetched only if their source URL has changed since the last sync. Pass `--force` to bypass the sha check.

### Approach fork — `sync-scope`

| Option | When selected |
|---|---|
| `full` | First sync for a PR, or `head_sha` changed since last sync (default) |
| `metadata-only` | Queue refresh: only title/author/head_sha needed; no code changed |
| `docs-only` | Supporting docs changed (Jira updated) but no code change |
| `code-only` | PR body + diff + worktree only; skip doc fetch (e.g., no doc links in this PR) |

Decision logged with `fork_id: sync-scope`. Auto-mode picks based on what changed since the last sync. Interactive mode (`-i-sync`) shows the options as a `ConfirmScreen`.

### CLI entry point
```
adk pr-task sync <pr-url> [--force] [--scope full|metadata-only|docs-only|code-only]
```

### Failure modes
- **Clone missing:** Sync creates the bare clone on first run. If the remote is unreachable and no clone exists, Sync hard-fails — Index and Review cannot proceed without a worktree.
- **Worktree conflict:** If `code/` exists at a different commit, Sync re-checks it out. If the directory is dirty (unlikely — it's read-only), Sync removes and re-creates it.
- **Doc fetch partial failure:** Marks the failed doc as `status: "failed: <reason>"` in `docs/index.json` and continues. Review should surface `[<adapter>: skipped]` in the report.

---

## Stage 3 — Index

### What it does
Chunks the worktree with tree-sitter, embeds chunks with ollama, builds a LanceDB table with a BM25 FTS index alongside the vector index, and optionally runs SCIP (scip-typescript / scip-python / scip-go / scip-java) to produce a cross-file symbol graph. Uses a seed-and-overlay strategy: if a base-branch index already exists under `$ADK_DATA_HOME/repos/<repo>/branch-<base>/code-index/`, the stage copies it and re-indexes only the files changed in the PR diff — dramatically faster for large repos.

### Inputs read
- Worktree at `<task_dir>/code/`
- Diff at `<task_dir>/diff.patch` (determines which files are changed, for incremental mode)
- Base-branch index at `$ADK_DATA_HOME/repos/<repo>/branch-<base>/code-index/` (if present)
- Prior `<task_dir>/code-index/meta.json` (to check if the index is current and which model was used)

### Outputs written
| Artifact | Path |
|---|---|
| LanceDB table | `<task_dir>/code-index/chunks.lance/` |
| SCIP indices | `<task_dir>/code-index/scip/<lang>/index.scip` (per language, optional) |
| Index manifest | `<task_dir>/code-index/meta.json` |

Queue row fields updated: `last_indexed_at`, `last_indexed_head_sha`.

### Idempotency
When `head_sha == last_indexed_head_sha` and the embed model in `meta.json` matches the current config, Index is a no-op (returns `skipped`). When head moved but the file delta is small, only the changed files are re-chunked + re-embedded (incremental overlay). Pass `--rebuild` to drop `meta.json` and start fresh (use when switching embed models or after a suspected index corruption).

### Approach fork — `index-mode`

| Option | When selected |
|---|---|
| `seed-and-overlay` | Base-branch index exists; only PR-changed files differ (default for most PRs) |
| `incremental` | PR-local index exists and head moved; only re-index changed files |
| `rebuild` | `--rebuild` flag set, or embed-model mismatch, or index corruption detected |
| `skip` | `head_sha == last_indexed_head_sha` and model matches — nothing to do |

Decision logged with `fork_id: index-mode`.

### CLI entry point
```
adk pr-task index <pr-url> [--rebuild] [--embed-model <name>]
```

`--rebuild` drops `meta.json` and re-indexes from scratch. `--embed-model` overrides the model (requires `--rebuild` if switching from a prior run).

### Failure modes
- **ollama unreachable:** hard-fail. Review cannot run without embeddings.
- **SCIP binary missing:** logged as `[scip-<lang>: skipped]`; Review falls back to the chunk view's `parent_symbol` field. Not a hard failure.
- **Base-branch index stale:** Index falls back to full rebuild when seed-and-overlay produces a mismatch (detected by checking file mtimes against the seed manifest).

---

## Stage 4 — Review

### What it does
You (the reviewing agent) read `precis.md`, `diff.patch`, `pr.json`, `pr-comments.json`, supporting docs in `docs/`, and the pre-loaded index context, then produce `findings.json`. This is the only stage that requires an LLM invocation with a full system prompt. You may spawn child agents (security pass, tests pass, feature-flow pass) via the `Agent` tool for independent dimension passes.

This stage is described in full in the main `SKILL.md`. The notes here cover only the stage-level mechanics (fork selection, state writes, re-run behaviour).

### Inputs read
- `<task_dir>/precis.md`
- `<task_dir>/diff.patch`
- `<task_dir>/pr.json`
- `<task_dir>/pr-comments.json`
- `<task_dir>/docs/` (all fetched docs)
- `<task_dir>/code-index/` (queried via `scripts/query_index.py`)
- `<task_dir>/queue-context.json`

### Outputs written
- `<task_dir>/findings.json` — raw findings array + `existing_comment_actions` + `recommendation`

Queue row fields updated: `last_reviewed_at`, `last_reviewed_head_sha`.

### Idempotency
Review does not short-circuit on a sha match — an already-posted review implies the stage ran, but re-running it is deliberate (e.g., after the diff changed). The only skip case: if `findings.json` exists AND `last_reviewed_head_sha == head_sha` AND the `--force` flag is not set, Review returns `skipped` and proceeds to Validate.

### Approach fork — `review-depth`

| Option | When selected |
|---|---|
| `default` | Standard sonnet-class model, hybrid retrieval, single-pass dimensions (default) |
| `detailed` | `bge-m3` embed model, wider retrieval top-k, better for large diffs with many cross-file dependencies |
| `deep` | Stronger reasoning model profile; auto-triggered when `_complexity_reason` matches (≥ 500 LOC changed, or ≥ 3 services affected, or `--deep` flag) |
| `no-rerank` | Skip the harness reranker step; useful when Haiku is unavailable or for very small PRs |

Decision logged with `fork_id: review-depth`. `--detailed` and `--deep` map to `detailed` and `deep` respectively. They are independent: `--deep` without `--detailed` uses the stronger model with the default retrieval path.

### CLI entry point
```
adk pr-task review <pr-url> [--detailed] [--deep] [--no-rerank] [--no-post] [-i]
```

When `-i` is not set, Validate + Post chain automatically after Review completes. Pass `-i` to stop at `findings.json` and walk findings manually before Validate runs.

### Failure modes
- **Index missing:** hard-fail. Run `adk pr-task index <url>` first.
- **precis.md missing:** hard-fail. Run `adk pr-task sync <url>` first.
- **Child agent timeout:** the spawning agent logs `[narrate] spawn: <name> timed out` and continues without that pass's findings; the dimension is noted as `skipped: child-agent-timeout` in the summary.

---

## Stage 5 — Validate

### What it does
Gates each finding in `findings.json` on two cheap deterministic checks:

1. **Anchor check** — the `file:line_start..line_end` range still resolves in the worktree at `code/`. Findings whose file was deleted or whose line range is out of bounds fail this check.
2. **Suggestion check** — a non-trivial `suggestion` is present, except for `question` and `appreciation` severities. The user's rule: "If the fix cannot be identified, we will not have it in the finding comments."

Findings that fail either check are moved to `initial-findings.json` as `status: rejected-by-validate` — they are kept in the audit trail but never posted.

### Inputs read
- `<task_dir>/findings.json`
- `<task_dir>/code/` (worktree, for anchor resolution)

### Outputs written
- `<task_dir>/validated-findings.json` — full audit (all findings, with `validate_status` per finding)
- `<task_dir>/initial-findings.json` — subset of findings that passed both checks
- `<task_dir>/validation-report.json` — summary: counts of passed / anchor-failed / suggestion-failed

Queue row fields updated: `last_validated_at`, `last_validated_head_sha`.

### Idempotency
Validate is pure and deterministic. Re-running on the same `findings.json` produces the same outputs. It does not short-circuit on a sha match — callers decide when to re-run.

### Approach fork — `validate-strict`

| Option | When selected |
|---|---|
| `anchor+fix` | Both anchor check and suggestion check apply (default for all code-touching PRs) |
| `anchor-only` | Suggestion check is waived; used for config-only or doc-only PRs where a code suggestion is not meaningful |

Decision logged with `fork_id: validate-strict`. Auto-mode picks `anchor+fix` for code PRs (detected by presence of `.ts`/`.py`/`.go`/etc. in the diff) and `anchor-only` for config/doc-only PRs.

### CLI entry point
```
adk pr-task validate <pr-url> [--strict anchor+fix|anchor-only]
```

### Failure modes
- **findings.json missing:** hard-fail. Run Review first.
- **Worktree missing:** hard-fail. The anchor check requires the worktree. Run Sync first.
- **All findings rejected:** Validate succeeds (exit 0) but logs a warning. Post will still run and produce an empty comment set; the Slack summary will reflect zero findings.

---

## Stage 6 — Post

### What it does
Renders each finding from `initial-findings.json` as an inline review comment (or a PR-level general comment for `appreciation` severity), resolves or reopens existing PR comment threads per `existing_comment_actions[]`, posts a Slack summary reply in the queue row's thread, and updates the queue row to reflect the review outcome.

In interactive mode (`-i`), Post is preceded by a triage walk (`triage.py --init --default-state pending`) where the user accepts, rejects, or edits each finding. Appreciations bypass the walk and are always posted. After the walk, `triage.py --finalize` produces `posted-comments.json` and Post proceeds.

Posting is MCP-first: `post_comments.py` writes `posting-plan.json` and exits; the Review agent dispatches each step via the named `mcp__adk-mcp-{github,bitbucket}__*` tool. Direct-API mode exists for headless CI runs.

### Inputs read
- `<task_dir>/initial-findings.json`
- `<task_dir>/findings.json` (for `existing_comment_actions[]`)
- `<task_dir>/pr.json` (PR host, owner, repo, number)
- `<task_dir>/queue-context.json` (Slack channel + thread_ts for the Slack summary)

### Outputs written
- `<task_dir>/posting-plan.json` — the full plan (MCP tool + args per step)
- `<task_dir>/posting-plan-final.json` — after interactive walk (identical to `posting-plan.json` in auto mode)
- `<task_dir>/report.md` — one-page summary with PR link and findings overview
- `<task_dir>/state.json` — final state: `{ recommendation, approve_ready, total_posted, total_resolved, total_reopened, last_posted_at }`
- Inline comments on the PR (via MCP)
- Slack reply in the queue thread (when `slack.channel_id` is present)
- Queue row fields: `status`, `last_posted_at`, `last_posted_head_sha`, `taken_at` cleared

### Idempotency
Post maintains `posting-plan.json` state. If a comment was already posted (detected by checking the PR's existing comment list against the plan's `finding_id` fields), the step is skipped with `status: already-posted`. Re-running after a crash is safe. Re-running after a code change is NOT idempotent — run Validate first to refresh `initial-findings.json`.

### Approach fork — `post-policy`

| Option | When selected |
|---|---|
| `auto` | Default: all findings in `initial-findings.json` are posted without an interactive walk |
| `interactive` | `-i` flag: triage walk runs before posting; user accepts/rejects/edits each finding |
| `rehearsal` | `--no-post` flag: plan is written to `posting-plan.json` but no HTTP transmission occurs |

Decision logged with `fork_id: post-policy`.

### CLI entry point
```
adk pr-task post <pr-url> [--no-post] [--no-slack-summary] [--no-resolve-existing] [-i]
```

### Failure modes
- **MCP unreachable:** falls back to the `rest` transport block in `posting-plan.json` when present (per `references/platform-mcp.md`). The Bitbucket `resolveComment` / `reopenComment` / `approvePullRequest` tools are known to have MCP bugs — use the REST escape hatch (`transport: "rest"` in the plan step). See memory `feedback_bitbucket_mcp_write_bugs.md`.
- **Slack MCP unreachable:** logs `[slack: skipped]` in the report; posting to the PR proceeds normally.
- **All findings were rejected at Validate:** Post runs successfully with an empty comment set; `report.md` notes zero findings posted.
- **Constitution §I.3:** Post never adds a merge step. `posting-plan.json.never_merge` is always `true`.

---

## Queue row `stage_status` enum

```
import → synced → indexed → reviewed → validated → posted → failed
```

Each stage writes its terminal `stage_status` on success. The scheduler uses this to decide which stage to run next. A row in `failed` state surfaces `stage_error` for diagnosis; the user can re-trigger from any stage via the CLI entry points above.

---

## Re-run cheat sheet

| Situation | Command |
|---|---|
| New commit pushed | `adk pr-task sync <url>` → `adk pr-task index <url>` → `adk pr-task review <url>` |
| Only comments changed | `adk pr-task sync <url> --scope docs-only` → `adk pr-task post <url>` |
| Re-review without re-indexing | `adk pr-task review <url>` |
| Re-validate + repost | `adk pr-task validate <url>` → `adk pr-task post <url>` |
| Switch embed model | `adk pr-task index <url> --rebuild --embed-model bge-m3` → `adk pr-task review <url>` |
| Recover from crashed post | `adk pr-task post <url>` (idempotent — skips already-posted steps) |
