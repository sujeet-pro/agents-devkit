#!/usr/bin/env python3
"""embedder.py — ollama → LanceDB.

Reads chunks.jsonl produced by chunker.py, batches them through ollama's /api/embed,
writes to <task-dir>/code-index/chunks.lance/ (LanceDB table named 'chunks').

Usage:
  python3 embedder.py --task-dir <path> --chunks chunks.jsonl --model nomic-embed-text [--batch 24]

Refuses to start if ollama isn't healthy (caller should have run ensure_ollama.py first).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable, Iterator

sys.path.insert(0, str(Path(__file__).parent))
from _common import get_logger, write_json, emit_json, die  # noqa: E402

try:
    import requests
except ImportError:
    die("`requests` not installed. pip install -r requirements.txt")

try:
    import lancedb  # type: ignore
    import pyarrow as pa  # type: ignore
except ImportError:
    die("`lancedb` (and pyarrow) not installed. pip install -r requirements.txt")


OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"


def iter_chunks(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def chunks_to_batches(rows: Iterable[dict], size: int) -> Iterator[list[dict]]:
    batch: list[dict] = []
    for r in rows:
        batch.append(r)
        if len(batch) >= size:
            yield batch
            batch = []
    if batch:
        yield batch


def embed_batch(model: str, texts: list[str], keep_alive: str = "5m",
                retries: int = 3, log=None) -> list[list[float]]:
    last_err = None
    for attempt in range(retries):
        try:
            r = requests.post(
                OLLAMA_EMBED_URL,
                json={"model": model, "input": texts, "keep_alive": keep_alive},
                timeout=120,
            )
            r.raise_for_status()
            data = r.json()
            embs = data.get("embeddings")
            if not embs or len(embs) != len(texts):
                raise RuntimeError(f"ollama returned {len(embs) if embs else 0} embeddings for {len(texts)} inputs")
            return embs
        except (requests.RequestException, RuntimeError) as e:
            last_err = e
            wait = 2 * (2 ** attempt)
            if log:
                log.warning("embed batch failed (attempt %d/%d): %s — sleeping %ds", attempt + 1, retries, e, wait)
            time.sleep(wait)
    raise RuntimeError(f"embed failed after {retries} attempts: {last_err}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--chunks", required=True)
    ap.add_argument("--model", default="nomic-embed-text")
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--mode", choices=("replace", "incremental"), default="replace",
                    help="replace: drop existing table and re-create. incremental: delete chunks for the files in --replaced-files, then add the new ones from --chunks.")
    ap.add_argument("--replaced-files", default=None,
                    help="(incremental only) file with one repo-relative path per line — chunks belonging to these files are deleted first")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    chunks_path = Path(args.chunks)
    log = get_logger("embedder", task_dir)

    if not chunks_path.exists():
        die(f"chunks file not found: {chunks_path}")

    code_index = task_dir / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)

    db = lancedb.connect(str(code_index))
    table_name = "chunks"

    if args.mode == "replace":
        if table_name in db.list_tables():
            db.drop_table(table_name)
        deleted = 0
    else:
        if table_name not in db.list_tables():
            die("incremental mode but no prior table — run with --mode replace first")
        if not args.replaced_files:
            die("incremental mode requires --replaced-files")
        files_path = Path(args.replaced_files)
        if not files_path.exists():
            die(f"--replaced-files not found: {files_path}")
        replaced = [ln.strip() for ln in files_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not replaced:
            log.info("incremental: nothing in --replaced-files; only adding new chunks")
            deleted = 0
        else:
            tbl = db.open_table(table_name)
            # LanceDB filter syntax: SQL-style WHERE.
            quoted = ",".join("'" + f.replace("'", "''") + "'" for f in replaced)
            where = f"file IN ({quoted})"
            before = tbl.count_rows()
            tbl.delete(where)
            after = tbl.count_rows()
            deleted = before - after
            log.info("incremental: deleted %d chunks across %d files", deleted, len(replaced))

    n_total = 0
    n_batches = 0
    dim: int | None = None
    table = db.open_table(table_name) if (args.mode == "incremental" and table_name in db.list_tables()) else None
    started = time.time()

    rows_buf: list[dict] = []
    n_skipped_oversized = 0

    # Pre-flight skip: ollama embed models cap input length somewhere around
    # 8k-16k tokens. A chunk above MAX_INPUT_CHARS will always fail; sending it
    # costs us a batch failure + N per-chunk retry probes (~4-6s each). Skip
    # upfront. The threshold is intentionally generous — only minified files,
    # large locale JSONs, and lockfile-shaped blobs should hit it.
    MAX_INPUT_CHARS = int(os.environ.get("ADK_PR_REVIEW_EMBED_MAX_CHARS", "30000"))
    def _under_cap(chunk: dict) -> bool:
        if len(chunk.get("content") or "") <= MAX_INPUT_CHARS:
            return True
        nonlocal n_skipped_oversized
        n_skipped_oversized += 1
        log.warning("skipping oversized chunk pre-flight: %s:%s-%s (%d chars > cap=%d)",
                    chunk.get("file"), chunk.get("line_start"), chunk.get("line_end"),
                    len(chunk.get("content", "")), MAX_INPUT_CHARS)
        return False
    chunks_iter = (c for c in iter_chunks(chunks_path) if _under_cap(c))
    for batch_idx, batch in enumerate(chunks_to_batches(chunks_iter, args.batch)):
        texts = [r["content"] for r in batch]
        try:
            embs = embed_batch(args.model, texts, keep_alive="5m", log=log)
        except RuntimeError as e:
            # Could be one oversized chunk poisoning the batch. Probe each
            # chunk individually; skip the ones the model rejects (likely
            # > model context window — minified files, etc.).
            log.warning("batch %d failed (%s); probing individually", batch_idx, str(e)[:120])
            embs = []
            survivors: list[dict] = []
            for r in batch:
                try:
                    single = embed_batch(args.model, [r["content"]], keep_alive="5m",
                                         retries=1, log=None)[0]
                    embs.append(single)
                    survivors.append(r)
                except RuntimeError as ee:
                    n_skipped_oversized += 1
                    log.warning("skipping chunk %s:%s-%s (%d chars): %s",
                                r.get("file"), r.get("line_start"), r.get("line_end"),
                                len(r.get("content", "")), str(ee)[:80])
            batch = survivors
            if not batch:
                continue
        if dim is None:
            dim = len(embs[0])
        for r, v in zip(batch, embs):
            rows_buf.append({
                "id": r["id"],
                "file": r["file"],
                "line_start": int(r["line_start"]),
                "line_end": int(r["line_end"]),
                "parent_symbol": r.get("parent_symbol") or "<module>",
                "language": r.get("language") or "",
                "kind": r.get("kind") or "",
                "content": r["content"],
                "snippet_hash": r.get("snippet_hash") or "",
                "vector": v,
            })
        n_total += len(batch)
        n_batches += 1
        if len(rows_buf) >= args.batch * 5:
            if table is None:
                table = db.create_table(table_name, data=rows_buf, mode="overwrite")
            else:
                table.add(rows_buf)
            log.info("flushed %d rows (total %d)", len(rows_buf), n_total)
            rows_buf = []

    if rows_buf:
        if table is None:
            table = db.create_table(table_name, data=rows_buf, mode="overwrite")
        else:
            table.add(rows_buf)

    # Send a tiny final call with keep_alive=0 to unload the model.
    try:
        requests.post(OLLAMA_EMBED_URL,
                      json={"model": args.model, "input": "x", "keep_alive": 0},
                      timeout=5)
    except requests.RequestException:
        pass

    elapsed = time.time() - started

    if n_total == 0 and args.mode == "replace":
        die("no chunks were embedded — the chunker produced 0 rows")
    if n_total == 0:
        log.info("incremental: no new chunks to add (only deletions). table now has %d rows.",
                 table.count_rows() if table is not None else -1)

    # Index for ANN. BRUTE_FORCE under 10k rows; IVF_PQ above.
    if table is not None:
        try:
            if n_total >= 10_000:
                table.create_index(metric="cosine", index_type="IVF_PQ",
                                   num_partitions=64, num_sub_vectors=16)
            else:
                # Lance's default flat scan is fast at this size; no index needed.
                pass
            # FTS for keyword fallback.
            try:
                table.create_fts_index("content", replace=True)
            except Exception as e:
                log.warning("FTS index failed (continuing without it): %s", e)
        except Exception as e:
            log.warning("vector index creation failed (continuing): %s", e)

    final_rows = table.count_rows() if table is not None else n_total
    meta = {
        "table": table_name,
        "model": args.model,
        "dim": dim,
        "rows": final_rows,
        "rows_added_this_run": n_total,
        "rows_deleted_this_run": int(deleted),
        "chunks_skipped_oversized": n_skipped_oversized,
        "mode": args.mode,
        "batches": n_batches,
        "batch_size": args.batch,
        "elapsed_s": round(elapsed, 2),
        "table_path": str(code_index / f"{table_name}.lance"),
        "indexed": (final_rows >= 10_000),
        "fts": True,
    }
    # In incremental mode, preserve prior meta where it makes sense (e.g. embed-model must match).
    prior_meta_path = code_index / "meta.json"
    if args.mode == "incremental" and prior_meta_path.exists():
        try:
            prior = json.loads(prior_meta_path.read_text(encoding="utf-8"))
            if prior.get("model") and prior["model"] != args.model:
                die(f"incremental embed-model mismatch: prior={prior['model']} new={args.model}. Use --rebuild to start over.")
            if not meta["dim"] and prior.get("dim"):
                meta["dim"] = prior["dim"]
        except Exception:
            pass
    write_json(code_index / "meta.json", meta)

    if args.json:
        return emit_json(meta)
    log.info("embedded %d chunks in %.1fs (dim=%s)", n_total, elapsed, dim)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
