"""repo.py — `adk repo` subcommands.

add <git-url>     clone the repo into ~/.agents-devkit/repos/<name>/, check out
                  the default branch, run the chunker + embedder + (optional)
                  scip indexer against it. The resulting index lives at
                  ~/.agents-devkit/repos/.indices/<name>/code-index/ (separate
                  from any per-PR review task dir).

update <name>     `git fetch --all --prune` + fast-forward the default branch.
                  If the HEAD oid has moved, run an incremental reindex (only
                  the files that differ between last_indexed_oid and current
                  HEAD). If HEAD is unchanged, no-op.

list              list repos known to adk (under ~/.agents-devkit/repos/) +
                  their last_indexed_oid + last_indexed_at.

All commands accept `-y` / `--yes` for non-interactive mode.

Index layout:
  ~/.agents-devkit/repos/<name>/          clone (working tree on default branch)
  ~/.agents-devkit/repos/.indices/<name>/ adk-owned index task dir
    code-index/
      chunks.jsonl                        chunker output
      chunks.lance/                       LanceDB table
      scip/<lang>/index.scip              SCIP cross-refs (when scip-* on PATH)
      meta.json                           rows + model + dim
    repo-meta.json                        last_indexed_oid + last_indexed_at +
                                          default_branch
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))

from _common import die, get_logger, which, ADK_HOME, REPOS_ROOT  # noqa: E402

REPO_INDICES_ROOT = REPOS_ROOT / ".indices"
PY = sys.executable

_EXT_TO_LANG = {".ts": "ts", ".tsx": "ts", ".py": "py", ".go": "go", ".java": "java"}


# ----- helpers ------------------------------------------------------------

def _repo_name_from_url(url: str) -> str:
    """Extract a repo name. Handles https/ssh/path forms."""
    s = url.strip().rstrip("/")
    # SSH form: git@host:owner/repo(.git)
    m = re.match(r"^[^@]+@[^:]+:[^/]+/([^/]+?)(\.git)?$", s)
    if m:
        return m.group(1)
    # https or local path: take the last path segment, strip .git.
    name = s.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def _detect_default_branch(repo_path: Path, log) -> str:
    """Resolve the remote's HEAD reference. Falls back to 'main' then 'master'."""
    try:
        cp = subprocess.run(
            ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
            cwd=repo_path, capture_output=True, text=True, check=False,
        )
        if cp.returncode == 0 and cp.stdout.strip():
            ref = cp.stdout.strip()
            return ref.rsplit("/", 1)[-1]
    except Exception as e:
        log.warning("symbolic-ref failed: %s", e)
    # Heuristic fallback.
    for b in ("main", "master"):
        cp = subprocess.run(
            ["git", "rev-parse", "--verify", f"refs/remotes/origin/{b}"],
            cwd=repo_path, capture_output=True, text=True, check=False,
        )
        if cp.returncode == 0:
            return b
    die(f"could not detect default branch in {repo_path}")
    return ""  # unreachable


def _current_oid(repo_path: Path) -> str:
    cp = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_path,
                        capture_output=True, text=True, check=True)
    return cp.stdout.strip()


def _diff_files(repo_path: Path, old: str, new: str, log) -> list[str]:
    if not old or old == new:
        return []
    cp = subprocess.run(["git", "diff", "--name-only", f"{old}..{new}"],
                        cwd=repo_path, capture_output=True, text=True, check=False)
    if cp.returncode != 0:
        log.warning("git diff failed (%d); will full reindex", cp.returncode)
        return []
    return [line for line in cp.stdout.splitlines() if line.strip()]


def _step(cmd: list[str], log) -> subprocess.CompletedProcess:
    log.info("$ %s", " ".join(cmd))
    cp = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if cp.stdout.strip():
        log.info("stdout: %s", cp.stdout.strip()[-800:])
    if cp.stderr.strip():
        log.info("stderr: %s", cp.stderr.strip()[-800:])
    if cp.returncode != 0:
        die(f"step failed (rc={cp.returncode}): {' '.join(cmd)}")
    return cp


def _index_task_dir(name: str) -> Path:
    return REPO_INDICES_ROOT / name


def _repo_meta_path(name: str) -> Path:
    return _index_task_dir(name) / "repo-meta.json"


def _read_repo_meta(name: str) -> dict:
    p = _repo_meta_path(name)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_repo_meta(name: str, meta: dict) -> None:
    p = _repo_meta_path(name)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


# ----- index pipeline -----------------------------------------------------

def _full_index(repo_clone: Path, task_dir: Path, embed_model: str, log) -> None:
    chunks_path = task_dir / "code-index" / "chunks.jsonl"
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    _step([PY, str(ADK_PR_REVIEW_SCRIPTS / "chunker.py"),
           "--worktree", str(repo_clone), "--out", str(chunks_path)], log)
    _step([PY, str(ADK_PR_REVIEW_SCRIPTS / "embedder.py"),
           "--task-dir", str(task_dir), "--chunks", str(chunks_path),
           "--model", embed_model, "--mode", "replace", "--json"], log)
    _step([PY, str(ADK_PR_REVIEW_SCRIPTS / "scip_runner.py"),
           "--task-dir", str(task_dir), "--worktree", str(repo_clone), "--json"], log)


def _incremental_index(repo_clone: Path, task_dir: Path, changed: list[str],
                       embed_model: str, log) -> None:
    if not changed:
        log.info("incremental index: no changed files; skipping")
        return
    code_index = task_dir / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    files_list = code_index / "changed-files.txt"
    files_list.write_text("\n".join(changed), encoding="utf-8")
    delta = code_index / "chunks-delta.jsonl"
    _step([PY, str(ADK_PR_REVIEW_SCRIPTS / "chunker.py"),
           "--worktree", str(repo_clone), "--files-list", str(files_list),
           "--out", str(delta)], log)
    _step([PY, str(ADK_PR_REVIEW_SCRIPTS / "embedder.py"),
           "--task-dir", str(task_dir), "--chunks", str(delta),
           "--model", embed_model, "--mode", "incremental",
           "--replaced-files", str(files_list), "--json"], log)
    langs = sorted({_EXT_TO_LANG[Path(f).suffix.lower()]
                    for f in changed if Path(f).suffix.lower() in _EXT_TO_LANG})
    if langs:
        _step([PY, str(ADK_PR_REVIEW_SCRIPTS / "scip_runner.py"),
               "--task-dir", str(task_dir), "--worktree", str(repo_clone),
               "--langs", ",".join(langs), "--json"], log)


# ----- subcommands --------------------------------------------------------

def cmd_add(args) -> int:
    log = get_logger("repo-add")
    if not which("git"):
        die("git not on PATH. brew install git.")

    url = args.url
    name = args.name or _repo_name_from_url(url)
    repo_clone = REPOS_ROOT / name
    task_dir = _index_task_dir(name)

    if repo_clone.exists():
        if not args.yes:
            die(f"{repo_clone} already exists. Pass --yes to refresh in place (no reclone), "
                "or use `adk repo update {name}` instead.")
        log.info("%s exists — skipping clone, falling through to reindex", repo_clone)
    else:
        REPOS_ROOT.mkdir(parents=True, exist_ok=True)
        _step(["git", "clone", url, str(repo_clone)], log)

    default_branch = _detect_default_branch(repo_clone, log)
    _step(["git", "-C", str(repo_clone), "checkout", default_branch], log)
    head_oid = _current_oid(repo_clone)
    log.info("indexing %s @ %s (%s)", name, head_oid[:12], default_branch)

    _full_index(repo_clone, task_dir, args.embed_model, log)
    _write_repo_meta(name, {
        "name": name,
        "url": url,
        "clone_path": str(repo_clone),
        "task_dir": str(task_dir),
        "default_branch": default_branch,
        "last_indexed_oid": head_oid,
        "last_indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    print(json.dumps({
        "name": name, "clone_path": str(repo_clone), "task_dir": str(task_dir),
        "default_branch": default_branch, "head_oid": head_oid, "indexed": "full",
    }, indent=2))
    return 0


def cmd_update(args) -> int:
    log = get_logger("repo-update")
    if not which("git"):
        die("git not on PATH.")

    name = args.name
    repo_clone = REPOS_ROOT / name
    task_dir = _index_task_dir(name)
    if not repo_clone.exists():
        die(f"{repo_clone} does not exist. Run `adk repo add <url>` first.")

    meta = _read_repo_meta(name)
    default_branch = meta.get("default_branch") or _detect_default_branch(repo_clone, log)
    last_oid = meta.get("last_indexed_oid", "")

    _step(["git", "-C", str(repo_clone), "fetch", "--all", "--prune"], log)
    _step(["git", "-C", str(repo_clone), "checkout", default_branch], log)
    _step(["git", "-C", str(repo_clone), "pull", "--ff-only"], log)
    new_oid = _current_oid(repo_clone)

    if new_oid == last_oid and not args.force:
        log.info("HEAD unchanged at %s; skipping reindex (use --force to reindex anyway)",
                 new_oid[:12])
        print(json.dumps({
            "name": name, "head_oid": new_oid, "indexed": "skipped",
            "reason": "HEAD unchanged",
        }, indent=2))
        return 0

    changed = _diff_files(repo_clone, last_oid, new_oid, log) if last_oid and not args.full else []
    indexed = "full"
    if last_oid and changed and not args.full:
        indexed = "incremental"
        _incremental_index(repo_clone, task_dir, changed, args.embed_model, log)
    else:
        _full_index(repo_clone, task_dir, args.embed_model, log)

    meta.update({
        "default_branch": default_branch,
        "last_indexed_oid": new_oid,
        "last_indexed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })
    _write_repo_meta(name, meta)
    print(json.dumps({
        "name": name, "head_oid": new_oid, "prev_oid": last_oid or None,
        "indexed": indexed, "files_changed": len(changed),
    }, indent=2))
    return 0


def cmd_list(args) -> int:
    if not REPOS_ROOT.exists():
        print("(no repos)")
        return 0
    rows = []
    for d in sorted(REPOS_ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        meta = _read_repo_meta(d.name)
        rows.append((
            d.name,
            (meta.get("last_indexed_oid") or "-")[:12],
            (meta.get("last_indexed_at") or "-"),
            meta.get("default_branch", "-"),
        ))
    if not rows:
        print("(no repos)")
        return 0
    w_name = max(len(r[0]) for r in rows + [("name", "", "", "")])
    w_oid = max(len(r[1]) for r in rows + [("", "head", "", "")])
    w_branch = max(len(r[3]) for r in rows + [("", "", "", "branch")])
    print(f"{'name'.ljust(w_name)}  {'head'.ljust(w_oid)}  "
          f"{'last_indexed_at'.ljust(20)}  {'branch'.ljust(w_branch)}")
    print(f"{'-' * w_name}  {'-' * w_oid}  {'-' * 20}  {'-' * w_branch}")
    for name, oid, ts, br in rows:
        print(f"{name.ljust(w_name)}  {oid.ljust(w_oid)}  {ts.ljust(20)}  {br.ljust(w_branch)}")
    return 0


# ----- entrypoint ---------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="adk repo",
                                 description="Manage repo clones + indices under ~/.agents-devkit/repos/")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp_add = sub.add_parser("add", help="clone + index a repo")
    sp_add.add_argument("url", help="git URL or local path")
    sp_add.add_argument("--name", default=None,
                        help="override repo name (default: derived from URL)")
    sp_add.add_argument("--embed-model", default="nomic-embed-text",
                        help="ollama embed model (default: nomic-embed-text)")
    sp_add.add_argument("-y", "--yes", action="store_true",
                        help="proceed even if clone exists (skip clone, reindex in place)")
    sp_add.set_defaults(func=cmd_add)

    sp_upd = sub.add_parser("update", help="fetch + fast-forward + incremental reindex")
    sp_upd.add_argument("name")
    sp_upd.add_argument("--full", action="store_true",
                        help="force a full reindex (default is incremental when HEAD moved)")
    sp_upd.add_argument("--force", action="store_true",
                        help="reindex even if HEAD is unchanged")
    sp_upd.add_argument("--embed-model", default="nomic-embed-text")
    sp_upd.add_argument("-y", "--yes", action="store_true")
    sp_upd.set_defaults(func=cmd_update)

    sp_list = sub.add_parser("list", help="list known repos + last_indexed_oid")
    sp_list.add_argument("-y", "--yes", action="store_true")
    sp_list.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
