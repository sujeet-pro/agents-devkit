# scripts/lib/code_index/ — shared code-index library

Built by `/adk-pr-review` originally; extracted in refactor-a so other
adk skills can consume it.

## Files

| File | Role |
|---|---|
| `chunker.py` | tree-sitter AST chunker → `chunks.jsonl`. Heuristic fallback for unsupported languages. |
| `embedder.py` | ollama → LanceDB embedder. Modes: `replace`, `incremental`. Pre-flight skip for oversized chunks. |
| `scip_runner.py` | runs `scip-{typescript,python,go,java}` against a worktree when on PATH. |
| `query_index.py` | CLI surface (`--query`, `--symbol`, `--callers`, `--defs`, `--feature-flag`, `--feature-flags-in-diff`, `--changed-file`, `--health`). |
| `query.py` | Python API for skills (`open_index`, `similar`, `by_symbol`, `defs`, `callers`, `feature_flag`). |
| `base_index.py` | Locate / freshness-check / seed-copy the repo-level base index. |
| `ensure_ollama.py` | Verify ollama is running + the named model is pulled. |
| `_common.py` | Focused subset of helpers (logging, IO, hashing, `which`, config). |
| `defaults.yaml` | Shipped defaults; user override at `~/.agents-devkit/config/code-index.yaml`. |
| `requirements.txt` | Single source of truth for `lancedb`, `tree_sitter_language_pack`, etc. |

## Two index roots

**Repo-level base** (long-lived; per branch):
```
~/.agents-devkit/repos/.indices/<repo>/
  repo-meta.json                                catalog: name, url, default_branch,
                                                tracked_branches[]
  branches/<slug>/
    branch-meta.json                            { branch, slug, last_indexed_oid,
                                                  last_indexed_at, embed_model }
    code-index/
      chunks.jsonl  chunks.lance/  scip/  meta.json
```
Built by `adk repo add <git-url>` (default branch by default; `--branch X`
adds more); refreshed by `adk repo update <name>` (default branch),
`adk repo update <name> --branch develop`, or `... --all-branches`. The
slug is `slugify_branch(name)`: lowercased, `/` → `__`, FS-unsafe chars
stripped.

> **Legacy layout** (`<repo>/code-index/` directly under the repo dir, no
> `branches/`) is still read by `base_index.py` and treated as the
> default-branch index. `adk repo migrate` moves it into the new layout;
> any `repo add/update/branch` call also triggers migration implicitly.

**Task-level** (per-PR or per-investigation; short-lived):
```
~/.agents-devkit/pr-reviews/<repo>_pr-<n>/code-index/
  chunks.jsonl  chunks.lance/  scip/  meta.json
```
Owned by the consuming skill's task dir.

## PR-review seeding flow

1. `/adk-pr-review` reads the PR's target branch from `pr.json.baseRefName`
   (populated by `fetch_pr.py`).
2. `pick_base_index(repo, target_branch=<baseRefName>, require_model=…)`
   walks: exact target-branch index → default-branch index → None. Skips
   model-mismatched indexes; staleness is a warning, not a rejection.
3. If a base is chosen, `seed_copy(base, task_dir)` copies the LanceDB
   table + chunks + SCIP into the PR's task dir and rewrites
   `meta.json.table_path` to point at the COPIED location (critical —
   otherwise the embedder mutates the shared base).
4. `embedder.py --mode incremental --replaced-files <diff>` overlays only
   the files that changed between the base's `indexed_sha` and the PR's
   `head_sha`. That diff naturally includes commits on the target branch
   since the base was built PLUS the PR's own commits — `git diff
   base_sha..pr_head_sha` returns the union in one call.

Cold path on 20k chunks: ~9 min. Warm seeded path on a 12-file PR: ~30 s.
Picking the *closest* base (target-branch instead of default) keeps the
overlay small when default and target have diverged significantly.

## Adding a new consumer (any non-pr-review skill)

```python
from scripts.lib.code_index.query import open_index, similar, IndexNotBuilt

try:
    idx = open_index("ecomm-ssr")
except IndexNotBuilt:
    log.info("base index not built; skipping related-code section")
else:
    hits = similar(idx, "checkout payment retry path", top_k=6)
    for h in hits:
        print(f"{h.path}:{h.line_start}-{h.line_end}  score={h.score:.2f}")
```

Full contract: `shared/guidelines/code-index.md`.

## CLI invocations (manual / debug)

For most users the friendlier path is `adk repo add <git-url>` +
`adk repo update <name>` (optionally `--branch develop`). The lib-level
commands below show what those `adk repo` subcommands run under the hood
and are useful for debugging a half-built index.

```sh
# Build a branch index from scratch — replace BRANCH_DIR with the per-branch
# location, e.g. ~/.agents-devkit/repos/.indices/myrepo/branches/develop/

BRANCH_DIR=~/.agents-devkit/repos/.indices/myrepo/branches/master

python3 scripts/lib/code_index/chunker.py \
        --worktree ~/.agents-devkit/repos/myrepo \
        --out      "$BRANCH_DIR/code-index/chunks.jsonl"

python3 scripts/lib/code_index/embedder.py \
        --task-dir "$BRANCH_DIR" \
        --chunks   "$BRANCH_DIR/code-index/chunks.jsonl" \
        --model    nomic-embed-text \
        --mode     replace --json

python3 scripts/lib/code_index/scip_runner.py \
        --task-dir "$BRANCH_DIR" \
        --worktree ~/.agents-devkit/repos/myrepo --json

# Query it:
python3 scripts/lib/code_index/query_index.py \
        --task-dir "$BRANCH_DIR" \
        --query "auth login flow" --top-k 8 --json

# Health check:
python3 scripts/lib/code_index/query_index.py \
        --task-dir "$BRANCH_DIR" \
        --health --json
```

## Versioning

`lancedb` is upper-bounded (`>=0.30,<0.40`) because 0.30 introduced a
breaking change to `list_tables()`. Floating past the cap will silently
break the table-existence check; bump deliberately and re-test.

`Hit` and `Index` are stable. Adding fields is non-breaking; renaming or
removing is. Internal helpers (`_open_table`, `_minmax`, `_to_hit`) are
not stable.

## Decision logging

`open_index` writes one JSONL line per call to
`~/.agents-devkit/improve/learning/decisions.jsonl`. Skip via `_log=False`
in hot paths. Fork id: `open_index`. Hot tight loops calling `similar()`
should pass `_log=False` to keep the log file tractable.
