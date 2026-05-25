# rerank-harness — how the parent agent scores rerank candidates

> The skill (`scripts/rerank.py`) emits `rerank-queue.jsonl` and consumes
> `rerank-scores.jsonl`. The step between them is the harness's job: the
> parent agent reads the queue, picks an LLM, scores each candidate against
> its query, and writes the scores file.
>
> The skill is LLM-agnostic. This file describes how each harness handles
> the scoring step.

## The queue file the harness reads

`<task-dir>/rerank-queue.jsonl` — one row per query:

```json
{
  "query_id": "q-001",
  "query": "callers of extractEvents that touch the v2 batch path",
  "context": "PR adds a new transport format; need to surface call sites that exercise the batch branch",
  "top_k_out": 10,
  "candidates": [
    {
      "id": "<sha>",
      "file": "src/api/router.ts",
      "line_start": 88,
      "line_end": 132,
      "kind": "function",
      "parent_symbol": "handleAnalyticsBatch",
      "language": "ts",
      "preview": "<≤800 chars of chunk content>",
      "v_score": 0.83,
      "f_score": 0.21,
      "hybrid_score": 0.6
    }
    /* … up to retrieval.top_k_merged candidates … */
  ]
}
```

## The scores file the harness writes

`<task-dir>/rerank-scores.jsonl` — one row per query:

```json
{
  "query_id": "q-001",
  "scores": [
    {"id": "<sha>", "score": 9.5},
    {"id": "<sha>", "score": 7.2},
    /* … one entry per candidate the harness chose to score … */
  ]
}
```

Score scale: **0 to 10**, where:

| Score | Meaning |
|---|---|
| 9–10 | Directly addresses the query; the reader needs to see this chunk. |
| 7–8  | Strong relevance; one of the right files. |
| 5–6  | Tangentially related; cite if you have spare budget. |
| 3–4  | Topically near but not the answer. |
| 0–2  | Drop — would be a distractor. |

Omitting a candidate from the scores list is equivalent to scoring it 0 (it gets dropped).

## The harness's scoring instructions (verbatim, give this to your scorer LLM)

```
You are scoring code-chunk relevance for a code review reranker.

Input: one QUERY (with CONTEXT) and N candidate chunks. Each chunk has
a file path, line range, parent symbol, and a content preview (the first
~800 chars of the chunk).

For each candidate, score 0-10 by how well it ANSWERS the query (not just
how topically related):

  - "callers of X" → high score if the candidate has `X(` call sites in
    the preview; low if it merely uses similar code.
  - "where is X defined" → high if the candidate defines X; low if it
    only imports or references X.
  - "side effects of X" → high if the candidate's body has reads/writes
    the user would need to know about.
  - "tests for X" → high only if the file is a real test file (filename
    pattern + assertions visible in the preview).

Output: JSON line per query in the format:
  {"query_id":"<id>", "scores":[{"id":"<id>","score":N}, ...]}

Omit candidates you would not include (= score 0). Do not invent
candidate IDs. Do not include fields other than id + score.
```

## Per-harness wiring

### Claude Code (this harness)

The parent agent reads `<task-dir>/rerank-queue.jsonl` directly. For cost,
delegate the scoring to a Haiku subagent rather than spending Sonnet tokens:

```
Agent({
  subagent_type: "general-purpose",
  model: "haiku",
  description: "Score rerank candidates",
  prompt: "Read <task-dir>/rerank-queue.jsonl. For each row, score each
           candidate 0-10 per the instructions in rerank-harness.md.
           Write <task-dir>/rerank-scores.jsonl (one JSON line per
           query_id). Do not modify any other file."
})
```

If you don't want to spawn a subagent, score inline — but keep it terse;
each query may have ~80 candidates and the rendering cost adds up. A useful
inline pattern: stream-read the queue, score one query at a time, append
to the scores file, move on.

After the scores file lands, the skill picks up the rest:

```
python3 scripts/rerank.py --task-dir <dir> \
                          --apply-scores <task-dir>/rerank-scores.jsonl \
                          --queue <task-dir>/rerank-queue.jsonl \
                          --out <task-dir>/rerank-final.jsonl
```

### Cursor

Pass the queue to the agent via Cursor's `@<file>` reference. Use the
standard Cursor profile (Composer 2.5) for normal rerank scoring; use the deep
profile from `shared/model-depth.md` only when the rerank queue spans a large or
risky PR. The agent writes the scores file the same way as Claude Code.

### Codex / Junie / other harnesses

Same JSONL contract. Each harness's parent agent picks its own model
and writes `rerank-scores.jsonl`. If a harness has no model selection,
use whatever it has — the score scale is robust to mid-tier models.

## When rerank should run

- After hybrid retrieval (`query_index.py --query` returns the merged top-K).
- Before findings generation — so the parent agent reads the reranked
  top-N candidates as context for writing findings.json.
- Skip it entirely with `reranker.enabled: false` in
  `~/.agents-devkit/config/adk-pr-review.yaml`. Hybrid merged scores then
  flow through unchanged.

## Cost & latency note

For a PR review with ~10 distinct queries × 80 candidates each = 800 pairs
to score. With a Haiku-class model emitting ~3 tokens per score (id + score)
this is ~10-20 seconds total. With Sonnet inline it's higher but the
quality lift on tight context windows is real.

The harness can also batch: pass multiple (query, candidate) pairs in one
prompt and parse the structured output. The contract is the JSONL files;
the LLM call shape is open.
