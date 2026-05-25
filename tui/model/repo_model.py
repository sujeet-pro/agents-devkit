from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

_LIB_DIR = Path(__file__).resolve().parents[2] / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import adk_repos_home  # noqa: E402


@dataclass(frozen=True)
class RepoBranchRow:
    repo_name: str
    branch: str
    slug: str
    created_by: str  # "user" | "auto"
    last_indexed_at: str | None
    last_used_at: str | None
    age_s: float | None  # seconds since last_used_at, or None if not set
    auto_reason: str | None


@dataclass(frozen=True)
class RepoRow:
    name: str
    url: str
    default_branch: str
    branches: tuple[RepoBranchRow, ...]


def default_repos_dir() -> Path:
    return adk_repos_home()


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


class RepoModel:
    """Reads $ADK_DATA_HOME/repos/ and exposes repos + branches as
    frozen dataclasses. Mtime-gated via a directory-fingerprint signature
    that samples both repo-meta.json and each branch-meta.json mtime."""

    def __init__(
        self,
        repos_dir: Path | None = None,
        *,
        now_fn: Callable[[], datetime] | None = None,
    ) -> None:
        self.repos_dir = repos_dir if repos_dir is not None else default_repos_dir()
        if now_fn is None:
            now_fn = lambda: datetime.now(tz=timezone.utc)  # noqa: E731
        self._now_fn = now_fn
        self._last_signature: tuple | None = None

    def _signature(self) -> tuple:
        if not self.repos_dir.exists():
            return ()
        items: list[tuple[str, float]] = []
        try:
            for p in self.repos_dir.iterdir():
                if not p.is_dir():
                    continue
                meta = p / "repo-meta.json"
                try:
                    items.append((p.name, meta.stat().st_mtime if meta.exists() else 0.0))
                except OSError:
                    items.append((p.name, 0.0))
                try:
                    for child in p.iterdir():
                        if child.is_dir() and child.name.startswith("branch-"):
                            bm = child / "branch-meta.json"
                            try:
                                items.append((
                                    f"{p.name}/{child.name}",
                                    bm.stat().st_mtime if bm.exists() else 0.0,
                                ))
                            except OSError:
                                items.append((f"{p.name}/{child.name}", 0.0))
                except OSError:
                    continue
        except OSError:
            return ()
        items.sort()
        return tuple(items)

    def has_changed(self) -> bool:
        cur = self._signature()
        return cur != self._last_signature

    def snapshot(self) -> list[RepoRow]:
        self._last_signature = self._signature()
        if not self.repos_dir.exists():
            return []
        now = self._now_fn()
        rows: list[RepoRow] = []
        try:
            entries = sorted(self.repos_dir.iterdir())
        except OSError:
            return []
        for p in entries:
            if not p.is_dir():
                continue
            meta_path = p / "repo-meta.json"
            if not meta_path.exists():
                continue
            try:
                raw = json.loads(meta_path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            name = str(raw.get("name") or p.name)
            branches = self._collect_branches(p, name, now)
            rows.append(RepoRow(
                name=name,
                url=str(raw.get("url") or raw.get("input_url") or ""),
                default_branch=str(raw.get("default_branch") or ""),
                branches=tuple(branches),
            ))
        return rows

    def _collect_branches(
        self, repo_dir: Path, repo_name: str, now: datetime,
    ) -> list[RepoBranchRow]:
        out: list[RepoBranchRow] = []
        try:
            entries = sorted(repo_dir.iterdir())
        except OSError:
            return out
        for child in entries:
            if not (child.is_dir() and child.name.startswith("branch-")):
                continue
            bm = child / "branch-meta.json"
            if not bm.exists():
                continue
            try:
                raw = json.loads(bm.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(raw, dict):
                continue
            last_used = _parse_iso(raw.get("last_used_at"))
            age_s = (now - last_used).total_seconds() if last_used is not None else None
            last_indexed_at = raw.get("last_indexed_at")
            last_used_at = raw.get("last_used_at")
            auto_reason = raw.get("auto_reason")
            out.append(RepoBranchRow(
                repo_name=repo_name,
                branch=str(raw.get("branch") or ""),
                slug=str(raw.get("slug") or child.name.removeprefix("branch-")),
                created_by=str(raw.get("created_by") or "user"),
                last_indexed_at=str(last_indexed_at) if last_indexed_at is not None else None,
                last_used_at=str(last_used_at) if last_used_at is not None else None,
                age_s=age_s,
                auto_reason=str(auto_reason) if auto_reason is not None else None,
            ))
        return out
