#!/usr/bin/env python3
"""adk_task_slug.py — generate a kebab-case task slug from a free-form prompt
and (optionally) create the .temp/<slug>/ working dir.

Slug rules:
  - lowercase ASCII letters + digits + hyphens only
  - max 60 chars
  - dedup against existing slugs in .temp/ by appending -2, -3, …
  - if input has a "key" pattern (jira: SF-1234, pr: #123, github: pr/123), preserve it as the leading discriminator.

Usage:
  python3 scripts/adk_task_slug.py "implement SF-1234 coupon engine"          # prints "implement-SF-1234-coupon-engine"
  python3 scripts/adk_task_slug.py --skill implement --input "fix the bug"    # prints "implement-fix-the-bug"
  python3 scripts/adk_task_slug.py --skill review --input <pr-url> --create   # creates .temp/review-pr-123/
  python3 scripts/adk_task_slug.py --skill review --input <pr-url> --json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

MAX_LEN = 60
JIRA_KEY = re.compile(r"\b([A-Z][A-Z0-9]+)-(\d+)\b")
GH_PR = re.compile(r"github\.com/[^/]+/[^/]+/pull/(\d+)", re.I)
GH_ISSUE = re.compile(r"github\.com/[^/]+/[^/]+/issues/(\d+)", re.I)


def find_discriminator(text: str) -> str | None:
    m = JIRA_KEY.search(text)
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    m = GH_PR.search(text)
    if m:
        return f"pr-{m.group(1)}"
    m = GH_ISSUE.search(text)
    if m:
        return f"issue-{m.group(1)}"
    return None


URL_JUNK = re.compile(r"https?://|www\.|\.com\b|\.io\b|\.atlassian\.net\b|\.slack\.com\b", re.I)
# Words that contribute nothing to a slug
SLUG_STOPWORDS = {"https", "http", "www", "com", "io", "the", "a", "an", "for", "of", "on", "in"}


def slugify(text: str) -> str:
    text = URL_JUNK.sub(" ", text)
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    # Drop stopwords
    parts = [p for p in text.split("-") if p and p not in SLUG_STOPWORDS]
    text = "-".join(parts)
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN].rstrip("-")
    return text or "task"


def build_slug(skill: str | None, input_text: str) -> str:
    disc = find_discriminator(input_text)
    if disc:
        body_text = input_text
        for pat in (JIRA_KEY, GH_PR, GH_ISSUE):
            body_text = pat.sub("", body_text)
        body = slugify(body_text)
        if skill:
            parts = [skill, disc]
            if body and body not in ("task", skill, "github", "atlassian"):
                parts.append(body[:30].rstrip("-"))
            return "-".join(parts)
        return f"{disc}-{body[:30].rstrip('-')}" if body and body != "task" else disc
    base = slugify(input_text)
    if skill:
        return f"{skill}-{base}" if base != "task" else skill
    return base


def dedup(slug: str, parent: Path) -> str:
    if not (parent / slug).exists():
        return slug
    n = 2
    while (parent / f"{slug}-{n}").exists():
        n += 1
    return f"{slug}-{n}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skill", help="skill name (no /adk- prefix), e.g. implement")
    ap.add_argument("--input", help="user prompt / URL / description (or pass as positional)")
    ap.add_argument("--temp-root", default=None, help="parent dir for .temp; defaults to cwd/.temp")
    ap.add_argument("--create", action="store_true", help="mkdir the task folder")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("rest", nargs="*")
    args = ap.parse_args()

    text = args.input or " ".join(args.rest)
    if not text.strip():
        sys.stderr.write("adk_task_slug: empty input\n")
        return 1

    skill = (args.skill or "").lstrip("/").removeprefix("adk-") or None
    slug = build_slug(skill, text)

    temp_root = Path(args.temp_root) if args.temp_root else Path.cwd() / ".temp"
    slug = dedup(slug, temp_root)
    task_dir = temp_root / slug

    if args.create:
        task_dir.mkdir(parents=True, exist_ok=True)
        # touch a prompt.txt with the original input for traceability
        prompt_path = task_dir / "prompt.txt"
        if not prompt_path.exists():
            prompt_path.write_text(text + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps({
            "slug": slug,
            "task_dir": str(task_dir),
            "created": args.create,
        }, indent=2))
        return 0

    print(slug)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
