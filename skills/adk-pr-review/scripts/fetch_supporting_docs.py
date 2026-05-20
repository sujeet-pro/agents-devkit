#!/usr/bin/env python3
"""fetch_supporting_docs.py — scan PR body + comments for doc URLs, fetch each as markdown.

One hop only (constitution §IV.1). Writes to <task-dir>/docs/<adapter>/<id>.md.

Supported adapters:
  - confluence — via adk-mcp-atlassian (not invoked directly here; we call the parallel /adk-sync --read helper via subprocess where possible, else we record the URL as 'pending').
  - jira       — same as confluence
  - gdoc       — requires the user to have the GDoc shared; we fetch via Drive MCP if available
  - markdown-remote — raw `requests.get` (only for github.com, raw.githubusercontent.com, gist.github.com — narrow allowlist)

Out of scope for direct fetch: arbitrary websites (we don't pretend to render them).

Usage:
  python3 fetch_supporting_docs.py --task-dir <path> [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).parent))
from _common import read_json, write_json, emit_json, get_logger  # noqa: E402

try:
    import requests  # type: ignore
except ImportError:
    requests = None  # type: ignore  # only needed for markdown-remote fetch


URL_RE = re.compile(r"https?://[^\s\)\]>]+", re.I)

CONFLUENCE_HOST_RE = re.compile(r"\.atlassian\.net$", re.I)
JIRA_PATH_RE = re.compile(r"/browse/[A-Z]+-\d+")
GDOC_HOST_RE = re.compile(r"docs\.google\.com$", re.I)
RAW_HOSTS = {"raw.githubusercontent.com", "gist.githubusercontent.com"}
GH_HOST = "github.com"

# Bare Jira keys in the PR body (no URL) — common pattern. E.g. "Implements SF-1234"
BARE_JIRA_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d+)\b")

IN_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")


# Names of MCP tools the agent should call to fetch each adapter. These names
# match `mcp/adk-mcp-atlassian.json` / `mcp/adk-mcp-google.json`. The orchestrator
# does NOT call MCPs (no MCP client in Python); the agent does, after reading
# docs/index.json.
MCP_TOOL = {
    "confluence": "mcp__adk-mcp-atlassian__confluence_get_page",
    "jira":       "mcp__adk-mcp-atlassian__jira_get_issue",
    "gdoc":       "mcp__adk-mcp-google__get_doc_as_markdown",
}


def strip_code_blocks(text: str) -> str:
    return IN_CODE_BLOCK_RE.sub("", text or "")


def classify(url: str) -> tuple[str, str, dict]:
    """Return (adapter, id-or-slug, extra). `extra` carries adapter-specific args the MCP tool needs."""
    p = urlparse(url)
    host = p.netloc.lower()
    path = p.path
    if CONFLUENCE_HOST_RE.search(host) and "/wiki/" in path:
        # /wiki/spaces/<KEY>/pages/<id>/<slug>
        m = re.search(r"/pages/(\d+)", path)
        ident = m.group(1) if m else path.split("/")[-1] or "page"
        space_m = re.search(r"/spaces/([^/]+)", path)
        return "confluence", ident, {"page_id": ident, "space_key": space_m.group(1) if space_m else None}
    if CONFLUENCE_HOST_RE.search(host) and JIRA_PATH_RE.search(path):
        m = JIRA_PATH_RE.search(path)
        key = m.group(0).replace("/browse/", "")
        return "jira", key, {"issue_key": key}
    if GDOC_HOST_RE.search(host):
        m = re.search(r"/document/d/([^/]+)", path)
        ident = m.group(1) if m else "doc"
        return "gdoc", ident, {"document_id": ident}
    if host in RAW_HOSTS or (host == GH_HOST and "/raw/" in path):
        return "markdown-remote", Path(path).stem, {"url": url}
    return "external", host, {}


def fetch_markdown_remote(url: str, dest: Path, log) -> bool:
    if requests is None:
        log.warning("markdown-remote skipped (requests not installed): %s", url)
        return False
    try:
        r = requests.get(url, timeout=20)
        if r.status_code != 200:
            log.warning("markdown-remote %s → HTTP %d", url, r.status_code)
            return False
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(r.text, encoding="utf-8")
        return True
    except requests.RequestException as e:
        log.warning("markdown-remote %s → %s", url, e)
        return False


def collect_urls_and_keys(task_dir: Path) -> tuple[list[str], list[str]]:
    """Returns (urls, bare_jira_keys). Bare jira keys appear in PR body without a URL."""
    urls: set[str] = set()
    bare_jira: set[str] = set()
    pr_json = task_dir / "pr.json"
    if pr_json.exists():
        pr = read_json(pr_json)
        for field in ("body", "title"):
            text = pr.get(field) or ""
            stripped = strip_code_blocks(text)
            for m in URL_RE.findall(stripped):
                urls.add(m.rstrip(".,);"))
            for m in BARE_JIRA_RE.finditer(stripped):
                # Skip if it appeared as part of a URL we already captured.
                key = f"{m.group(1)}-{m.group(2)}"
                bare_jira.add(key)
    cm_json = task_dir / "pr-comments.json"
    if cm_json.exists():
        data = read_json(cm_json)
        bodies: list[str] = []
        for k in ("review_comments", "issue_comments", "comments"):
            for c in data.get(k, []):
                body = (c.get("body") or c.get("content", {}).get("raw") or "")
                if body:
                    bodies.append(body)
        for body in bodies:
            stripped = strip_code_blocks(body)
            for m in URL_RE.findall(stripped):
                urls.add(m.rstrip(".,);"))
            for m in BARE_JIRA_RE.finditer(stripped):
                bare_jira.add(f"{m.group(1)}-{m.group(2)}")

    # Subtract any jira key that's already covered by a URL.
    url_jiras = set()
    for u in urls:
        m = re.search(r"/browse/([A-Z]+-\d+)", u)
        if m:
            url_jiras.add(m.group(1))
    bare_only = sorted(bare_jira - url_jiras)
    return sorted(urls), bare_only


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    task_dir = Path(args.task_dir)
    log = get_logger("fetch_supporting_docs", task_dir)

    urls, bare_jira_keys = collect_urls_and_keys(task_dir)

    # Forced supporting docs (from /adk-pr-reviews queue.json5 supporting_docs[]).
    # When the batch driver pre-writes <task_dir>/forced-supporting-docs.json, those
    # URLs are added as first-class inputs even if they don't appear in the PR body.
    forced_path = task_dir / "forced-supporting-docs.json"
    if forced_path.exists():
        try:
            forced = json.loads(forced_path.read_text(encoding="utf-8"))
            if isinstance(forced, list):
                existing = set(urls)
                for url in forced:
                    if isinstance(url, str) and url not in existing:
                        urls.append(url)
                        existing.add(url)
                log.info("forced supporting docs: %d added from %s", len(forced), forced_path)
        except Exception as e:
            log.warning("failed to read forced-supporting-docs.json: %s", e)

    results: list[dict] = []
    for url in urls:
        adapter, ident, extra = classify(url)
        rec = {
            "url": url,
            "adapter": adapter,
            "id": ident,
            "status": "pending",
            "path": str(task_dir / "docs" / adapter / f"{ident}.md"),
        }
        dest = Path(rec["path"])
        if adapter == "markdown-remote":
            ok = fetch_markdown_remote(url, dest, log)
            rec["status"] = "fetched" if ok else "failed"
            if not ok:
                rec["path"] = None
        elif adapter in ("confluence", "jira", "gdoc"):
            # The agent dispatches the MCP tool listed in `mcp_tool` and writes
            # the markdown body to `path`. The orchestrator can't do this from
            # Python — only the host agent has MCP access.
            rec["status"] = "pending_mcp"
            rec["mcp_tool"] = MCP_TOOL.get(adapter)
            rec["mcp_args"] = extra
        else:
            rec["status"] = "skipped_external"
            rec["path"] = None
        results.append(rec)

    # Bare Jira keys from the PR body (no URL).
    for key in bare_jira_keys:
        results.append({
            "url": None,
            "adapter": "jira",
            "id": key,
            "status": "pending_mcp",
            "mcp_tool": MCP_TOOL["jira"],
            "mcp_args": {"issue_key": key},
            "path": str(task_dir / "docs" / "jira" / f"{key}.md"),
        })

    index = {
        "task_dir": str(task_dir),
        "found_urls": len(urls),
        "bare_jira_keys": bare_jira_keys,
        "results": results,
        "notes": [
            "For each entry with status=pending_mcp, the calling agent must:",
            "  1. Call mcp_tool with mcp_args.",
            "  2. Convert the response to markdown.",
            "  3. Write it to `path`.",
            "  4. Update status to 'fetched' (or 'failed: <reason>') in this index.",
            "Then re-read precis.md; the docs/ folder is referenced from there.",
        ],
    }
    write_json(task_dir / "docs" / "index.json", index)

    if args.json:
        return emit_json(index)
    log.info("collected %d URLs + %d bare jira keys (%d fetched, %d pending_mcp, %d skipped)",
             len(urls), len(bare_jira_keys),
             sum(1 for r in results if r["status"] == "fetched"),
             sum(1 for r in results if r["status"] == "pending_mcp"),
             sum(1 for r in results if r["status"] == "skipped_external"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
