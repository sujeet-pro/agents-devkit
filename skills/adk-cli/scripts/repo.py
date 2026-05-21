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
from datetime import datetime, timezone
from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(THIS_DIR))
# Indexer modules live in scripts/lib/code_index/; shared helpers (_common,
# parse_pr_url, etc.) live alongside the PR-review skill scripts.
CODE_INDEX_LIB = THIS_DIR.parent.parent.parent / "scripts" / "lib" / "code_index"
ADK_PR_REVIEW_SCRIPTS = THIS_DIR.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
sys.path.insert(0, str(CODE_INDEX_LIB))

from _common import die, get_logger, which, ADK_HOME, REPOS_ROOT  # noqa: E402
from base_index import slugify_branch  # noqa: E402
from queue_io import _now_iso, _parse_iso  # noqa: E402

PY = sys.executable

_EXT_TO_LANG = {".ts": "ts", ".tsx": "ts", ".py": "py", ".go": "go", ".java": "java"}


# ----- helpers ------------------------------------------------------------

def _repo_name_from_url(url: str) -> str:
    """Extract a repo name. Handles https/ssh/ssh-protocol/path forms."""
    s = url.strip().rstrip("/")
    # ssh:// form: ssh://git@host/owner/repo(.git)
    m = re.match(r"^ssh://[^@]+@[^/]+/[^/]+/([^/]+?)(\.git)?$", s)
    if m:
        return m.group(1)
    # SCP/SSH form: git@host:owner/repo(.git)
    m = re.match(r"^[^@]+@[^:]+:[^/]+/([^/]+?)(\.git)?$", s)
    if m:
        return m.group(1)
    # https or local path: take the last path segment, strip .git.
    name = s.split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


# Hosts where we always rewrite HTTPS → SSH so the actual clone uses the
# user's ssh-agent identity (no password prompts, no token handling).
# Per user request: input flexibility on both forms, but the clone itself
# goes over ssh.
_HOST_HTTPS_RE = re.compile(
    r"^https?://([^/]+)/([^/]+)/(.+?)(?:\.git)?/?$", re.IGNORECASE,
)
_SSH_HOSTS = {
    "github.com", "bitbucket.org", "gitlab.com",
    # subdomains (e.g. ghe.example.com) are matched via the regex pattern;
    # this set is the well-known short list for emoji/logging only.
}


def _normalize_to_ssh(url: str) -> str:
    """Normalise a repo URL to its SSH form for `git clone`.

    Accepts the three common input forms and emits one of two outputs:

      Input                                          → Output (clone form)
      ─────────────────────────────────────────────── ────────────────────────────────
      https://github.com/owner/repo                   git@github.com:owner/repo.git
      https://github.com/owner/repo.git               git@github.com:owner/repo.git
      https://bitbucket.org/ws/repo                   git@bitbucket.org:ws/repo.git
      ssh://git@github.com/owner/repo.git             git@github.com:owner/repo.git
      git@github.com:owner/repo.git                   git@github.com:owner/repo.git (no-op)
      git@github.com:owner/repo                       git@github.com:owner/repo.git (add .git)
      /local/path/to/repo (or file://)                <unchanged> (no auth swap for local)

    Why: the user can paste either form (browser URL or git clone hint), but
    the actual `git clone` always goes over ssh — relies on the user's
    ssh-agent identity, no password prompts, no token handling. Local paths
    and file:// URLs pass through unchanged.

    Hosts that don't match the standard https://host/owner/repo shape (e.g.
    self-hosted forges with a /scm/ prefix) pass through unchanged with a
    warning; the user can pre-normalise if needed.
    """
    s = url.strip().rstrip("/")
    # Local path or file:// — never rewrite.
    if s.startswith(("/", "file://", ".")):
        return s
    # Already SSH (scp-style): just ensure .git suffix.
    m = re.match(r"^([^@]+@[^:]+:[^/]+/.+?)(\.git)?$", s)
    if m and "@" in s.split(":")[0]:
        head = m.group(1)
        return head + ".git"
    # ssh:// protocol form → scp form.
    m = re.match(r"^ssh://([^@]+@[^/]+)/(.+?)(?:\.git)?/?$", s)
    if m:
        auth_host, path = m.group(1), m.group(2)
        return f"{auth_host}:{path}.git"
    # HTTPS → SSH.
    m = _HOST_HTTPS_RE.match(s)
    if m:
        host, owner, repo = m.group(1), m.group(2), m.group(3)
        # Strip trailing .git if it slipped through (regex non-greedy).
        if repo.endswith(".git"):
            repo = repo[:-4]
        # Strip credentials embedded in https URLs (e.g. user:token@host).
        if "@" in host:
            host = host.rsplit("@", 1)[1]
        return f"git@{host}:{owner}/{repo}.git"
    # Unknown shape — return unchanged. Caller can decide whether to proceed.
    return s


def _detect_default_branch(bare_clone: Path, log) -> str:
    """Resolve the default branch from a bare clone's HEAD (set by
    `git clone --bare`). Falls back to 'main' then 'master'."""
    try:
        cp = subprocess.run(
            ["git", "symbolic-ref", "HEAD"],
            cwd=bare_clone, capture_output=True, text=True, check=False,
        )
        if cp.returncode == 0 and cp.stdout.strip():
            ref = cp.stdout.strip()
            if ref.startswith("refs/heads/"):
                return ref.removeprefix("refs/heads/")
            return ref.rsplit("/", 1)[-1]
    except Exception as e:
        log.warning("symbolic-ref failed: %s", e)
    # Heuristic fallback.
    for b in ("main", "master"):
        cp = subprocess.run(
            ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{b}"],
            cwd=bare_clone, capture_output=True, text=True, check=False,
        )
        if cp.returncode == 0:
            return b
    die(f"could not detect default branch in {bare_clone}")
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
    return REPOS_ROOT / name


def _repo_meta_path(name: str) -> Path:
    return _repo_dir(name) / "repo-meta.json"


def _bare_clone_dir(name: str) -> Path:
    """Bare clone: holds .git only, source for every worktree."""
    return _repo_dir(name) / "original-clone"


def _branch_dir(name: str, slug: str) -> Path:
    return _repo_dir(name) / f"branch-{slug}"


def _branch_worktree(name: str, slug: str) -> Path:
    """Worktree of the branch — `git worktree add` target."""
    return _branch_dir(name, slug) / "code"


def _branch_meta_path(name: str, slug: str) -> Path:
    return _branch_dir(name, slug) / "branch-meta.json"


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
    repo_dir = _repo_dir(name)
    if not repo_dir.exists():
        return []
    return sorted(
        d.name.removeprefix("branch-") for d in repo_dir.iterdir()
        if d.is_dir() and d.name.startswith("branch-")
    )


# ----- catalog ------------------------------------------------------------

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
    _write_repo_meta(name, meta)


# ----- index pipeline -----------------------------------------------------

def _full_index(worktree: Path, branch_dir: Path, embed_model: str, log) -> None:
    """Chunk + embed + SCIP-index the worktree into `branch_dir/code-index/`."""
    chunks_path = branch_dir / "code-index" / "chunks.jsonl"
    chunks_path.parent.mkdir(parents=True, exist_ok=True)
    _step([PY, str(CODE_INDEX_LIB / "chunker.py"),
           "--worktree", str(worktree), "--out", str(chunks_path)], log)
    _step([PY, str(CODE_INDEX_LIB / "embedder.py"),
           "--task-dir", str(branch_dir), "--chunks", str(chunks_path),
           "--model", embed_model, "--mode", "replace", "--json"], log)
    _step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
           "--task-dir", str(branch_dir), "--worktree", str(worktree), "--json"], log)


def _incremental_index(worktree: Path, branch_dir: Path, changed: list[str],
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
           "--worktree", str(worktree), "--files-list", str(files_list),
           "--out", str(delta)], log)
    _step([PY, str(CODE_INDEX_LIB / "embedder.py"),
           "--task-dir", str(branch_dir), "--chunks", str(delta),
           "--model", embed_model, "--mode", "incremental",
           "--replaced-files", str(files_list), "--json"], log)
    langs = sorted({_EXT_TO_LANG[Path(f).suffix.lower()]
                    for f in changed if Path(f).suffix.lower() in _EXT_TO_LANG})
    if langs:
        _step([PY, str(CODE_INDEX_LIB / "scip_runner.py"),
               "--task-dir", str(branch_dir), "--worktree", str(worktree),
               "--langs", ",".join(langs), "--json"], log)


# ----- per-branch index orchestration ------------------------------------

def _ensure_worktree(bare_clone: Path, worktree: Path, branch: str, log) -> None:
    """Make sure `worktree` is a worktree of `branch` checked out from
    `bare_clone`, refreshed to the latest remote head. Idempotent."""
    # Fetch the branch into the bare clone so we have an up-to-date ref.
    _step(["git", "-C", str(bare_clone), "fetch", "origin",
           f"+refs/heads/{branch}:refs/heads/{branch}"], log)
    if (worktree / ".git").exists():
        # Existing worktree — reset to the freshly-fetched branch tip.
        _step(["git", "-C", str(worktree), "reset", "--hard", branch], log)
        return
    # No worktree yet. If the dir exists but isn't a worktree, clear it.
    if worktree.exists():
        shutil.rmtree(worktree)
    worktree.parent.mkdir(parents=True, exist_ok=True)
    _step(["git", "-C", str(bare_clone), "worktree", "add",
           str(worktree), branch], log)


def _index_one_branch(name: str, bare_clone: Path, branch: str,
                      embed_model: str, *, rebuild: bool,
                      log, created_by: str = "user",
                      auto_reason: str | None = None) -> dict:
    """Refresh (or build from scratch) the index for one branch. Returns a
    summary dict including {branch, slug, head_sha, indexed, files_changed}.

    `created_by` records whether the branch index was added explicitly by the
    user or auto-created by pr-sync (§5.4). When the branch-meta.json already
    exists, the existing `created_by` is preserved — a user-promoted branch
    stays "user" even on a routine update.
    """
    slug = slugify_branch(branch)
    if not slug:
        return {"branch": branch, "status": "failed", "reason": "empty slug"}
    branch_dir = _branch_dir(name, slug)
    worktree = _branch_worktree(name, slug)
    bm = _read_branch_meta(name, slug)
    last_oid = bm.get("last_indexed_oid", "")
    # Preserve created_by + created_at on re-indexes; only set on first build.
    prior_created_by = bm.get("created_by") or created_by
    prior_created_at = bm.get("created_at") or _now_iso()
    prior_auto_reason = bm.get("auto_reason") or auto_reason

    _ensure_worktree(bare_clone, worktree, branch, log)
    new_oid = _current_oid(worktree)

    if new_oid == last_oid and not rebuild:
        log.info("[%s] HEAD unchanged at %s; skipping reindex (use --rebuild to force)",
                 branch, new_oid[:12])
        return {"branch": branch, "slug": slug, "head_sha": new_oid,
                "indexed": "skipped", "reason": "HEAD unchanged"}

    changed = _diff_files(worktree, last_oid, new_oid, log) if (last_oid and not rebuild) else []
    indexed = "full"
    if last_oid and changed and not rebuild:
        indexed = "incremental"
        _incremental_index(worktree, branch_dir, changed, embed_model, log)
    else:
        _full_index(worktree, branch_dir, embed_model, log)

    meta_out = {
        "name": name,
        "branch": branch,
        "slug": slug,
        "last_indexed_oid": new_oid,
        "last_indexed_sha": new_oid,  # v4 canonical field name (alias of last_indexed_oid)
        "last_indexed_at": _now_iso(),
        "embed_model": embed_model,
        "created_by": prior_created_by,
        "created_at": prior_created_at,
        "last_used_at": _now_iso(),
    }
    if prior_auto_reason:
        meta_out["auto_reason"] = prior_auto_reason
    _write_branch_meta(name, slug, meta_out)
    return {"branch": branch, "slug": slug, "head_sha": new_oid,
            "prev_sha": last_oid or None, "indexed": indexed,
            "files_changed": len(changed)}


# ----- subcommands --------------------------------------------------------

def cmd_add(args) -> int:
    log = get_logger("repo-add")
    if not which("git"):
        die("git not on PATH. brew install git.")

    # User can paste either https or ssh; the clone itself always uses ssh
    # so it relies on the user's ssh-agent identity (no tokens, no prompts).
    user_url = args.url
    clone_url = _normalize_to_ssh(user_url)
    if clone_url != user_url:
        log.info("normalised %s → %s for clone (input form preserved in repo-meta)",
                 user_url, clone_url)
    name = args.name or _repo_name_from_url(clone_url)
    bare_clone = _bare_clone_dir(name)

    if bare_clone.exists():
        if not args.yes:
            die(f"{bare_clone} already exists. Pass --yes to refresh in place "
                f"(no reclone), or use `adk repo update {name}` instead.")
        log.info("%s exists — skipping clone, falling through to reindex", bare_clone)
    else:
        bare_clone.parent.mkdir(parents=True, exist_ok=True)
        _step(["git", "clone", "--bare", clone_url, str(bare_clone)], log)

    default_branch = _detect_default_branch(bare_clone, log)
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
    # Record both the user-supplied URL (whatever form they pasted) AND the
    # normalised SSH URL we cloned through, so the user can audit later.
    _write_repo_meta(name, {
        "name": name,
        "url": clone_url,                # canonical: the ssh URL git is using
        "input_url": user_url,           # what the user originally typed
        "clone_path": str(bare_clone),
        "default_branch": default_branch,
        "tracked_branches": [],
    })

    results: list[dict] = []
    for br in branches:
        log.info("indexing %s/%s", name, br)
        results.append(_index_one_branch(
            name, bare_clone, br, args.embed_model,
            rebuild=True, log=log,
        ))
    _rewrite_repo_catalog(name, log)
    print(json.dumps({
        "name": name, "clone_path": str(bare_clone),
        "default_branch": default_branch, "branches": results,
    }, indent=2))
    return 0


def _known_repo_names() -> list[str]:
    """Names of every repo currently registered under REPOS_ROOT (those with
    an `original-clone/` directory)."""
    if not REPOS_ROOT.exists():
        return []
    return sorted(d.name for d in REPOS_ROOT.iterdir()
                  if d.is_dir() and not d.name.startswith(".")
                  and (d / "original-clone").exists())


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
    bare_clone = _bare_clone_dir(name)
    if not bare_clone.exists():
        return {"name": name, "status": "missing",
                "reason": f"{bare_clone} does not exist"}

    meta = _read_repo_meta(name)
    default_branch = meta.get("default_branch") or _detect_default_branch(bare_clone, log)

    _step(["git", "-C", str(bare_clone), "fetch", "--all", "--prune"], log)
    branches = _resolve_branches_for_update(name, args, default_branch, log)
    results: list[dict] = []
    for br in branches:
        results.append(_index_one_branch(
            name, bare_clone, br, args.embed_model,
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
    bare_clone = _bare_clone_dir(name)
    if not bare_clone.exists():
        die(f"{bare_clone} does not exist. Run `adk repo add <url>` first.")

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
        worktree = _branch_worktree(name, slug)
        if (worktree / ".git").exists():
            _step(["git", "-C", str(bare_clone), "worktree", "remove",
                   "--force", str(worktree)], log)
        shutil.rmtree(branch_dir, ignore_errors=True)

    # v4 §5.4 auto-base support: --auto records the branch as "auto" in
    # branch-meta.json so the cleanup pass (P5) can tell user-created bases
    # apart from those added by pr-sync's Phase C.
    created_by = "auto" if getattr(args, "auto", False) else "user"
    auto_reason = getattr(args, "auto_reason", None)
    result = _index_one_branch(
        name, bare_clone, branch, args.embed_model,
        rebuild=True, log=log,
        created_by=created_by, auto_reason=auto_reason,
    )
    _rewrite_repo_catalog(name, log)
    print(json.dumps({"name": name, **result, "created_by": created_by}, indent=2))
    return 0


def cmd_rebuild_index(args) -> int:
    """Rebuild the index for one repo+branch from scratch. Use when the
    branch-<slug>/code-index/ folder was deleted by hand and the catalog
    needs to be reconstructed. Equivalent to `adk repo branch add --yes`
    but doesn't require the branch to be untracked.

    Plan §8 P3 exit: 'adk repo rebuild-index works when a folder was
    deleted by hand.'
    """
    log = get_logger("repo-rebuild-index")
    if not which("git"):
        die("git not on PATH.")
    name = args.name
    bare_clone = _bare_clone_dir(name)
    if not bare_clone.exists():
        die(f"{bare_clone} does not exist. Run `adk repo add <url>` first.")

    # Branch — use --branch if given, else the repo's default_branch from
    # repo-meta.json, else detect from the clone.
    branch = getattr(args, "branch", None)
    if not branch:
        meta = _read_repo_meta(name)
        branch = meta.get("default_branch") or _detect_default_branch(bare_clone, log)
    slug = slugify_branch(branch)
    if not slug:
        die(f"invalid branch name {branch!r}")

    branch_dir = _branch_dir(name, slug)
    if branch_dir.exists():
        log.info("clearing existing branch dir before rebuild: %s", branch_dir)
        worktree = _branch_worktree(name, slug)
        if (worktree / ".git").exists():
            _step(["git", "-C", str(bare_clone), "worktree", "remove",
                   "--force", str(worktree)], log)
        shutil.rmtree(branch_dir, ignore_errors=True)

    # Preserve created_by if a stale branch-meta still exists (it shouldn't
    # at this point, since we just rmtree'd, but be defensive).
    result = _index_one_branch(
        name, bare_clone, branch, args.embed_model,
        rebuild=True, log=log, created_by="user",
    )
    _rewrite_repo_catalog(name, log)
    print(json.dumps({"name": name, **result, "action": "rebuilt"}, indent=2))
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
    _drop_branch_dir(name, slug, log)
    _rewrite_repo_catalog(name, log)
    print(json.dumps({"removed": branch, "slug": slug, "name": name}, indent=2))
    return 0


def cmd_branch_list(args) -> int:
    name = args.name
    repo_dir = _repo_dir(name)
    if not repo_dir.exists():
        print(f"(no repo: {name})")
        return 1
    slugs = _tracked_slugs(name)
    if not slugs:
        print(f"(no branches tracked for {name})")
        return 0
    rows: list[tuple[str, str, str, str]] = []
    for slug in slugs:
        bm = _read_branch_meta(name, slug)
        rows.append((bm.get("branch") or slug, slug,
                     (bm.get("last_indexed_oid") or "")[:12],
                     bm.get("last_indexed_at") or "-"))
    w_b = max(len(r[0]) for r in rows + [("branch", "", "", "")])
    w_s = max(len(r[1]) for r in rows + [("", "slug", "", "")])
    print(f"{'branch'.ljust(w_b)}  {'slug'.ljust(w_s)}  {'head':<12}  last_indexed_at")
    print(f"{'-' * w_b}  {'-' * w_s}  {'-' * 12}  {'-' * 20}")
    for b, s, h, t in rows:
        print(f"{b.ljust(w_b)}  {s.ljust(w_s)}  {h:<12}  {t}")
    return 0


def _drop_branch_dir(name: str, slug: str, log) -> None:
    """Remove a branch's worktree (if any) + its branch_dir. Used by
    branch-remove and auto-base cleanup."""
    branch_dir = _branch_dir(name, slug)
    if not branch_dir.exists():
        return
    bare_clone = _bare_clone_dir(name)
    worktree = _branch_worktree(name, slug)
    if (worktree / ".git").exists() and bare_clone.exists():
        _step(["git", "-C", str(bare_clone), "worktree", "remove",
               "--force", str(worktree)], log)
    shutil.rmtree(branch_dir, ignore_errors=True)


def _list_auto_bases() -> list[dict]:
    """v4 §5.4: enumerate every branch dir with branch-meta.created_by == 'auto'.

    Returns one dict per (repo, branch) auto-base, with the meta fields the
    cleanup pass needs: name, branch, slug, created_at, last_used_at,
    auto_reason.
    """
    out: list[dict] = []
    if not REPOS_ROOT.exists():
        return out
    for repo_dir in sorted(REPOS_ROOT.iterdir()):
        if not repo_dir.is_dir() or repo_dir.name.startswith("."):
            continue
        name = repo_dir.name
        for branch_dir in sorted(repo_dir.iterdir()):
            if not branch_dir.is_dir() or not branch_dir.name.startswith("branch-"):
                continue
            slug = branch_dir.name.removeprefix("branch-")
            bm = _read_branch_meta(name, slug)
            if (bm.get("created_by") or "user") != "auto":
                continue
            out.append({
                "name": name,
                "branch": bm.get("branch") or slug,
                "slug": slug,
                "created_at": bm.get("created_at"),
                "last_used_at": bm.get("last_used_at"),
                "auto_reason": bm.get("auto_reason"),
                "path": str(branch_dir),
            })
    return out


def _auto_base_in_use(name: str, branch: str, queue_path: Path) -> bool:
    """Check whether any non-terminal queue row references this auto-base
    (as target_branch OR as prep_used_base.branch). Used by cleanup to
    avoid deleting a base that just gained a user.
    """
    sys.path.insert(0, str(THIS_DIR))
    from queue_io import read_queue, TERMINAL_STATUSES  # local import to avoid cycle
    queue = read_queue(queue_path)
    prs = queue.get("prs", []) or []
    for e in prs:
        if (e.get("status") or "") in TERMINAL_STATUSES:
            continue
        if e.get("target_branch") == branch:
            return True
        used = e.get("prep_used_base") or {}
        if isinstance(used, dict) and used.get("branch") == branch:
            return True
    return False


def cmd_auto_bases_list(args) -> int:
    """List every auto-created branch index."""
    bases = _list_auto_bases()
    if not bases:
        print(json.dumps({"auto_bases": [], "count": 0}, indent=2))
        return 0
    print(json.dumps({"auto_bases": bases, "count": len(bases)}, indent=2))
    return 0


def cmd_auto_bases_clean(args) -> int:
    """Delete auto-bases with 0 active users + >= auto_base_ttl_hours of age.

    A base is considered in use if any non-terminal queue row has the
    same target_branch or prep_used_base.branch.

    --force <repo> --branch X clears ONE specific base unconditionally.
    --dry-run shows what would be deleted; no action.
    -y / --yes confirms the bulk clean.
    """
    log = get_logger("repo-auto-bases-clean")
    queue_path = Path(args.queue).expanduser() if getattr(args, "queue", None) \
        else Path.home() / ".agents-devkit" / "config" / "pr-queue.json5"

    # --force one specific base.
    if getattr(args, "force", False):
        if not (args.name and args.branch):
            die("--force requires both <name> and --branch X")
        slug = slugify_branch(args.branch)
        branch_dir = _branch_dir(args.name, slug)
        if not branch_dir.exists():
            print(json.dumps({"action": "noop", "reason": "not found",
                              "name": args.name, "branch": args.branch}, indent=2))
            return 0
        bm = _read_branch_meta(args.name, slug)
        if (bm.get("created_by") or "user") != "auto":
            die(f"refusing to force-clean a user-created base "
                f"({args.name}:{args.branch}); user bases are never auto-cleaned. "
                f"Use `adk repo branch remove` instead.")
        if args.dry_run:
            print(json.dumps({"action": "would_force_delete",
                              "name": args.name, "branch": args.branch,
                              "path": str(branch_dir)}, indent=2))
            return 0
        _drop_branch_dir(args.name, slug, log)
        _rewrite_repo_catalog(args.name, log)
        print(json.dumps({"action": "force_deleted",
                          "name": args.name, "branch": args.branch}, indent=2))
        return 0

    # Bulk clean.
    import os
    # Resolution order: env var (operator escape hatch) → adk-cli.json5 →
    # built-in default of 24h. Env wins so a one-off scripted run can lower
    # the TTL without touching the config file.
    ttl_hours_default = 24.0
    try:
        # scripts/config_io.py is the sibling of scripts/lib/code_index/, so
        # add its parent to sys.path on first use.
        sys.path.insert(0, str(CODE_INDEX_LIB.parent.parent))
        from config_io import get_adk_cli  # noqa: WPS433
        ttl_cfg = get_adk_cli("pr_sync", "auto_demote_ttl_hours",
                              default=ttl_hours_default)
        ttl_hours_default = float(ttl_cfg)
    except Exception:
        pass
    ttl_hours = float(os.environ.get("ADK_AUTO_BASE_TTL_HOURS", ttl_hours_default))
    now_dt = datetime.now(tz=timezone.utc)
    eligible: list[dict] = []
    for ab in _list_auto_bases():
        created = _parse_iso(ab.get("created_at"))
        if created is None:
            log.warning("auto-base %s:%s has no created_at; skipping",
                        ab["name"], ab["branch"])
            continue
        age_h = (now_dt - created).total_seconds() / 3600.0
        if age_h < ttl_hours:
            continue
        if _auto_base_in_use(ab["name"], ab["branch"], queue_path):
            continue
        eligible.append(ab)

    if args.dry_run:
        print(json.dumps({"action": "dry_run", "would_delete": eligible,
                          "count": len(eligible)}, indent=2))
        return 0
    if not args.yes:
        if not eligible:
            print(json.dumps({"action": "noop", "count": 0,
                              "reason": "no eligible auto-bases"}, indent=2))
            return 0
        print(f"Would delete {len(eligible)} auto-base(s). Re-run with --yes.")
        return 2

    deleted: list[dict] = []
    for ab in eligible:
        slug = slugify_branch(ab["branch"])
        try:
            _drop_branch_dir(ab["name"], slug, log)
            deleted.append({"name": ab["name"], "branch": ab["branch"]})
            _rewrite_repo_catalog(ab["name"], log)
        except OSError as e:
            log.warning("failed to clean %s:%s: %s", ab["name"], ab["branch"], e)
    print(json.dumps({"action": "deleted", "deleted": deleted,
                      "count": len(deleted)}, indent=2))
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
        # Per-(repo, branch) view. One row per tracked branch.
        rows: list[tuple[str, str, str, str, str]] = []
        for d in sorted(REPOS_ROOT.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            name = d.name
            meta = _read_repo_meta(name)
            default_branch = meta.get("default_branch", "-")
            for slug in _tracked_slugs(name):
                bm = _read_branch_meta(name, slug)
                rows.append((
                    name,
                    bm.get("branch") or slug,
                    (bm.get("last_indexed_oid") or "-")[:12],
                    bm.get("last_indexed_at") or "-",
                    "default" if (bm.get("branch") or slug) == default_branch else "",
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
        head = bm.get("last_indexed_oid") or "-"
        ts = bm.get("last_indexed_at") or "-"
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
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="write a structured DEBUG log to ~/.agents-devkit/logs/")
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
    sp_ba.add_argument("--rebuild", "-y", dest="yes", action="store_true",
                       help="if the branch is already tracked, rebuild its index "
                            "from scratch. (`-y` is a deprecated alias for --rebuild.)")
    sp_ba.add_argument("--auto", action="store_true",
                       help="v4 §5.4: mark this branch as auto-created (by pr-sync), "
                            "so the auto-base cleanup pass can tell it from user-added bases")
    sp_ba.add_argument("--auto-reason", default=None,
                       help="optional human-readable reason recorded when --auto is set "
                            "(e.g. 'shared by 3 PRs: #1234, #1235, #1240')")
    sp_ba.set_defaults(func=cmd_branch_add)

    sp_rb = sub.add_parser("rebuild-index",
                           help="rebuild the index for a branch (when its dir was deleted by hand)")
    sp_rb.add_argument("name", help="repo name")
    sp_rb.add_argument("--branch", default=None,
                       help="branch to rebuild (default: the repo's default_branch)")
    sp_rb.add_argument("--embed-model", default="nomic-embed-text")
    sp_rb.add_argument("-y", "--yes", action="store_true")
    sp_rb.set_defaults(func=cmd_rebuild_index)

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

    sp_ab = sub.add_parser("auto-bases",
                           help="v4 §5.4: manage auto-created branch indices")
    ab_sub = sp_ab.add_subparsers(dest="ab_cmd", required=True)
    sp_abl = ab_sub.add_parser("list", help="list every auto-created branch index")
    sp_abl.set_defaults(func=cmd_auto_bases_list)
    sp_abc = ab_sub.add_parser("clean",
                               help="delete auto-bases with 0 active users + >= 24h old")
    sp_abc.add_argument("--queue", default=None,
                        help="path to pr-queue.json5 (default: ~/.agents-devkit/config/pr-queue.json5)")
    sp_abc.add_argument("--dry-run", action="store_true")
    sp_abc.add_argument("-y", "--yes", action="store_true")
    sp_abc.add_argument("--force", action="store_true",
                        help="force-clean one specific auto-base (requires --name + --branch)")
    sp_abc.add_argument("--name", default=None, help="repo name (with --force)")
    sp_abc.add_argument("--branch", default=None, help="branch name (with --force)")
    sp_abc.set_defaults(func=cmd_auto_bases_clean)

    sp_list = sub.add_parser("list", help="list known repos")
    sp_list.add_argument("--names-only", action="store_true",
                         help="emit one repo name per line (for shell completion)")
    sp_list.add_argument("--branches", action="store_true",
                         help="per-(repo, branch) view instead of one row per repo")
    sp_list.add_argument("-y", "--yes", action="store_true")
    sp_list.set_defaults(func=cmd_list)

    args = ap.parse_args(argv)
    if getattr(args, "verbose", False):
        from _verbose import setup_verbose  # type: ignore  # noqa: WPS433
        setup_verbose("repo", enabled=True, argv=argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
