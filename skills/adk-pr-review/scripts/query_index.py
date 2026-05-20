#!/usr/bin/env python3
"""query_index.py — query the LanceDB code index + SCIP + repo grep.

Sub-commands:
  --query <text>                  similarity search over chunks (top-k)
  --symbol <name>                 lookup chunk by parent_symbol
  --callers <symbol>              SCIP-backed callers; grep fallback
  --defs <symbol>                 SCIP definitions; grep fallback
  --feature-flag <name>           resolve a flag (repo grep + Statsig MCP placeholder)
  --feature-flags-in-diff         scan diff.patch for flag references
  --health                        verify index integrity
  --changed-file <path>           list chunks for a single file (for context preloading)

Usage:
  python3 query_index.py --task-dir <path> --query "auth login flow" --top-k 8 --json
  python3 query_index.py --task-dir <path> --feature-flag checkout-redesign-v2 --json
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import emit_json, die, get_logger, which, get_cfg  # noqa: E402

try:
    import requests
except ImportError:
    requests = None  # type: ignore

try:
    import lancedb  # type: ignore
except ImportError:
    lancedb = None  # type: ignore


OLLAMA_EMBED_URL = "http://localhost:11434/api/embed"


def _embed(text: str, model: str) -> list[float]:
    if not requests:
        die("`requests` not installed.")
    r = requests.post(OLLAMA_EMBED_URL, json={"model": model, "input": text, "keep_alive": "30s"}, timeout=30)
    r.raise_for_status()
    return r.json()["embeddings"][0]


def _open_table(task_dir: Path):
    if not lancedb:
        die("`lancedb` not installed. pip install -r requirements.txt")
    code_index = task_dir / "code-index"
    if not code_index.exists():
        die(f"code-index not found at {code_index}")
    db = lancedb.connect(str(code_index))
    if "chunks" not in db.list_tables():
        die("table `chunks` not present in code-index — run embedder.py first")
    return db.open_table("chunks")


def _meta(task_dir: Path) -> dict:
    p = task_dir / "code-index" / "meta.json"
    if not p.exists():
        die(f"meta.json missing at {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _row(h: dict, score: float, score_breakdown: dict | None = None) -> dict:
    out = {
        "id": h.get("id"),
        "file": h.get("file"),
        "line_start": h.get("line_start"),
        "line_end": h.get("line_end"),
        "parent_symbol": h.get("parent_symbol"),
        "language": h.get("language"),
        "kind": h.get("kind"),
        "score": float(score),
    }
    if score_breakdown:
        out["score_breakdown"] = score_breakdown
    return out


def _minmax(values: list[float]) -> list[float]:
    if not values:
        return []
    lo, hi = min(values), max(values)
    if hi - lo < 1e-12:
        return [1.0 if v else 0.0 for v in values]
    return [(v - lo) / (hi - lo) for v in values]


def _hybrid_merge(vector_hits: list[dict], fts_hits: list[dict],
                  v_weight: float, f_weight: float, top_k: int) -> list[dict]:
    """Min-max normalize each list's scores to [0,1], then weighted sum.
    Vector: lower _distance is better → similarity = 1 - distance.
    FTS:   higher _score is better → use as-is.
    """
    v_sim = [1.0 - float(h.get("_distance", 1.0)) for h in vector_hits]
    v_norm = _minmax(v_sim)
    f_raw = [float(h.get("_score", 0.0)) for h in fts_hits]
    f_norm = _minmax(f_raw)

    merged: dict[str, dict] = {}
    for h, vs in zip(vector_hits, v_norm):
        cid = h["id"]
        merged[cid] = {"row": h, "v": vs, "f": 0.0, "v_raw": h.get("_distance"), "f_raw": 0.0}
    for h, fs in zip(fts_hits, f_norm):
        cid = h["id"]
        if cid in merged:
            merged[cid]["f"] = fs
            merged[cid]["f_raw"] = h.get("_score")
        else:
            merged[cid] = {"row": h, "v": 0.0, "f": fs, "v_raw": None, "f_raw": h.get("_score")}

    ranked = []
    for cid, rec in merged.items():
        combined = v_weight * rec["v"] + f_weight * rec["f"]
        ranked.append(_row(rec["row"], combined, {
            "vector": round(rec["v"], 4),
            "fts": round(rec["f"], 4),
            "v_raw_distance": rec["v_raw"],
            "f_raw_bm25": rec["f_raw"],
        }))
    ranked.sort(key=lambda r: r["score"], reverse=True)
    return ranked[:top_k]


def cmd_query(task_dir: Path, text: str, top_k: int,
              hybrid: bool | None = None) -> dict:
    """Hybrid (vector + BM25/FTS) by default; flag --no-hybrid forces vector-only."""
    table = _open_table(task_dir)
    meta = _meta(task_dir)
    model = meta.get("model", "nomic-embed-text")

    if hybrid is None:
        hybrid = bool(get_cfg("retrieval.hybrid", default=True))
    v_weight = float(get_cfg("retrieval.vector_weight", default=0.6))
    f_weight = float(get_cfg("retrieval.fts_weight", default=0.4))
    k_dense = int(get_cfg("retrieval.top_k_dense", default=50))
    k_fts = int(get_cfg("retrieval.top_k_fts", default=50))
    k_merged = int(get_cfg("retrieval.top_k_merged", default=80))
    # The CLI --top-k is the final cap; allow it to narrow the merged result.
    final_k = min(top_k, k_merged) if hybrid else top_k

    vec = _embed(text, model)
    vector_hits = table.search(vec).metric("cosine").limit(k_dense if hybrid else top_k).to_list()

    if not hybrid:
        return {
            "query": text, "top_k": top_k, "mode": "vector-only",
            "results": [_row(h, 1.0 - float(h.get("_distance", 1.0))) for h in vector_hits],
        }

    # FTS path: try it; if no FTS index, fall back to vector-only with a marker.
    try:
        fts_hits = table.search(text, query_type="fts").limit(k_fts).to_list()
    except Exception as e:
        return {
            "query": text, "top_k": top_k, "mode": "vector-only",
            "fts_fallback_reason": str(e)[:160],
            "results": [_row(h, 1.0 - float(h.get("_distance", 1.0))) for h in vector_hits],
        }

    results = _hybrid_merge(vector_hits, fts_hits, v_weight, f_weight, final_k)
    return {
        "query": text,
        "top_k": top_k,
        "mode": "hybrid",
        "weights": {"vector": v_weight, "fts": f_weight},
        "candidates": {"dense": len(vector_hits), "fts": len(fts_hits), "merged": len(results)},
        "results": results,
    }


def cmd_symbol(task_dir: Path, name: str) -> dict:
    table = _open_table(task_dir)
    df = table.search().where(f"parent_symbol = '{name.replace('\'', '')}'").limit(20).to_list()
    return {"symbol": name, "matches": [
        {"file": r["file"], "line_start": r["line_start"], "line_end": r["line_end"],
         "kind": r["kind"], "language": r["language"]}
        for r in df
    ]}


def cmd_changed_file(task_dir: Path, file_path: str) -> dict:
    table = _open_table(task_dir)
    df = table.search().where(f"file = '{file_path.replace('\'', '')}'").limit(200).to_list()
    return {"file": file_path, "chunks": [
        {"line_start": r["line_start"], "line_end": r["line_end"],
         "parent_symbol": r["parent_symbol"], "kind": r["kind"]}
        for r in df
    ]}


def _grep_callers(worktree: Path, sym: str) -> list[dict]:
    # Cheap fallback: rg or grep for `name(` matches.
    if not (worktree / ".").exists():
        return []
    cmd = ["rg", "--json", "-n", "-w", rf"{re.escape(sym)}\s*\("]
    if not which("rg"):
        cmd = ["grep", "-rn", "-w", "--include=*.ts", "--include=*.tsx", "--include=*.js",
               "--include=*.jsx", "--include=*.py", "--include=*.go", "--include=*.java",
               "--include=*.rs", "--include=*.rb", f"{sym}(", "."]
    try:
        cp = subprocess.run(cmd, cwd=worktree, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return []
    callers = []
    if which("rg"):
        for line in cp.stdout.splitlines():
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            if ev.get("type") == "match":
                data = ev["data"]
                callers.append({
                    "file": data["path"]["text"],
                    "line": data["line_number"],
                    "preview": data["lines"]["text"].rstrip(),
                })
    else:
        for line in cp.stdout.splitlines():
            parts = line.split(":", 2)
            if len(parts) == 3:
                callers.append({"file": parts[0], "line": int(parts[1]), "preview": parts[2]})
    return callers[:50]


def cmd_callers(task_dir: Path, sym: str) -> dict:
    worktree = task_dir / "code"
    # SCIP path TODO: parse the protobuf via `scip-cli` if available.
    # For now we hand back grep results; the model can rank.
    return {"symbol": sym, "source": "grep", "callers": _grep_callers(worktree, sym)}


def cmd_defs(task_dir: Path, sym: str) -> dict:
    return cmd_symbol(task_dir, sym)


FLAG_CALL_RE = re.compile(
    r"""(?:
        useGate\(\s*['"]([\w\-:.]+)['"]            # statsig client
       | useExperiment\(\s*['"]([\w\-:.]+)['"]
       | useDynamicConfig\(\s*['"]([\w\-:.]+)['"]
       | checkGate\(\s*[^,]+,\s*['"]([\w\-:.]+)['"]
       | get_experiment\(\s*[^,]+,\s*['"]([\w\-:.]+)['"]
       | get_config\(\s*[^,]+,\s*['"]([\w\-:.]+)['"]
       | isFeatureEnabled\(\s*['"]([\w\-:.]+)['"]
       | flag\.get\(\s*['"]([\w\-:.]+)['"]
       )""",
    re.VERBOSE,
)


def cmd_feature_flag(task_dir: Path, name: str) -> dict:
    worktree = task_dir / "code"
    # Locate call sites in the worktree.
    sites = _grep_callers(worktree, name) if name else []
    # Statsig MCP would resolve gate state; we leave it as a marker so the orchestrator can fill it.
    return {
        "name": name,
        "call_sites": [{"file": s["file"], "line": s["line"]} for s in sites],
        "statsig": None,
        "notes": "Statsig state lookup is handled by the orchestrator via adk-mcp-statsig when reachable.",
    }


def cmd_flags_in_diff(task_dir: Path) -> dict:
    diff_path = task_dir / "diff.patch"
    if not diff_path.exists():
        return {"flags": [], "note": "diff.patch missing"}
    seen: dict[str, dict] = {}
    in_added = False
    cur_file = None
    line_no = 0
    for raw in diff_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if raw.startswith("+++ "):
            cur_file = raw[6:].strip() if raw.startswith("+++ b/") else raw[4:].strip()
            line_no = 0
            in_added = True
            continue
        if raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            if m:
                line_no = int(m.group(1)) - 1
            continue
        if not in_added or not cur_file:
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            line_no += 1
            for m in FLAG_CALL_RE.finditer(raw):
                name = next((g for g in m.groups() if g), None)
                if not name:
                    continue
                rec = seen.setdefault(name, {"name": name, "call_sites": []})
                rec["call_sites"].append({"file": cur_file, "line": line_no, "added_in_diff": True})
        elif raw.startswith(" "):
            line_no += 1
    return {"flags": list(seen.values())}


def cmd_health(task_dir: Path) -> dict:
    code_index = task_dir / "code-index"
    if not code_index.exists():
        return {"status": "missing", "code_index": str(code_index)}
    meta_path = code_index / "meta.json"
    if not meta_path.exists():
        return {"status": "no_meta"}
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    try:
        t = _open_table(task_dir)
        n = t.count_rows()
    except Exception as e:
        return {"status": "table_error", "error": str(e), "meta": meta}
    scip = code_index / "meta-scip.json"
    scip_summary = json.loads(scip.read_text(encoding="utf-8")) if scip.exists() else None
    return {"status": "ok", "rows": n, "meta": meta, "scip": scip_summary}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    grp = ap.add_mutually_exclusive_group(required=True)
    grp.add_argument("--query")
    grp.add_argument("--symbol")
    grp.add_argument("--callers")
    grp.add_argument("--defs")
    grp.add_argument("--feature-flag", dest="feature_flag")
    grp.add_argument("--feature-flags-in-diff", action="store_true")
    grp.add_argument("--changed-file", dest="changed_file")
    grp.add_argument("--health", action="store_true")
    ap.add_argument("--top-k", type=int, default=10)
    ap.add_argument("--no-hybrid", action="store_true",
                    help="vector-only; default reads retrieval.hybrid from config")
    ap.add_argument("--json", action="store_true", default=True)
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    if args.query:
        result = cmd_query(task_dir, args.query, args.top_k,
                           hybrid=False if args.no_hybrid else None)
    elif args.symbol:
        result = cmd_symbol(task_dir, args.symbol)
    elif args.callers:
        result = cmd_callers(task_dir, args.callers)
    elif args.defs:
        result = cmd_defs(task_dir, args.defs)
    elif args.feature_flag:
        result = cmd_feature_flag(task_dir, args.feature_flag)
    elif args.feature_flags_in_diff:
        result = cmd_flags_in_diff(task_dir)
    elif args.changed_file:
        result = cmd_changed_file(task_dir, args.changed_file)
    elif args.health:
        result = cmd_health(task_dir)
    else:
        die("no sub-command specified")
        return 1

    return emit_json(result)


if __name__ == "__main__":
    raise SystemExit(main())
