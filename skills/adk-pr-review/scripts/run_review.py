#!/usr/bin/env python3
"""run_review.py — orchestrator for /adk-pr-review.

Behavior on EVERY invocation (whether first run or N-th):

  Phase 0 (prereq)     — always runs.
  Phase 2a (fetch PR)  — always runs. Pulls fresh PR metadata + diff. Records the
                         new head_oid.
  Phase 1 (worktree)   — always runs. `git fetch --all --prune` in the clone,
                         then `git worktree add --detach <task>/code <head_oid>`
                         (or `git checkout --detach <head_oid>` if the worktree
                         already exists). Serialized via the global lock.
  Phase 2b (docs)      — always runs. Re-scans PR body + comments for doc URLs;
                         writes docs/index.json with pending-MCP markers so the
                         agent can fetch Confluence / Jira / GDoc via MCPs.
  Phase 3 (index)      — runs if head_oid changed OR --rebuild. When head_oid
                         changed AND prior state exists: INCREMENTAL re-index
                         (only the files that differ between old and new
                         head_oid). When no prior state OR --rebuild: full
                         re-index.
  Phase 4a (precis)    — always runs (regenerates the precis the agent reads).

What this script does NOT do: invoke `claude -p`. The calling agent does that
after reading precis.md + SKILL.md + finding.template.json, then calls back into
comment_resolver.py + post_comments.py + report.py.

Usage:
  python3 run_review.py <pr-url> [--auto] [--rebuild] [--no-post]
                                 [--no-resolve-existing]
                                 [--embed-model nomic-embed-text]
                                 [--scope all|security|correctness|tests]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (  # noqa: E402
    parse_pr_url, ensure_dirs, task_dir_for, repo_clone_for,
    pr_lock_for, try_file_lock, LockHeldError,
    read_state, mark_phase, write_state, write_json, read_json,
    get_logger, die, run, which, get_cfg,
)

THIS_DIR = Path(__file__).parent
PY = sys.executable


def step(cmd: list[str], log, env=None):
    log.info("$ %s", " ".join(cmd))
    cp = run(cmd, env=env, check=False)
    if cp.stdout:
        log.info("stdout:\n%s", cp.stdout.strip())
    if cp.stderr.strip():
        log.info("stderr:\n%s", cp.stderr.strip())
    if cp.returncode != 0:
        raise SystemExit(f"step failed (rc={cp.returncode}): {' '.join(cmd)}")
    return cp


def diff_changed_files(repo_path: Path, old_oid: str | None, new_oid: str, log) -> list[str]:
    """Return relative paths changed between old_oid..new_oid. Empty if old_oid is None."""
    if not old_oid:
        return []
    if not old_oid or old_oid == new_oid:
        return []
    try:
        cp = run(["git", "diff", "--name-only", f"{old_oid}..{new_oid}"], cwd=repo_path, check=False)
    except Exception as e:
        log.warning("diff_changed_files: %s", e)
        return []
    if cp.returncode != 0:
        # old_oid may not be reachable any more if rebased + force-pushed;
        # fall back to full re-index.
        log.warning("git diff failed (rc=%d); will full re-index", cp.returncode)
        return []
    return [line.strip() for line in cp.stdout.splitlines() if line.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="PR URL")
    ap.add_argument("--auto", action="store_true")
    ap.add_argument("--rebuild", action="store_true", help="force full re-index from scratch")
    ap.add_argument("--no-post", action="store_true")
    ap.add_argument("--no-resolve-existing", action="store_true")
    ap.add_argument("--detailed", action="store_true",
                    help="use the configured detailed embedder (default: bge-m3) instead of "
                         "the fast default (nomic-embed-text). Higher retrieval quality, ~4-5x slower indexing.")
    ap.add_argument("--embed-model",
                    help="explicit embed model name; overrides --detailed and config.embed.*")
    ap.add_argument("--no-hybrid", action="store_true",
                    help="disable BM25 (FTS) in retrieval; vector-only.")
    ap.add_argument("--no-reranker", action="store_true",
                    help="skip the rerank stage; use hybrid-merged scores as final ranking.")
    ap.add_argument("--no-triage", action="store_true",
                    help="skip the triage step (auto-accept all findings); same as --auto for posting.")
    ap.add_argument("-i", "--interactive", action="store_true",
                    help="walk each finding accept / reject / edit before posting.")
    ap.add_argument("--scope", choices=("all", "security", "correctness", "tests"), default="all")
    ap.add_argument("--top-k-context", type=int, default=6, help="top-k chunks per changed file for precis")
    ap.add_argument("--wait", action="store_true",
                    help="if another /adk-pr-review is already running against the same PR, wait instead of failing fast")
    args = ap.parse_args()

    # Resolve the embed model: explicit --embed-model wins, else --detailed picks
    # config.embed.detailed_model, else config.embed.default_model, else
    # env-var, else literal "nomic-embed-text".
    if args.embed_model:
        embed_model = args.embed_model
    elif args.detailed:
        embed_model = get_cfg("embed.detailed_model", default="bge-m3")
    else:
        embed_model = (
            os.environ.get("ADK_PR_REVIEW_EMBED_MODEL")
            or get_cfg("embed.default_model", default="nomic-embed-text")
        )
    args.embed_model = embed_model  # for downstream code that reads args.embed_model

    ensure_dirs()
    parsed = parse_pr_url(args.url)
    host, owner, repo, n = parsed["host"], parsed["owner"], parsed["repo"], parsed["pr_number"]
    task_dir = task_dir_for(repo, n)
    task_dir.mkdir(parents=True, exist_ok=True)
    log = get_logger("orchestrator", task_dir)
    log.info("=== /adk-pr-review %s ===", args.url)

    # Per-PR lock — prevents two simultaneous reviews of the same PR.
    # Fail fast by default (use --wait to queue). Parallel reviews of
    # DIFFERENT PRs do not contend on this lock.
    #
    # ADK_PR_LOCK_HELD=1 (set by the /adk-pr-reviews batch worker) signals that
    # the caller already holds this PR's lock; skip re-acquisition.
    pr_lock_ctx = None
    if os.environ.get("ADK_PR_LOCK_HELD") != "1":
        try:
            pr_lock_ctx = try_file_lock(pr_lock_for(repo, n), wait=args.wait, timeout_s=0.0)
            pr_lock_ctx.__enter__()
        except LockHeldError as e:
            die(str(e))
            return 1  # unreachable
    try:
        return _main_inner(args, parsed, task_dir, log)
    finally:
        if pr_lock_ctx is not None:
            try:
                pr_lock_ctx.__exit__(None, None, None)
            except Exception:
                pass


def _main_inner(args, parsed, task_dir, log) -> int:
    host, owner, repo, n = parsed["host"], parsed["owner"], parsed["repo"], parsed["pr_number"]
    state = read_state(task_dir)
    prior_index_head = state.get("phases", {}).get("3_index", {}).get("head_oid_at_index")
    if args.rebuild:
        log.info("--rebuild: prior index will be discarded")
        prior_index_head = None

    # ---------- Phase 0: prereqs ----------
    log.info("--- Phase 0: prereq ---")
    cp = run([PY, str(THIS_DIR / "ensure_ollama.py"), "--model", args.embed_model, "--json"], check=False)
    if cp.returncode != 0:
        sys.stderr.write(cp.stdout + cp.stderr)
        die("ollama not ready — see hint above")
    if host == "github" and not which("gh"):
        die("gh CLI required for GitHub PRs. brew install gh.")
    mark_phase(task_dir, "0_prereq", "done",
               url=args.url, host=host, owner=owner, repo=repo, pr_number=n,
               embed_model=args.embed_model)

    # ---------- Phase 2a: fetch PR (always — gets fresh head_oid) ----------
    log.info("--- Phase 2a: fetch PR (always; gets fresh head_oid) ---")
    step([PY, str(THIS_DIR / "fetch_pr.py"),
          "--host", host, "--owner", owner, "--repo", repo,
          "--pr-number", str(n), "--task-dir", str(task_dir), "--json"], log)
    pr = read_json(task_dir / "pr.json")
    head_oid = pr.get("head_oid")
    if not head_oid:
        die("fetch_pr.py did not populate head_oid")
    log.info("PR head_oid: %s (prior indexed: %s)", head_oid[:12], (prior_index_head or "<none>")[:12])

    # ---------- Phase 1: clone + worktree (ALWAYS — pulls latest) ----------
    log.info("--- Phase 1a: ensure repo clone (always fetch --all --prune) ---")
    step([PY, str(THIS_DIR / "ensure_repo_clone.py"),
          "--host", host, "--owner", owner, "--repo", repo, "--json"], log)
    log.info("--- Phase 1b: create/update worktree at %s (serialized) ---", head_oid[:12])
    step([PY, str(THIS_DIR / "create_worktree.py"),
          "--repo", repo, "--pr-number", str(n), "--head-oid", head_oid,
          "--json"] + (["--rebuild"] if args.rebuild else []), log)
    mark_phase(task_dir, "1_worktree", "done",
               worktree_path=str(task_dir / "code"), head_oid=head_oid)

    # ---------- Phase 2b: supporting docs scan (always) ----------
    log.info("--- Phase 2b: scan supporting docs ---")
    step([PY, str(THIS_DIR / "fetch_supporting_docs.py"),
          "--task-dir", str(task_dir), "--json"], log)
    mark_phase(task_dir, "2_fetch", "done", head_oid=head_oid)

    # ---------- Phase 3: index (full or incremental) ----------
    code_index_dir = task_dir / "code-index"
    chunks_path = code_index_dir / "chunks.jsonl"
    has_prior_index = (code_index_dir / "meta.json").exists() and prior_index_head is not None
    changed_files: list[str] = []
    if has_prior_index and prior_index_head != head_oid:
        repo_clone = repo_clone_for(repo)
        changed_files = diff_changed_files(repo_clone, prior_index_head, head_oid, log)
        log.info("incremental re-index: %d files changed between %s..%s",
                 len(changed_files), prior_index_head[:12], head_oid[:12])

    if not has_prior_index:
        log.info("--- Phase 3: FULL index (no prior state) ---")
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        step([PY, str(THIS_DIR / "chunker.py"),
              "--worktree", str(task_dir / "code"),
              "--out", str(chunks_path)], log)
        step([PY, str(THIS_DIR / "embedder.py"),
              "--task-dir", str(task_dir),
              "--chunks", str(chunks_path),
              "--model", args.embed_model,
              "--mode", "replace", "--json"], log)
        step([PY, str(THIS_DIR / "scip_runner.py"),
              "--task-dir", str(task_dir),
              "--worktree", str(task_dir / "code"), "--json"], log)
    elif prior_index_head == head_oid:
        log.info("--- Phase 3: prior index matches head_oid; skipping reindex ---")
    elif changed_files:
        log.info("--- Phase 3: INCREMENTAL re-index (%d files) ---", len(changed_files))
        # Write the changed-files list to a tmp file.
        files_list = code_index_dir / "changed-files.txt"
        files_list.write_text("\n".join(changed_files), encoding="utf-8")
        # Chunk only those files, output to a delta jsonl.
        delta_chunks = code_index_dir / "chunks-delta.jsonl"
        step([PY, str(THIS_DIR / "chunker.py"),
              "--worktree", str(task_dir / "code"),
              "--files-list", str(files_list),
              "--out", str(delta_chunks)], log)
        # Embed in incremental mode (delete chunks for these files, then add new).
        step([PY, str(THIS_DIR / "embedder.py"),
              "--task-dir", str(task_dir),
              "--chunks", str(delta_chunks),
              "--model", args.embed_model,
              "--mode", "incremental",
              "--replaced-files", str(files_list),
              "--json"], log)
        # SCIP: re-run only for languages whose files changed.
        langs = _languages_for(changed_files)
        if langs:
            step([PY, str(THIS_DIR / "scip_runner.py"),
                  "--task-dir", str(task_dir),
                  "--worktree", str(task_dir / "code"),
                  "--langs", ",".join(sorted(langs)), "--json"], log)
        else:
            log.info("no SCIP-supported languages in the changed-files set; skipping SCIP")
    else:
        log.info("--- Phase 3: head_oid changed but no resolvable file delta — full re-index ---")
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        step([PY, str(THIS_DIR / "chunker.py"),
              "--worktree", str(task_dir / "code"),
              "--out", str(chunks_path)], log)
        step([PY, str(THIS_DIR / "embedder.py"),
              "--task-dir", str(task_dir),
              "--chunks", str(chunks_path),
              "--model", args.embed_model,
              "--mode", "replace", "--json"], log)
        step([PY, str(THIS_DIR / "scip_runner.py"),
              "--task-dir", str(task_dir),
              "--worktree", str(task_dir / "code"), "--json"], log)

    step([PY, str(THIS_DIR / "query_index.py"),
          "--task-dir", str(task_dir), "--health", "--json"], log)
    mark_phase(task_dir, "3_index", "done",
               head_oid_at_index=head_oid,
               incremental=bool(has_prior_index and changed_files),
               files_changed=len(changed_files))

    # ---------- Phase 4a: precis ----------
    log.info("--- Phase 4a: build precis.md ---")
    precis = build_precis(task_dir, args.top_k_context, args.scope)
    (task_dir / "precis.md").write_text(precis, encoding="utf-8")

    # ---------- Hand-off ----------
    log.info("Orchestrator prepared all inputs.")
    # The orchestrator surfaces user-flag intent here so the parent agent
    # knows which posting path to take after generating findings.json.
    triage_mode = "interactive" if args.interactive else "auto"
    if args.no_triage:
        triage_mode = "auto"
    retrieval_flags = {
        "hybrid": not args.no_hybrid and bool(get_cfg("retrieval.hybrid", default=True)),
        "rerank_enabled": not args.no_reranker and bool(get_cfg("reranker.enabled", default=True)),
        "embed_model": args.embed_model,
        "detailed": bool(args.detailed),
    }
    next_steps = [
        f"agent: walk {task_dir / 'docs' / 'index.json'} — for each pending_mcp entry, fetch via the right MCP and write to its `path`.",
        f"agent: read {task_dir / 'precis.md'} + SKILL.md + finding.template.json; produce findings.json (multi-dimension).",
    ]
    if retrieval_flags["rerank_enabled"]:
        next_steps.append(
            "agent (optional): if you've authored queries.json5, run "
            f"`python3 scripts/rerank.py --task-dir {task_dir} --build-queue --queries <q.json5> --out {task_dir}/rerank-queue.jsonl`, "
            f"score via your harness, then `--apply-scores ... --queue ... --out {task_dir}/rerank-final.jsonl`."
        )
    next_steps.append(f"python3 scripts/comment_resolver.py --task-dir {task_dir} --json")
    if triage_mode == "interactive":
        next_steps += [
            f"python3 scripts/triage.py --task-dir {task_dir} --init --default-state pending",
            "agent: walk pending findings via AskUserQuestion; --mark accept|reject|edit; iterate edits with --rewrite + --mark accept.",
            f"python3 scripts/triage.py --task-dir {task_dir} --finalize",
        ]
    else:
        next_steps.append(
            f"python3 scripts/triage.py --task-dir {task_dir} --init --default-state accept "
            f"&& python3 scripts/triage.py --task-dir {task_dir} --finalize"
        )
    next_steps += [
        f"python3 scripts/post_comments.py --task-dir {task_dir} --confirmed yes --json   # gated; --no for plan-only",
        f"python3 scripts/report.py --task-dir {task_dir}",
    ]
    summary = {
        "task_dir": str(task_dir),
        "pr_url": args.url,
        "host": host, "owner": owner, "repo": repo, "pr_number": n,
        "head_oid": head_oid,
        "worktree": str(task_dir / "code"),
        "precis": str(task_dir / "precis.md"),
        "finding_template": str(Path(__file__).parent.parent / "finding.template.json"),
        "skill_md": str(Path(__file__).parent.parent / "SKILL.md"),
        "docs_index": str(task_dir / "docs" / "index.json"),
        "incremental_reindex": bool(has_prior_index and changed_files),
        "files_changed_since_last_index": len(changed_files),
        "retrieval": retrieval_flags,
        "triage_mode": triage_mode,
        "next_steps": next_steps,
    }
    print(json.dumps(summary, indent=2))
    return 0


# Lang detection (matches scip_runner.py LANG_DETECT_GLOBS)
_EXT_TO_LANG = {
    ".ts": "ts", ".tsx": "ts",
    ".py": "py",
    ".go": "go",
    ".java": "java",
}


def _languages_for(files: list[str]) -> set[str]:
    out: set[str] = set()
    for f in files:
        ext = Path(f).suffix.lower()
        if ext in _EXT_TO_LANG:
            out.add(_EXT_TO_LANG[ext])
    return out


def build_precis(task_dir: Path, top_k: int, scope: str) -> str:
    """Build a markdown precis the model reads. Has changed-files + index-context preloaded."""
    pr = read_json(task_dir / "pr.json")
    diff_path = task_dir / "diff.patch"
    diff_text = diff_path.read_text(encoding="utf-8", errors="replace") if diff_path.exists() else ""

    comments_blob = read_json(task_dir / "pr-comments.json") if (task_dir / "pr-comments.json").exists() else {}

    meta_path = task_dir / "code-index" / "meta.json"
    meta = read_json(meta_path) if meta_path.exists() else {}
    scip_meta_path = task_dir / "code-index" / "meta-scip.json"
    scip = read_json(scip_meta_path) if scip_meta_path.exists() else None
    docs_idx_path = task_dir / "docs" / "index.json"
    docs_idx = read_json(docs_idx_path) if docs_idx_path.exists() else {"results": []}

    # Changed files (best-effort: parse diff headers).
    changed_files: list[str] = []
    for line in diff_text.splitlines():
        if line.startswith("+++ ") and not line.endswith("/dev/null"):
            p = line[4:].strip()
            if p.startswith("b/"):
                p = p[2:]
            if p and p not in changed_files:
                changed_files.append(p)

    # Per-file chunk context.
    file_contexts = []
    for f in changed_files[:30]:
        cp = run([sys.executable, str(THIS_DIR / "query_index.py"),
                  "--task-dir", str(task_dir),
                  "--changed-file", f, "--json"], check=False)
        try:
            data = json.loads(cp.stdout) if cp.stdout else {}
        except json.JSONDecodeError:
            data = {}
        file_contexts.append({"file": f, "chunks": data.get("chunks", [])[:6]})

    # Feature flags in diff.
    cp = run([sys.executable, str(THIS_DIR / "query_index.py"),
              "--task-dir", str(task_dir), "--feature-flags-in-diff", "--json"], check=False)
    try:
        flags = json.loads(cp.stdout).get("flags", []) if cp.stdout else []
    except json.JSONDecodeError:
        flags = []

    # Existing comments digest (truncated bodies).
    threads = []
    if pr.get("host") == "github":
        for c in comments_blob.get("review_comments", [])[:50]:
            threads.append({
                "id": c.get("id"),
                "path": c.get("path"),
                "line": c.get("line"),
                "user": (c.get("user") or {}).get("login"),
                "body": (c.get("body") or "")[:240],
            })
    elif pr.get("host") == "bitbucket":
        for c in comments_blob.get("comments", [])[:50]:
            threads.append({
                "id": c.get("id"),
                "path": (c.get("inline") or {}).get("path"),
                "line": (c.get("inline") or {}).get("to") or (c.get("inline") or {}).get("from"),
                "user": (c.get("user") or {}).get("display_name"),
                "body": ((c.get("content") or {}).get("raw") or "")[:240],
            })

    lines = [
        f"# precis for {pr.get('host')}:{pr.get('owner')}/{pr.get('repo')}#{pr.get('pr_number')}",
        "",
        "## PR",
        f"- title: {pr.get('title')}",
        f"- url: {pr.get('url')}",
        f"- head: {pr.get('head_oid')}  base: {pr.get('base_oid')}",
        f"- changed files: {len(changed_files)}",
        f"- scope: {scope}",
        "",
        "## PR body (truncated)",
        "```",
        (pr.get("body") or "")[:2000],
        "```",
        "",
        "## Index status",
        f"- chunks: {meta.get('rows')} | model: {meta.get('model')} | dim: {meta.get('dim')}",
        f"- scip: {json.dumps(scip) if scip else 'none'}",
        "",
        "## Supporting docs (linked from PR / comments)",
    ]
    for r in docs_idx.get("results", []):
        marker = r.get("status", "?")
        line = f"- [{marker}] {r.get('adapter')}:{r.get('id')} — {r.get('url')}"
        if r.get("path"):
            line += f"  → `{r['path']}`"
        if r.get("mcp_tool"):
            line += f"  · mcp_tool=`{r['mcp_tool']}`"
        lines.append(line)
    lines += ["",
              "**Before reviewing:** for every `pending_mcp` entry above, call the named MCP tool and write the result as markdown to the listed `path`. If the MCP is unreachable, mark `[mcp: skipped]` in the report.",
              ""]

    lines += [f"## Existing comment threads ({len(threads)})"]
    for t in threads:
        lines.append(f"- id={t['id']} {t.get('path')}:{t.get('line')} by @{t.get('user')}")
        lines.append(f"    > {t.get('body', '')[:200]!s}")
    lines += ["", "## Changed files (with top chunks)"]
    for fc in file_contexts:
        lines.append(f"### {fc['file']}")
        for c in fc["chunks"]:
            lines.append(f"- L{c.get('line_start')}-{c.get('line_end')}  symbol={c.get('parent_symbol')}  kind={c.get('kind')}")
    if flags:
        lines += ["", "## Feature flags referenced in the diff"]
        for f in flags:
            lines.append(f"- {f['name']} ({len(f.get('call_sites', []))} call sites)")
            for cs in f.get("call_sites", [])[:5]:
                lines.append(f"    - {cs.get('file')}:{cs.get('line')}")

    lines += ["",
              "## How to use this file",
              "1. Walk `docs/index.json` and fetch all `pending_mcp` entries first (Atlassian / Drive MCP).",
              "2. Read SKILL.md (system prompt). Use Read/Grep/Glob against the worktree at `code/`.",
              "3. Run `python3 scripts/query_index.py --task-dir <dir> --query <text> --json` for retrieval.",
              "4. Run **every applicable dimension** — correctness, security, tests, performance, observability, feature-flow, api, docs, concurrency. Don't shortcut to one.",
              "5. Emit one JSON matching `finding.template.json` to `findings.json`. Nothing else."]

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
