# shared/guidelines/code-index.md — using the repo-level code index from any skill

> Loaded by `/adk-implement` (TDD sub-flow), `/adk-investigate`,
> `/adk-document` (runbook / ADR / migration), and `/adk-review` (light
> path) when those skills want repo-symbol context.

## What this is

`scripts/lib/code_index/` is the shared code-index library. It's the
chunker + embedder + LanceDB + SCIP + grep stack that `/adk-pr-review`
already uses, with the wiring extracted so other skills can consume the
same data.

Storage:

```
$ADK_DATA_HOME/repos/<repo>/                    clone (default branch)
$ADK_DATA_HOME/repos/.indices/<repo>/           adk-owned index
  repo-meta.json                                  indexed_oid, indexed_at, default_branch
  code-index/
    chunks.jsonl  chunks.lance/  scip/  meta.json
```

Built by `adk repo add <git-url>` and refreshed by `adk repo update <name>`.
PR-review seeds from this when present and falls back to a full reindex when not.

## Public surface — what skills may rely on

```python
from scripts.lib.code_index.query import (
    open_index, similar, by_symbol, defs, callers, feature_flag,
    Hit, Index,
    IndexNotBuilt, IndexStale, ModelMismatch,
)
```

Every other name in the module is internal and may change without notice.

### `open_index(target, *, kind="repo", max_staleness_days=None, require_fresh=False, require_model=None, skill="...", _log=True) -> Index`

Resolves the on-disk index. Two roots:

- `kind="repo"`: `target` is a repo name; resolves to
  `$ADK_DATA_HOME/repos/.indices/<target>/code-index/`.
- `kind="task"`: `target` is a task-dir path; resolves to
  `<target>/code-index/`. PR-review uses this internally.

Errors:

| Exception | When | Recommended caller behavior |
|---|---|---|
| `IndexNotBuilt(target)` | No index on disk for this repo | Tell the user to run `adk repo add <git-url>` or `adk repo update <name>`. Offer to skip semantic search and proceed without. |
| `IndexStale(age_days, last_refreshed, cap_days)` | `require_fresh=True` and the index is older than the cap | Either re-call with `require_fresh=False` (proceed stale + surface "your index is N days old"), or offer to refresh. |
| `ModelMismatch(expected, found)` | `require_model` is set and differs from the on-disk model | Hard fail. Querying across embed models returns nonsense. |

Sensible defaults: `require_fresh=False`, `require_model=None`. Most consumers should **warn** on staleness, not refuse.

### `similar(idx, query, *, top_k=8, mode="hybrid", file_glob=None) -> list[Hit]`

Hybrid (vector + BM25) by default. `mode` is one of `"hybrid"`, `"vector"`, `"bm25"`. `file_glob` like `"src/auth/**"` is server-side filtered against the `file` column. Empty / whitespace query returns `[]`.

### `by_symbol(idx, symbol, *, limit=20) -> list[Hit]`

Exact-match on the chunk's `parent_symbol` column.

### `defs(idx, symbol) -> list[Hit]`

Definition sites. Today: same as `by_symbol`. SCIP-backed lookup on the roadmap.

### `callers(idx, symbol, *, limit=50) -> list[Hit]`

Code locations that call `symbol`. Uses ripgrep (or grep fallback) over `idx.worktree`. Empty when no worktree is available.

### `feature_flag(idx, key) -> list[Hit]`

Code sites referencing a feature-flag / experiment key. Grep over the worktree. Statsig MCP correlation is the caller's job.

### `Hit` (frozen dataclass)

Stable fields: `path`, `line_start`, `line_end`, `score`, `snippet`, `symbol`, `source`. New fields go in `extras: dict` — never inline.

### `Index`

Carries `repo`, `code_index_dir`, `embed_model`, `dim`, `rows`, `indexed_sha`, `last_refreshed`, `kind`, `worktree`. The `age_days` property returns float days since `last_refreshed` (None for `kind="task"`).

## Worked examples

### `/adk-implement` TDD sub-flow — "related code patterns"

```python
from scripts.lib.code_index.query import open_index, similar, callers, IndexNotBuilt, IndexStale

try:
    idx = open_index("ecomm-ssr")
except IndexNotBuilt:
    log.info("repo not indexed yet; skipping related-code section")
    related_section = ""
else:
    if idx.age_days and idx.age_days > 7:
        log.warning("base index is %.1f days old — relations may be stale", idx.age_days)
    hits = []
    for bullet in tdd.requirement_bullets:
        hits.extend(similar(idx, bullet, top_k=3))
    # De-dupe by path:line.
    seen = set()
    for h in hits:
        key = (h.path, h.line_start)
        if key in seen: continue
        seen.add(key)
        related_section += f"- `{h.path}:{h.line_start}-{h.line_end}` — {h.symbol or h.path}\n"
```

### `/adk-investigate` — symptom → candidate code paths

```python
idx = open_index(repo_for_service(service))   # may raise IndexNotBuilt
hits = similar(idx, symptom_text, top_k=6, mode="hybrid")
# Confidence: medium when ≥2 of the top-3 hits land in the same module;
# low otherwise. Always anchor next to the DD trace evidence.
```

### `/adk-document` (migration) — enumerate API surface

```python
idx = open_index(repo)
api_callers = callers(idx, deprecated_fn)
api_defs    = defs(idx, deprecated_fn)
```

## Rules

1. **Pin the embed model.** When you care about cross-comparable scores, pass `require_model=`. Mixing `nomic-embed-text` and `bge-m3` returns nonsense — `ModelMismatch` is a hard fail by design.
2. **Surface staleness.** Every consumer prints `indexed_sha`, `age_days`, and `embed_model` somewhere in its output. `/adk-document` puts it at the top of an ADR; `/adk-investigate` puts it in the report's "Evidence" section.
3. **Fail open.** If the index isn't built, the consumer skill MUST still complete — just without the semantic-search section. Never block a skill on the index.
4. **Don't write through the API.** This surface is read-only. Building / refreshing is the job of `adk repo add` and `adk repo update`. Each skill's `--rebuild` is for its own task-dir, not the base.
5. **No PII queries.** Don't pass user IDs, emails, message bodies, or PR review comments as `query`. The query embedding is sent to a local ollama process today, but the rule keeps us safe when we move to a hosted model.
6. **Cap top_k.** Default 8. Crank to 15 only when the consumer is genuinely scanning for everything (e.g. a migration enumeration). Bigger top_k ≠ better — the precis is for the model, and 20 hits dilute the signal.

## Configuration

Defaults ship in `scripts/lib/code_index/defaults.yaml`. User overrides go in `$ADK_CONFIG_HOME/code-index.yaml` — same shape, deep merged:

```yaml
embed:
  default_model: nomic-embed-text   # change to bge-m3 if you want higher quality everywhere
retrieval:
  hybrid: true
  vector_weight: 0.6
  fts_weight: 0.4
base_index:
  max_staleness_days: 7              # how old before consumers warn
```

## Failure modes the caller must handle

| Failure | What happens | What to do |
|---|---|---|
| ollama not running | `similar()` raises `CodeIndexError` from the HTTP layer | Skip semantic; fall back to `by_symbol` + `callers` (SCIP + grep paths). |
| LanceDB version skew | `_open_table` raises | Pin via the shared requirements. Re-run install.py if breaking. |
| `chunks.lance` corrupted | `_open_table` raises | `adk repo update <name> --force` rebuilds. |
| User passes an unknown repo | `IndexNotBuilt` | Print `Run: adk repo add <git-url>` and skip the section. |
| `require_fresh=True` + 30-day-old index | `IndexStale` | Re-call without `require_fresh`, surface the age. |
