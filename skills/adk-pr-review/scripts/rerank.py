#!/usr/bin/env python3
"""rerank.py — harness-agnostic reranker interface.

The skill never picks the LLM. It defines a queue-file contract:

  1. SKILL emits  rerank-queue.jsonl  (one row per query, with candidates + previews).
  2. HARNESS reads the queue, scores each (query, candidate) pair, and writes
     rerank-scores.jsonl  (one row per query, with {id: score} entries).
  3. SKILL reads the scores, sorts each query's candidates, applies the
     retrieval.top_k_final cap, and writes  rerank-final.jsonl  (the
     authoritative ranked candidate list per query).

The scoring step in between is the harness's responsibility. In Claude Code,
the parent agent reads the queue and scores via its own LLM (Sonnet inline,
or a Haiku subagent for cost). Other harnesses (Cursor, Codex, Junie) use
whichever model their parent agent has access to. The skill itself is
LLM-agnostic; reranker.mode controls the contract, not the model.

Modes
-----
  rerank.py --task-dir <dir> --build-queue --queries <queries.json5> --out queue.jsonl
  rerank.py --task-dir <dir> --apply-scores <scores.jsonl> --queue <queue.jsonl> --out final.jsonl

File schemas
------------
queries.json5 (input to --build-queue):
  [
    {"query_id": "q-001", "query": "callers of extractEvents", "context": "..."},
    {"query_id": "q-002", "query": "validation profile=ssr override flow", "context": "..."}
  ]

rerank-queue.jsonl (skill emits, harness reads):
  {"query_id":"q-001","query":"...","context":"...","top_k_out":10,
   "candidates":[
     {"id":"<hash>","file":"...","line_start":12,"line_end":45,"kind":"function",
      "parent_symbol":"extractEvents","language":"ts",
      "preview":"<≤ 800 chars from content>",
      "v_score":0.83,"f_score":0.21,"hybrid_score":0.6},
     ...
   ]}

rerank-scores.jsonl (harness emits, skill reads):
  {"query_id":"q-001","scores":[{"id":"<hash>","score":9.5},{"id":"...","score":7.2},...]}

rerank-final.jsonl (skill emits, downstream uses):
  {"query_id":"q-001","query":"...","ranked":[<candidate with rerank_score>, ...]}

The harness's scoring step instructions live in SKILL.md (and references/rerank-harness.md).
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from _common import die, get_logger, get_cfg, read_json, write_json  # noqa: E402

THIS_DIR = Path(__file__).parent
PY = sys.executable


# ---------------- JSON5-lite reader (handle trailing commas + // comments) ----------------

def _read_queries(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    # Strip // line comments outside of strings (simple-minded, fine for queries file).
    cleaned_lines = []
    for line in text.splitlines():
        m = re.search(r"(^|[^:])//", line)
        if m and "'" not in line[: m.end()] and '"' not in line[: m.end()]:
            line = line[: m.start() + (1 if m.group(1) else 0)]
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)
    # Drop trailing commas before } or ]
    text = re.sub(r",(\s*[}\]])", r"\1", text)
    return json.loads(text)


def _preview(content: str, max_chars: int = 800) -> str:
    if len(content) <= max_chars:
        return content
    return content[: max_chars - 3].rstrip() + "..."


def _query_index_json(task_dir: Path, query: str, top_k: int) -> dict:
    cp = subprocess.run(
        [PY, str(THIS_DIR / "query_index.py"),
         "--task-dir", str(task_dir), "--query", query, "--top-k", str(top_k), "--json"],
        capture_output=True, text=True, check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(f"query_index failed (rc={cp.returncode}): {cp.stderr[:300]}")
    return json.loads(cp.stdout)


def _read_content_for_id(task_dir: Path, chunk_id: str) -> str:
    """Look up a chunk's content in LanceDB by id. Used to attach previews."""
    try:
        import lancedb  # noqa: WPS433
    except ImportError:
        return ""
    code_index = task_dir / "code-index"
    if not code_index.exists():
        return ""
    db = lancedb.connect(str(code_index))
    t = db.open_table("chunks")
    # LanceDB doesn't have a primary-key-by-id index in our setup; the chunks table is small
    # enough (~20k rows in ecomm-ssr) to scan. We pass a where-clause.
    rs = t.search().where(f"id = '{chunk_id.replace(chr(39), '')}'", prefilter=True).limit(1).to_list()
    if not rs:
        return ""
    return rs[0].get("content", "") or ""


def cmd_build_queue(task_dir: Path, queries_path: Path, out_path: Path, log) -> dict:
    queries = _read_queries(queries_path)
    if not isinstance(queries, list):
        die(f"queries file must be a JSON array; got {type(queries).__name__}")

    top_k_in = int(get_cfg("retrieval.top_k_merged", default=80))
    top_k_out = int(get_cfg("retrieval.top_k_final", default=10))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    with out_path.open("w", encoding="utf-8") as fh:
        for q in queries:
            qid = q.get("query_id") or q.get("id")
            text = q.get("query") or q.get("text")
            if not qid or not text:
                log.warning("skipping malformed query entry: %s", q)
                continue
            ctx = q.get("context", "")
            try:
                resp = _query_index_json(task_dir, text, top_k_in)
            except RuntimeError as e:
                log.warning("query failed for %s: %s", qid, e)
                continue
            candidates = []
            for r in resp.get("results", [])[:top_k_in]:
                content = _read_content_for_id(task_dir, r["id"])
                candidates.append({
                    "id": r["id"],
                    "file": r["file"],
                    "line_start": r["line_start"],
                    "line_end": r["line_end"],
                    "kind": r["kind"],
                    "parent_symbol": r["parent_symbol"],
                    "language": r["language"],
                    "preview": _preview(content),
                    "v_score": (r.get("score_breakdown") or {}).get("vector"),
                    "f_score": (r.get("score_breakdown") or {}).get("fts"),
                    "hybrid_score": r.get("score"),
                })
            fh.write(json.dumps({
                "query_id": qid,
                "query": text,
                "context": ctx,
                "top_k_out": top_k_out,
                "candidates": candidates,
            }, ensure_ascii=False) + "\n")
            written += 1
    return {"queries": written, "out": str(out_path), "top_k_in": top_k_in, "top_k_out": top_k_out}


def cmd_apply_scores(task_dir: Path, queue_path: Path, scores_path: Path, out_path: Path, log) -> dict:
    """Join scores with queue, sort by rerank score desc, cap at top_k_out, emit final."""
    queue: dict[str, dict] = {}
    with queue_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                obj = json.loads(line)
                queue[obj["query_id"]] = obj

    scores_by_query: dict[str, dict[str, float]] = {}
    with scores_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            qid = obj["query_id"]
            scores_by_query[qid] = {s["id"]: float(s["score"]) for s in obj.get("scores", [])}

    out_path.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    missing_queries: list[str] = []
    with out_path.open("w", encoding="utf-8") as fh:
        for qid, q in queue.items():
            scoremap = scores_by_query.get(qid)
            if scoremap is None:
                missing_queries.append(qid)
                # Fall back to hybrid order — preserves the candidates as-is.
                ranked = list(q.get("candidates", []))
                for r in ranked:
                    r["rerank_score"] = None
            else:
                ranked = []
                for c in q.get("candidates", []):
                    score = scoremap.get(c["id"])
                    if score is None:
                        continue  # candidate not scored → drop (harness chose to omit)
                    cc = dict(c)
                    cc["rerank_score"] = score
                    ranked.append(cc)
                ranked.sort(key=lambda r: r["rerank_score"], reverse=True)
            top_k_out = int(q.get("top_k_out") or get_cfg("retrieval.top_k_final", default=10))
            fh.write(json.dumps({
                "query_id": qid,
                "query": q.get("query"),
                "context": q.get("context", ""),
                "ranked": ranked[:top_k_out],
                "n_input": len(q.get("candidates", [])),
                "n_scored": len(scoremap or {}),
                "fallback_to_hybrid": scoremap is None,
            }, ensure_ascii=False) + "\n")
            written += 1
    return {
        "queries": written,
        "missing_query_scores": missing_queries,
        "out": str(out_path),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    sub = ap.add_mutually_exclusive_group(required=True)
    sub.add_argument("--build-queue", action="store_true")
    sub.add_argument("--apply-scores", dest="apply_scores", default=None,
                     help="path to rerank-scores.jsonl emitted by the harness")
    ap.add_argument("--queries", help="path to queries.json5 (for --build-queue)")
    ap.add_argument("--queue", default=None, help="path to rerank-queue.jsonl (for --apply-scores)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    log = get_logger("rerank", task_dir if task_dir.exists() else None)

    if args.build_queue:
        if not args.queries:
            die("--build-queue requires --queries <path>")
        result = cmd_build_queue(task_dir, Path(args.queries), Path(args.out), log)
    else:
        # apply-scores
        if not args.queue:
            die("--apply-scores requires --queue <path>")
        result = cmd_apply_scores(task_dir, Path(args.queue), Path(args.apply_scores), Path(args.out), log)

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
