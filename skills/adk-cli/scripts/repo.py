"""repo.py — `adk repo` subcommands.

add <git-url>                 clone the repo into ~/.agents-devkit/repos/<name>/,
                              check out the default branch, run the chunker +
                              embedder + (optional) scip indexer. Use --branch
                              N times to also index other branches (e.g.
                              `--branch develop`).

update <name>                 `git fetch --all --prune` + fast-forward the
                              default branch + incremental reindex. Add --branch
                              to refresh a specific branch, --all-branches to
                              refresh every tracked branch for this repo, or
                              --all to refresh every repo.

branch add <name> --branch X  Start tracking branch X for an already-cloned
                              repo. Builds a full index for X under branches/<slug>/.

branch remove <name> --branch X
                              Drop the index for branch X. Cannot remove the
                              default branch.

branch list <name>            Show every tracked branch for this repo + the
                              SHA + timestamp of its index.

migrate [<name>]              One-shot move from the legacy single-index layout
                              (<repo>/code-index/) to the multi-branch layout
                              (<repo>/branches/<slug(default)>/code-index/).
                              Idempotent. add/update/branch trigger this
                              implicitly on the touched repo.

list                          list repos known to adk. Add --branches for the
                              per-(repo, branch) view.

All commands accept `-y` / `--yes` for non-interactive mode.

Index layout:
  ~/.agents-devkit/repos/<name>/                                  clone (working tree)
  ~/.agents-devkit/repos/.indices/<name>/                         per-repo dir
    repo-meta.json                                                catalog: name,
                                                                  url, default_branch,
                                                                  tracked_branches[]
    branches/<slug>/
      branch-meta.json                                            { branch, slug,
                                                                    last_indexed_oid,
                                                                    last_indexed_at,
                                                                    embed_model }
      code-index/
        chunks.jsonl                                              chunker output
        chunks.lance/                                             LanceDB table
        scip/<lang>/index.scip                                    SCIP cross-refs (optional)
        meta.json                                                 rows + model + dim
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
# Phase 2 moved the indexer to scripts/lib/code_index/. The pr-review-scripts
# path is still added to sys.path for back-compat with any helper that hasn't
# migrated, but indexer invocations now point at the lib directly.
CODE_INDEX_LIB = THIS_DIR.parent.parent.parent / "scripts" / "lib" / "code_index"
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
sys.path.insert(0, str(CODE_INDEX_LIB))

from _common import die, get_logger, which, ADK_HOME, REPOS_ROOT  # noqa: E402
from base_index import slugify_branch  # noqa: E402

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


# ----- repo + branch paths ------------------------------------------------

def _repo_dir(name: str) -> Path:
    return REPO_INDICES_ROOT / name


def _index_task_dir(name: str) -> Path:
    """Back-compat alias for `_repo_dir`; some helpers still call it."""
    return _repo_dir(name)


def _repo_meta_path(name: str) -> Path:
    return _repo_dir(name) / "repo-meta.json"


def _branch_dir(name: str, slug: str) -> Path:
    return _repo_dir(name) / "branches" / slug


def _branch_meta_path(name: str, slug: str) -> Path:
    return _branch_dir(name, slug) / "branch-meta.json"


def _now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


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


def _read_branch_meta(name: str, slug: str) -> dict:
    p = _branch_meta_path(name, slug)
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _write_branch_meta(name: str, slug: str, meta: dict) -> None:
    p = _branch_meta_path(name, slug)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")


def _tracked_slugs(name: str) -> list[str]:
    branches_dir = _repo_dir(name) / "branches"
    if not branches_dir.exists():
        return []
    return sorted(
        d.name for d in branches_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


# ----- migration ----------------------------------------------------------

def _migrate_if_legacy(name: str, log) -> bool:
    """If `<repo>/code-index/` exists but `<repo>/branches/` doesn't, move the
    legacy index under `branches/<slug(default_branch)>/code-index/` and
    rewrite the catalog. Idempotent. Returns True if a migration happened."""
    repo_dir = _repo_dir(name)
    legacy_code = repo_dir / "code-index"
    branches_dir = repo_dir / "branches"
    if not legacy_code.exists() or branches_dir.exists():
        return False
    meta = _read_repo_meta(name)
    default_branch = meta.get("default_branch") or ""
    if not default_branch:
        log.warning(
            "legacy layout at %s has no default_branch in repo-meta.json; "
            "skipping migration", repo_dir
        )
        return False
    slug = slugify_branch(default_branch)
    dst = branches_dir / slug
    log.info("migrating legacy index: %s → %s/code-index/", legacy_code, dst)
    dst.mkdir(parents=True, exist_ok=True)
    (legacy_code).rename(dst / "code-index")
    _write_branch_meta(name, slug, {
        "name": name,
        "branch": default_branch,
        "slug": slug,
        "last_indexed_oid": meta.get("last_indexed_oid", ""),
        "last_indexed_at": meta.get("last_indexed_at", ""),
        "embed_model": meta.get("embed_model", ""),
    })
    meta["tracked_branches"] = [{
        "branch": default_branch,
        "slug": slug,
        "last_indexed_oid": meta.get("last_indexed_oid", ""),
        "last_indexed_at": meta.get("last_indexed_at", ""),
    }]
    meta.pop("last_indexed_oid", None)
    meta.pop("last_indexed_at", None)
    _write_repo_meta(name, meta)
    return True


def _rewrite_repo_catalog(name: str, log) -> None:
    """Re-derive repo-meta.json's tracked_branches from disk. Called after any
    branch add/update/remove."""
    repo_dir = _repo_dir(name)
    meta = _read_repo_meta(name)
    meta.setdefault("name", name)
    tracked: list[dict] = []
    for slug in _tracked_slugs(name):
        bm = _read_branch_meta(name, slug)
        if not bm.get("last_indexed_oid"):
            continue
        tracked.append({
            "branch": bm.get("branch") or slug,
            "slug": slug,
            "last_indexed_oid": bm.get("last_indexed_oid"),
            "last_indexed_at": bm.get("last_indexed_at"),
        })
    meta["tracked_branches"] = tracked
    # Drop the legacy per-repo SHA fields once we have a real tracked list.
    if tracked:
        meta.pop("last_indexed_oid", None)
        meta.pop("last_indexed_at", None)
    _write_repo_meta(name, meta)


# ----- index pipeline -----------------------------------------------------

def _full_index(repo_clone: Path, branch_dir: Path, embed_model: str, log) -> None:
    """Chunk + embed + SCIP-index the worktree into `branch_dir/code-index/`."""
    chunks_path = branch_dir / "code-index" / "chunks.jsonl"
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    _step([PY, str(CODE_INDEX_LIB / "chunker.py"),
           "--worktree", str(repo_clone), "--out", str(chunks_path)], log)
    _step([PY, str(CODE_INDEX_LIB / "embedder.py"),
           "--task-dir", str(branch_dir), "--chunks", str(chunks_path),
           "--model", embed_model, "--mode", "replace", "--json"], log)
    _step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
           "--task-dir", str(branch_dir), "--worktree", str(repo_clone), "--json"], log)


def _incremental_index(repo_clone: Path, branch_dir: Path, changed: list[str],
                       embed_model: str, log) -> None:
    if not changed:
        log.info("incremental index: no changed files; skipping")
        return
    code_index = branch_dir / "code-index"
    code_index.mkdir(parents=True, exist_ok=True)
    files_list = code_index / "changed-files.txt"
    files_list.write_text("\n".join(changed), encoding="utf-8")
    delta = code_index / "chunks-delta.jsonl"
    _step([PY, str(CODE_INDEX_LIB / "chunker.py"),
           "--worktree", str(repo_clone), "--files-list", str(files_list),
           "--out", str(delta)], log)
    _step([PY, str(CODE_INDEX_LIB / "embedder.py"),
           "--task-dir", str(branch_dir), "--chunks", str(delta),
           "--model", embed_model, "--mode", "incremental",
           "--replaced-files", str(files_list), "--json"], log)
    langs = sorted({_EXT_TO_LANG[Path(f).suffix.lower()]
                    for f in changed if Path(f).suffix.lower() in _EXT_TO_LANG})
    if langs:
        _step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
               "--task-dir", str(branch_dir), "--worktree", str(repo_clone),
               "--langs", ",".join(langs), "--json"], log)


# ----- per-branch index orchestration ------------------------------------

def _ensure_branch_checked_out(repo_clone: Path, branch: str, log) -> None:
    """Fetch + checkout + fast-forward one branch in the shared clone. Used
    by both `branch add` (first index) and `update --branch …` (refresh)."""
    _step(["git", "-C", str(repo_clone), "fetch", "origin",
           f"+refs/heads/{branch}:refs/remotes/origin/{branch}"], log)
    _step(["git", "-C", str(repo_clone), "checkout", branch], log)
    _step(["git", "-C", str(repo_clone), "pull", "--ff-only"], log)


def _index_one_branch(name: str, repo_clone: Path, branch: str,
                      embed_model: str, *, rebuild: bool,
                      log) -> dict:
    """Refresh (or build from scratch) the index for one branch. Returns a
    summary dict including {branch, slug, head_oid, indexed, files_changed}."""
    slug = slugify_branch(branch)
    if not slug:
        return {"branch": branch, "status": "failed", "reason": "empty slug"}
    branch_dir = _branch_dir(name, slug)
    bm = _read_branch_meta(name, slug)
    last_oid = bm.get("last_indexed_oid", "")

    _ensure_branch_checked_out(repo_clone, branch, log)
    new_oid = _current_oid(repo_clone)

    if new_oid == last_oid and not rebuild:
        log.info("[%s] HEAD unchanged at %s; skipping reindex (use --rebuild to force)",
                 branch, new_oid[:12])
        return {"branch": branch, "slug": slug, "head_oid": new_oid,
                "indexed": "skipped", "reason": "HEAD unchanged"}

    changed = _diff_files(repo_clone, last_oid, new_oid, log) if (last_oid and not rebuild) else []
    indexed = "full"
    if last_oid and changed and not rebuild:
        indexed = "incremental"
        _incremental_index(repo_clone, branch_dir, changed, embed_model, log)
    else:
        _full_index(repo_clone, branch_dir, embed_model, log)

    _write_branch_meta(name, slug, {
        "name": name,
        "branch": branch,
        "slug": slug,
        "last_indexed_oid": new_oid,
        "last_indexed_at": _now_iso(),
        "embed_model": embed_model,
    })
    return {"branch": branch, "slug": slug, "head_oid": new_oid,
            "prev_oid": last_oid or None, "indexed": indexed,
            "files_changed": len(changed)}


# ----- subcommands --------------------------------------------------------

def cmd_add(args) -> int:
    log = get_logger("repo-add")
    if not which("git"):
        die("git not on PATH. brew install git.")

    url = args.url
    name = args.name or _repo_name_from_url(url)
    repo_clone = REPOS_ROOT / name

    if repo_clone.exists():
        if not args.yes:
            die(f"{repo_clone} already exists. Pass --yes to refresh in place "
                f"(no reclone), or use `adk repo update {name}` instead.")
        log.info("%s exists — skipping clone, falling through to reindex", repo_clone)
    else:
        REPOS_ROOT.mkdir(parents=True, exist_ok=True)
        _step(["git", "clone", url, str(repo_clone)], log)

    # Move any pre-existing legacy layout into branches/<default>/ before we
    # start writing branch-meta.json files.
    _migrate_if_legacy(name, log)

    default_branch = _detect_default_branch(repo_clone, log)
    extra = [b for b in (args.branch or []) if b]
    # Always include the default branch unless the caller explicitly said
    # otherwise. `add --branch develop` still indexes default + develop;
    # `add --branch develop --skip-default` indexes only develop.
    if args.skip_default:
        branches = list(dict.fromkeys(extra))
    else:
        branches = list(dict.fromkeys([default_branch, *extra]))
    if not branches:
        die("no branches to index — refusing to add a repo with zero indexes.")

    # Catalog stub — branch results overwrite tracked_branches at the end.
    _write_repo_meta(name, {
        "name": name,
        "url": url,
        "clone_path": str(repo_clone),
        "default_branch": default_branch,
        "tracked_branches": [],
    })

    results: list[dict] = []
    for br in branches:
        log.info("indexing %s/%s", name, br)
        results.append(_index_one_branch(
            name, repo_clone, br, args.embed_model,
            rebuild=True, log=log,
        ))
    _rewrite_repo_catalog(name, log)
    print(json.dumps({
        "name": name, "clone_path": str(repo_clone),
        "default_branch": default_branch, "branches": results,
    }, indent=2))
    return 0


def _known_repo_names() -> list[str]:
    """Names of every repo currently indexed under REPOS_ROOT."""
    if not REPOS_ROOT.exists():
        return []
    return sorted(d.name for d in REPOS_ROOT.iterdir()
                  if d.is_dir() and not d.name.startswith("."))


def _resolve_branches_for_update(name: str, args, default_branch: str,
                                 log) -> list[str]:
    """Choose which branches to refresh in this `update` call.

    Precedence: explicit `--branch X [--branch Y]` → those. Else
    `--all-branches` → every tracked branch in the catalog. Else → default
    branch alone."""
    if args.branch:
        return list(args.branch)
    if args.all_branches:
        meta = _read_repo_meta(name)
        tracked = [tb.get("branch") for tb in (meta.get("tracked_branches") or [])
                   if tb.get("branch")]
        if tracked:
            return tracked
        log.info("[%s] no tracked branches in catalog; falling back to default", name)
        return [default_branch]
    return [default_branch]


def _update_one(name: str, args, log) -> dict:
    """Update one repo. Returns a summary dict (never raises for indexing
    failures when called from `--all`; the caller decides how to react)."""
    repo_clone = REPOS_ROOT / name
    if not repo_clone.exists():
        return {"name": name, "status": "missing",
                "reason": f"{repo_clone} does not exist"}

    _migrate_if_legacy(name, log)

    meta = _read_repo_meta(name)
    default_branch = meta.get("default_branch") or _detect_default_branch(repo_clone, log)

    _step(["git", "-C", str(repo_clone), "fetch", "--all", "--prune"], log)
    branches = _resolve_branches_for_update(name, args, default_branch, log)
    results: list[dict] = []
    for br in branches:
        results.append(_index_one_branch(
            name, repo_clone, br, args.embed_model,
            rebuild=args.rebuild, log=log,
        ))
    meta["default_branch"] = default_branch
    _write_repo_meta(name, meta)
    _rewrite_repo_catalog(name, log)
    return {"name": name, "default_branch": default_branch, "branches": results,
            "count": len(results)}


def cmd_update(args) -> int:
    log = get_logger("repo-update")
    if not which("git"):
        die("git not on PATH.")

    if args.all:
        if args.name:
            die("pass either <name> or --all, not both")
        names = _known_repo_names()
        if not names:
            print(json.dumps({"updated": [], "reason": "no repos"}, indent=2))
            return 0
        log.info("updating %d repo(s): %s", len(names), ", ".join(names))
        results: list[dict] = []
        had_failure = False
        for n in names:
            try:
                results.append(_update_one(n, args, log))
            except SystemExit as e:  # die() raises SystemExit
                had_failure = True
                results.append({"name": n, "status": "failed", "reason": str(e)})
                log.warning("update failed for %s: %s", n, e)
        print(json.dumps({"updated": results, "count": len(results)},
                         indent=2, default=str))
        return 1 if had_failure else 0

    if not args.name:
        die("missing <name>. Pass a repo name or `--all`. "
            "List known repos with `adk repo list`.")
    result = _update_one(args.name, args, log)
    if result.get("status") == "missing":
        die(f"{result['reason']}. Run `adk repo add <url>` first.")
    print(json.dumps(result, indent=2))
    return 0


def cmd_branch_add(args) -> int:
    log = get_logger("repo-branch-add")
    if not which("git"):
        die("git not on PATH.")
    name = args.name
    repo_clone = REPOS_ROOT / name
    if not repo_clone.exists():
        die(f"{repo_clone} does not exist. Run `adk repo add <url>` first.")
    _migrate_if_legacy(name, log)

    branch = args.branch
    slug = slugify_branch(branch)
    if not slug:
        die(f"invalid branch name {branch!r}")
    branch_dir = _branch_dir(name, slug)
    if branch_dir.exists() and not args.yes:
        die(f"branch {branch!r} already tracked for {name}. "
            f"Use `adk repo update {name} --branch {branch}` to refresh, "
            f"or pass --yes to re-build from scratch.")

    if branch_dir.exists() and args.yes:
        log.info("removing existing branch dir before re-add: %s", branch_dir)
        shutil.rmtree(branch_dir)

    result = _index_one_branch(
        name, repo_clone, branch, args.embed_model,
        rebuild=True, log=log,
    )
    _rewrite_repo_catalog(name, log)
    print(json.dumps({"name": name, **result}, indent=2))
    return 0


def cmd_branch_remove(args) -> int:
    log = get_logger("repo-branch-remove")
    name = args.name
    branch = args.branch
    slug = slugify_branch(branch)
    if not slug:
        die(f"invalid branch name {branch!r}")
    branch_dir = _branch_dir(name, slug)
    if not branch_dir.exists():
        die(f"branch {branch!r} not tracked for {name}.")
    meta = _read_repo_meta(name)
    if meta.get("default_branch") == branch and not args.yes:
        die(f"refusing to remove the default branch {branch!r} for {name}. "
            f"Pass --yes to override.")
    log.info("removing branch dir: %s", branch_dir)
    shutil.rmtree(branch_dir)
    _rewrite_repo_catalog(name, log)
    print(json.dumps({"removed": branch, "slug": slug, "name": name}, indent=2))
    return 0


def cmd_branch_list(args) -> int:
    name = args.name
    repo_dir = _repo_dir(name)
    if not repo_dir.exists():
        print(f"(no repo: {name})")
        return 1
    branches_dir = repo_dir / "branches"
    if not branches_dir.exists():
        # Legacy layout — no per-branch dirs; report what's in repo-meta.
        meta = _read_repo_meta(name)
        default_branch = meta.get("default_branch") or "<unknown>"
        print(f"(legacy layout — only '{default_branch}' is indexed; "
              f"run `adk repo migrate {name}` to move it into branches/)")
        return 0
    rows: list[tuple[str, str, str, str]] = []
    for slug in _tracked_slugs(name):
        bm = _read_branch_meta(name, slug)
        rows.append((bm.get("branch") or slug, slug,
                     (bm.get("last_indexed_oid") or "")[:12],
                     bm.get("last_indexed_at") or "-"))
    if not rows:
        print("(no branches tracked)")
        return 0
    w_b = max(len(r[0]) for r in rows + [("branch", "", "", "")])
    w_s = max(len(r[1]) for r in rows + [("", "slug", "", "")])
    print(f"{'branch'.ljust(w_b)}  {'slug'.ljust(w_s)}  {'head':<12}  last_indexed_at")
    print(f"{'-' * w_b}  {'-' * w_s}  {'-' * 12}  {'-' * 20}")
    for b, s, h, t in rows:
        print(f"{b.ljust(w_b)}  {s.ljust(w_s)}  {h:<12}  {t}")
    return 0


def cmd_migrate(args) -> int:
    log = get_logger("repo-migrate")
    names = [args.name] if args.name else _known_repo_names()
    if not names:
        print(json.dumps({"migrated": [], "reason": "no repos"}, indent=2))
        return 0
    out = []
    for n in names:
        moved = _migrate_if_legacy(n, log)
        out.append({"name": n, "migrated": moved})
    print(json.dumps({"results": out}, indent=2))
    return 0


def cmd_list(args) -> int:
    if args.names_only:
        for n in _known_repo_names():
            print(n)
        return 0
    if not REPOS_ROOT.exists():
        print("(no repos)")
        return 0

    if args.branches:
        # Per-(repo, branch) view. One row per tracked branch; legacy repos
        # surface as one row each, marked.
        rows: list[tuple[str, str, str, str, str]] = []
        for d in sorted(REPOS_ROOT.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            name = d.name
            meta = _read_repo_meta(name)
            default_branch = meta.get("default_branch", "-")
            slugs = _tracked_slugs(name)
            if slugs:
                for slug in slugs:
                    bm = _read_branch_meta(name, slug)
                    rows.append((
                        name,
                        bm.get("branch") or slug,
                        (bm.get("last_indexed_oid") or "-")[:12],
                        bm.get("last_indexed_at") or "-",
                        "default" if (bm.get("branch") or slug) == default_branch else "",
                    ))
            else:
                # Legacy layout — synthesize a single row from repo-meta.
                rows.append((
                    name, default_branch,
                    (meta.get("last_indexed_oid") or "-")[:12],
                    meta.get("last_indexed_at") or "-",
                    "default (legacy)",
                ))
        if not rows:
            print("(no repos)")
            return 0
        w_n = max(len(r[0]) for r in rows + [("repo", "", "", "", "")])
        w_b = max(len(r[1]) for r in rows + [("", "branch", "", "", "")])
        print(f"{'repo'.ljust(w_n)}  {'branch'.ljust(w_b)}  "
              f"{'head':<12}  {'last_indexed_at':<20}  flags")
        print(f"{'-' * w_n}  {'-' * w_b}  {'-' * 12}  {'-' * 20}  -----")
        for n, b, h, t, f in rows:
            print(f"{n.ljust(w_n)}  {b.ljust(w_b)}  {h:<12}  {t:<20}  {f}")
        return 0

    # Default flat view — one row per repo (default branch's index).
    rows1: list[tuple[str, str, str, str]] = []
    for d in sorted(REPOS_ROOT.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        name = d.name
        meta = _read_repo_meta(name)
        default_branch = meta.get("default_branch", "-")
        # Find the default-branch index's SHA.
        default_slug = slugify_branch(default_branch) if default_branch != "-" else ""
        bm = _read_branch_meta(name, default_slug) if default_slug else {}
        head = bm.get("last_indexed_oid") or meta.get("last_indexed_oid") or "-"
        ts = bm.get("last_indexed_at") or meta.get("last_indexed_at") or "-"
        rows1.append((name, head[:12], ts, default_branch))
    if not rows1:
        print("(no repos)")
        return 0
    w_name = max(len(r[0]) for r in rows1 + [("name", "", "", "")])
    w_oid = max(len(r[1]) for r in rows1 + [("", "head", "", "")])
    w_branch = max(len(r[3]) for r in rows1 + [("", "", "", "branch")])
    print(f"{'name'.ljust(w_name)}  {'head'.ljust(w_oid)}  "
          f"{'last_indexed_at'.ljust(20)}  {'branch'.ljust(w_branch)}")
    print(f"{'-' * w_name}  {'-' * w_oid}  {'-' * 20}  {'-' * w_branch}")
    for name, oid, ts, br in rows1:
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
    sp_add.add_argument("--branch", action="append", default=None,
                        help="additional branch(es) to index alongside the default. "
                             "Repeat for multiple branches.")
    sp_add.add_argument("--skip-default", action="store_true",
                        help="don't auto-include the default branch; index only "
                             "the branches given via --branch.")
    sp_add.add_argument("--embed-model", default="nomic-embed-text",
                        help="ollama embed model (default: nomic-embed-text)")
    sp_add.add_argument("-y", "--yes", action="store_true",
                        help="proceed even if clone exists (skip clone, reindex in place)")
    sp_add.set_defaults(func=cmd_add)

    sp_upd = sub.add_parser("update", help="fetch + fast-forward + incremental reindex")
    sp_upd.add_argument("name", nargs="?", default=None,
                        help="repo name to update (omit when using --all)")
    sp_upd.add_argument("--all", action="store_true",
                        help="update every indexed repo under ~/.agents-devkit/repos/; "
                             "continues past per-repo failures and exits 1 if any failed")
    sp_upd.add_argument("--branch", action="append", default=None,
                        help="refresh only the named branch(es). Repeat for several.")
    sp_upd.add_argument("--all-branches", action="store_true",
                        help="refresh every tracked branch for the repo (default: "
                             "only the default branch).")
    sp_upd.add_argument("--rebuild", action="store_true",
                        help="ignore the HEAD-unchanged short-circuit AND drop the "
                             "incremental path: re-index from scratch.")
    sp_upd.add_argument("--embed-model", default="nomic-embed-text")
    sp_upd.add_argument("-y", "--yes", action="store_true")
    sp_upd.set_defaults(func=cmd_update)

    sp_branch = sub.add_parser("branch",
                               help="manage tracked branches for an existing repo")
    branch_sub = sp_branch.add_subparsers(dest="branch_cmd", required=True)

    sp_ba = branch_sub.add_parser("add",
                                  help="start tracking + index a new branch")
    sp_ba.add_argument("name", help="repo name (must already be cloned)")
    sp_ba.add_argument("--branch", required=True,
                       help="branch name to add (e.g. develop)")
    sp_ba.add_argument("--embed-model", default="nomic-embed-text")
    sp_ba.add_argument("-y", "--yes", action="store_true",
                       help="if the branch is already tracked, rebuild its index from scratch")
    sp_ba.set_defaults(func=cmd_branch_add)

    sp_br = branch_sub.add_parser("remove",
                                  help="drop the index for a branch (cannot remove the default)")
    sp_br.add_argument("name")
    sp_br.add_argument("--branch", required=True)
    sp_br.add_argument("-y", "--yes", action="store_true",
                       help="allow removing the default branch (dangerous)")
    sp_br.set_defaults(func=cmd_branch_remove)

    sp_bl = branch_sub.add_parser("list", help="show tracked branches for a repo")
    sp_bl.add_argument("name")
    sp_bl.add_argument("-y", "--yes", action="store_true")
    sp_bl.set_defaults(func=cmd_branch_list)

    sp_mig = sub.add_parser("migrate",
                            help="move legacy <repo>/code-index/ → "
                                 "<repo>/branches/<slug(default)>/code-index/. "
                                 "Idempotent; run on a single repo or all of them.")
    sp_mig.add_argument("name", nargs="?", default=None)
    sp_mig.add_argument("-y", "--yes", action="store_true")
    sp_mig.set_defaults(func=cmd_migrate)

    sp_list = sub.add_parser("list", help="list known repos")
    sp_list.add_argument("--names-only", action="store_true",
                         help="emit one repo name per line (for shell completion)")
    sp_list.add_argument("--branches", action="store_true",
                         help="per-(repo, branch) view instead of one row per repo")
    sp_list.add_argument("-y", "--yes", action="store_true")
    sp_list.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
