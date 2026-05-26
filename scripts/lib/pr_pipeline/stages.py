"""pr_pipeline/stages.py — the six stage functions.

Each function is a THIN subprocess wrapper around an existing script:
  do_import  → fetch_pr.py --metadata-only  (+ queue row update)
  do_sync    → prepare_task.py --prepare-only --phases sync
  do_index   → prepare_task.py --prepare-only --phases index
  do_review  → agent harness (_spawn_review from auto_run.py, extracted here)
  do_validate → validate_findings.py --task-dir ...
  do_post     → post_comments.py --task-dir ... [--use-mcp]

Contracts:
  - Each function takes a PRState + keyword args, returns a StageResult.
  - Pure: never calls another stage function directly.
  - Safe to call concurrently across DIFFERENT PRs; NOT safe against the same PR.
  - Writes last_<stage>_at + last_<stage>_head_sha to the queue row on success.
"""
from __future__ import annotations

import json
import os
import selectors
import shlex
import subprocess
import sys
import threading
import time
from pathlib import Path

_LIB_DIR = Path(__file__).resolve().parent.parent
_REPO_ROOT = _LIB_DIR.parent
_ADK_PR_REVIEW_SCRIPTS = _REPO_ROOT / "skills" / "adk-pr-review" / "scripts"
_ADK_CLI_SCRIPTS = _REPO_ROOT / "skills" / "adk-cli" / "scripts"

for _p in [str(_LIB_DIR), str(_ADK_PR_REVIEW_SCRIPTS), str(_ADK_CLI_SCRIPTS)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pr_pipeline.state import PRState, StageResult  # noqa: E402

PY = sys.executable
_PREPARE_TASK = _ADK_PR_REVIEW_SCRIPTS / "prepare_task.py"
_VALIDATE_FINDINGS = _ADK_PR_REVIEW_SCRIPTS / "validate_findings.py"
_POST_COMMENTS = _ADK_PR_REVIEW_SCRIPTS / "post_comments.py"
_FETCH_PR = _ADK_PR_REVIEW_SCRIPTS / "fetch_pr.py"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _update_queue(queue_path: Path, pr_url: str, updates: dict) -> None:
    """Write fields back to the queue row. Never raises."""
    try:
        from queue_io import update_pr_entry  # noqa: WPS433
        update_pr_entry(queue_path, pr_url, updates)
    except Exception as exc:
        # Never let a queue-write failure abort the stage.
        pass


def _run_subprocess(cmd: list[str], *, log) -> tuple[int, str, str]:
    """Run cmd, capture stdout+stderr, return (returncode, stdout, stderr)."""
    log.info("$ %s", " ".join(shlex.quote(c) for c in cmd))
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if cp.stdout:
            log.info("stdout: %s", cp.stdout.strip()[:500])
        if cp.stderr.strip():
            log.info("stderr: %s", cp.stderr.strip()[:500])
        return cp.returncode, cp.stdout or "", cp.stderr or ""
    except FileNotFoundError as exc:
        log.error("binary not found: %s", exc)
        return -1, "", str(exc)
    except Exception as exc:
        log.error("subprocess error: %s", exc)
        return -1, "", str(exc)


def do_import(state: PRState, *, queue_path: Path, log) -> StageResult:
    """Import stage: fetch lightweight PR metadata and enrich the queue row.

    Calls fetch_pr.py --metadata-only so we get title/author/head_sha/etc.
    without pulling the full diff or comments. Cheap enough to run at queue-add
    time so the TUI shows titles immediately.
    """
    t0 = time.time()
    # Parse the PR URL to extract host/owner/repo/pr_number.
    try:
        from _common import parse_pr_url  # noqa: WPS433
        parsed = parse_pr_url(state.pr_url)
    except Exception as exc:
        return StageResult(
            stage="import", status="failed",
            reason=f"could not parse PR URL: {exc}",
            elapsed_s=round(time.time() - t0, 2),
        )

    host = parsed["host"]
    owner = parsed["owner"]
    repo = parsed["repo"]
    pr_number = str(parsed["pr_number"])

    state.task_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        PY, str(_FETCH_PR),
        "--host", host,
        "--owner", owner,
        "--repo", repo,
        "--pr-number", pr_number,
        "--task-dir", str(state.task_dir),
        "--json",
        "--metadata-only",
    ]
    rc, stdout, stderr = _run_subprocess(cmd, log=log)
    elapsed = round(time.time() - t0, 2)

    if rc != 0:
        return StageResult(
            stage="import", status="failed",
            reason=f"fetch_pr --metadata-only rc={rc}: {stderr.strip()[:200]}",
            elapsed_s=elapsed,
        )

    # Parse the JSON result to extract enrichment fields.
    artifacts: dict = {}
    try:
        result = json.loads(stdout.strip().splitlines()[-1])
        artifacts = {k: result[k] for k in ("head_sha", "title", "author",
                                             "target_branch", "is_draft",
                                             "additions", "deletions",
                                             "changed_files")
                     if result.get(k) is not None}
    except Exception:
        pass  # Best-effort; the pr.json was still written to disk.

    # Write back to queue row.
    queue_updates: dict = {
        "last_imported_at": _now_iso(),
    }
    queue_updates.update(artifacts)
    if artifacts.get("head_sha"):
        queue_updates["last_imported_head_sha"] = artifacts["head_sha"]
    _update_queue(queue_path, state.pr_url, queue_updates)

    return StageResult(
        stage="import", status="ok",
        elapsed_s=elapsed,
        artifacts=artifacts,
    )


def do_sync(state: PRState, *, queue_path: Path, log, **kw) -> StageResult:
    """Sync stage: fetch full PR data + worktree + supporting docs.

    Calls prepare_task.py --prepare-only --phases sync which runs:
      Phase 0 (prereq) + Phase 2a (fetch PR) + Phase 1a/1b (worktree) +
      Phase 2b (supporting docs) + Phase 4a (precis). NO index.
    """
    t0 = time.time()
    cmd = [
        PY, str(_PREPARE_TASK),
        "--prepare-only",
        "--phases", "sync",
        "--queue", str(queue_path),
    ]
    for flag in ("rebuild", "detailed", "deep"):
        if kw.get(flag):
            cmd.append(f"--{flag}")
    if kw.get("embed_model"):
        cmd += ["--embed-model", kw["embed_model"]]
    cmd.append(state.pr_url)

    rc, stdout, stderr = _run_subprocess(cmd, log=log)
    elapsed = round(time.time() - t0, 2)

    if rc != 0:
        return StageResult(
            stage="sync", status="failed",
            reason=f"prepare_task --phases sync rc={rc}: {stderr.strip()[:200]}",
            elapsed_s=elapsed,
        )

    _update_queue(queue_path, state.pr_url, {"last_synced_at": _now_iso()})
    return StageResult(stage="sync", status="ok", elapsed_s=elapsed)


def do_index(state: PRState, *, queue_path: Path, log,
             embed_model: str | None = None, rebuild: bool = False,
             **kw) -> StageResult:
    """Index stage: chunk + embed + SCIP.

    Calls prepare_task.py --prepare-only --phases index which runs Phase 3
    ONLY (assumes worktree exists from Sync stage).
    """
    t0 = time.time()
    cmd = [
        PY, str(_PREPARE_TASK),
        "--prepare-only",
        "--phases", "index",
        "--queue", str(queue_path),
    ]
    if rebuild:
        cmd.append("--rebuild")
    if embed_model:
        cmd += ["--embed-model", embed_model]
    cmd.append(state.pr_url)

    rc, stdout, stderr = _run_subprocess(cmd, log=log)
    elapsed = round(time.time() - t0, 2)

    if rc != 0:
        return StageResult(
            stage="index", status="failed",
            reason=f"prepare_task --phases index rc={rc}: {stderr.strip()[:200]}",
            elapsed_s=elapsed,
        )

    _update_queue(queue_path, state.pr_url, {"last_indexed_at": _now_iso()})
    return StageResult(stage="index", status="ok", elapsed_s=elapsed)


def do_review(state: PRState, *, queue_path: Path, log,
              runner: str = "claude", agent: str | None = None,
              model: str | None = None, detailed: bool = False,
              deep: bool = False, deep_reason: str | None = None,
              rebuild: bool = False, run_dir: Path | None = None,
              run_state_id: str | None = None,
              work_mode: str | None = None,
              **kw) -> StageResult:
    """Review stage: spawn the agent harness for one PR.

    This is the extracted logic from auto_run._spawn_review, called through
    the pipeline so the scheduler can semaphore-gate it.
    """
    t0 = time.time()

    # Resolve the log path for the agent subprocess.
    try:
        log_path = state.task_dir / "agent.log"
    except Exception:
        log_path = (run_dir or Path("/tmp")) / f"agent-{state.pr_number}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Build the agent command via the existing harness.
    try:
        from agent_harness import build_agent_cmd, resolve_runner_model  # noqa: WPS433
        from queue_io import WORK_COMMENTS  # noqa: WPS433
    except ImportError as exc:
        return StageResult(
            stage="review", status="failed",
            reason=f"import error: {exc}",
            elapsed_s=round(time.time() - t0, 2),
        )

    _REPO_ROOT_BIN = _REPO_ROOT / "bin" / "adk"
    resolved_model = resolve_runner_model(
        runner=runner,
        explicit_model=model,
        deep=deep,
    )
    flags = []
    if detailed:
        flags.append("--detailed")
    if deep:
        flags.append("--deep")
    if rebuild:
        flags.append("--rebuild")
    if work_mode == WORK_COMMENTS:
        flags.append("--comments-only")
    prompt = " ".join(["/adk-pr-review", state.pr_url] + flags)

    if work_mode == WORK_COMMENTS:
        cmd = [
            PY, str(_REPO_ROOT_BIN), "pr-task", "review-comments", state.pr_url,
            "--queue", str(queue_path),
        ]
    else:
        try:
            cmd = build_agent_cmd(
                prompt,
                runner=runner,
                agent=agent,
                model=resolved_model,
                workspace=_REPO_ROOT,
            )
        except ValueError as exc:
            return StageResult(
                stage="review", status="failed",
                reason=str(exc),
                elapsed_s=round(time.time() - t0, 2),
            )

    # Run a context-refresh first (unless comments-only).
    if work_mode != WORK_COMMENTS:
        refresh_cmd = [
            PY, str(_REPO_ROOT_BIN), "pr", "--queue", str(queue_path),
            "context-refresh", state.pr_url, "--no-prepare",
        ]
        log.info("context-refresh: $ %s", " ".join(shlex.quote(c) for c in refresh_cmd))
        try:
            subprocess.run(refresh_cmd, capture_output=True, text=True, check=False)
        except Exception:
            pass  # Non-fatal; context-refresh failure doesn't block review.

    # Mark attempt started in queue.
    try:
        from queue_io import REVIEW_ATTEMPT_STARTED, update_pr_entry  # noqa: WPS433
        update_pr_entry(queue_path, state.pr_url, {
            "last_review_attempt_at": _now_iso(),
            "last_review_attempt_status": REVIEW_ATTEMPT_STARTED,
            "last_review_attempt_work_mode": work_mode,
        })
    except Exception:
        pass

    # Spawn the agent.
    log.info("review: $ %s", " ".join(shlex.quote(c) for c in cmd))
    try:
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write("$ " + " ".join(shlex.quote(c) for c in cmd) + "\n")
            fh.flush()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            # Heartbeat thread renews taken_at so the queue lock doesn't expire.
            _stop = threading.Event()

            def _renew():
                while not _stop.wait(timeout=30 * 60):
                    try:
                        from queue_io import update_pr_entry as _upd  # noqa: WPS433
                        _upd(queue_path, state.pr_url, {"taken_at": _now_iso()})
                    except Exception:
                        pass

            _hb = threading.Thread(target=_renew, daemon=True)
            _hb.start()

            sel = selectors.DefaultSelector()
            if proc.stdout is not None:
                sel.register(proc.stdout, selectors.EVENT_READ)
            while proc.poll() is None:
                for key, _ in sel.select(timeout=0.2):
                    line = key.fileobj.readline()
                    if line:
                        fh.write(line)
                        fh.flush()
            for line in (proc.stdout or []):
                fh.write(line)
                fh.flush()
            sel.close()
            _stop.set()
            _hb.join()
            exit_code = proc.returncode
    except FileNotFoundError as exc:
        elapsed = round(time.time() - t0, 2)
        return StageResult(
            stage="review", status="failed",
            reason=f"agent binary not found: {exc}",
            elapsed_s=elapsed,
            artifacts={"log": str(log_path)},
        )
    except Exception as exc:
        elapsed = round(time.time() - t0, 2)
        return StageResult(
            stage="review", status="failed",
            reason=str(exc),
            elapsed_s=elapsed,
            artifacts={"log": str(log_path)},
        )

    elapsed = round(time.time() - t0, 2)

    # Update queue attempt status.
    try:
        from queue_io import REVIEW_ATTEMPT_FAILED, update_pr_entry as _upd2  # noqa: WPS433
        if exit_code != 0:
            _upd2(queue_path, state.pr_url, {
                "last_review_attempt_status": REVIEW_ATTEMPT_FAILED,
                "last_review_attempt_error": f"exit_code={exit_code}",
            })
        else:
            _upd2(queue_path, state.pr_url, {"last_reviewed_at": _now_iso()})
    except Exception:
        pass

    if exit_code != 0:
        return StageResult(
            stage="review", status="failed",
            reason=f"agent exited rc={exit_code}",
            elapsed_s=elapsed,
            artifacts={"log": str(log_path), "exit_code": exit_code},
        )
    return StageResult(
        stage="review", status="ok",
        elapsed_s=elapsed,
        artifacts={"log": str(log_path), "model": resolved_model, "deep": deep},
    )


def do_validate(state: PRState, *, queue_path: Path, log, **kw) -> StageResult:
    """Validate stage: anchor + suggestion check on findings.json."""
    t0 = time.time()
    cmd = [
        PY, str(_VALIDATE_FINDINGS),
        "--task-dir", str(state.task_dir),
        "--json",
    ]
    rc, stdout, stderr = _run_subprocess(cmd, log=log)
    elapsed = round(time.time() - t0, 2)

    if rc != 0:
        return StageResult(
            stage="validate", status="failed",
            reason=f"validate_findings rc={rc}: {stderr.strip()[:200]}",
            elapsed_s=elapsed,
        )

    _update_queue(queue_path, state.pr_url, {"last_validated_at": _now_iso()})
    return StageResult(stage="validate", status="ok", elapsed_s=elapsed)


def do_post(state: PRState, *, queue_path: Path, log,
            use_mcp: bool = True, no_slack_summary: bool = False,
            no_approve: bool = False, plan_only: bool = False,
            **kw) -> StageResult:
    """Post stage: post inline comments + Slack reply + queue row update."""
    t0 = time.time()
    cmd = [
        PY, str(_POST_COMMENTS),
        "--task-dir", str(state.task_dir),
        "--json",
    ]
    if use_mcp:
        cmd.append("--use-mcp")
    if no_slack_summary:
        cmd.append("--no-slack-summary")
    if plan_only:
        cmd.append("--plan-only")

    env = dict(os.environ)
    if no_approve:
        env["ADK_NO_APPROVE"] = "1"

    log.info("post: $ %s", " ".join(shlex.quote(c) for c in cmd))
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
        rc = cp.returncode
        stdout = cp.stdout or ""
        stderr = cp.stderr or ""
    except Exception as exc:
        return StageResult(
            stage="post", status="failed",
            reason=str(exc),
            elapsed_s=round(time.time() - t0, 2),
        )

    elapsed = round(time.time() - t0, 2)

    if rc != 0:
        return StageResult(
            stage="post", status="failed",
            reason=f"post_comments rc={rc}: {stderr.strip()[:200]}",
            elapsed_s=elapsed,
        )

    _update_queue(queue_path, state.pr_url, {"last_posted_at": _now_iso()})
    return StageResult(stage="post", status="ok", elapsed_s=elapsed)
