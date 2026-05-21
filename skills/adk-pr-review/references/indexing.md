# indexing — chunker + embedder + SCIP

How the per-PR code index is built. Ported from the proven design in `~/nogit/pr-review/src/main/services/IndexService.ts`, with two changes: Python instead of TypeScript, and LanceDB instead of better-sqlite3 + FTS5.

## Chunker

`scripts/chunker.py` — heuristic AST chunker. Reads every file under `code/`, emits one row per chunk.

| Language | Detection | Strategy |
|---|---|---|
| `ts` / `tsx` / `js` / `jsx` | extension | regex on `function\s+`, `class\s+`, `=>`, `const \w+ =`, `export ` |
| `py` | extension | regex on `^def\s+`, `^async def`, `^class\s+`, top-level constants |
| `go` | extension | regex on `^func\s+`, `^type\s+`, `^var\s+`, `^const\s+` |
| `java` | extension | regex on `(public|private|protected)?\s+(static\s+)?(class|interface|enum)\s+`, methods |
| `rs` | extension | regex on `pub fn\|fn `, `struct\|enum\|trait\|impl` |
| `rb` | extension | regex on `^def\s+`, `^class\s+`, `^module\s+` |
| `md` | extension | split on `^# ` and `^## ` headings |
| anything else | fallback | fixed-size sliding window |

Per-chunk fields:

```python
{
  "id": "<sha1 of file + line_start + content>",
  "file": "src/auth/login.ts",
  "line_start": 42,
  "line_end": 88,
  "parent_symbol": "loginUser",
  "language": "ts",
  "kind": "function",     # function | class | method | const | top-level | doc | chunk
  "content": "<= 1500 tokens worth>",
  "snippet_hash": "<sha1 of content>",
}
```

Caps:
- 1500 tokens per chunk (approximated as `len(content) / 4`).
- 50 token minimum (chunks shorter than this fold into the parent symbol).
- Oversized symbols (a 4000-line function) split into multiple chunks; each retains the same `parent_symbol`.

The chunker is deterministic given the same input — the same chunk produces the same `id`, so re-indexing is idempotent (no duplicates).

## Embedder

`scripts/embedder.py` — `requests`-based ollama HTTP client.

```
POST http://localhost:11434/api/embed
{ "model": "<name>", "input": ["chunk1", "chunk2", …], "keep_alive": "5m" }
→ { "embeddings": [[…], […], …] }
```

Defaults:
- Model: `nomic-embed-text` (768-dim). Configurable via `--embed-model` or `overrides.yaml.defaults.adk-pr-review.embed_model`.
- Batch: 24. Empirically the sweet spot on a stock ollama install — larger batches OOM the model server on small machines.
- Idle eviction: set `"keep_alive": 0` on the final batch to let ollama unload the model. The Electron app uses an idle timer; the CLI just does it on the last call.

After all chunks are embedded, write to LanceDB:

```python
import lancedb
db = lancedb.connect(task_dir / "code-index")
table = db.create_table("chunks", schema={
    "id": "string",
    "file": "string",
    "line_start": "int32",
    "line_end": "int32",
    "parent_symbol": "string",
    "language": "string",
    "kind": "string",
    "content": "string",
    "snippet_hash": "string",
    "vector": ("float32", 768),  # dim = model.dim
}, mode="overwrite")
table.add(rows)
table.create_index("vector", index_type="IVF_PQ", num_partitions=64, num_sub_vectors=16)  # or BRUTE_FORCE if rows < 10000
table.create_fts_index("content", replace=True)  # for keyword fallback
```

The Lance table lives at `code-index/chunks.lance/` — a directory of parquet + manifest files. **Don't** treat it as a single sqlite file; use the `lancedb` Python API to open it.

## SCIP

`scripts/scip_runner.py` — language-by-language indexer. Skipped if the binary isn't on PATH.

```
scip-typescript index --output code-index/scip/ts/index.scip code/
scip-python    index --output code-index/scip/py/index.scip code/
scip-go        index --output code-index/scip/go/index.scip code/
scip-java      index --output code-index/scip/java/index.scip code/
```

Each command runs in a subprocess with cwd = the worktree. Stdout/stderr → `code-index/scip/<lang>/build.log`. A non-zero exit marks `failed` in `code-index/meta.json`.

**The SCIP file is protobuf** — reading it from Python needs the `scip-python` library's protobuf bindings, or use `scip-cli` (if installed) to dump JSON for spot queries:

```
scip-cli convert --format json code-index/scip/ts/index.scip > /tmp/scip.json
```

`scripts/query_index.py` shells out to `scip-cli` when SCIP queries are needed (`--callers`, `--defs`, `--moniker`). If `scip-cli` isn't installed, the script falls back to chunker `parent_symbol` regex.

## Query API (`scripts/query_index.py`)

| Sub-command | Implementation | Purpose |
|---|---|---|
| `--query <text> [--top-k 10]` | LanceDB `table.search(embed(text)).limit(k)` + reranked by snippet hash dedup | "show me code like this" |
| `--symbol <name>` | LanceDB filter on `parent_symbol == name` | look up the chunk that defines `name` |
| `--callers <symbol>` | SCIP query (or grep fallback) | who calls `name` |
| `--defs <symbol>` | SCIP query (or grep fallback) | where is `name` defined |
| `--feature-flag <name>` | grep for `flag-name-pattern` across `code/` + cross-check Statsig MCP | resolve a flag's state + on/off code paths |
| `--feature-flags-in-diff` | parse `diff.patch`, extract flag references, return resolutions for each | preload context for Phase 4 |
| `--health` | verify table exists + row count > 0 + SCIP indices exist (or marked not_installed) | validators in Phase 3 |

All sub-commands print JSON when given `--json`.

## Re-indexing on PR push

`<task>/state.json` carries `phases.3_index.head_sha`. If a re-run sees a different `head_sha` from `pr.json.head_sha`:

1. `git fetch` + `git worktree` update.
2. Compute the file delta: `git diff --name-only <old> <new>`.
3. For each changed file: delete its chunks from the LanceDB table, re-chunk, re-embed, insert.
4. SCIP: rerun only for languages whose files changed.
5. Bump `head_sha` in `state.json`.

This is much cheaper than a full rebuild for incremental pushes. Force a full rebuild with `--rebuild`.

## Storage budget

| Repo size | Chunks | LanceDB size | SCIP size (ts) | Time on M1 Pro |
|---|---|---|---|---|
| ~10 KLOC (imagestore-like) | ~400 | ~6 MB | ~2 MB | ~10 s |
| ~100 KLOC (ecomm-ssr-like) | ~4 000 | ~50 MB | ~25 MB | ~60 s |
| ~500 KLOC | ~20 000 | ~250 MB | ~150 MB | ~5 min |

These are estimates from the nogit Electron app's measurements (P5 phase). The Python port should be within 30 % on the time figures.
