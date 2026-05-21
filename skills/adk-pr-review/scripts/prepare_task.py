#!/usr/bin/env python3
"""prepare_task.py — orchestrator for /adk-pr-review.

Two invocation modes:

  1. URL mode:   `python3 prepare_task.py <pr-url> [...flags]`
     Reviews the named PR. If the PR is found in the queue
     (~/.agents-devkit/config/pr-queue.json5) the row's `taken_at` is
     atomically claimed for the duration of this run, and the row's
     `slack` + `supporting_docs` are merged into the review context.

  2. Queue mode: `python3 prepare_task.py [--queue <path>] [...flags]`
     With no URL, picks the next eligible row from the queue (oldest by
     last_checked_at, nulls first; status != merged; `taken_at` null or
     older than the 30-min auto-expire). Atomically claims it and reviews
     it. Another `/adk-pr-review` running in a parallel terminal picks
     a different row.

Behavior on EVERY invocation (whether first run or N-th):

  Phase 0 (prereq)     — always runs.
  Phase 2a (fetch PR)  — always runs. Pulls fresh PR metadata + diff. Records the
                         new head_sha.
  Phase 1 (worktree)   — always runs. `git fetch --all --prune` in the clone,
                         then `git worktree add --detach <task>/code <head_sha>`
                         (or `git checkout --detach <head_sha>` if the worktree
                         already exists). Serialized via the global lock.
  Phase 2b (docs)      — always runs. Re-scans PR body + comments for doc URLs;
                         writes docs/index.json with pending-MCP markers so the
                         agent can fetch Confluence / Jira / GDoc via MCPs.
  Phase 3 (index)      — runs if head_sha changed OR --rebuild. When head_sha
                         changed AND prior state exists: INCREMENTAL re-index
                         (only the files that differ between old and new
                         head_sha). When no prior state OR --rebuild: full
                         re-index.
  Phase 4a (precis)    — always runs (regenerates the precis the agent reads).

What this script does NOT do: invoke `claude -p`. The calling agent does that
after reading precis.md + SKILL.md + finding.template.json, then calls back into
comment_resolver.py + post_comments.py + report.py.

The queue release (set status, clear taken_at, update slack reaction) happens
in report.py at the tail of the review.

Usage:
  python3 prepare_task.py [<pr-url>] [--auto] [--rebuild] [--no-post]
                                   [--no-resolve-existing]
                                   [--embed-model nomic-embed-text]
                                   [--scope all|security|correctness|tests]
                                   [--queue <path>]
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

# CLI helpers live under skills/adk-cli/scripts/. Add to sys.path so we can
# import queue_io for the queue-acquire / URL-lookup flow.
ADK_CLI_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "adk-cli" / "scripts"
sys.path.insert(0, str(ADK_CLI_SCRIPTS))
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH, acquire_next_row, find_row, update_pr_entry,
    TAKEN_LOCK_MAX_AGE_SECONDS, STATUS_IN_REVIEW,
)

# Decision-log helper — improvement #4 (decisions.jsonl was getting zero new
# entries per session). Import the importable Python helper from scripts/.
ADK_SCRIPTS = Path(__file__).resolve().parent.parent.parent.parent / "scripts"
sys.path.insert(0, str(ADK_SCRIPTS))
try:
    from decision_logger import append_decision  # noqa: E402
except Exception:
    def append_decision(*_a, **_kw):  # type: ignore[misc]
        pass  # fail-open: never block a review run on the log

# `.resolve()` follows the install-time symlink (~/.claude/skills/... or
# ~/.cursor/rules/...) back to the real file inside the agents-devkit repo.
# Without it, THIS_DIR.parent.parent.parent walks up the symlinked tree —
# e.g. ~/.claude/scripts/lib/code_index/ — which does not exist.
THIS_DIR = Path(__file__).resolve().parent
# Phase 2: indexer scripts moved to scripts/lib/code_index/. Shims remain at
# the old location but new callers should point at the lib directly to skip
# the runpy hop.
CODE_INDEX_LIB = THIS_DIR.parent.parent.parent / "scripts" / "lib" / "code_index"
PY = sys.executable

# Phase 3: optional seeding from the repo-level base index. The lib path
# lookup must succeed before we import.
sys.path.insert(0, str(CODE_INDEX_LIB))
try:
    from base_index import (  # noqa: E402
        get_default_branch, is_fresh, pick_base_index, seed_copy,
    )
    _BASE_INDEX_AVAILABLE = True
except Exception:
    _BASE_INDEX_AVAILABLE = False


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


def _read_manifest_model(pr_url: str | None) -> str | None:
    """Return the embed-model recorded in an existing index manifest for
    this PR's task folder, or None if no prior index exists.

    Used by the model resolver so a re-run of `adk pr-task prepare URL`
    (no flags) doesn't drift away from the model the index was built with.
    """
    if not pr_url:
        return None
    try:
        parsed = parse_pr_url(pr_url)
    except Exception:
        return None
    manifest_path = task_dir_for(parsed["repo"], parsed["pr_number"]) / "code-index" / "meta.json"
    if not manifest_path.exists():
        return None
    try:
        return json.loads(manifest_path.read_text(encoding="utf-8")).get("model")
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url", nargs="?", default=None,
                    help="PR URL (omit to acquire the next eligible row from the queue)")
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH),
                    help=f"queue path (default: {DEFAULT_QUEUE_PATH})")
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
    ap.add_argument("--no-base-seed", action="store_true",
                    help="skip seeding from the repo-level base index; index the PR worktree from scratch.")
    ap.add_argument("--max-base-staleness", type=int, default=None,
                    help="reject the base index if older than N days (default: from config base_index.max_staleness_days, fallback 7).")
    ap.add_argument("--use-mcp", action="store_true", default=True,
                    help="emit posting-plan.json for the host agent to dispatch via MCP "
                         "(default). Add --no-use-mcp for the direct-API fallback path "
                         "(headless CI runs).")
    ap.add_argument("--no-use-mcp", dest="use_mcp", action="store_false",
                    help="disable MCP-first posting; post_comments.py uses direct REST API.")
    ap.add_argument("--no-slack-summary", action="store_true",
                    help="suppress the Slack summary reply that would otherwise post to the "
                         "queue row's slack thread.")
    ap.add_argument("--prepare-only", action="store_true",
                    help="run phases 0-1 of the pipeline (clone + worktree + index + "
                         "supporting-docs + precis) and exit BEFORE the agent reviews. "
                         "Does NOT claim the queue's `taken_at` lock and does NOT invoke "
                         "the agent. Used by `adk pr-task prepare` and "
                         "`adk pr-queue update --full` to pre-warm cached state so a "
                         "later interactive review skips re-indexing. This flag never "
                         "produces a review — Phase 2 (you) is exactly that step.")
    ap.add_argument("--merge-if-approved", action="store_true",
                    help="Phase 6 disposition: if the final recommendation is `approve`, "
                         "print `MERGEABLE — click to merge: <pr-url>` so the human can "
                         "click. Constitution §I.3 forbids the script from merging "
                         "itself, regardless of this flag.")
    args = ap.parse_args()

    # Did the user explicitly choose a model? We need this BEFORE the manifest
    # peek so we know whether to override an existing index's model.
    user_chose_model = bool(args.embed_model) or bool(args.detailed)

    # Stage-1 model resolution from CLI/config (the "intent" model). This is
    # what gets used for a fresh index, OR what overrides the manifest when
    # --rebuild + explicit flag is passed.
    if args.embed_model:
        embed_model = args.embed_model
    elif args.detailed:
        embed_model = get_cfg("embed.detailed_model", default="bge-m3")
    else:
        embed_model = (
            os.environ.get("ADK_PR_REVIEW_EMBED_MODEL")
            or get_cfg("embed.default_model", default="nomic-embed-text")
        )

    # Stage-2: peek at the existing index manifest (if any). If the user
    # didn't pass a model flag and didn't pass --rebuild, honor whatever the
    # index was built with. This preserves the incremental contract: a re-run
    # of `adk pr-task prepare URL` (no flags) after a previous `--detailed`
    # run keeps using bge-m3 instead of erroring out with model-mismatch.
    ensure_dirs()
    queue_path = Path(args.queue).expanduser()
    manifest_model = _read_manifest_model(args.url)
    if manifest_model and not user_chose_model and not args.rebuild:
        if embed_model != manifest_model:
            sys.stderr.write(
                f"[run_review] embed_model: honoring existing index manifest "
                f"({manifest_model}). Config default was {embed_model}. "
                f"Pass --rebuild to switch back to the default.\n"
            )
        embed_model = manifest_model
    elif manifest_model and user_chose_model and not args.rebuild \
            and manifest_model != embed_model:
        # User wants a different model but didn't ask for a rebuild. The
        # embedder would die anyway with a mismatch — bail early with a
        # clearer message.
        die(
            f"embed_model mismatch: existing index uses {manifest_model}, "
            f"you requested {embed_model}. Pass --rebuild to reindex from "
            f"scratch with the new model."
        )
    args.embed_model = embed_model  # downstream code reads args.embed_model

    # Resolve URL: either explicit (URL mode) or by claiming the next eligible
    # queue row (queue mode). In both cases queue_row may be None — when the
    # PR isn't tracked in the queue OR the queue is empty in queue mode.
    queue_row: dict | None = None
    if args.url is None:
        if args.prepare_only:
            die("--prepare-only requires an explicit URL (no queue-claim semantics).")
        # Queue mode: route through `get_next_eligible` so we validate the
        # candidate against the origin API and auto-drop merged/closed rows
        # before they can be claimed for review.
        try:
            from pr_queue import get_next_eligible  # type: ignore[import-not-found]
            queue_row = get_next_eligible(queue_path, validate=True)
        except Exception:
            # If the CLI module can't be imported for any reason, fall back
            # to the in-memory primitive so the skill still functions.
            queue_row = acquire_next_row(queue_path)
        if queue_row is None:
            print(json.dumps({
                "action": "queue_empty",
                "queue": str(queue_path),
                "message": "no eligible rows in the queue. Run `adk pr-scan` to refresh, or pass a PR URL.",
            }, indent=2))
            return 0
        args.url = queue_row["pr_url"]
    else:
        # URL mode — check the queue for a matching row and claim it (so a
        # parallel queue-mode terminal won't pick the same PR while we review).
        existing = find_row(queue_path, args.url)
        if existing is not None:
            from datetime import datetime, timezone
            taken_at = existing.get("taken_at")
            if taken_at:
                try:
                    iso = taken_at[:-1] + "+00:00" if taken_at.endswith("Z") else taken_at
                    ts = datetime.fromisoformat(iso)
                    age = (datetime.now(tz=timezone.utc) - ts).total_seconds()
                    if age < TAKEN_LOCK_MAX_AGE_SECONDS:
                        if args.prepare_only:
                            # Pre-warm should never wrestle with an active reviewer.
                            # Surface and bail with rc=0 so `--all` can keep going.
                            print(json.dumps({
                                "action": "skipped",
                                "pr_url": args.url,
                                "reason": "locked by another reviewer",
                                "taken_at": taken_at,
                            }, indent=2))
                            return 0
                        die(
                            f"queue row for {args.url} is locked by another reviewer "
                            f"(taken_at={taken_at}, {int(TAKEN_LOCK_MAX_AGE_SECONDS - age)}s remaining). "
                            f"Wait or `adk pr-queue release {args.url}` to override."
                        )
                except ValueError:
                    pass
            # Prepare-only mode does NOT claim the queue lock — its job is to
            # pre-warm cached state, not to begin a review session. A real
            # reviewer must still be able to claim the row immediately after.
            if not args.prepare_only:
                from queue_io import _now_iso  # type: ignore[attr-defined]
                update_pr_entry(queue_path, args.url, {"taken_at": _now_iso(),
                                                        "status": STATUS_IN_REVIEW})
            queue_row = find_row(queue_path, args.url)

    parsed = parse_pr_url(args.url)
    host, owner, repo, n = parsed["host"], parsed["owner"], parsed["repo"], parsed["pr_number"]
    task_dir = task_dir_for(repo, n)
    task_dir.mkdir(parents=True, exist_ok=True)
    log = get_logger("orchestrator", task_dir)
    log.info("=== /adk-pr-review %s ===", args.url)
    if queue_row is not None:
        log.info("queue context: pr_url=%s, slack=%s, supporting_docs=%d",
                 queue_row.get("pr_url"),
                 bool(queue_row.get("slack")),
                 len(queue_row.get("supporting_docs") or []))
        # Write queue-context.json so report.py can pick up slack-info + queue_path
        # without re-parsing the queue at the end.
        write_json(task_dir / "queue-context.json", {
            "queue_path": str(queue_path),
            "pr_url": queue_row.get("pr_url"),
            "slack": queue_row.get("slack"),
            "supporting_docs": queue_row.get("supporting_docs") or [],
        })
        # Forced supporting docs — fetch_supporting_docs.py picks these up.
        forced = queue_row.get("supporting_docs") or []
        if forced:
            write_json(task_dir / "forced-supporting-docs.json", forced)

    # Per-PR lock — prevents two simultaneous reviews of the same PR. Sits
    # underneath the queue-row `taken_at` lock as a low-level safety net for
    # the corner case where two terminals somehow both think they own this PR.
    # Fail fast by default (use --wait to queue). Parallel reviews of DIFFERENT
    # PRs do not contend on this lock.
    pr_lock_ctx = None
    try:
        pr_lock_ctx = try_file_lock(pr_lock_for(repo, n), wait=args.wait, timeout_s=0.0)
        pr_lock_ctx.__enter__()
    except LockHeldError as e:
        # Release the queue-row claim so it doesn't sit locked for 30 min.
        if queue_row is not None:
            try:
                update_pr_entry(queue_path, args.url, {"taken_at": None})
            except Exception:
                pass
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
    prior_index_head = state.get("phases", {}).get("3_index", {}).get("head_sha_at_index")
    if args.rebuild:
        log.info("--rebuild: prior index will be discarded")
        prior_index_head = None

    # ---------- Phase 0: prereqs ----------
    log.info("--- Phase 0: prereq ---")
    cp = run([PY, str(CODE_INDEX_LIB / "ensure_ollama.py"), "--model", args.embed_model, "--json"], check=False)
    if cp.returncode != 0:
        sys.stderr.write(cp.stdout + cp.stderr)
        die("ollama not ready — see hint above")
    if host == "github" and not which("gh"):
        die("gh CLI required for GitHub PRs. brew install gh.")
    mark_phase(task_dir, "0_prereq", "done",
               url=args.url, host=host, owner=owner, repo=repo, pr_number=n,
               embed_model=args.embed_model)
    append_decision(
        skill="adk-pr-review", fork_id="embed_model", fork_type="inferred",
        default_offered=args.embed_model,
        evidence="--detailed=%s, --embed-model=%s" % (args.detailed, args.embed_model),
        repo=repo, task_slug=f"{repo}_pr-{n}",
    )

    # ---------- Phase 2a: fetch PR (always — gets fresh head_sha) ----------
    log.info("--- Phase 2a: fetch PR (always; gets fresh head_sha) ---")
    step([PY, str(THIS_DIR / "fetch_pr.py"),
          "--host", host, "--owner", owner, "--repo", repo,
          "--pr-number", str(n), "--task-dir", str(task_dir), "--json"], log)
    pr = read_json(task_dir / "pr.json")
    head_sha = pr.get("head_sha")
    if not head_sha:
        die("fetch_pr.py did not populate head_sha")
    log.info("PR head_sha: %s (prior indexed: %s)", head_sha[:12], (prior_index_head or "<none>")[:12])

    # ---------- Phase 1: clone + worktree (ALWAYS — pulls latest) ----------
    log.info("--- Phase 1a: ensure repo clone (always fetch --all --prune) ---")
    step([PY, str(THIS_DIR / "ensure_repo_clone.py"),
          "--host", host, "--owner", owner, "--repo", repo, "--json"], log)
    log.info("--- Phase 1b: create/update worktree at %s (serialized) ---", head_sha[:12])
    step([PY, str(THIS_DIR / "create_worktree.py"),
          "--repo", repo, "--pr-number", str(n), "--head-sha", head_sha,
          "--json"] + (["--rebuild"] if args.rebuild else []), log)
    mark_phase(task_dir, "1_worktree", "done",
               worktree_path=str(task_dir / "code"), head_sha=head_sha)

    # ---------- Phase 2b: supporting docs scan (always) ----------
    log.info("--- Phase 2b: scan supporting docs ---")
    step([PY, str(THIS_DIR / "fetch_supporting_docs.py"),
          "--task-dir", str(task_dir), "--json"], log)
    mark_phase(task_dir, "2_fetch", "done", head_sha=head_sha)

    # ---------- Phase 3: index (full or incremental) ----------
    code_index_dir = task_dir / "code-index"
    chunks_path = code_index_dir / "chunks.jsonl"
    has_prior_index = (code_index_dir / "meta.json").exists() and prior_index_head is not None
    changed_files: list[str] = []
    seed_info: dict | None = None
    if has_prior_index and prior_index_head != head_sha:
        repo_clone = repo_clone_for(repo)
        changed_files = diff_changed_files(repo_clone, prior_index_head, head_sha, log)
        log.info("incremental re-index: %d files changed between %s..%s",
                 len(changed_files), prior_index_head[:12], head_sha[:12])

    # NEW: when there's no prior PR-task-local index, consider seeding from a
    # repo-level base index (built by `adk repo add|update`). This converts
    # the cold 9-minute full reindex into a warm overlay: copy the base table
    # dir, then run the embedder in incremental mode for the files that
    # changed between the base's indexed SHA and the PR's head_sha.
    #
    # Branch selection: the PR's target branch (`baseRefName` from pr.json) is
    # preferred — if `develop` is indexed and the PR targets `develop`, the
    # overlay is just (develop_indexed_sha → pr_head). When the target branch
    # isn't indexed we fall back to the repo's default branch; that still
    # beats a cold reindex but the overlay is larger.
    target_branch = (pr.get("baseRefName") or "").strip()
    if not has_prior_index and not args.rebuild and not args.no_base_seed and _BASE_INDEX_AVAILABLE:
        base = pick_base_index(repo, target_branch=target_branch or None)
        if base is None:
            log.info("base index: not built for %s (run `adk repo add <url>` or "
                     "`adk repo branch add %s --branch %s` to enable warm seeding)",
                     repo, repo, target_branch or "<default>")
        elif base.embed_model != args.embed_model:
            log.info("base index: skipping seed — model mismatch (base=%s, run=%s)",
                     base.embed_model, args.embed_model)
        else:
            # Surface the branch decision before we commit to seeding. If the
            # PR targets X but only Y is indexed, the reviewer needs to know
            # the overlay will include X-only commits.
            if target_branch and base.branch != target_branch:
                log.info("base index: target branch %s not indexed; falling back to %s "
                         "(overlay will include commits that landed on %s since base)",
                         target_branch, base.branch or "<default>", target_branch)
            else:
                log.info("base index: matched target branch %s", base.branch or "<default>")
            if not is_fresh(base, max_staleness_days=args.max_base_staleness):
                log.info("base index: %s @ %.1f days old (cap=%s) — seeding anyway "
                         "and overlaying diff vs base SHA %s",
                         base.branch or "<default>", base.age_days,
                         args.max_base_staleness or "config", base.indexed_sha[:12])
            else:
                log.info("base index: %s fresh (%.1f days old) — seeding from %s",
                         base.branch or "<default>", base.age_days,
                         base.indexed_sha[:12])
            seed_info = seed_copy(base, task_dir, log=log)
            seed_info["seeded_from_branch"] = base.branch
            seed_info["seeded_from_branch_slug"] = base.slug

    if seed_info is not None:
        # We seeded the base; overlay only the files that differ between
        # base.indexed_sha and the PR's head_sha.
        repo_clone = repo_clone_for(repo)
        overlay_files = diff_changed_files(repo_clone, seed_info["seeded_from_sha"], head_sha, log)
        log.info("--- Phase 3: SEEDED from base @ %s; overlaying %d files vs head %s ---",
                 seed_info["seeded_from_sha"][:12], len(overlay_files), head_sha[:12])
        if overlay_files:
            files_list = code_index_dir / "overlay-files.txt"
            files_list.write_text("\n".join(overlay_files), encoding="utf-8")
            delta_chunks = code_index_dir / "chunks-overlay.jsonl"
            step([PY, str(CODE_INDEX_LIB / "chunker.py"),
                  "--worktree", str(task_dir / "code"),
                  "--files-list", str(files_list),
                  "--out", str(delta_chunks)], log)
            step([PY, str(CODE_INDEX_LIB / "embedder.py"),
                  "--task-dir", str(task_dir),
                  "--chunks", str(delta_chunks),
                  "--model", args.embed_model,
                  "--mode", "incremental",
                  "--replaced-files", str(files_list),
                  "--json"], log)
            langs = _languages_for(overlay_files)
            if langs:
                step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
                      "--task-dir", str(task_dir),
                      "--worktree", str(task_dir / "code"),
                      "--langs", ",".join(sorted(langs)), "--json"], log)
            else:
                log.info("overlay: no SCIP-supported languages in delta; skipping SCIP")
        else:
            log.info("overlay: 0 files changed since base — no chunker/embedder work needed")
        # State write goes here (BEFORE health check) so a transient health
        # failure doesn't orphan a usable index. Improvement #9 / #11.
        _base_now = pick_base_index(repo, target_branch=seed_info.get("seeded_from_branch"))
        mark_phase(task_dir, "3_index", "done",
                   head_sha_at_index=head_sha,
                   incremental=True,
                   seeded_from_base=True,
                   base_oid=seed_info["seeded_from_sha"],
                   base_branch=seed_info.get("seeded_from_branch"),
                   base_branch_slug=seed_info.get("seeded_from_branch_slug"),
                   target_branch=target_branch or None,
                   target_branch_matched=bool(
                       target_branch and seed_info.get("seeded_from_branch") == target_branch
                   ),
                   base_age_days=round(_base_now.age_days, 2) if _base_now else None,
                   files_changed=len(overlay_files),
                   embed_model=seed_info["embed_model"])
        append_decision(
            skill="adk-pr-review", fork_id="index_path", fork_type="inferred",
            default_offered="seed-from-base-and-overlay",
            evidence=(f"base={seed_info.get('seeded_from_branch') or '<default>'} "
                      f"@ {seed_info['seeded_from_sha'][:12]} "
                      f"target={target_branch or '<unknown>'} "
                      f"overlay={len(overlay_files)} files"),
            repo=repo, task_slug=f"{repo}_pr-{n}",
        )
    elif not has_prior_index:
        log.info("--- Phase 3: FULL index (no prior state, no base seed) ---")
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        step([PY, str(CODE_INDEX_LIB / "chunker.py"),
              "--worktree", str(task_dir / "code"),
              "--out", str(chunks_path)], log)
        step([PY, str(CODE_INDEX_LIB / "embedder.py"),
              "--task-dir", str(task_dir),
              "--chunks", str(chunks_path),
              "--model", args.embed_model,
              "--mode", "replace", "--json"], log)
        step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
              "--task-dir", str(task_dir),
              "--worktree", str(task_dir / "code"), "--json"], log)
        mark_phase(task_dir, "3_index", "done",
                   head_sha_at_index=head_sha, incremental=False, seeded_from_base=False)
    elif prior_index_head == head_sha:
        log.info("--- Phase 3: prior index matches head_sha; skipping reindex ---")
        mark_phase(task_dir, "3_index", "done",
                   head_sha_at_index=head_sha, incremental=False, skipped=True)
    elif changed_files:
        log.info("--- Phase 3: INCREMENTAL re-index (%d files) ---", len(changed_files))
        files_list = code_index_dir / "changed-files.txt"
        files_list.write_text("\n".join(changed_files), encoding="utf-8")
        delta_chunks = code_index_dir / "chunks-delta.jsonl"
        step([PY, str(CODE_INDEX_LIB / "chunker.py"),
              "--worktree", str(task_dir / "code"),
              "--files-list", str(files_list),
              "--out", str(delta_chunks)], log)
        step([PY, str(CODE_INDEX_LIB / "embedder.py"),
              "--task-dir", str(task_dir),
              "--chunks", str(delta_chunks),
              "--model", args.embed_model,
              "--mode", "incremental",
              "--replaced-files", str(files_list),
              "--json"], log)
        langs = _languages_for(changed_files)
        if langs:
            step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
                  "--task-dir", str(task_dir),
                  "--worktree", str(task_dir / "code"),
                  "--langs", ",".join(sorted(langs)), "--json"], log)
        else:
            log.info("no SCIP-supported languages in the changed-files set; skipping SCIP")
        mark_phase(task_dir, "3_index", "done",
                   head_sha_at_index=head_sha, incremental=True,
                   files_changed=len(changed_files), seeded_from_base=False)
    else:
        log.info("--- Phase 3: head_sha changed but no resolvable file delta — full re-index ---")
        chunks_path.parent.mkdir(parents=True, exist_ok=True)
        step([PY, str(CODE_INDEX_LIB / "chunker.py"),
              "--worktree", str(task_dir / "code"),
              "--out", str(chunks_path)], log)
        step([PY, str(CODE_INDEX_LIB / "embedder.py"),
              "--task-dir", str(task_dir),
              "--chunks", str(chunks_path),
              "--model", args.embed_model,
              "--mode", "replace", "--json"], log)
        step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
              "--task-dir", str(task_dir),
              "--worktree", str(task_dir / "code"), "--json"], log)
        mark_phase(task_dir, "3_index", "done",
                   head_sha_at_index=head_sha, incremental=False,
                   seeded_from_base=False, reason="head_sha moved but no resolvable diff")

    # Health check AFTER state write — a transient health-check failure no
    # longer orphans the index. The earlier mark_phase call captured what
    # actually landed on disk.
    step([PY, str(CODE_INDEX_LIB / "query_index.py"),
          "--task-dir", str(task_dir), "--health", "--json"], log)

    # ---------- Phase 4a: precis ----------
    log.info("--- Phase 4a: build precis.md ---")
    precis = build_precis(task_dir, args.top_k_context, args.scope)
    (task_dir / "precis.md").write_text(precis, encoding="utf-8")

    # ---------- Prepare-only exit (no agent handoff) ----------
    if args.prepare_only:
        log.info("--prepare-only: phases 0-4a complete, skipping agent handoff")
        print(json.dumps({
            "action": "prepared",
            "pr_url": args.url,
            "task_dir": str(task_dir),
            "head_sha": head_sha,
            "worktree": str(task_dir / "code"),
            "precis": str(task_dir / "precis.md"),
        }, indent=2))
        return 0

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
        f"agent: read {task_dir / 'precis.md'} + SKILL.md + finding.template.json; produce findings.json (multi-dimension). [Phase 2]",
        f"python3 scripts/validate_findings.py --task-dir {task_dir} --json   # Phase 3: drop drifted anchors + no-fix findings",
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
    # Default behavior is to POST in auto mode and to post-after-triage in
    # interactive mode. Pass --no-post on the orchestrator to inhibit (rehearsal
    # only). The post_comments.py default is now `--confirmed yes` so we don't
    # need to pass any flag in the happy path; --plan-only flips it off.
    #
    # `--use-mcp` makes post_comments.py emit posting-plan.json and exit
    # without touching the direct API — the host agent then dispatches each
    # step via the named mcp__adk-mcp-{github,bitbucket}__* tool per
    # references/platform-mcp.md. Falls back to direct API when --no-mcp.
    post_flag = " --plan-only" if args.no_post else ""
    use_mcp_flag = " --use-mcp" if args.use_mcp else ""
    no_slack_flag = " --no-slack-summary" if args.no_slack_summary else ""
    post_comment_hint = "   # plan-only (--no-post was set)" if args.no_post else "   # auto-post (constitution §I.4: task requires this)"
    next_steps += [
        f"python3 scripts/post_comments.py --task-dir {task_dir} --json{use_mcp_flag}{no_slack_flag}{post_flag}{post_comment_hint}",
    ]
    if args.use_mcp:
        next_steps.append(
            f"agent: read {task_dir / 'posting-plan.json'} — for each step, "
            "invoke its mcp_tool with mcp_args. NEVER call merge_pull_request / "
            "mergePullRequest. See references/platform-mcp.md."
        )
    merge_flag = " --merge-if-approved" if args.merge_if_approved else ""
    next_steps.append(f"python3 scripts/report.py --task-dir {task_dir}{merge_flag}")
    summary = {
        "task_dir": str(task_dir),
        "pr_url": args.url,
        "host": host, "owner": owner, "repo": repo, "pr_number": n,
        "head_sha": head_sha,
        "worktree": str(task_dir / "code"),
        "precis": str(task_dir / "precis.md"),
        "finding_template": str(THIS_DIR.parent / "finding.template.json"),
        "skill_md": str(THIS_DIR.parent / "SKILL.md"),
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
        cp = run([sys.executable, str(CODE_INDEX_LIB / "query_index.py"),
                  "--task-dir", str(task_dir),
                  "--changed-file", f, "--json"], check=False)
        try:
            data = json.loads(cp.stdout) if cp.stdout else {}
        except json.JSONDecodeError:
            data = {}
        file_contexts.append({"file": f, "chunks": data.get("chunks", [])[:6]})

    # Feature flags in diff.
    cp = run([sys.executable, str(CODE_INDEX_LIB / "query_index.py"),
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
        f"- head: {pr.get('head_sha')}  base: {pr.get('base_oid')}",
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
              "3. Run `python3 scripts/lib/code_index/query_index.py --task-dir <dir> --query <text> --json` for retrieval.",
              "4. Run **every applicable dimension** — correctness, security, tests, performance, observability, feature-flow, api, docs, concurrency. Don't shortcut to one.",
              "5. Emit one JSON matching `finding.template.json` to `findings.json`. Nothing else."]

    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
