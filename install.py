#!/usr/bin/env python3
"""install.py — adk v3 installer.

What it does (per agent target):
  - Symlinks skills/adk-* into the agent's skill dir (where supported).
  - Symlinks agents-<agent>/agents/* into the agent's agents dir.
  - Symlinks agents-<agent>/commands/* (or rules/) into the agent's commands dir.
  - Merges mcp/adk-mcp-*.json into the agent's MCP config (idempotent).
  - Appends a one-line reference to AGENTS.md in the agent's global guidelines
    file (idempotent, by marker).
  - Seeds ~/.config/adk/learning/decisions.jsonl with shared/seed-decisions.jsonl
    (first install only).
  - Creates ~/.config/adk/ skeleton if missing.

Targets: claude, cursor, codex, junie, all.

Idempotency markers:
  - <!-- adk-marker:start --> ... <!-- adk-marker:end -->  for markdown
  - # adk-marker:start ... # adk-marker:end                for toml / shell
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Iterable

MARKER_MD_START = "<!-- adk-marker:start -->"
MARKER_MD_END = "<!-- adk-marker:end -->"
MARKER_HASH_START = "# adk-marker:start"
MARKER_HASH_END = "# adk-marker:end"

ADK_USER_DIR = Path.home() / ".config" / "adk"


# ----------------------------------------------------------------------------
# Detection
# ----------------------------------------------------------------------------

def detect_claude() -> bool:
    return (Path.home() / ".claude").is_dir() or shutil.which("claude") is not None


def detect_cursor() -> bool:
    return (Path.home() / ".cursor").is_dir() or shutil.which("cursor") is not None


def detect_codex() -> bool:
    return (Path.home() / ".codex").is_dir() or shutil.which("codex") is not None


def detect_junie() -> bool:
    return (Path.home() / ".junie").is_dir()


SUPPORTED = ["claude", "cursor", "codex", "junie"]
DETECTORS = {"claude": detect_claude, "cursor": detect_cursor, "codex": detect_codex, "junie": detect_junie}


# ----------------------------------------------------------------------------
# Generic helpers
# ----------------------------------------------------------------------------

def info(msg: str) -> None:
    print(f"[adk:install] {msg}")


def warn(msg: str) -> None:
    print(f"[adk:install] WARN: {msg}", file=sys.stderr)


def err(msg: str) -> None:
    print(f"[adk:install] ERROR: {msg}", file=sys.stderr)


def ensure_dir(p: Path, dry_run: bool) -> None:
    if dry_run:
        if not p.exists():
            info(f"would create dir: {p}")
        return
    p.mkdir(parents=True, exist_ok=True)


def make_symlink(src: Path, dst: Path, dry_run: bool) -> str:
    """Create dst as a symlink to src. Returns 'created' / 'updated' / 'kept' / 'would-create' / 'skipped'."""
    if dry_run:
        if dst.exists() or dst.is_symlink():
            if dst.is_symlink() and dst.resolve() == src.resolve():
                return "kept"
            return "would-update"
        return "would-create"
    if dst.exists() or dst.is_symlink():
        try:
            if dst.is_symlink() and dst.readlink() == src:
                return "kept"
        except OSError:
            pass
        # Replace if it was a previous symlink we own; else skip
        if dst.is_symlink():
            dst.unlink()
        else:
            warn(f"refusing to overwrite non-symlink at {dst}; manually remove + re-run")
            return "skipped"
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.symlink_to(src)
    return "created"


def append_with_marker(target: Path, content: str, marker_start: str, marker_end: str,
                       dry_run: bool, repo_root: Path) -> str:
    """Append `content` to `target` between markers. If markers already present, replace
    the block. Returns 'created' / 'updated' / 'replaced' / 'would-update'."""
    rendered = content.replace("{{ADK_REPO}}", str(repo_root))
    block = f"{marker_start}\n{rendered.strip()}\n{marker_end}\n"
    if dry_run:
        if not target.exists():
            return "would-create"
        existing = target.read_text(encoding="utf-8")
        if marker_start in existing and marker_end in existing:
            return "would-replace"
        return "would-update"
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(block, encoding="utf-8")
        return "created"
    existing = target.read_text(encoding="utf-8")
    if marker_start in existing and marker_end in existing:
        pattern = re.compile(
            rf"{re.escape(marker_start)}.*?{re.escape(marker_end)}\n?", re.DOTALL
        )
        new_text = pattern.sub(block, existing, count=1)
        target.write_text(new_text, encoding="utf-8")
        return "replaced"
    sep = "" if existing.endswith("\n\n") else ("\n" if existing.endswith("\n") else "\n\n")
    target.write_text(existing + sep + block, encoding="utf-8")
    return "updated"


def strip_marker(target: Path, marker_start: str, marker_end: str, dry_run: bool) -> str:
    if not target.exists():
        return "absent"
    existing = target.read_text(encoding="utf-8")
    if marker_start not in existing:
        return "absent"
    if dry_run:
        return "would-remove"
    pattern = re.compile(rf"{re.escape(marker_start)}.*?{re.escape(marker_end)}\n?", re.DOTALL)
    new_text = pattern.sub("", existing, count=1)
    target.write_text(new_text, encoding="utf-8")
    return "removed"


# ----------------------------------------------------------------------------
# MCP merging helpers
# ----------------------------------------------------------------------------

def read_json(p: Path) -> dict[str, Any]:
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        warn(f"existing {p} is invalid JSON; leaving alone")
        return {}


def write_json(p: Path, data: dict[str, Any], dry_run: bool) -> None:
    if dry_run:
        info(f"would write {p}")
        return
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def load_mcp_configs(repo_root: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for p in sorted((repo_root / "mcp").glob("adk-mcp-*.json")):
        data = read_json(p)
        name = data.get("name") or p.stem
        out[name] = data
    return out


def merge_mcp_into_claude(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Merge mcp/* into ~/.claude/settings.json under mcpServers.<name>."""
    settings = Path.home() / ".claude" / "settings.json"
    current = read_json(settings)
    current.setdefault("mcpServers", {})
    results: dict[str, str] = {}
    for name, cfg in load_mcp_configs(repo_root).items():
        # Translate adk schema to Claude's MCP schema
        entry: dict[str, Any] = {}
        if "url" in cfg:
            entry["type"] = "http"
            entry["url"] = cfg["url"]
            if "headers" in cfg:
                entry["headers"] = cfg["headers"]
        elif "command" in cfg:
            entry["command"] = cfg["command"]
            if "args" in cfg:
                entry["args"] = cfg["args"]
            if "env" in cfg:
                entry["env"] = cfg["env"]
        if "description" in cfg:
            entry["description"] = cfg["description"]
        # Skip rag if URL env var unset
        if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
            results[name] = "skipped (RAG_MCP_URL unset)"
            continue
        if current["mcpServers"].get(name) == entry:
            results[name] = "kept"
        else:
            current["mcpServers"][name] = entry
            results[name] = "updated"
    write_json(settings, current, dry_run)
    return results


def merge_mcp_into_cursor(repo_root: Path, dry_run: bool) -> dict[str, str]:
    settings = Path.home() / ".cursor" / "mcp.json"
    current = read_json(settings)
    current.setdefault("mcpServers", {})
    results: dict[str, str] = {}
    for name, cfg in load_mcp_configs(repo_root).items():
        entry: dict[str, Any] = {}
        if "url" in cfg:
            entry["url"] = cfg["url"]
            if "headers" in cfg:
                entry["headers"] = cfg["headers"]
        elif "command" in cfg:
            entry["command"] = cfg["command"]
            if "args" in cfg:
                entry["args"] = cfg["args"]
            if "env" in cfg:
                entry["env"] = cfg["env"]
        if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
            results[name] = "skipped (RAG_MCP_URL unset)"
            continue
        if current["mcpServers"].get(name) == entry:
            results[name] = "kept"
        else:
            current["mcpServers"][name] = entry
            results[name] = "updated"
    write_json(settings, current, dry_run)
    return results


def append_codex_toml(repo_root: Path, dry_run: bool) -> str:
    src = repo_root / "agents-codex" / "codex-config.toml.append"
    if not src.exists():
        return "no-template"
    content = src.read_text(encoding="utf-8")
    target = Path.home() / ".codex" / "config.toml"
    return append_with_marker(target, content, MARKER_HASH_START, MARKER_HASH_END, dry_run, repo_root)


# ----------------------------------------------------------------------------
# Per-agent install
# ----------------------------------------------------------------------------

def merge_hooks_into_claude(repo_root: Path, dry_run: bool) -> dict[str, Any]:
    """Merge hooks/hooks.json into ~/.claude/settings.json `hooks` block.

    Idempotent: we write a marker key `_adk_managed: true` next to the inserted
    hooks; on re-run we replace those keys but never touch user-authored hooks.
    """
    src = repo_root / "hooks" / "hooks.json"
    if not src.exists():
        return {"status": "no-hooks-file"}
    src_data = json.loads(src.read_text(encoding="utf-8"))
    src_hooks = src_data.get("hooks", {})
    if not src_hooks:
        return {"status": "empty"}
    # Substitute ${ADK_REPO} in the command string for SessionStart.
    serialized = json.dumps(src_hooks)
    serialized = serialized.replace("${ADK_REPO}", str(repo_root))
    src_hooks = json.loads(serialized)
    # Tag each adk-managed hook entry
    for matcher_list in src_hooks.values():
        for entry in matcher_list:
            entry["_adk_managed"] = True

    settings = Path.home() / ".claude" / "settings.json"
    current = read_json(settings)
    current.setdefault("hooks", {})
    actions: dict[str, str] = {}
    for event, src_entries in src_hooks.items():
        existing = current["hooks"].get(event, [])
        # Drop existing adk-managed entries; preserve the rest.
        kept = [e for e in existing if not (isinstance(e, dict) and e.get("_adk_managed"))]
        current["hooks"][event] = kept + src_entries
        actions[event] = f"merged ({len(src_entries)} entries)"
    write_json(settings, current, dry_run)
    return {"status": "ok", "events": actions}


def install_claude(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Claude Code ===")
    home_claude = Path.home() / ".claude"
    ensure_dir(home_claude / "skills", dry_run)
    ensure_dir(home_claude / "agents", dry_run)
    ensure_dir(home_claude / "commands", dry_run)
    # skills
    skill_results = {}
    for skill_dir in sorted((repo_root / "skills").glob("adk-*")):
        if skill_dir.is_dir():
            dst = home_claude / "skills" / skill_dir.name
            skill_results[skill_dir.name] = make_symlink(skill_dir, dst, dry_run)
    # agents
    agent_results = {}
    for agent_file in sorted((repo_root / "agents-claude" / "agents").glob("adk-agent-*.md")):
        dst = home_claude / "agents" / agent_file.name
        agent_results[agent_file.name] = make_symlink(agent_file, dst, dry_run)
    # commands
    cmd_results = {}
    for cmd_file in sorted((repo_root / "agents-claude" / "commands").glob("adk-*.md")):
        dst = home_claude / "commands" / cmd_file.name
        cmd_results[cmd_file.name] = make_symlink(cmd_file, dst, dry_run)
    # global CLAUDE.md append
    tmpl = (repo_root / "agents-claude" / "claude.md.append.tmpl").read_text(encoding="utf-8")
    append_result = append_with_marker(
        Path.home() / ".claude" / "CLAUDE.md",
        tmpl, MARKER_MD_START, MARKER_MD_END, dry_run, repo_root,
    )
    # MCP merge
    mcp_results = merge_mcp_into_claude(repo_root, dry_run)
    # Hooks merge
    hooks_result = merge_hooks_into_claude(repo_root, dry_run)
    results["claude"] = {
        "skills": skill_results, "agents": agent_results, "commands": cmd_results,
        "claude_md_append": append_result, "mcp_merge": mcp_results, "hooks": hooks_result,
    }


def install_cursor(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Cursor ===")
    rules_dir = Path.home() / ".cursor" / "rules"
    ensure_dir(rules_dir, dry_run)
    # rules
    rule_results = {}
    for rule_file in sorted((repo_root / "agents-cursor" / "rules").glob("adk-*.mdc")):
        dst = rules_dir / rule_file.name
        rule_results[rule_file.name] = make_symlink(rule_file, dst, dry_run)
    # global always-rule (the AGENTS.md pointer)
    tmpl = (repo_root / "agents-cursor" / "cursor-rules.append.tmpl").read_text(encoding="utf-8")
    append_result = append_with_marker(
        rules_dir / "_adk.mdc", tmpl, MARKER_MD_START, MARKER_MD_END, dry_run, repo_root,
    )
    # MCP merge
    mcp_results = merge_mcp_into_cursor(repo_root, dry_run)
    results["cursor"] = {
        "rules": rule_results, "always_rule_append": append_result, "mcp_merge": mcp_results,
    }


def install_codex(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Codex ===")
    codex_dir = Path.home() / ".codex"
    ensure_dir(codex_dir / "prompts", dry_run)
    prompt_results = {}
    for prompt_file in sorted((repo_root / "agents-codex" / "prompts").glob("adk-*.md")):
        dst = codex_dir / "prompts" / prompt_file.name
        prompt_results[prompt_file.name] = make_symlink(prompt_file, dst, dry_run)
    toml_append = append_codex_toml(repo_root, dry_run)
    # Global instructions pointer
    instructions = codex_dir / "instructions.md"
    pointer = f"For every prompt, follow the routing in @{repo_root}/AGENTS.md."
    instructions_append = append_with_marker(
        instructions, pointer, MARKER_MD_START, MARKER_MD_END, dry_run, repo_root,
    )
    results["codex"] = {
        "prompts": prompt_results,
        "config_toml_append": toml_append,
        "instructions_append": instructions_append,
        "gaps": "see agents-codex/README.md for the capability table",
    }


def install_junie(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Junie ===")
    junie_dir = Path.home() / ".junie"
    ensure_dir(junie_dir, dry_run)
    tmpl = (repo_root / "agents-junie" / "guidelines.md.append.tmpl").read_text(encoding="utf-8")
    guidelines_append = append_with_marker(
        junie_dir / "guidelines.md", tmpl, MARKER_MD_START, MARKER_MD_END, dry_run, repo_root,
    )
    # Write MCP snippet for manual paste
    mcp_snippet_path = repo_root / "agents-junie" / "junie-mcp.json.snippet"
    mcp_snippet = {"mcpServers": {}}
    for name, cfg in load_mcp_configs(repo_root).items():
        if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
            continue
        mcp_snippet["mcpServers"][name] = cfg
    if not dry_run:
        mcp_snippet_path.write_text(json.dumps(mcp_snippet, indent=2) + "\n", encoding="utf-8")
    results["junie"] = {
        "guidelines_append": guidelines_append,
        "mcp_snippet_written": str(mcp_snippet_path) if not dry_run else "(dry-run)",
        "gaps": "see agents-junie/README.md — MCP wiring is manual",
    }


# ----------------------------------------------------------------------------
# Uninstall
# ----------------------------------------------------------------------------

def uninstall_target(target: str, dry_run: bool, results: dict[str, Any]) -> None:
    info(f"=== uninstall: {target} ===")
    if target == "claude":
        home_claude = Path.home() / ".claude"
        for sub in ("skills", "agents", "commands"):
            for p in (home_claude / sub).glob("adk-*"):
                if p.is_symlink():
                    if dry_run:
                        info(f"would remove symlink {p}")
                    else:
                        p.unlink()
        strip_marker(home_claude / "CLAUDE.md", MARKER_MD_START, MARKER_MD_END, dry_run)
        # Hooks: remove adk-managed entries
        settings = home_claude / "settings.json"
        if settings.exists():
            current = read_json(settings)
            hooks = current.get("hooks", {})
            removed = 0
            for event in list(hooks):
                kept = [e for e in hooks[event] if not (isinstance(e, dict) and e.get("_adk_managed"))]
                removed += len(hooks[event]) - len(kept)
                if kept:
                    hooks[event] = kept
                else:
                    del hooks[event]
            if not dry_run:
                write_json(settings, current, dry_run=False)
            results["claude_hooks_removed"] = removed
        # MCPs: leave them (user may have customized)
        results["claude"] = "uninstalled (symlinks removed; CLAUDE.md marker stripped; adk hooks removed; MCPs left)"
    elif target == "cursor":
        rules = Path.home() / ".cursor" / "rules"
        for p in rules.glob("adk-*.mdc"):
            if p.is_symlink():
                if dry_run:
                    info(f"would remove {p}")
                else:
                    p.unlink()
        strip_marker(rules / "_adk.mdc", MARKER_MD_START, MARKER_MD_END, dry_run)
        results["cursor"] = "uninstalled (rules removed; _adk.mdc marker stripped)"
    elif target == "codex":
        prompts = Path.home() / ".codex" / "prompts"
        for p in prompts.glob("adk-*.md"):
            if p.is_symlink():
                if dry_run:
                    info(f"would remove {p}")
                else:
                    p.unlink()
        strip_marker(Path.home() / ".codex" / "config.toml", MARKER_HASH_START, MARKER_HASH_END, dry_run)
        strip_marker(Path.home() / ".codex" / "instructions.md", MARKER_MD_START, MARKER_MD_END, dry_run)
        results["codex"] = "uninstalled"
    elif target == "junie":
        strip_marker(Path.home() / ".junie" / "guidelines.md", MARKER_MD_START, MARKER_MD_END, dry_run)
        results["junie"] = "uninstalled"


# ----------------------------------------------------------------------------
# Bootstrap user dir
# ----------------------------------------------------------------------------

def bootstrap_user_dir(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Create ~/.config/adk/ skeleton; seed decisions.jsonl on first install."""
    out: dict[str, str] = {}
    learning = ADK_USER_DIR / "learning"
    metadata = ADK_USER_DIR / "metadata"
    memory = ADK_USER_DIR / "memory"
    sessions = learning / "sessions"
    proposals = learning / "proposals"
    archive = learning / "archive"
    ensure_dir(learning, dry_run)
    ensure_dir(metadata, dry_run)
    ensure_dir(memory, dry_run)
    ensure_dir(sessions, dry_run)
    ensure_dir(proposals, dry_run)
    ensure_dir(archive, dry_run)
    decisions = learning / "decisions.jsonl"
    seed = repo_root / "shared" / "seed-decisions.jsonl"
    if not decisions.exists():
        if dry_run:
            out["decisions_seed"] = "would-seed"
        else:
            shutil.copyfile(seed, decisions)
            out["decisions_seed"] = f"seeded from {seed.name}"
    else:
        out["decisions_seed"] = "exists (left alone)"
    return out


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="adk v3 installer")
    ap.add_argument("--repo-root", required=True, type=Path)
    ap.add_argument("--target", default=None, help="comma-separated; or 'all'")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    repo_root: Path = args.repo_root.resolve()
    dry_run: bool = args.dry_run

    # Resolve targets
    if args.target is None:
        detected = [t for t in SUPPORTED if DETECTORS[t]()]
        if not detected:
            warn("no supported agents detected. Use --target all to force install for all four.")
            return 1
        targets = detected
        info(f"autodetected: {targets}")
    elif args.target == "all":
        targets = list(SUPPORTED)
    else:
        targets = [t.strip() for t in args.target.split(",") if t.strip()]
        bad = [t for t in targets if t not in SUPPORTED]
        if bad:
            err(f"unknown targets: {bad}. Supported: {SUPPORTED}")
            return 2

    results: dict[str, Any] = {"targets": targets, "dry_run": dry_run}

    if args.uninstall:
        for t in targets:
            uninstall_target(t, dry_run, results)
        print(json.dumps(results, indent=2))
        return 0

    # Always bootstrap ~/.config/adk/
    results["user_dir"] = bootstrap_user_dir(repo_root, dry_run)

    for t in targets:
        try:
            {"claude": install_claude, "cursor": install_cursor,
             "codex": install_codex, "junie": install_junie}[t](repo_root, dry_run, results)
        except Exception as e:
            err(f"{t} install failed: {e}")
            results[t] = {"error": str(e)}

    print(json.dumps(results, indent=2))

    # Final summary
    print()
    print("=" * 60)
    if dry_run:
        print("DRY RUN — no changes written.")
    else:
        print("install complete.")
    print("=" * 60)
    print(f"  - repo: {repo_root}")
    print(f"  - user dir: {ADK_USER_DIR}")
    print(f"  - targets: {targets}")
    print()
    print("next:")
    print("  1. edit ~/.config/adk/overrides.yaml (run /adk-setup --init from your agent to scaffold).")
    print("  2. set env vars per SETUP.md.")
    print("  3. restart your agent so it picks up env + MCP changes.")
    print("  4. run /adk-setup --check to verify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
