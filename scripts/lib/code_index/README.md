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

**Repo-level base** (long-lived; default branch):
```
~/.agents-devkit/repos/.indices/<repo>/
  repo-meta.json
  code-index/
    chunks.jsonl  chunks.lance/  scip/  meta.json
```
Built by `adk repo add <git-url>`; refreshed by `adk repo update <name>`.

**Task-level** (per-PR or per-investigation; short-lived):
```
~/.agents-devkit/pr-reviews/<repo>_pr-<n>/code-index/
  chunks.jsonl  chunks.lance/  scip/  meta.json
```
Owned by the consuming skill's task dir.

## PR-review seeding flow

1. PR-review checks `~/.agents-devkit/repos/.indices/<repo>/`.
2. If present, fresh enough, and the embed-model matches → `seed_copy()`
   into the task dir (`chunks.lance/` dir + `chunks.jsonl` + `scip/` + meta).
3. `meta.json.table_path` is rewritten to point at the COPIED location
   (critical — otherwise the embedder mutates the shared base).
4. `embedder.py --mode incremental --replaced-files <diff>` overlays only
   files that changed between the base's `indexed_sha` and the PR's head.

Cold path on 20k chunks: ~9 min. Warm seeded path on a 12-file PR: ~30 s.

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

```sh
# Build a base index from scratch:
python3 scripts/lib/code_index/chunker.py \
        --worktree ~/.agents-devkit/repos/myrepo \
        --out ~/.agents-devkit/repos/.indices/myrepo/code-index/chunks.jsonl

python3 scripts/lib/code_index/embedder.py \
        --task-dir ~/.agents-devkit/repos/.indices/myrepo \
        --chunks   ~/.agents-devkit/repos/.indices/myrepo/code-index/chunks.jsonl \
        --model    nomic-embed-text \
        --mode     replace --json

python3 scripts/lib/code_index/scip_runner.py \
        --task-dir ~/.agents-devkit/repos/.indices/myrepo \
        --worktree ~/.agents-devkit/repos/myrepo --json

# Query it:
python3 scripts/lib/code_index/query_index.py \
        --task-dir ~/.agents-devkit/repos/.indices/myrepo \
        --query "auth login flow" --top-k 8 --json

# Health check:
python3 scripts/lib/code_index/query_index.py \
        --task-dir ~/.agents-devkit/repos/.indices/myrepo \
        --health --json
```

The friendlier path is `adk repo add <git-url>` + `adk repo update <name>`.

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
