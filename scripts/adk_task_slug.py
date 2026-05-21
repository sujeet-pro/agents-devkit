#!/usr/bin/env python3
"""adk_task_slug.py — resolve the task folder for a skill invocation.

Single source of truth for path resolution: shared/paths.md.

Two roots:
  - repo-bound: <repo>/.temp/adk/<skill-stem>/<task>/
  - global:     ~/.agents-devkit/<area>/<task>/

Skill scopes:
  - repo-bound (always): implement, document
  - global    (always): pr-review, investigate, setup, improve, explain
  - hybrid    (caller picks): review, sync
      review → repo if input is local path or no URL; else global at ~/.agents-devkit/reviews/
      sync   → repo if --repo-coupled; else global at ~/.agents-devkit/sync/

Slug rules:
  - lowercase ASCII letters + digits + hyphens; max 60 chars
  - dedup against existing folders by appending -2, -3, …
  - input discriminators preserved: SF-1234 (jira), pr-123 (gh/bb), issue-456 (gh)

Usage:
  python3 scripts/adk_task_slug.py --skill implement --input "SF-1234 coupon engine" --create --json
  python3 scripts/adk_task_slug.py --skill pr-review --input https://github.com/acme/foo/pull/42 --json
  python3 scripts/adk_task_slug.py --skill investigate --input "checkout 500s" --scope global --json
  python3 scripts/adk_task_slug.py --skill review --input . --scope auto --json   # → repo
  python3 scripts/adk_task_slug.py --skill review --input https://github.com/acme/foo/pull/42 --scope auto --json  # → global
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

MAX_LEN = 60
JIRA_KEY = re.compile(r"\b([A-Z][A-Z0-9]+)-(\d+)\b")
GH_PR = re.compile(r"github\.com/[^/]+/[^/]+/pull/(\d+)", re.I)
GH_ISSUE = re.compile(r"github\.com/[^/]+/[^/]+/issues/(\d+)", re.I)
BB_PR = re.compile(r"bitbucket\.org/[^/]+/([^/]+)/pull-requests/(\d+)", re.I)
GH_PR_REPO = re.compile(r"github\.com/[^/]+/([^/]+)/pull/(\d+)", re.I)

URL_JUNK = re.compile(r"https?://|www\.|\.com\b|\.io\b|\.atlassian\.net\b|\.slack\.com\b", re.I)
SLUG_STOPWORDS = {"https", "http", "www", "com", "io", "the", "a", "an", "for", "of", "on", "in"}

# Per shared/paths.md
ALWAYS_REPO_BOUND = {"implement", "document"}
ALWAYS_GLOBAL = {"pr-review", "pr-reviews", "investigate", "setup", "improve", "explain"}
HYBRID = {"review", "sync"}

# Area name under ~/.agents-devkit/ for global skills. v4: every skill has a
# `skill-<stem>/` task-root. The pre-v4 layout (pr-reviews, investigations,
# reviews, sync, setup, improve, explain) is the legacy path; resolve_path()
# falls back to the legacy name when the new dir doesn't exist on disk but
# the legacy one does (preserves the user's in-flight work until P7
# migrates).
GLOBAL_AREA = {
    "pr-review": "skill-pr-review",
    "pr-reviews": "skill-pr-review",   # batch shares the per-PR root; the batch state is the CSV.
    "investigate": "skill-investigate",
    "review": "skill-review",
    "sync": "skill-sync",
    "setup": "skill-setup",
    "improve": "skill-improve",
    "explain": "skill-explain",
    "document": "skill-document",
    "implement": "skill-implement",
}

# Legacy v3 area names (kept for read-shim fallback only; never written to).
LEGACY_GLOBAL_AREA = {
    "skill-pr-review": "pr-reviews",
    "skill-investigate": "investigations",
    "skill-review": "reviews",
    "skill-sync": "sync",
    "skill-setup": "setup",
    "skill-improve": "improve",
    "skill-explain": "explain",
}

GLOBAL_ROOT = Path.home() / ".agents-devkit"


def find_discriminator(text: str) -> tuple[str, dict] | tuple[None, dict]:
    """Return (discriminator, parsed) — parsed has whatever entities we extracted."""
    parsed: dict = {}
    m = JIRA_KEY.search(text)
    if m:
        key = f"{m.group(1)}-{m.group(2)}"
        parsed["jira_key"] = key
        return key, parsed
    m = GH_PR_REPO.search(text)
    if m:
        repo, n = m.group(1), m.group(2)
        parsed["github_repo"] = repo
        parsed["pr_number"] = int(n)
        return f"{repo}_pr-{n}", parsed
    m = BB_PR.search(text)
    if m:
        repo, n = m.group(1), m.group(2)
        parsed["bitbucket_repo"] = repo
        parsed["pr_number"] = int(n)
        return f"{repo}_pr-{n}", parsed
    m = GH_ISSUE.search(text)
    if m:
        n = m.group(1)
        parsed["issue_number"] = int(n)
        return f"issue-{n}", parsed
    return None, parsed


def slugify(text: str) -> str:
    text = URL_JUNK.sub(" ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    parts = [p for p in text.split("-") if p and p not in SLUG_STOPWORDS]
    text = "-".join(parts)
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN].rstrip("-")
    return text or "task"


def build_slug(skill_stem: str, input_text: str) -> tuple[str, dict]:
    """Return (slug, parsed-entities). The slug does NOT carry the skill prefix —
    the skill is the parent folder under .temp/adk/<skill>/ or ~/.agents-devkit/<area>/.
    """
    if not input_text.strip():
        # No input ⇒ timestamp slug
        return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()), {}
    disc, parsed = find_discriminator(input_text)
    if disc:
        return disc, parsed
    return slugify(input_text), parsed


def find_repo_root(start: Path) -> Path | None:
    p = start.resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / ".git").exists():
            return ancestor
    return None


def resolve_scope(skill_stem: str, scope_flag: str, input_text: str, cwd: Path) -> str:
    """Return 'repo' or 'global'."""
    if scope_flag in ("repo", "global"):
        return scope_flag
    if skill_stem in ALWAYS_REPO_BOUND:
        return "repo"
    if skill_stem in ALWAYS_GLOBAL:
        return "global"
    # Hybrid:
    if skill_stem == "review":
        # If input is a path or empty, repo-bound. If it's a URL pointing OUTSIDE
        # the current repo, global. Conservative: if URL present and we can't
        # match it to cwd, choose global.
        if input_text.strip() in ("", ".") or Path(input_text).expanduser().exists():
            return "repo" if find_repo_root(cwd) else "global"
        if "://" in input_text:
            return "global"
        return "repo" if find_repo_root(cwd) else "global"
    if skill_stem == "sync":
        # Default to global unless explicitly inside a repo AND the user implied
        # repo-coupling (we don't have a great signal, so default global).
        return "global"
    return "global"


def base_dir_for(skill_stem: str, scope: str, cwd: Path) -> Path:
    if scope == "repo":
        repo = find_repo_root(cwd)
        if not repo:
            raise SystemExit(
                f"adk_task_slug: scope=repo but cwd {cwd} is not inside a git repo"
            )
        return repo / ".temp" / "adk" / skill_stem
    # global — prefer the v4 path; fall back to the legacy v3 path ONLY if
    # the new one is absent AND the legacy one exists on disk (preserves the
    # user's in-flight task folders until P7 migrates the data).
    area = GLOBAL_AREA.get(skill_stem, skill_stem)
    new = GLOBAL_ROOT / area
    legacy_area = LEGACY_GLOBAL_AREA.get(area)
    if not new.exists() and legacy_area:
        legacy = GLOBAL_ROOT / legacy_area
        if legacy.exists():
            return legacy
    return new


def dedup(slug: str, parent: Path) -> str:
    if not (parent / slug).exists():
        return slug
    n = 2
    while (parent / f"{slug}-{n}").exists():
        n += 1
    return f"{slug}-{n}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", required=True, help="skill stem (no /adk- prefix), e.g. implement, pr-review")
    ap.add_argument("--input", default="", help="user prompt / URL / description")
    ap.add_argument("--scope", default="auto", choices=("auto", "repo", "global"), help="path scope")
    ap.add_argument("--cwd", default=None, help="cwd override (used to find the repo root for repo-bound skills)")
    ap.add_argument("--temp-root", default=None, help="explicit base dir (overrides scope logic)")
    ap.add_argument("--create", action="store_true", help="mkdir the task folder + write prompt.txt")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("rest", nargs="*")
    args = ap.parse_args()

    text = (args.input or " ".join(args.rest)).strip()
    skill_stem = args.skill.lstrip("/").removeprefix("adk-")
    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()

    if args.temp_root:
        base = Path(args.temp_root).expanduser().resolve()
        scope = "explicit"
    else:
        scope = resolve_scope(skill_stem, args.scope, text, cwd)
        base = base_dir_for(skill_stem, scope, cwd)

    slug, parsed = build_slug(skill_stem, text)
    # Folder dedup is per base folder.
    base.mkdir(parents=True, exist_ok=True)
    slug = dedup(slug, base)
    task_dir = base / slug

    if args.create:
        task_dir.mkdir(parents=True, exist_ok=True)
        prompt_path = task_dir / "prompt.txt"
        if not prompt_path.exists():
            prompt_path.write_text(text + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({
            "skill": skill_stem,
            "scope": scope,
            "base": str(base),
            "slug": slug,
            "task_dir": str(task_dir),
            "created": args.create,
            "parsed": parsed,
        }, indent=2))
        return 0

    print(task_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
