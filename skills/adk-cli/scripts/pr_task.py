"""pr_task.py — `adk pr-task` subcommands.

The stable CLI surface for managing the per-PR task folder under
$ADK_DATA_HOME/skill-pr-review/<repo>_pr-<n>/. The /adk-pr-review skill calls
through this binary so it doesn't depend on internal script paths.

prepare <pr-url>     Create or refresh the task folder for one PR. Runs the
                     same Phase 0-4a prep that /adk-pr-review's orchestrator
                     would: clone fetch, worktree at the PR head, PR metadata
                     + comments + diff, supporting docs index, tree-sitter
                     chunks + ollama embeddings + (optional) SCIP, precis.md.
                     Does NOT claim the queue's `taken_at` lock and does NOT
                     run a review. Idempotent: re-running on an unchanged
                     head_sha short-circuits the index step.

info <pr-url>        JSON view of a task folder's current state: paths,
                     head_sha, last_indexed_head, whether findings.json
                     exists. Used by the skill (and by humans) to decide
                     whether the folder is ready for an interactive review.

list                 Names of every task folder under
                     $ADK_DATA_HOME/skill-pr-review/. Pair with `--paths` to
                     get the full paths instead. Powers shell completion.

Internals: prepare delegates to skills/adk-pr-review/scripts/prepare_task.py
--prepare-only. This module is a stable wrapper — the skill (and any
external caller) doesn't need to know that path.

Depth flags: `--detailed` controls the embedding/retrieval path. `--deep` is
accepted and forwarded for symmetry with `/adk-pr-review`; the parent harness
chooses the actual review model.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
SCRIPTS_ROOT = THIS_DIR.parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_ROOT))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import (  # noqa: E402
    ADK_HOME,
    RunEvent,
    die,
    emit_event,
    format_file_ref,
    format_pr_ref,
    get_logger,
    is_orchestrated,
    parse_pr_url,
    pr_review_file,
    read_state,
    status_glyph,
    task_dir_for,
)
from queue_io import (  # noqa: E402
    DEFAULT_QUEUE_PATH, STATUS_MERGED, STATUS_PENDING,
    TERMINAL_STATUSES, read_queue, find_row,
)


def _default_prepare_jobs() -> int:
    """Read `pr_sync.prepare_jobs` from adk-cli.json5.

    Returns 1 when the file/key is absent. The bound is enforced at
    `cmd_prepare`; this helper just resolves the default.
    """
    try:
        from config_io import get_adk_cli  # noqa: WPS433
        val = get_adk_cli("pr_sync", "prepare_jobs", default=None)
        if val is None:
            return 1
        return max(1, int(val))
    except Exception:
        return 1

PR_REVIEW_ROOT = ADK_HOME / "skill-pr-review"
PREPARE_TASK = ADK_PR_REVIEW_SCRIPTS / "prepare_task.py"
VALIDATE_FINDINGS = ADK_PR_REVIEW_SCRIPTS / "validate_findings.py"


def _queued_task_dirs(queue_path: Path) -> dict[str, Path]:
    """Map of `pr_url → task_dir` for every non-merged row in the queue.

    Used by `prepare --all` (iterate eligible rows) and `clean-orphans`
    (decide which folders on disk no longer have a backing queue row).
    """
    out: dict[str, Path] = {}
    queue = read_queue(queue_path)
    for e in queue.get("prs", []) or []:
        link = e.get("pr_url")
        if not link:
            continue
        # Skip rows that have reached a terminal state (merged or declined).
        # Their task folders will be reaped by `pr-queue clean` /
        # `pr-task clean-orphans` later in the sync pipeline.
        if (e.get("status") or STATUS_PENDING) in TERMINAL_STATUSES:
            continue
        try:
            p = parse_pr_url(link)
        except ValueError:
            continue
        out[link] = task_dir_for(p["repo"], p["pr_number"])
    return out


def _task_dir_for(pr_url: str) -> Path:
    p = parse_pr_url(pr_url)
    return task_dir_for(p["repo"], p["pr_number"])


# ----- prepare -------------------------------------------------------------

def _extract_trailing_json(text: str) -> dict | None:
    """Pull the last balanced `{...}` block out of `text`.

    Retained for callers that need to parse output from explicitly
    machine-readable subcommands; the default prepare path now renders a human
    terminal summary instead of a trailing JSON object.
    """
    if not text:
        return None
    end = text.rfind("}")
    if end < 0:
        return None
    depth = 0
    in_str = False
    esc = False
    start = -1
    # Walk backwards from the closing brace until brace depth returns to 0.
    for i in range(end, -1, -1):
        ch = text[i]
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "}":
            depth += 1
        elif ch == "{":
            depth -= 1
            if depth == 0:
                start = i
                break
    if start < 0:
        return None
    block = text[start:end + 1]
    try:
        obj = json.loads(block)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _extract_error_reason(stderr: str, stdout: str) -> str:
    """Produce a one-line reason from a failed subprocess output.

    `prepare_task.py` re-raises with `SystemExit(f"step failed (rc=…): <cmd>")`
    after logging a Python traceback to stderr. The previous code took
    `stderr[-400:]` which sliced mid-line — producing `"ise RuntimeError(…)"`
    (the tail of `raise`). We instead prefer, in order:

      1. the SystemExit line — the orchestrator's own framing of the failure,
      2. the last RuntimeError/Exception line in the traceback,
      3. the last non-empty stderr line,
      4. the last non-empty stdout line,
      5. "<no output>".
    """
    def _scan(text: str, prefix: str) -> str | None:
        out: str | None = None
        for line in (text or "").splitlines():
            ln = line.strip()
            if ln.startswith(prefix):
                out = ln
        return out

    err = stderr or ""
    # 1. orchestrator's framing
    for ln in reversed(err.splitlines()):
        s = ln.strip()
        if s.startswith("step failed (rc="):
            return s
    # 2. last exception line
    for prefix in ("RuntimeError:", "ValueError:", "FileNotFoundError:",
                   "PermissionError:", "TimeoutError:", "subprocess.CalledProcessError:",
                   "Exception:", "AssertionError:"):
        hit = _scan(err, prefix)
        if hit:
            return hit
    # 3. last non-empty stderr line
    for ln in reversed(err.splitlines()):
        s = ln.strip()
        if s:
            return s
    # 4. last non-empty stdout line
    for ln in reversed((stdout or "").splitlines()):
        s = ln.strip()
        if s:
            return s
    return "<no output>"


def _prepared_result(pr_url: str) -> dict:
    """Build a small result object from files on disk after prepare succeeds."""
    try:
        task_dir = _task_dir_for(pr_url)
        state = read_state(task_dir)
        idx = (state.get("phases") or {}).get("3_index") or {}
        head = idx.get("head_sha_at_index")
        return {
            "pr_url": pr_url,
            "status": "prepared",
            "task_dir": str(task_dir),
            "head_sha": head,
            "incremental": bool(idx.get("incremental")),
            "skipped": bool(idx.get("skipped")),
        }
    except Exception:
        return {"pr_url": pr_url, "status": "prepared"}


def _prepare_summary_detail(results: list[dict]) -> str:
    failed = [r for r in results if r.get("status") == "failed"]
    prepared = len(results) - len(failed)
    incremental = sum(1 for r in results if r.get("incremental"))
    unchanged = sum(1 for r in results if r.get("skipped"))
    parts = [f"{prepared} ready"]
    if unchanged:
        parts.append(f"{unchanged} unchanged")
    if incremental:
        parts.append(f"{incremental} incremental")
    if failed:
        parts.append(f"{len(failed)} failed")
    return ", ".join(parts)


def _print_prepare_results(results: list[dict], *, queue: str) -> None:
    failed = [r for r in results if r.get("status") == "failed"]
    print(f"\n{'✅' if not failed else '⚠️'} pr-task prepare complete")
    print(f"   ├─ queue: {format_file_ref(queue)}")
    print(f"   ├─ prepared: {len(results) - len(failed)}")
    print(f"   └─ failed: {len(failed)}")
    if not results:
        return
    print("\n   PRs:")
    for r in results:
        status = r.get("status")
        ref = format_pr_ref(r.get("pr_url", ""))
        details = []
        if r.get("head_sha"):
            details.append(f"head {str(r['head_sha'])[:12]}")
        if r.get("skipped"):
            details.append("index unchanged")
        elif r.get("incremental"):
            details.append("incremental index")
        if r.get("reason"):
            details.append(str(r["reason"])[:160])
        print(f"   ├─ {status_glyph(status)} {ref}"
              f"{' · ' + ' · '.join(details) if details else ''}")
        if r.get("task_dir"):
            print(f"   │  └─ task: {format_file_ref(r['task_dir'])}")


def _prepare_one(pr_url: str, *, queue: str, rebuild: bool, detailed: bool,
                 deep: bool,
                 embed_model: str | None, log) -> dict:
    """Spawn prepare_task.py --prepare-only for one PR. Returns a structured
    dict so the --all caller can aggregate. Never raises."""
    cmd = [sys.executable, str(PREPARE_TASK), "--prepare-only",
           "--queue", str(Path(queue).expanduser())]
    if rebuild:
        cmd.append("--rebuild")
    if detailed:
        cmd.append("--detailed")
    if deep:
        cmd.append("--deep")
    if embed_model:
        cmd += ["--embed-model", embed_model]
    cmd.append(pr_url)

    log.info("$ %s --prepare-only %s", PREPARE_TASK.name, pr_url)
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except Exception as e:
        return {"pr_url": pr_url, "status": "failed", "reason": str(e)}
    if cp.returncode != 0:
        return {"pr_url": pr_url, "status": "failed",
                "reason": _extract_error_reason(cp.stderr or "", cp.stdout or "")}
    return _prepared_result(pr_url)


def cmd_prepare(args) -> int:
    log = get_logger("pr-task-prepare")
    quiet = bool(getattr(args, "quiet", False) or is_orchestrated())
    if not PREPARE_TASK.exists():
        die(f"prepare_task.py not found at {PREPARE_TASK} — check your install")

    if args.all:
        if args.pr_url:
            die("pass either <pr-url> or --all, not both")
        queued = _queued_task_dirs(Path(args.queue).expanduser())
        if not queued:
            if quiet:
                emit_event(RunEvent(kind="step_done", name="prepare tasks",
                                    status="done", detail="no active rows"))
            else:
                _print_prepare_results([], queue=args.queue)
            return 0
        urls = list(queued)
        jobs = args.jobs if args.jobs is not None else _default_prepare_jobs()
        jobs = max(1, min(jobs, len(urls)))
        if not quiet:
            log.info("preparing %d task folder(s) (jobs=%d)", len(urls), jobs)
        else:
            emit_event(RunEvent(kind="step_start", name="prepare tasks",
                                status="run", detail=f"0/{len(urls)} ready"))
        results: list[dict] = []
        had_failure = False

        if jobs == 1:
            for url in urls:
                if quiet:
                    emit_event(RunEvent(kind="step_progress", name="prepare tasks",
                                        status="run",
                                        detail=f"{len(results)}/{len(urls)} ready; preparing {format_pr_ref(url)}"))
                r = _prepare_one(url, queue=args.queue, rebuild=args.rebuild,
                                 detailed=args.detailed,
                                 deep=args.deep,
                                 embed_model=args.embed_model, log=log)
                if r.get("status") == "failed":
                    had_failure = True
                results.append(r)
        else:
            # Each worker spawns its own prepare_task.py subprocess. Effective
            # parallelism is capped further by (1) the per-repo clone lock
            # held briefly during Phase 1a/1b in run_review and (2) Ollama's
            # OLLAMA_NUM_PARALLEL for concurrent embed requests. Failures are
            # isolated by _prepare_one (it never raises).
            total = len(urls)
            done = 0
            with ThreadPoolExecutor(max_workers=jobs) as ex:
                futures = {
                    ex.submit(_prepare_one, url,
                              queue=args.queue, rebuild=args.rebuild,
                              detailed=args.detailed,
                              deep=args.deep,
                              embed_model=args.embed_model, log=log): url
                    for url in urls
                }
                for fut in as_completed(futures):
                    url = futures[fut]
                    done += 1
                    try:
                        r = fut.result()
                    except Exception as e:
                        r = {"pr_url": url, "status": "failed",
                             "reason": f"worker exception: {e}"}
                    if r.get("status") == "failed":
                        had_failure = True
                        if not quiet:
                            log.warning("(%d/%d) failed %s: %s", done, total, url,
                                        (r.get("reason") or "")[:200])
                    else:
                        if not quiet:
                            log.info("(%d/%d) prepared %s", done, total, url)
                    results.append(r)

        if quiet:
            emit_event(RunEvent(
                kind="step_done",
                name="prepare tasks",
                status="done" if not had_failure else "warn",
                detail=_prepare_summary_detail(results),
            ))
        else:
            _print_prepare_results(results, queue=args.queue)
        return 1 if had_failure else 0

    if not args.pr_url:
        die("missing <pr-url>. Pass a URL or `--all`.")

    # Single-PR path: stream stdout/stderr through unchanged so the caller
    # sees the orchestrator's live phase log, not just the trailing JSON.
    cmd = [sys.executable, str(PREPARE_TASK), "--prepare-only",
           "--queue", str(Path(args.queue).expanduser())]
    if args.rebuild:
        cmd.append("--rebuild")
    if args.detailed:
        cmd.append("--detailed")
    if args.deep:
        cmd.append("--deep")
    if args.embed_model:
        cmd += ["--embed-model", args.embed_model]
    cmd.append(args.pr_url)
    log.info("$ %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return cp.returncode


# ----- validate ------------------------------------------------------------

def cmd_validate(args) -> int:
    """Phase 3 gate: drop findings whose anchor drifted or whose suggested
    fix isn't actionable. Reads `<task_dir>/findings.json` (agent's Phase 2
    output) and writes `validated-findings.json` + `initial-findings.json`.
    """
    if not VALIDATE_FINDINGS.exists():
        die(f"validate_findings.py not found at {VALIDATE_FINDINGS} — check your install")
    task_dir = _task_dir_for(args.pr_url)
    if not task_dir.exists():
        die(f"task dir not found: {task_dir} — run `adk pr-task prepare {args.pr_url}` first")
    log = get_logger("pr-task-validate")
    cmd = [sys.executable, str(VALIDATE_FINDINGS),
           "--task-dir", str(task_dir), "--json"]
    log.info("$ %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if cp.stdout:
        sys.stdout.write(cp.stdout)
    if cp.stderr:
        sys.stderr.write(cp.stderr)
    return cp.returncode


# ----- clean-orphans -------------------------------------------------------

def cmd_clean_orphans(args) -> int:
    """Drop task folders under $ADK_DATA_HOME/skill-pr-review/ that no longer
    have a matching queue row (or whose row is merged). Idempotent."""
    log = get_logger("pr-task-clean-orphans")
    root = PR_REVIEW_ROOT
    if not root.exists():
        print("\n✅ pr-task clean-orphans complete")
        print("   └─ no task folders found")
        return 0

    queued = _queued_task_dirs(Path(args.queue).expanduser())
    queued_names = {p.name for p in queued.values()}

    candidates = []
    for d in sorted(root.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        if d.name in queued_names:
            continue
        candidates.append(d)

    if not candidates:
        print("\n✅ pr-task clean-orphans complete")
        print("   └─ no orphan task folders")
        return 0

    if args.dry_run:
        print(f"\n🧪 pr-task clean-orphans dry run: {len(candidates)} folder(s) would be removed")
        for d in candidates:
            print(f"   ├─ {format_file_ref(d)}")
        return 0

    if not args.yes:
        print(f"About to remove {len(candidates)} orphan task folder(s):")
        for d in candidates:
            print(f"  - {d}")
        print("Re-run with --yes to confirm (or --dry-run to preview).")
        return 2

    import shutil
    removed = []
    failed = []
    for d in candidates:
        try:
            shutil.rmtree(d)
            removed.append(str(d))
        except OSError as e:
            failed.append({"path": str(d), "error": str(e)})
            log.warning("failed to remove %s: %s", d, e)

    print(f"\n{'✅' if not failed else '⚠️'} pr-task clean-orphans complete")
    print(f"   ├─ removed: {len(removed)}")
    print(f"   └─ failed: {len(failed)}")
    for path in removed:
        print(f"   ├─ 🗑️  {format_file_ref(path)}")
    for item in failed:
        print(f"   ├─ ❌ {format_file_ref(item['path'])} · {item['error']}")
    return 1 if failed else 0


# ----- info ----------------------------------------------------------------

def cmd_info(args) -> int:
    task_dir = _task_dir_for(args.pr_url)
    info = {
        "pr_url": args.pr_url,
        "task_dir": str(task_dir),
        "exists": task_dir.exists(),
    }
    if task_dir.exists():
        pr_json = task_dir / "pr.json"
        precis = task_dir / "precis.md"
        findings = task_dir / "findings.json"
        info.update({
            "has_pr_json": pr_json.exists(),
            "has_precis": precis.exists(),
            "has_findings": findings.exists(),
        })
        # head_sha + last index head come from state.json (phase markers).
        state = read_state(task_dir) or {}
        phases = state.get("phases") or {}
        fetch_phase = phases.get("2a_fetch_pr") or {}
        index_phase = phases.get("3_index") or {}
        if fetch_phase.get("head_sha"):
            info["head_sha"] = fetch_phase["head_sha"]
        if index_phase.get("head_sha_at_index"):
            info["last_indexed_head"] = index_phase["head_sha_at_index"]
        if pr_json.exists():
            try:
                pr = json.loads(pr_json.read_text(encoding="utf-8"))
                info["title"] = pr.get("title")
                info["state"] = pr.get("state") or pr.get("status")
            except Exception:
                pass
    print(json.dumps(info, indent=2, default=str))
    return 0


# ----- list ----------------------------------------------------------------

def cmd_list(args) -> int:
    root = PR_REVIEW_ROOT
    if not root.exists():
        if args.names_only or args.paths:
            return 0
        print("(no task folders)")
        return 0
    folders = sorted(d for d in root.iterdir()
                     if d.is_dir() and not d.name.startswith("."))
    if args.names_only:
        for f in folders:
            print(f.name)
        return 0
    if args.paths:
        for f in folders:
            print(f)
        return 0
    if not folders:
        print("(no task folders)")
        return 0
    rows = []
    for f in folders:
        state = read_state(f) or {}
        phases = state.get("phases") or {}
        head = (phases.get("2a_fetch_pr") or {}).get("head_sha") or "-"
        idx_head = (phases.get("3_index") or {}).get("head_sha_at_index") or "-"
        has_findings = (f / "findings.json").exists()
        rows.append((f.name, head[:12], idx_head[:12], "✓" if has_findings else "-"))
    w_name = max(len(r[0]) for r in rows + [("task", "", "", "")])
    print(f"{'task'.ljust(w_name)}  {'head':<12}  {'index':<12}  findings")
    print(f"{'-' * w_name}  {'-' * 12}  {'-' * 12}  --------")
    for r in rows:
        print(f"{r[0].ljust(w_name)}  {r[1]:<12}  {r[2]:<12}  {r[3]}")
    return 0


# ----- v4 §8 P6 wrapper verbs (triage / post / report / resolve-comments) --

TRIAGE_PY = ADK_PR_REVIEW_SCRIPTS / "triage.py"
POST_PY = ADK_PR_REVIEW_SCRIPTS / "post_comments.py"
REPORT_PY = ADK_PR_REVIEW_SCRIPTS / "report.py"
RESOLVER_PY = ADK_PR_REVIEW_SCRIPTS / "comment_resolver.py"


def _task_dir_or_die(pr_url: str) -> Path:
    """Resolve <pr_url> to its task dir or die with a clear message."""
    try:
        p = parse_pr_url(pr_url)
    except ValueError as e:
        die(f"unrecognised PR URL: {pr_url} ({e})")
    td = task_dir_for(p["repo"], p["pr_number"])
    if not td.exists():
        die(f"no task folder for {pr_url} at {td}. Run "
            f"`adk pr-task prepare {pr_url}` first.")
    return td


def _forward(script: Path, args_list: list[str]) -> int:
    """Spawn the underlying script + forward stdout/stderr verbatim."""
    if not script.exists():
        die(f"script not found at {script} — check your install")
    return subprocess.run([sys.executable, str(script), *args_list]).returncode


def cmd_triage(args) -> int:
    """adk pr-task triage <url> [--init|--finalize|--mark id --state s|--list|...]"""
    td = _task_dir_or_die(args.pr_url)
    fwd = ["--task-dir", str(td)]
    if args.init:
        fwd.append("--init")
    if args.finalize:
        fwd.append("--finalize")
    if args.default_state:
        fwd += ["--default-state", args.default_state]
    if args.mark:
        fwd += ["--mark", args.mark]
    if args.state:
        fwd += ["--state", args.state]
    if args.list:
        fwd.append("--list")
    if args.show:
        fwd += ["--show", args.show]
    if args.render:
        fwd += ["--render", args.render]
    if args.rewrite:
        fwd += ["--rewrite", args.rewrite]
    if args.fields_json:
        fwd += ["--fields-json", args.fields_json]
    if args.filter_state:
        fwd += ["--filter-state", args.filter_state]
    if args.include_content:
        fwd.append("--include-content")
    return _forward(TRIAGE_PY, fwd)


def cmd_post(args) -> int:
    """adk pr-task post <url> [--no-post|--use-mcp|--no-slack-summary|--no-approve]"""
    td = _task_dir_or_die(args.pr_url)
    fwd = ["--task-dir", str(td)]
    if args.no_post:
        fwd.append("--plan-only")
    if args.use_mcp:
        fwd.append("--use-mcp")
    if args.no_resolve_existing:
        fwd.append("--no-resolve-existing")
    if args.no_slack_summary:
        fwd.append("--no-slack-summary")
    if args.no_approve:
        # post_comments.py reads ADK_NO_APPROVE from env when the flag isn't
        # in its own argparse (defer touching post_comments.py — pass via env).
        import os as _os
        _os.environ["ADK_NO_APPROVE"] = "1"
    return _forward(POST_PY, fwd)


def cmd_report(args) -> int:
    """adk pr-task report <url> [--merge-if-approved]"""
    td = _task_dir_or_die(args.pr_url)
    fwd = ["--task-dir", str(td)]
    if args.merge_if_approved:
        fwd.append("--merge-if-approved")
    return _forward(REPORT_PY, fwd)


def cmd_resolve_comments(args) -> int:
    """adk pr-task resolve-comments <url>"""
    td = _task_dir_or_die(args.pr_url)
    return _forward(RESOLVER_PY, ["--task-dir", str(td)])


def cmd_review_comments(args) -> int:
    """Refresh comments, resolve/reopen acceptable threads, and release queue."""
    parsed = parse_pr_url(args.pr_url)
    td = _task_dir_for(args.pr_url)
    td.mkdir(parents=True, exist_ok=True)

    fetch = ADK_PR_REVIEW_SCRIPTS / "fetch_pr.py"
    fetch_rc = _forward(fetch, [
        "--host", parsed["host"],
        "--owner", parsed["owner"],
        "--repo", parsed["repo"],
        "--pr-number", str(parsed["pr_number"]),
        "--task-dir", str(td),
        "--json",
    ])
    if fetch_rc != 0:
        return fetch_rc

    findings_path = pr_review_file(td, "findings-final.json")
    original_findings = findings_path.read_text(encoding="utf-8") if findings_path.exists() else None
    row = find_row(Path(args.queue).expanduser(), args.pr_url) or {}
    try:
        if original_findings:
            try:
                findings = json.loads(original_findings)
            except json.JSONDecodeError:
                findings = {}
        else:
            findings = {}
        findings["findings"] = []
        findings["recommendation"] = row.get("recommendation") or findings.get("recommendation") or "approve"
        findings["summary"] = "Comment activity reviewed; no code review rerun because the PR head is unchanged."
        findings_path.write_text(json.dumps(findings, indent=2), encoding="utf-8")

        resolver_rc = _forward(RESOLVER_PY, ["--task-dir", str(td), "--json"])
        if resolver_rc != 0:
            return resolver_rc

        post_args = ["--task-dir", str(td), "--comments-only", "--json"]
        if args.no_post:
            post_args.append("--plan-only")
        if args.no_slack_summary:
            post_args.append("--no-slack-summary")
        post_rc = _forward(POST_PY, post_args)
        if post_rc != 0:
            return post_rc

        try:
            from pr_queue import main as queue_main  # type: ignore
            queue_main(["--queue", args.queue, "update", args.pr_url])
        except Exception:
            pass

        report_rc = _forward(REPORT_PY, ["--task-dir", str(td)])
        return report_rc
    finally:
        if original_findings is not None:
            findings_path.write_text(original_findings, encoding="utf-8")


# ----- entrypoint ----------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk pr-task",
                                 description="Manage per-PR task folders "
                                             "under $ADK_DATA_HOME/skill-pr-review/")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to $ADK_DATA_HOME/logs/")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_prep = sub.add_parser("prepare",
                             help="create / refresh the task folder for one PR "
                                  "(runs Phase 0-4a prep; no review, no posting). "
                                  "Use --all to prep every non-merged queue row.")
    sp_prep.add_argument("pr_url", nargs="?", default=None,
                         help="PR URL to prepare (omit when using --all)")
    sp_prep.add_argument("--all", action="store_true",
                         help="prepare task folders for every non-merged queue row; "
                              "continues past per-row failures and exits 1 if any failed")
    sp_prep.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sp_prep.add_argument("--rebuild", action="store_true",
                         help="force a full index rebuild even if head_sha is unchanged")
    sp_prep.add_argument("--detailed", action="store_true",
                         help="use the detailed embed model (bge-m3) for higher recall")
    sp_prep.add_argument("--deep", action="store_true",
                         help="accepted for /adk-pr-review symmetry; model depth is selected by the review harness")
    sp_prep.add_argument("--embed-model", default=None,
                         help="override embed model (default from config)")
    sp_prep.add_argument("--jobs", type=int, default=None,
                         help="parallel workers for --all (default: from "
                              "core.yaml pr_sync.prepare_jobs, fallback 1). "
                              "Effective parallelism is capped by the per-repo "
                              "clone lock and OLLAMA_NUM_PARALLEL.")
    sp_prep.add_argument("--quiet", action="store_true", help=argparse.SUPPRESS)
    sp_prep.add_argument("-y", "--yes", action="store_true")
    sp_prep.set_defaults(func=cmd_prepare)

    sp_info = sub.add_parser("info",
                             help="show task-folder state as JSON")
    sp_info.add_argument("pr_url")
    sp_info.add_argument("-y", "--yes", action="store_true")
    sp_info.set_defaults(func=cmd_info)

    sp_list = sub.add_parser("list", help="list every task folder")
    sp_list.add_argument("--names-only", action="store_true",
                         help="one folder name per line")
    sp_list.add_argument("--paths", action="store_true",
                         help="one absolute path per line")
    sp_list.add_argument("-y", "--yes", action="store_true")
    sp_list.set_defaults(func=cmd_list)

    sp_val = sub.add_parser("validate",
                            help="Phase 3 gate: anchor + suggestion check on "
                                 "the agent's findings.json. Produces "
                                 "validated-findings.json + initial-findings.json.")
    sp_val.add_argument("pr_url")
    sp_val.add_argument("-y", "--yes", action="store_true")
    sp_val.set_defaults(func=cmd_validate)

    sp_orph = sub.add_parser("clean-orphans",
                             help="drop task folders that no longer have a "
                                  "matching queue row (or whose row is merged)")
    sp_orph.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sp_orph.add_argument("--dry-run", action="store_true",
                         help="show what would be removed without deleting")
    sp_orph.add_argument("-y", "--yes", action="store_true",
                         help="confirm deletion (required unless --dry-run)")
    sp_orph.set_defaults(func=cmd_clean_orphans)

    # v4 §8 P6 wrapper verbs — thin shells that resolve <pr_url> → task_dir
    # and forward to the corresponding adk-pr-review script. Lets SKILL.md
    # stop referencing `python3 scripts/...` paths.
    sp_tri = sub.add_parser("triage",
                            help="walk findings accept/reject/edit (delegates to triage.py)")
    sp_tri.add_argument("pr_url")
    sp_tri.add_argument("--init", action="store_true")
    sp_tri.add_argument("--finalize", action="store_true")
    sp_tri.add_argument("--default-state", choices=("accept", "pending"), default=None)
    sp_tri.add_argument("--mark", help="finding_id to mark")
    sp_tri.add_argument("--state", help="for --mark")
    sp_tri.add_argument("--list", action="store_true")
    sp_tri.add_argument("--show", help="finding_id to inspect")
    sp_tri.add_argument("--render", help="finding_id to render as rich markdown")
    sp_tri.add_argument("--rewrite", help="finding_id to rewrite")
    sp_tri.add_argument("--fields-json", help="for --rewrite, JSON object")
    sp_tri.add_argument("--filter-state", help="for --list")
    sp_tri.add_argument("--include-content", action="store_true")
    sp_tri.set_defaults(func=cmd_triage)

    sp_post = sub.add_parser("post",
                             help="post inline comments + Slack reply (delegates to post_comments.py)")
    sp_post.add_argument("pr_url")
    sp_post.add_argument("--no-post", action="store_true",
                         help="plan only; don't actually call the host API")
    sp_post.add_argument("--use-mcp", action="store_true",
                         help="prefer MCP for posting where available")
    sp_post.add_argument("--no-resolve-existing", action="store_true",
                         help="skip the resolve-existing-comments step")
    sp_post.add_argument("--no-slack-summary", action="store_true",
                         help="suppress the Slack reply (reaction flip still happens)")
    sp_post.add_argument("--no-approve", action="store_true",
                         help="force approve_ready=false even when §6.z gate passes")
    sp_post.set_defaults(func=cmd_post)

    sp_rep = sub.add_parser("report",
                            help="render findings.md + report.md + clickable links tail (delegates to report.py)")
    sp_rep.add_argument("pr_url")
    sp_rep.add_argument("--merge-if-approved", action="store_true",
                        help="print 'MERGEABLE — click to merge: <url>' when "
                             "the review recommendation is approve. Advisory; "
                             "never calls the merge API (constitution §I.3).")
    sp_rep.set_defaults(func=cmd_report)

    sp_rc = sub.add_parser("resolve-comments",
                           help="walk prior PR comments and decide resolve/reopen/leave (delegates to comment_resolver.py)")
    sp_rc.add_argument("pr_url")
    sp_rc.set_defaults(func=cmd_resolve_comments)

    sp_cr = sub.add_parser("review-comments",
                           help="comment-only review: refresh comments, resolve/reopen, approve if ready")
    sp_cr.add_argument("pr_url")
    sp_cr.add_argument("--queue", default=str(DEFAULT_QUEUE_PATH))
    sp_cr.add_argument("--no-post", action="store_true",
                       help="plan only; do not call host APIs")
    sp_cr.add_argument("--no-slack-summary", action="store_true",
                       help="suppress Slack summary")
    sp_cr.set_defaults(func=cmd_review_comments)

    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("pr-task", enabled=True, argv=argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
