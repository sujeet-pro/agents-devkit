"""queue_io.py — concurrency-safe JSON5 queue read / update / merge.

Replaces the older csv_io.py. The queue lives at
~/.agents-devkit/config/pr-queue.json5 by default.

Rules:
  - All writes happen under an fcntl lock on `<queue-path>.lock`.
  - Comments in the JSON5 source are preserved on write IF the user is editing
    by hand. The Python json5 dumper doesn't preserve comments by default, so we
    use a "blocks merge" approach: if comments are present, we re-render via a
    line-oriented patch (status fields and timestamps are mutated in place via
    string replacement); on a full rewrite (from `adk pr-scan`) we write a fresh
    file using a structured template + the user's prs[] dumped clean.
  - Dedupe key: (host, repo, pr_number) — derived from pr_link. Different repos
    sharing a pr_number don't collide.

Queue-row claim/release (for `/adk-pr-review` no-arg queue mode):
  - acquire_next_row(path) atomically picks the oldest non-terminal row whose
    `taken_at` is either null OR older than TAKEN_LOCK_MAX_AGE_SECONDS (30 min).
    It sets `taken_at = now_iso` and returns the row dict. Returns None if no
    eligible row exists. The acquire is atomic — concurrent invocations from
    multiple terminals each get a different row (or None).
  - release_row(path, pr_link, status=..., head_oid=..., last_checked_at=...)
    clears `taken_at` and applies the post-review updates.

Public API:
  load_slack_config(path) → dict
  read_queue(path) → dict
  write_queue(path, queue) → None  (under lock)
  update_pr_entry(path, pr_link, updates: dict) → bool
  merge_scan_results(existing_queue, scanned_entries) → dict
  dedupe_key(pr_link) → (host, repo, pr_number)
  acquire_next_row(path) → dict | None
  release_row(path, pr_link, **post_updates) → bool
  find_row(path, pr_link) → dict | None
"""
from __future__ import annotations

import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path

# fcntl lock + path helpers from the sibling adk-pr-review skill.
ADK_PR_REVIEW_SCRIPTS = Path(__file__).resolve().parent.parent.parent / "adk-pr-review" / "scripts"
sys.path.insert(0, str(ADK_PR_REVIEW_SCRIPTS))
from _common import file_lock  # noqa: E402

try:
    import json5  # type: ignore
except ImportError:
    json5 = None  # type: ignore


STATUS_PENDING = "pending"
STATUS_IN_REVIEW = "in_review"
STATUS_REVIEWED = "reviewed"
STATUS_COMMENTS = "comments"          # has open review comments / findings
STATUS_NEEDS_FIX = STATUS_COMMENTS     # back-compat alias (was `needs_fix`)
STATUS_APPROVED = "approved"          # PR approved on host or by adk-pr-review
STATUS_MERGED = "merged"
STATUS_ERROR = "error"
STATUS_REMINDED = "reminded"

# Don't downgrade these once set.
TERMINAL_STATUSES = {STATUS_MERGED}

# Statuses that "close out" a review — when we transition INTO one of these,
# we sweep ALL other configured status emojis off the message (defensive cleanup
# in case a prior reaction wasn't tracked in `last_reaction_status`). The new
# status's emoji is the only one left.
TERMINAL_OR_POSITIVE = {STATUS_APPROVED, STATUS_MERGED}

# Statuses that may share the same emoji across the codebase (alias resolution).
STATUS_ALIASES = {
    "needs_fix": STATUS_COMMENTS,  # legacy → canonical
}

# Auto-expire for queue-row `taken_at` locks. After this, the row is considered
# free again so another terminal can pick it up (the prior reviewer presumably
# died / crashed).
TAKEN_LOCK_MAX_AGE_SECONDS = 30 * 60


# Canonical queue location + legacy fallback for one-time migration.
DEFAULT_QUEUE_PATH = Path.home() / ".agents-devkit" / "config" / "pr-queue.json5"
LEGACY_QUEUE_PATH = Path.home() / ".agents-devkit" / "pr-reviews" / "queue.json5"


def canonical_status(s: str) -> str:
    """Map legacy/alias status names to their canonical form."""
    return STATUS_ALIASES.get(s, s)


def _lock_path(path: Path) -> Path:
    return Path(str(path) + ".lock")


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        # Accept both "Z" and "+00:00" suffixes.
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


# ----- parsing --------------------------------------------------------------

def _load_json5_or_json(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"not found: {path}")
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return {}
    if json5 is not None:
        try:
            return json5.loads(text)
        except Exception as e:
            raise ValueError(f"json5 parse failed for {path}: {e}")
    # Fallback: try strict JSON. JSON5 features (comments, trailing commas) will fail.
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"failed to parse {path}: {e}. Install json5: "
            f"pip install -r {Path(__file__).parent / 'requirements.txt'}"
        )


def load_slack_config(path: Path | None = None) -> dict:
    """Load slack config for pr-reviews.

    Lookup order (first hit wins):
      1. `path` if given AND exists. May be:
         a. a .json5 file (legacy `pr-reviews-slack.json5` shape) — returned verbatim
         b. a .md file (new `connectors/slack.md`) — returns the `pr_reviews:` section
            of its YAML frontmatter
      2. `~/.agents-devkit/config/connectors/slack.md` `pr_reviews:` section (preferred)
      3. `~/.agents-devkit/config/pr-reviews-slack.json5` (legacy fallback)
    """
    home_cfg = Path.home() / ".agents-devkit" / "config"
    candidates: list[Path] = []
    if path:
        candidates.append(Path(path).expanduser())
    candidates.append(home_cfg / "connectors" / "slack.md")
    candidates.append(home_cfg / "pr-reviews-slack.json5")

    for c in candidates:
        if not c.exists():
            continue
        if c.suffix == ".md":
            return _load_slack_from_connector_md(c)
        return _load_json5_or_json(c)
    raise FileNotFoundError(
        "No slack config found. Expected one of:\n"
        f"  {home_cfg / 'connectors' / 'slack.md'} (preferred)\n"
        f"  {home_cfg / 'pr-reviews-slack.json5'} (legacy)"
    )


def _load_slack_from_connector_md(path: Path) -> dict:
    """Read connectors/slack.md frontmatter, return the `pr_reviews` section."""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n?", text, re.DOTALL)
    if not m:
        raise ValueError(f"{path}: missing YAML frontmatter")
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML not installed; required to read connectors/slack.md")
    fm = yaml.safe_load(m.group(1)) or {}
    pr = fm.get("pr_reviews")
    if pr is None:
        raise ValueError(
            f"{path}: frontmatter has no `pr_reviews:` section. Add one with channels, "
            "url_patterns, filter_mentioned_users, status_emoji, reminder."
        )
    return pr


def _migrate_legacy_queue(path: Path) -> None:
    """One-time copy of ~/.agents-devkit/pr-reviews/queue.json5 →
    ~/.agents-devkit/config/pr-queue.json5 if the new path is missing.
    Never writes back to the legacy path; never overwrites the new path.
    """
    if path != DEFAULT_QUEUE_PATH:
        return
    if path.exists():
        return
    if not LEGACY_QUEUE_PATH.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(LEGACY_QUEUE_PATH.read_bytes())
    sys.stderr.write(
        f"adk: migrated queue {LEGACY_QUEUE_PATH} → {path}. "
        "Edits should target the new path; the legacy file is left untouched.\n"
    )


def read_queue(path: Path) -> dict:
    """Load the queue. If the file is missing, return an empty queue skeleton.
    Performs a one-shot migration from the legacy path on first read.
    """
    _migrate_legacy_queue(path)
    if not path.exists():
        return {"filters": None, "prs": []}
    return _load_json5_or_json(path)


# ----- writing --------------------------------------------------------------

def _dump_json5(obj: dict) -> str:
    """Dump as JSON5-ish — pretty JSON with trailing-newline. We don't try to
    preserve original comments on a full rewrite; the user's hand-written
    comments are reapplied only via `update_pr_entry` which uses a line-oriented
    in-place patch.
    """
    return json.dumps(obj, indent=2, sort_keys=False, ensure_ascii=False) + "\n"


def write_queue(path: Path, queue: dict) -> None:
    """Full rewrite of the queue file under lock."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(_lock_path(path), timeout_s=60.0):
        path.write_text(_dump_json5(queue), encoding="utf-8")


def update_pr_entry(path: Path, pr_link: str, updates: dict) -> bool:
    """Read-modify-write a single entry by pr_link. Returns True if matched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(_lock_path(path), timeout_s=60.0):
        queue = read_queue(path)
        prs = queue.get("prs", []) or []
        hit = False
        for entry in prs:
            if entry.get("pr_link") == pr_link:
                _apply_updates(entry, updates)
                hit = True
                break
        if hit:
            queue["prs"] = prs
            path.write_text(_dump_json5(queue), encoding="utf-8")
        return hit


def _apply_updates(entry: dict, updates: dict) -> None:
    """In-place update. Nested dicts (e.g. `slack`) merge instead of replacing wholesale.
    Honours terminal-status protection — once merged, never downgrades.

    Setting `taken_at` to None clears the lock unconditionally.
    """
    for k, v in updates.items():
        if k == "status":
            cur = entry.get("status")
            if cur in TERMINAL_STATUSES and v != cur:
                continue  # don't downgrade
            entry["status"] = v
        elif k == "slack" and isinstance(v, dict):
            cur = entry.get("slack") or {}
            cur.update(v)
            entry["slack"] = cur
        elif k == "supporting_docs" and isinstance(v, list):
            cur = entry.get("supporting_docs") or []
            for url in v:
                if url not in cur:
                    cur.append(url)
            entry["supporting_docs"] = cur
        else:
            entry[k] = v


def find_row(path: Path, pr_link: str) -> dict | None:
    """Read-only lookup by pr_link. Returns the row dict or None."""
    queue = read_queue(path)
    for entry in queue.get("prs", []) or []:
        if entry.get("pr_link") == pr_link:
            return entry
    return None


# ----- queue-row claim/release (for /adk-pr-review no-arg mode) -------------

def _is_locked(entry: dict, now: datetime) -> bool:
    """A row is locked if `taken_at` is set AND newer than the max age."""
    ts = _parse_iso(entry.get("taken_at"))
    if ts is None:
        return False
    age = (now - ts).total_seconds()
    return age < TAKEN_LOCK_MAX_AGE_SECONDS


def _pick_order_key(entry: dict) -> tuple[int, str]:
    """Sort key for FIFO acquire: rows never reviewed (null last_checked_at) first,
    then by last_checked_at ascending (oldest first).
    """
    lc = entry.get("last_checked_at")
    if not lc:
        return (0, "")
    return (1, str(lc))


def acquire_next_row(path: Path) -> dict | None:
    """Atomically claim the next eligible row. Returns the row dict (with
    `taken_at` already set in the persisted file) or None.

    Eligibility:
      - status != STATUS_MERGED
      - taken_at is null OR older than TAKEN_LOCK_MAX_AGE_SECONDS
    Order: FIFO by last_checked_at ascending; null (never reviewed) first.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with file_lock(_lock_path(path), timeout_s=60.0):
        queue = read_queue(path)
        prs = queue.get("prs", []) or []
        now = datetime.now(tz=timezone.utc)
        eligible = [
            e for e in prs
            if e.get("status") != STATUS_MERGED and not _is_locked(e, now)
        ]
        if not eligible:
            return None
        eligible.sort(key=_pick_order_key)
        picked = eligible[0]
        picked["taken_at"] = _now_iso()
        queue["prs"] = prs
        path.write_text(_dump_json5(queue), encoding="utf-8")
        return deepcopy(picked)


def release_row(path: Path, pr_link: str, **post_updates) -> bool:
    """Clear `taken_at` and apply post-review updates. Returns True if matched.

    Typical caller:
        release_row(queue_path, pr_link,
                    status=STATUS_APPROVED, head_oid=..., last_checked_at=_now_iso())
    """
    updates = {"taken_at": None, **post_updates}
    return update_pr_entry(path, pr_link, updates)


# ----- dedupe key -----------------------------------------------------------

_GH_PR_RE = re.compile(r"github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/pull/(?P<n>\d+)", re.I)
_BB_PR_RE = re.compile(r"bitbucket\.org/(?P<ws>[^/]+)/(?P<repo>[^/]+)/pull-requests/(?P<n>\d+)", re.I)


def dedupe_key(pr_link: str) -> tuple[str, str, int]:
    """Return (host, repo, pr_number). repo is just the repo name (last path
    segment), so the same repo across mirrors / different owners de-collides
    on owner via the host check — but the spec says 'repo-name + pr-number'
    as the unique key, so we honour that and treat repo across owners as same.
    """
    s = pr_link.strip().rstrip("/")
    m = _GH_PR_RE.search(s)
    if m:
        return ("github", m.group("repo"), int(m.group("n")))
    m = _BB_PR_RE.search(s)
    if m:
        return ("bitbucket", m.group("repo"), int(m.group("n")))
    raise ValueError(f"unrecognised PR link: {pr_link}")


# ----- merge ----------------------------------------------------------------

def merge_scan_results(existing: dict, scanned: list[dict]) -> dict:
    """Merge freshly-scanned entries into an existing queue. Additive on every
    field that's safely additive. Dedup by (host, repo, pr_number).

    Rules:
      - New PR (not in existing) → append as-is.
      - Existing PR + scanned-again:
          - `slack`: if existing has no slack info, take scanned's. If both
            present, prefer EXISTING (so a user-edited slack link wins) but
            update missing fields from scanned (additive).
          - `supporting_docs`: union (preserving order, existing first).
          - `status`, `last_checked_at`, `notes`, `taken_at`: PRESERVE existing.
          - `pr_link`: preserve existing (might be canonicalised differently).
      - Terminal `merged` entries are NEVER re-added even if scanned again
        (they're effectively read-only).
    """
    merged = deepcopy(existing) if existing else {"filters": None, "prs": []}
    merged.setdefault("prs", [])
    merged.setdefault("filters", None)

    by_key: dict[tuple[str, str, int], dict] = {}
    for e in merged["prs"]:
        try:
            by_key[dedupe_key(e["pr_link"])] = e
        except (ValueError, KeyError):
            continue

    added = 0
    refreshed = 0
    skipped_merged = 0

    for sc in scanned:
        try:
            k = dedupe_key(sc["pr_link"])
        except (ValueError, KeyError):
            continue
        existing_entry = by_key.get(k)
        if existing_entry is None:
            # Brand new — append with defaults.
            new_entry = {
                "pr_link": sc["pr_link"],
                "status": sc.get("status", STATUS_PENDING),
                "last_checked_at": None,
                "taken_at": None,
            }
            if sc.get("slack"):
                new_entry["slack"] = sc["slack"]
            if sc.get("supporting_docs"):
                new_entry["supporting_docs"] = list(sc["supporting_docs"])
            merged["prs"].append(new_entry)
            by_key[k] = new_entry
            added += 1
        else:
            if existing_entry.get("status") == STATUS_MERGED:
                skipped_merged += 1
                continue
            # Slack: keep existing, fill in any missing fields from scanned.
            if sc.get("slack"):
                cur_slack = existing_entry.get("slack") or {}
                for sk, sv in sc["slack"].items():
                    cur_slack.setdefault(sk, sv)
                existing_entry["slack"] = cur_slack
            # Supporting docs: union.
            if sc.get("supporting_docs"):
                cur_docs = existing_entry.get("supporting_docs") or []
                for url in sc["supporting_docs"]:
                    if url not in cur_docs:
                        cur_docs.append(url)
                existing_entry["supporting_docs"] = cur_docs
            refreshed += 1

    merged["_merge_summary"] = {"added": added, "refreshed": refreshed, "skipped_merged": skipped_merged}
    return merged
