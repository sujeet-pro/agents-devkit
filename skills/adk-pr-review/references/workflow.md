# workflow — adk-pr-review

Six phases. Phase 1 (worktree creation) is **serialized**; every other phase can fan out. The orchestrator is `scripts/prepare_task.py`.

## Always-resync semantics (every invocation)

Every time `/adk-pr-review <url>` runs, the orchestrator:

1. Re-fetches the PR (`fetch_pr.py`) to get the latest `head_sha`.
2. Re-runs `ensure_repo_clone.py` → `git fetch --all --prune` against the adk-owned clone, hard-resets to `origin/<default>`.
3. Re-runs `create_worktree.py` against the new `head_sha` (no-op if the worktree is already at that OID, `git checkout --detach` if it isn't).
4. Re-runs `fetch_supporting_docs.py` to refresh `docs/index.json` from the (possibly updated) PR body + comments.
5. Decides what to do with the embeddings + SCIP index based on whether `head_sha` changed since the prior index pass — see *Incremental re-index* below.

There is no "skip phase X because it ran last time" path for phases 1 (worktree) or 2 (fetch). They run on every invocation.

## Incremental re-index

`state.phases.3_index.head_sha_at_index` records the OID the index was built against. On a fresh invocation:

| Condition | Action |
|---|---|
| No prior index | Full chunk + embed + SCIP. |
| `head_sha_at_index == current head_sha` | Skip Phase 3 entirely — index is up to date. |
| `head_sha_at_index != current head_sha` AND `git diff --name-only <old>..<new>` succeeds | **Incremental**: chunk only the changed files, delete those files' rows from the LanceDB table, embed + insert. Re-run SCIP only for languages whose files changed. |
| `head_sha_at_index != current head_sha` AND the old OID is unreachable (e.g. PR was force-pushed with a rebase) | Full re-index. |
| `--rebuild` | Full re-index regardless. |

The AI review pass never starts before Phase 3 settles — the precis the model reads always reflects the current `head_sha`.

## Phase 0 — prerequisites + URL dispatch

1. Parse the PR URL → `(host, owner, repo, pr_number)` via `scripts/parse_pr_url.py`.
2. Probe ollama: `scripts/ensure_ollama.py` checks (a) `ollama` binary on PATH, (b) the daemon responds at `http://localhost:11434`, (c) the embedding model is pulled. Default model: `nomic-embed-text`; `--detailed` selects the detailed embedding model (`bge-m3` by default). Override via `--embed-model` or `core.yaml.defaults.adk-pr-review.embed_model`. If ollama is missing, refuse and print the install command (do not try to install for the user).
3. Probe MCP availability: `gh` CLI for GitHub PRs; `adk-mcp-bitbucket` for Bitbucket PRs. If neither is reachable for the host, refuse and surface the gap.
4. Resolve the task folder: `python3 scripts/adk_task_slug.py --skill pr-review --input <url> --create --json` → `~/.agents-devkit/skill-pr-review/<repo>_pr-<n>/`.

## Phase 1 — repo + worktree (serialized)

A **process-level file lock** at `~/.agents-devkit/repos/.worktree-lock` serializes worktree creation across concurrent invocations. Without this, two simultaneous `/adk-pr-review` runs on the same repo would race on `git worktree add`.

1. `scripts/ensure_repo_clone.py` — if `~/.agents-devkit/repos/<repo-name>/` doesn't exist, clone via `gh repo clone` (GitHub) or `git clone` from the BB SSH URL. If it exists, `git fetch --all --prune`.
2. **Reset to current implementation** — the user's note: "Before creating working tree, it must be set back to its current implementation." The clone's default branch is checked out and reset to the remote head. Any local commits in the clone are unexpected (it's an adk-owned clone) and surfaced as a refusal.
3. `scripts/create_worktree.py` — acquires the lock, then `git worktree add <task>/code <head-sha>`. Sets the worktree to detached HEAD so no branch shenanigans.
4. Release the lock. The orchestrator records `worktree_path` in `<task>/state.json`.

## Phase 2 — fetch PR + supporting docs (parallel)

Fanned out concurrently:

1. `scripts/fetch_pr.py` — fetches metadata + review-comments via `gh pr view --json` (GitHub) or `adk-mcp-bitbucket.getPullRequest` + `getPullRequestComments` (Bitbucket). Writes `pr.json` + `pr-comments.json`. Diff via `git diff --binary -M30% -B <base>...<head>` against the worktree (no remote call needed once the head is fetched).
2. `scripts/fetch_supporting_docs.py` — scans `pr.json.body` + each comment body for URLs (Confluence, Jira, GDoc, raw markdown). One hop only (constitution §IV.1). Writes `docs/<adapter>/<id>.md` per fetched doc.

## Phase 3 — index (parallel)

> **Indexer paths.** The chunker / embedder / scip_runner / query_index live in `scripts/lib/code_index/` (Phase 2 of refactor-a). Run paths in this doc that say `scripts/chunker.py` (etc.) resolve via the runpy shim in `skills/adk-pr-review/scripts/`; new callers should point at `scripts/lib/code_index/<file>.py` directly.

1. `scripts/lib/code_index/chunker.py` — tree-sitter AST chunker (function / class / method / top-level / const / doc) for `ts / tsx / js / jsx / py / go / java / rs / rb / md`. Caps: 1500-token chunks, 50-token minimum, oversized-split. Heuristic fallback for any language without a grammar.
2. `scripts/lib/code_index/embedder.py` — POST batches of 24 chunks to ollama (`/api/embed`), idle-eviction via `keep_alive: 0`. Writes to LanceDB table `code-index/chunks.lance/` with schema `(id, file, line_start, line_end, parent_symbol, language, content, vector)`. Modes: `replace`, `incremental`. Oversized-input errors short-circuit retries (improvement #8).
3. `scripts/lib/code_index/scip_runner.py` — detect `scip-typescript` / `scip-python` / `scip-go` / `scip-java` on PATH. For each language present in the worktree, run the corresponding scip indexer at `code/`, output to `code-index/scip/<lang>/index.scip`. Missing binaries are marked `not_installed` in `code-index/meta.json` — the review falls back to chunker `parent_symbol` matching.
4. **Seed-from-base** (Phase 3 of refactor-a): before chunking, check `~/.agents-devkit/repos/.indices/<repo>/code-index/`. If present, fresh enough, and the embed model matches → `seed_copy()` into the task dir, then run the embedder in `--mode incremental` for just the files that changed between `base.indexed_sha` and the PR's `head_sha`. Cold path: ~9 min. Warm seeded path on a 12-file PR: ~30 s. Disable with `--no-base-seed` for a clean reindex.
5. Write `code-index/meta.json` — provider, dim, chunk count, SCIP languages indexed, ts, `seeded_from_base` + `seeded_from_sha` when seeding. The Phase-3 `state.json` entry is written BEFORE the post-Phase-3 health check (improvements #9 + #11) — a transient health failure no longer orphans the index.

## Phase 4 — review

> **Orchestrator hand-off (current behavior).** The orchestrator does NOT spawn `claude -p`. It exits cleanly after Phase 3 / precis with `state.next-step = phase-4`; the parent agent (already loaded with `SKILL.md` as system prompt) reads `precis.md` and writes `findings.json`. The old `claude -p`-subprocess design described below is preserved as a historical reference for a possible future revival.

1. The orchestrator prepares the user-prompt with a pre-loaded `# Index context` section: changed-files, top-k chunks per changed file, symbol matches, feature-flag references found in the diff (via `scripts/lib/code_index/query_index.py --feature-flags-in-diff`).
2. (Hypothetical `claude -p` revival, not the current path.) Invoke `claude -p` with:
   - `--system-prompt skills/adk-pr-review/SKILL.md`
   - `--add-dir ~/.agents-devkit/skill-pr-review/<task>/code`
   - `--allowedTools Read,Glob,Grep,Bash` (Bash limited to `python3 scripts/lib/code_index/query_index.py …` via permissions)
   - `--permission-mode auto`
   - `--output-format stream-json`
   - `--json-schema skills/adk-pr-review/finding.template.json`
3. The model issues retrieval queries via `query_index.py`. **Hybrid (vector + BM25) is on by default** — both signals contribute to candidate selection. The `score_breakdown` in each result shows which signal pulled it. Disable with `--no-hybrid` (CLI) or `retrieval.hybrid: false` (config).
4. **Optional rerank stage.** When the candidate pool is wide (≥ 50 chunks per query × multiple queries), the model emits a `queries.json5` and the orchestrator runs `rerank.py --build-queue` → harness-LLM scoring → `rerank.py --apply-scores`. The harness picks the model per `references/rerank-harness.md` and `shared/model-depth.md`. Skipped when retrieval already converges on a small candidate set.
5. Parse `structured_output` from the result. Validate every finding: `file` in worktree, `line_start ≤ line_end`, `line_end ≤ file LOC`, `evidence` non-empty. Invalid findings drop to `status=rejected` in the local store and are not posted.
6. Cross-check existing comments: `scripts/comment_resolver.py` consumes `existing_comment_actions` from the model + `pr-comments.json` + the worktree diff to verify each decision (see `references/comment-resolution.md`).

## Phase 5 — triage (auto / interactive)

Every finding posted to the PR is a public mutation (constitution §I.4). The triage step ensures only findings the user has approved go out.

1. `scripts/triage.py --init --default-state {accept|pending}` — `accept` for auto mode (every finding pre-marked, no user prompts), `pending` for interactive (`-i` flag on `/adk-pr-review`).
2. **Interactive only.** Parent agent walks pending findings one at a time via `AskUserQuestion`:
   - **Accept** → `triage.py --mark <id> --state accept`. Will post as-is.
   - **Reject** → `triage.py --mark <id> --state reject`. Dropped before post.
   - **Edit** → iterative loop. Parent agent shows the current finding, asks for an edit prompt, rewrites `title` / `body` / `suggestion` / `impact_if_unfixed` via the harness LLM, pushes back with `triage.py --rewrite <id> --fields-json '{...}'`, shows the new version. The finding stays in `edit` state until the user gives `accept` or `reject`.
3. `triage.py --finalize` — refuses to finalize while any finding is `pending` or `edit`. Writes `findings-final.json` (only `accept`-state findings, edits applied; originals in `findings.json` are never mutated, for audit). Triage stats land in a `triage` block: `{mode, accepted, rejected, edited}`.

## Phase 6 — post + report (user-gated)

`scripts/post_comments.py` reads `findings-final.json` if present (preferred — produced by triage), else falls back to `findings.json` (back-compat for runs that skipped triage). Per constitution §I.4 posting requires per-invocation user confirmation — passing `--confirmed yes` IS the confirmation.

1. Show the user a 1-page summary: PR link, accepted/rejected/edited counts, comment-resolution actions, posting plan.
2. On confirm:
   - `scripts/post_comments.py` posts each accepted finding as an inline review comment via `adk-mcp-github.add_comment_to_pending_review` + `submit_pending_pull_request_review` (GH) or `adk-mcp-bitbucket.addPullRequestComment` (BB).
   - For each `existing_comment_actions` entry: `resolveComment` / `reopenComment` (BB) or the GH equivalent (`resolveReviewThread` via GraphQL — falls back to a status comment when the API endpoint is unavailable for the user's token).
3. Write `findings.md` (human-readable) + `report.md` (1-page).
4. Final CLI output: PR link + one-line summary per accepted finding (≤ 80 chars each).

## State file

`<task>/state.json` is the orchestrator's checkpoint — survives across re-runs:

```json
{
  "task_dir": "/Users/sujeet/.agents-devkit/pr-reviews/foo_pr-42",
  "host": "github",
  "owner": "acme",
  "repo": "foo",
  "pr_number": 42,
  "head_sha": "abc123…",
  "worktree_path": "/Users/sujeet/.agents-devkit/pr-reviews/foo_pr-42/code",
  "phases": {
    "0_prereq": {"status": "done", "ts": "2026-05-19T20:00:00Z"},
    "1_worktree": {"status": "done", "ts": "2026-05-19T20:00:15Z"},
    "2_fetch": {"status": "done", "ts": "2026-05-19T20:00:25Z"},
    "3_index": {"status": "done", "ts": "2026-05-19T20:01:10Z", "scip_langs": ["typescript"], "chunks": 384, "embed_model": "nomic-embed-text"},
    "4_review": {"status": "done", "ts": "2026-05-19T20:02:30Z", "findings": 3, "finding_set_hash": "…"},
    "5_post": {"status": "pending"}
  }
}
```

A re-run of `/adk-pr-review <same-url>` resumes from the last incomplete phase. To force a re-do from scratch: `--rebuild`.

## Validators

- Phase 1: `git worktree list` shows the new worktree; `git -C <worktree> rev-parse HEAD` matches `pr.json.head_sha`.
- Phase 3: `code-index/chunks.lance/` exists and `query_index.py --health` returns `ok`. SCIP indices' size > 0 if produced.
- Phase 4: `findings.json` parses against `finding.template.json`; every `file` exists in the worktree; every `line_end <= LOC(file)`.
- Phase 5: post is no-op when `--no-post`; under `--no-resolve-existing`, the comment-resolver phase is skipped.

## Failure modes

- ollama unreachable mid-embedding → orchestrator retries with backoff (3 tries, 2 s / 8 s / 30 s); fails the phase if all retry.
- scip-typescript crashed → log to `code-index/scip/<lang>/error.log`, mark `not_installed`-equivalent (`failed`), continue.
- MCP intermittently 5xx → retry 3×; on persistent failure, refuse post (don't half-post).
- Comment-resolver classification ambiguous → leaves the comment as-is, surfaces the ambiguity in the report.
