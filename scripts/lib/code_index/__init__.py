"""scripts.lib.code_index — shared code-index library for adk skills.

Phase 2 (refactor-a) extracted the indexer (chunker + embedder + scip_runner)
out of skills/adk-pr-review/scripts/ so multiple skills can build / query the
repo-level base index without each owning a private copy.

Public surface (stable for skill consumers):

    from scripts.lib.code_index.query import (
        open_index, similar, callers, defs, by_symbol, feature_flag,
        Hit, Index,
        IndexNotBuilt, IndexStale, ModelMismatch,
    )

Storage layout (see also shared/paths.md):

    ~/.agents-devkit/repos/<name>/                clone (default branch)
    ~/.agents-devkit/repos/.indices/<name>/       adk-owned base index task dir
      code-index/
        chunks.jsonl                              chunker output
        chunks.lance/                             LanceDB table
        scip/<lang>/index.scip                    SCIP cross-refs (optional)
        meta.json                                 rows + model + dim
      repo-meta.json                              last_indexed_oid + last_indexed_at +
                                                  default_branch

Indexing entrypoints (CLI):
    python3 scripts/lib/code_index/chunker.py    --worktree <path> --out <chunks.jsonl>
    python3 scripts/lib/code_index/embedder.py   --task-dir <path> --chunks <chunks.jsonl> --mode replace|incremental
    python3 scripts/lib/code_index/scip_runner.py --task-dir <path> --worktree <path>
    python3 scripts/lib/code_index/query_index.py --task-dir <path> --query "<text>" --json
"""
