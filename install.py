#!/usr/bin/env python3
"""install.py — adk installer.

What it does (per agent target):
  - Enforces an ADK-only agent profile by deleting non-ADK skills/rules/MCP
    caches and quarantining legacy ADK v2/v3 state.
  - Symlinks skills/adk-* into the agent's skill dir (where supported).
  - Symlinks agents-<agent>/agents/* into the agent's agents dir.
  - Symlinks agents-<agent>/commands/* (or rules/) into the agent's commands dir.
  - Merges mcp/adk-mcp-*.json into the agent's MCP config (idempotent).
  - Appends a one-line reference to AGENTS.md in the agent's global guidelines
    file (idempotent, by marker).
  - Seeds ~/.agents-devkit/improve/learning/decisions.jsonl with shared/seed-decisions.jsonl
    (first install only).
  - Creates ~/.agents-devkit/config/ skeleton if missing.

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
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Iterable

_LIB_DIR = Path(__file__).resolve().parent / "scripts" / "lib"
if str(_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(_LIB_DIR))
from adk_home import (  # noqa: E402
    adk_config_home, adk_data_home, adk_improve_home, adk_memory_home,
)

MARKER_MD_START = "<!-- adk-marker:start -->"
MARKER_MD_END = "<!-- adk-marker:end -->"
MARKER_HASH_START = "# adk-marker:start"
MARKER_HASH_END = "# adk-marker:end"
MARKER_PERMS_HASH_START = "# adk-permissions-marker:start"
MARKER_PERMS_HASH_END = "# adk-permissions-marker:end"

# JSON key used to record what permission entries adk added, so we can
# cleanly remove them on re-install or uninstall without touching user
# entries.
ADK_PERMS_BOOKKEEPING_KEY = "_adkManagedPermissions"

# JSON key used to stash the user's pre-existing (non-adk) mcpServers entries
# at first install so they can be restored on uninstall. Per the user's
# explicit request, on install we WIPE non-adk mcpServers from each agent's
# config; this key lets us undo that safely.
ADK_REMOVED_MCP_KEY = "_adkRemovedMcpServers"

# Prefix every adk-installed MCP server name uses; anything else in the
# `mcpServers` map is considered user-authored.
ADK_MCP_NAME_PREFIX = "adk-mcp-"

ADK_USER_DIR = adk_config_home()

# Skill directories under skills/ that are NOT slash-invokable agent skills:
# they hold shared python modules / CLI subcommands and should not be symlinked
# into ~/.claude/skills/, ~/.junie/skills/, etc.
NON_SLASH_SKILLS: set[str] = {"adk-cli"}

# Where the `adk` CLI binary lives (symlinked at install time).
ADK_BIN_TARGET = Path.home() / ".local" / "bin" / "adk"

ADK_ZSH_COMPLETION_START = "# >>> adk completion (managed by adk install) >>>"
ADK_ZSH_COMPLETION_END = "# <<< adk completion <<<"
ADK_ZSH_COMPLETION_BLOCK = (
    f"{ADK_ZSH_COMPLETION_START}\n"
    '[[ -d "$HOME/.zsh/completions" ]] && fpath=("$HOME/.zsh/completions" $fpath)\n'
    f"{ADK_ZSH_COMPLETION_END}\n"
)


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


def write_rendered_file(src: Path, dst: Path, repo_root: Path, dry_run: bool) -> str:
    """Write a rendered ADK-managed file, replacing old symlink installs."""
    rendered = src.read_text(encoding="utf-8").replace("{{ADK_REPO}}", str(repo_root))
    if dry_run:
        if not dst.exists() and not dst.is_symlink():
            return "would-create"
        if dst.is_symlink():
            return "would-replace-symlink"
        try:
            return "kept" if dst.read_text(encoding="utf-8") == rendered else "would-update"
        except OSError:
            return "would-update"
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink():
            dst.unlink()
        elif dst.read_text(encoding="utf-8") == rendered:
            return "kept"
    dst.parent.mkdir(parents=True, exist_ok=True)
    existed = dst.exists()
    dst.write_text(rendered, encoding="utf-8")
    return "updated" if existed else "created"


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
        # Greedy on .* so we consume EVERYTHING from the first marker_start to
        # the LAST marker_end — including duplicate start/end markers left
        # behind by earlier buggy installs (where the templates themselves
        # contained the markers). count=1 keeps us from crossing into a
        # different marker family (e.g. # adk-permissions-marker).
        pattern = re.compile(
            rf"{re.escape(marker_start)}.*{re.escape(marker_end)}\n?", re.DOTALL
        )
        # Pass `block` via a callable so re.sub() does NOT interpret backslash
        # escapes in the replacement (otherwise `\n` inside a generated TOML
        # string — e.g. the slack MCP's multi-line python args — becomes a
        # real newline and breaks the resulting file).
        new_text = pattern.sub(lambda _m: block, existing, count=1)
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
    # Greedy on .* so we consume all duplicate markers between the first start
    # and the last end (cleanup for earlier buggy-install corruption).
    pattern = re.compile(rf"{re.escape(marker_start)}.*{re.escape(marker_end)}\n?", re.DOTALL)
    new_text = pattern.sub("", existing, count=1)
    target.write_text(new_text, encoding="utf-8")
    return "removed"


# ----------------------------------------------------------------------------
# ADK-only cleanup helpers
# ----------------------------------------------------------------------------

def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def _safe_path(p: Path) -> Path:
    # Use lexical absolute paths for cleanup authorization. `resolve()` follows
    # symlinks, which would incorrectly block removal of a symlink stored inside
    # an allowlisted agent directory when its target points back to this repo.
    return Path(os.path.abspath(os.fspath(p.expanduser())))


def _cleanup_allowed(path: Path) -> tuple[bool, str]:
    """Return whether install.py is allowed to remove/quarantine `path`.

    The ADK-only cleanup intentionally deletes agent integration caches, so keep
    the guard boring and explicit. Credential stores are never in scope.
    """
    home = Path.home().resolve(strict=False)
    target = _safe_path(path)
    allowed_roots = [
        home / ".cursor",
        home / ".claude",
        home / ".codex",
        home / ".junie",
        home / ".agents-devkit",
        home / ".config" / "adk",
    ]
    forbidden_roots = [
        home / ".config" / "creds",
        home / ".ssh",
        home / ".gnupg",
    ]
    if any(_is_relative_to(target, forbidden) for forbidden in forbidden_roots):
        return False, "blocked (credential/sensitive path)"
    if any(target == root or _is_relative_to(target, root) for root in allowed_roots):
        return True, "ok"
    return False, "blocked (outside ADK cleanup allowlist)"


def _manifest_entry(path: Path, status: str, reason: str, **extra: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "path": str(path),
        "status": status,
        "reason": reason,
    }
    entry.update(extra)
    return entry


def _remove_path(path: Path, dry_run: bool, reason: str) -> dict[str, Any]:
    allowed, why = _cleanup_allowed(path)
    if not allowed:
        return _manifest_entry(path, why, reason)
    if not path.exists() and not path.is_symlink():
        return _manifest_entry(path, "absent", reason)
    if dry_run:
        return _manifest_entry(path, "would-delete", reason)
    try:
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        return _manifest_entry(path, "deleted", reason)
    except OSError as e:
        return _manifest_entry(path, f"error: {e}", reason)


def _legacy_dest_for(path: Path, quarantine_root: Path) -> Path:
    home = Path.home().resolve(strict=False)
    source = _safe_path(path)
    try:
        rel = source.relative_to(home)
    except ValueError:
        rel = Path(source.name)
    name = "__".join(rel.parts).replace(".", "dot-")
    dest = quarantine_root / name
    if not dest.exists():
        return dest
    for i in range(2, 1000):
        candidate = quarantine_root / f"{name}-{i}"
        if not candidate.exists():
            return candidate
    return quarantine_root / f"{name}-{os.getpid()}"


def _quarantine_path(path: Path, quarantine_root: Path, dry_run: bool,
                     reason: str) -> dict[str, Any]:
    allowed, why = _cleanup_allowed(path)
    if not allowed:
        return _manifest_entry(path, why, reason)
    if not path.exists() and not path.is_symlink():
        return _manifest_entry(path, "absent", reason)
    dest = _legacy_dest_for(path, quarantine_root)
    if dry_run:
        return _manifest_entry(path, "would-quarantine", reason, dest=str(dest))
    try:
        quarantine_root.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(dest))
        return _manifest_entry(path, "quarantined", reason, dest=str(dest))
    except OSError as e:
        return _manifest_entry(path, f"error: {e}", reason, dest=str(dest))


def _clean_directory_children(root: Path, keep: Callable[[Path], bool],
                              dry_run: bool, reason: str) -> dict[str, Any]:
    if not root.exists():
        return {"path": str(root), "status": "absent", "removed": []}
    removed: list[dict[str, Any]] = []
    kept = 0
    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if keep(child):
            kept += 1
            continue
        removed.append(_remove_path(child, dry_run, reason))
    return {"path": str(root), "status": "scanned", "kept": kept, "removed": removed}


def _keep_adk_prefixed(path: Path) -> bool:
    return path.name.startswith("adk-")


def _keep_cursor_rule(path: Path) -> bool:
    return path.name == "_adk.mdc" or path.name.startswith("adk-")


def _clean_claude_enabled_plugins(dry_run: bool) -> dict[str, Any]:
    settings = Path.home() / ".claude" / "settings.json"
    if not settings.exists():
        return {"path": str(settings), "status": "absent"}
    current = read_json(settings)
    enabled = current.get("enabledPlugins")
    if not isinstance(enabled, dict):
        return {"path": str(settings), "status": "no-enabledPlugins"}
    kept = {k: v for k, v in enabled.items() if "adk" in str(k).lower()}
    removed = sorted(str(k) for k in enabled if k not in kept)
    if not removed:
        return {"path": str(settings), "status": "unchanged", "kept": sorted(kept)}
    if dry_run:
        return {"path": str(settings), "status": "would-filter",
                "kept": sorted(kept), "removed": removed}
    current["enabledPlugins"] = kept
    write_json(settings, current, dry_run=False)
    return {"path": str(settings), "status": "filtered",
            "kept": sorted(kept), "removed": removed}


def _sanitize_codex_non_adk_mcp_blocks(dry_run: bool) -> dict[str, Any]:
    config = Path.home() / ".codex" / "config.toml"
    if not config.exists():
        return {"path": str(config), "status": "absent", "removed": []}
    text = config.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    removed: list[str] = []
    out: list[str] = []
    i = 0
    table_re = re.compile(r'^\s*\[mcp_servers\.("?)([^"\].]+)\1(?:\.[^\]]+)?\]\s*$')
    any_table_re = re.compile(r"^\s*\[[^\]]+\]\s*$")
    while i < len(lines):
        m = table_re.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        name = m.group(2)
        block = [lines[i]]
        i += 1
        while i < len(lines) and not any_table_re.match(lines[i]):
            block.append(lines[i])
            i += 1
        if name.startswith(ADK_MCP_NAME_PREFIX):
            out.extend(block)
        else:
            removed.append(name)
    if not removed:
        return {"path": str(config), "status": "unchanged", "removed": []}
    if dry_run:
        return {"path": str(config), "status": "would-remove-non-adk-mcps",
                "removed": sorted(set(removed))}
    config.write_text("".join(out), encoding="utf-8")
    return {"path": str(config), "status": "removed-non-adk-mcps",
            "removed": sorted(set(removed))}


def _clear_cursor_project_mcp_caches(dry_run: bool) -> list[dict[str, Any]]:
    projects = Path.home() / ".cursor" / "projects"
    if not projects.exists():
        return [_manifest_entry(projects, "absent", "Cursor project MCP cache root")]
    out: list[dict[str, Any]] = []
    for mcp_dir in sorted(projects.glob("*/mcps"), key=lambda p: str(p)):
        if not mcp_dir.exists():
            continue
        for child in sorted(mcp_dir.iterdir(), key=lambda p: p.name):
            out.append(_remove_path(child, dry_run, "clear Cursor project MCP descriptor cache"))
    return out


def cleanup_cursor_adk_only(dry_run: bool) -> dict[str, Any]:
    cursor = Path.home() / ".cursor"
    return {
        "rules": _clean_directory_children(
            cursor / "rules", _keep_cursor_rule, dry_run,
            "remove non-ADK Cursor rules",
        ),
        "skills_cursor": _remove_path(
            cursor / "skills-cursor", dry_run,
            "remove non-ADK Cursor built-in skill pack",
        ),
        "public_plugin_cache": _remove_path(
            cursor / "plugins" / "cache" / "cursor-public", dry_run,
            "remove non-ADK Cursor marketplace plugin cache",
        ),
        "project_mcp_caches": _clear_cursor_project_mcp_caches(dry_run),
    }


def cleanup_claude_adk_only(quarantine_root: Path, dry_run: bool) -> dict[str, Any]:
    claude = Path.home() / ".claude"
    return {
        "skills": _clean_directory_children(
            claude / "skills", _keep_adk_prefixed, dry_run,
            "remove non-ADK Claude skills",
        ),
        "agents": _clean_directory_children(
            claude / "agents", _keep_adk_prefixed, dry_run,
            "remove non-ADK Claude agents",
        ),
        "commands": _clean_directory_children(
            claude / "commands", _keep_adk_prefixed, dry_run,
            "remove non-ADK Claude commands",
        ),
        "enabled_plugins": _clean_claude_enabled_plugins(dry_run),
        "legacy_adk_plugin_cache": _quarantine_path(
            claude / "plugins" / "cache" / "adk", quarantine_root, dry_run,
            "quarantine legacy ADK Claude plugin cache",
        ),
        "plugin_state": _remove_path(
            claude / "plugins", dry_run,
            "remove non-ADK Claude plugin registries/caches/marketplaces",
        ),
    }


def cleanup_codex_adk_only(dry_run: bool) -> dict[str, Any]:
    codex = Path.home() / ".codex"
    return {
        "prompts": _clean_directory_children(
            codex / "prompts", _keep_adk_prefixed, dry_run,
            "remove non-ADK Codex prompts",
        ),
        "plugin_cache": _remove_path(
            codex / ".tmp" / "plugins", dry_run,
            "remove non-ADK Codex bundled plugin cache",
        ),
        "vendor_skills": _remove_path(
            codex / "vendor_imports" / "skills", dry_run,
            "remove non-ADK Codex imported skill packs",
        ),
        "config_non_adk_mcps": _sanitize_codex_non_adk_mcp_blocks(dry_run),
    }


def cleanup_junie_adk_only(dry_run: bool) -> dict[str, Any]:
    junie = Path.home() / ".junie"
    return {
        "skills": _clean_directory_children(
            junie / "skills", _keep_adk_prefixed, dry_run,
            "remove non-ADK Junie skills",
        ),
        "commands": _clean_directory_children(
            junie / "commands", _keep_adk_prefixed, dry_run,
            "remove non-ADK Junie commands",
        ),
        "bundled_skills": _remove_path(
            junie / "1588.21" / "skills", dry_run,
            "remove non-ADK Junie bundled skill cache",
        ),
        "allowlist": _remove_junie_non_adk_allowlist(dry_run),
    }


def _remove_junie_non_adk_allowlist(dry_run: bool) -> dict[str, Any]:
    allowlist = Path.home() / ".junie" / "allowlist.json"
    if not allowlist.exists():
        return _manifest_entry(
            allowlist, "absent",
            "remove existing Junie allowlist so ADK can rewrite managed permissions",
        )
    try:
        data = json.loads(allowlist.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _remove_path(
            allowlist, dry_run,
            "remove invalid Junie allowlist so ADK can rewrite managed permissions",
        )
    if isinstance(data, dict) and data.get("_adk_managed"):
        return _manifest_entry(
            allowlist, "kept",
            "ADK-managed Junie allowlist will be refreshed by install",
        )
    return _remove_path(
        allowlist, dry_run,
        "remove existing Junie allowlist so ADK can rewrite managed permissions",
    )


def cleanup_legacy_adk_state(quarantine_root: Path, dry_run: bool) -> dict[str, Any]:
    return {
        "config_adk": _quarantine_path(
            Path.home() / ".config" / "adk", quarantine_root, dry_run,
            "quarantine legacy ADK v2/v3 config state without migration",
        ),
    }


def cleanup_adk_only(repo_root: Path, targets: list[str], dry_run: bool) -> dict[str, Any]:
    """Delete non-ADK integrations/caches and quarantine legacy ADK state."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    quarantine_root = adk_data_home() / "legacy" / stamp
    out: dict[str, Any] = {
        "mode": "adk-only",
        "quarantine_root": str(quarantine_root),
        "repo_root": str(repo_root),
    }
    if "cursor" in targets:
        out["cursor"] = cleanup_cursor_adk_only(dry_run)
    if "claude" in targets:
        out["claude"] = cleanup_claude_adk_only(quarantine_root, dry_run)
    if "codex" in targets:
        out["codex"] = cleanup_codex_adk_only(dry_run)
    if "junie" in targets:
        out["junie"] = cleanup_junie_adk_only(dry_run)
    # Legacy ADK state is global, not target-specific. Quarantine it on every
    # normal install so the v4 ~/.agents-devkit tree is the only active ADK
    # runtime state.
    out["legacy_adk"] = cleanup_legacy_adk_state(quarantine_root, dry_run)
    return out


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


def _merge_permission_lists(target_section: dict[str, Any], bookkeeping: dict[str, Any],
                             desired: dict[str, Any], list_keys: Iterable[str]) -> None:
    """Idempotently merge list-valued permission keys.

    For each list key (e.g. "allow", "ask", "deny"):
      1. Drop entries previously added by adk (tracked in bookkeeping[key]).
      2. Union-in the desired entries (preserving user-added entries already there).
      3. Record what we managed so the next run / uninstall can clean up.
    """
    for key in list_keys:
        prev_managed = list(bookkeeping.get(key, []))
        existing = list(target_section.get(key, []))
        # Step 1: remove previously-managed entries that the user did not re-add.
        existing = [x for x in existing if x not in prev_managed]
        # Step 2: union-in desired.
        desired_list = list(desired.get(key, []))
        for item in desired_list:
            if item not in existing:
                existing.append(item)
        target_section[key] = existing
        # Step 3: record exactly what we manage now.
        bookkeeping[key] = desired_list


def _set_scalar_with_bookkeeping(target_section: dict[str, Any], bookkeeping: dict[str, Any],
                                  desired: dict[str, Any], key: str,
                                  bookkeeping_key: str | None = None) -> None:
    """Set a scalar key while preserving the user's previous value for uninstall."""
    if key not in desired:
        return
    prev_key = bookkeeping_key or f"{key}__previous"
    if prev_key not in bookkeeping:
        bookkeeping[prev_key] = target_section.get(key)
    target_section[key] = desired[key]


def merge_permissions_into_claude(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Merge shared/permissions/claude.json into ~/.claude/settings.json.

    Allows all read / generally-safe tools by default, prompts only on entries
    listed under permissions.ask (dangerous bash commands). Idempotent.
    """
    src = repo_root / "shared" / "permissions" / "claude.json"
    if not src.exists():
        return {"status": "no-template"}
    desired_root = read_json(src)
    desired_perms = desired_root.get("permissions", {})

    settings_path = Path.home() / ".claude" / "settings.json"
    current = read_json(settings_path)
    perms = current.setdefault("permissions", {})
    book = current.setdefault(ADK_PERMS_BOOKKEEPING_KEY, {})

    _merge_permission_lists(perms, book, desired_perms, ("allow", "ask", "deny"))
    _set_scalar_with_bookkeeping(perms, book, desired_perms, "defaultMode",
                                  bookkeeping_key="defaultMode__previous")

    write_json(settings_path, current, dry_run)
    return {"status": "merged",
            "allow_count": str(len(perms.get("allow", []))),
            "ask_count": str(len(perms.get("ask", []))),
            "defaultMode": str(perms.get("defaultMode"))}


def merge_permissions_into_cursor(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Merge shared/permissions/cursor.json into ~/.cursor/cli-config.json.

    Sets approvalMode + sandbox to permissive-but-safe defaults, and
    unions our allow/deny shell entries with the user's existing ones.
    """
    src = repo_root / "shared" / "permissions" / "cursor.json"
    if not src.exists():
        return {"status": "no-template"}
    desired_root = read_json(src)

    settings_path = Path.home() / ".cursor" / "cli-config.json"
    current = read_json(settings_path)
    book = current.setdefault(ADK_PERMS_BOOKKEEPING_KEY, {})

    # permissions.allow / permissions.deny
    desired_perms = desired_root.get("permissions", {})
    perms = current.setdefault("permissions", {"allow": [], "deny": []})
    _merge_permission_lists(perms, book, desired_perms, ("allow", "deny"))

    # approvalMode (top-level scalar)
    _set_scalar_with_bookkeeping(current, book, desired_root, "approvalMode",
                                  bookkeeping_key="approvalMode__previous")

    # sandbox.{mode,networkAccess}
    desired_sandbox = desired_root.get("sandbox", {})
    if desired_sandbox:
        sandbox = current.setdefault("sandbox", {})
        sandbox_book = book.setdefault("sandbox", {})
        for skey in ("mode", "networkAccess"):
            if skey in desired_sandbox:
                if f"{skey}__previous" not in sandbox_book:
                    sandbox_book[f"{skey}__previous"] = sandbox.get(skey)
                sandbox[skey] = desired_sandbox[skey]

    write_json(settings_path, current, dry_run)
    return {"status": "merged",
            "approvalMode": str(current.get("approvalMode")),
            "allow_count": str(len(perms.get("allow", []))),
            "deny_count": str(len(perms.get("deny", [])))}


def merge_permissions_into_codex(repo_root: Path, dry_run: bool) -> str:
    """Append (or replace) the adk permissions marker block in ~/.codex/config.toml.

    NOTE: if the user already defined `approval_policy` or `sandbox_mode` at the
    top level outside our marker, TOML will reject the duplicate. We detect this
    and refuse to write — the user must remove their own entry first.
    """
    src = repo_root / "shared" / "permissions" / "codex.toml"
    if not src.exists():
        return "no-template"
    content = src.read_text(encoding="utf-8")
    target = Path.home() / ".codex" / "config.toml"

    if target.exists():
        existing = target.read_text(encoding="utf-8")
        # Strip our marker block (if any) before scanning for duplicate keys.
        without_block = re.sub(
            rf"{re.escape(MARKER_PERMS_HASH_START)}.*?{re.escape(MARKER_PERMS_HASH_END)}\n?",
            "", existing, flags=re.DOTALL,
        )
        for key in ("approval_policy", "sandbox_mode"):
            if re.search(rf"(?m)^\s*{key}\s*=", without_block):
                warn(f"~/.codex/config.toml already defines `{key}` outside the adk marker — "
                     f"leaving it alone. Remove it manually and re-run to enable adk permissions.")
                return "skipped (user-defined keys present)"

    return append_with_marker(target, content, MARKER_PERMS_HASH_START, MARKER_PERMS_HASH_END,
                              dry_run, repo_root)


def merge_permissions_into_junie(repo_root: Path, dry_run: bool) -> str:
    """Write ~/.junie/allowlist.json from shared/permissions/junie-allowlist.json.

    If the user already has an allowlist.json that is NOT adk-managed (no
    `_adk_managed: true` marker), leave it alone with a warning. Otherwise
    overwrite (which refreshes our managed contents on every install).
    """
    src = repo_root / "shared" / "permissions" / "junie-allowlist.json"
    if not src.exists():
        return "no-template"
    target = Path.home() / ".junie" / "allowlist.json"

    if target.exists():
        try:
            existing = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            warn(f"existing {target} is invalid JSON; leaving alone")
            return "skipped (invalid existing json)"
        if not existing.get("_adk_managed"):
            warn(f"{target} exists and is not adk-managed — leaving alone. "
                 f"Delete it (or add `\"_adk_managed\": true`) and re-run to enable adk allowlist.")
            return "skipped (user-owned)"

    pre_existed = target.exists()
    desired = read_json(src)
    write_json(target, desired, dry_run)
    if dry_run:
        return "would-update" if pre_existed else "would-create"
    return "updated" if pre_existed else "created"


def _translate_mcp_entry_claude(cfg: dict[str, Any]) -> dict[str, Any]:
    """Translate adk schema → Claude Code's `mcpServers.<name>` schema."""
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
    return entry


_URL_DEFAULT_REF_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*):-(.*?)\}")


def _expand_url_defaults_install_time(url: str) -> str:
    """Expand only `${VAR:-default}` URL placeholders at install time.

    Cursor's MCP loader does not reliably shell-expand default expressions in
    remote HTTP URLs, so a literal `${VAR:-...}` can prevent tool discovery.
    Endpoint hostnames are not credential values; secret-bearing headers stay as
    env placeholders.
    """
    return _URL_DEFAULT_REF_RE.sub(lambda m: os.environ.get(m.group(1), m.group(2)), url)


def _translate_mcp_entry_generic(cfg: dict[str, Any]) -> dict[str, Any]:
    """Translate adk schema → Cursor/Junie-style `mcpServers.<name>` schema."""
    entry: dict[str, Any] = {}
    if "url" in cfg:
        entry["url"] = _expand_url_defaults_install_time(cfg["url"])
        if "headers" in cfg:
            entry["headers"] = cfg["headers"]
    elif "command" in cfg:
        entry["command"] = cfg["command"]
        if "args" in cfg:
            entry["args"] = cfg["args"]
        if "env" in cfg:
            entry["env"] = cfg["env"]
    return entry


def _toml_key(k: str) -> str:
    """Quote a TOML bare key when it contains chars outside [A-Za-z0-9_-]."""
    if re.fullmatch(r"[A-Za-z0-9_-]+", k):
        return k
    return json.dumps(k)


# Codex 0.43+ requires `mcp_servers` to be a TOML map (`[mcp_servers.NAME]`),
# not an array of tables (`[[mcp_servers]]`). Older Codex builds accepted the
# array form; the loader was tightened (see openai/codex codex-rs/config/src/
# mcp_edit.rs::load_global_mcp_servers — it does `value.try_into::<BTreeMap>`).
# Codex also does NOT shell-expand `${VAR}` in TOML values, so we wrap stdio
# servers whose env values reference env vars in `sh -c` and forward those
# vars via `env_vars` (Codex inherits them from the host process — see
# codex-rs/rmcp-client/src/utils.rs::create_env_for_mcp_server).


_SHELL_REF_RE = re.compile(r"\$\{([A-Z_][A-Z0-9_]*)(?::-[^}]*)?\}|\$([A-Z_][A-Z0-9_]*)")


def _ref_vars(s: str) -> set[str]:
    """Return the set of shell env var names referenced as ${VAR}, ${VAR:-default}, or $VAR."""
    out: set[str] = set()
    if not isinstance(s, str):
        return out
    for m in _SHELL_REF_RE.finditer(s):
        out.add(m.group(1) or m.group(2))
    return out


def _expand_url_install_time(url: str) -> str:
    """Expand `${VAR}` / `${VAR:-default}` in a URL at install time.

    URLs are not secrets (constitution §VII applies to credential values, not
    endpoint hostnames). Variables that are unset and have no default become
    empty strings — callers must already skip unreachable MCPs (see
    `merge_mcp_into_codex` skipping `adk-mcp-rag` when `RAG_MCP_URL` is unset).
    """
    def repl(m: re.Match[str]) -> str:
        if m.group(1):
            var, default = m.group(1), None
            inner = m.group(0)[2:-1]  # strip ${ ... }
            if ":-" in inner:
                _, default = inner.split(":-", 1)
            return os.environ.get(var, default if default is not None else "")
        var = m.group(2)
        return os.environ.get(var, "")
    return _SHELL_REF_RE.sub(repl, url)


def _shell_dquote(s: str) -> str:
    """Wrap a string in double quotes for sh, preserving `$VAR` expansion."""
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _shell_arg(s: str) -> str:
    """Quote an arg for sh without expanding anything inside it."""
    if not s:
        return "''"
    if re.fullmatch(r"[A-Za-z0-9_./@:=+-]+", s):
        return s
    return "'" + s.replace("'", "'\\''") + "'"


def _translate_mcp_entry_codex(cfg: dict[str, Any]) -> str:
    """Translate adk schema → a Codex `[mcp_servers.NAME]` TOML block.

    Shape (per openai/codex codex-rs/config/src/mcp_edit.rs):
      HTTP:  url; bearer_token_env_var (Bearer-only auth); [.http_headers]
             (literal values); [.env_http_headers] (value = env var name).
      stdio: command + args + [.env] (literal values) + env_vars (forwarded
             from host by name).
    Env values that reference `${VAR}` are moved into an `sh -c` wrapper so
    the shell — not Codex — expands them at launch time; the referenced var
    names are added to `env_vars` so Codex forwards them from the host.
    """
    name = cfg["name"]
    section = f"[mcp_servers.{_toml_key(name)}]"
    if "url" in cfg:
        return _codex_http_block(name, cfg, section)
    if "command" in cfg:
        return _codex_stdio_block(name, cfg, section)
    return section


def _codex_http_block(name: str, cfg: dict[str, Any], section: str) -> str:
    lines: list[str] = [section]
    url = _expand_url_install_time(cfg["url"])
    lines.append(f"url = {json.dumps(url)}")

    headers = cfg.get("headers", {}) or {}
    bearer_env: str | None = None
    env_headers: dict[str, str] = {}
    literal_headers: dict[str, str] = {}
    for k, v in headers.items():
        if not isinstance(v, str):
            literal_headers[k] = v
            continue
        m_bearer = re.fullmatch(r"Bearer \$\{(\w+)\}", v)
        m_envonly = re.fullmatch(r"\$\{(\w+)(?::-[^}]*)?\}", v) or re.fullmatch(r"\$(\w+)", v)
        if k.lower() == "authorization" and m_bearer:
            bearer_env = m_bearer.group(1)
        elif m_envonly:
            env_headers[k] = m_envonly.group(1)
        else:
            literal_headers[k] = v

    if bearer_env:
        lines.append(f"bearer_token_env_var = {json.dumps(bearer_env)}")
    if literal_headers:
        lines.append("")
        lines.append(f"[mcp_servers.{_toml_key(name)}.http_headers]")
        for k, v in literal_headers.items():
            lines.append(f"{_toml_key(k)} = {json.dumps(v)}")
    if env_headers:
        lines.append("")
        lines.append(f"[mcp_servers.{_toml_key(name)}.env_http_headers]")
        for k, v in env_headers.items():
            lines.append(f"{_toml_key(k)} = {json.dumps(v)}")
    return "\n".join(lines)


def _codex_stdio_block(name: str, cfg: dict[str, Any], section: str) -> str:
    command: str = cfg["command"]
    args: list[str] = list(cfg.get("args", []) or [])
    env: dict[str, str] = dict(cfg.get("env", {}) or {})

    # Collect every env var name referenced in args + env values. Codex needs
    # these listed in `env_vars` so it forwards them from the host into the
    # MCP subprocess (see codex-rs/rmcp-client/src/utils.rs).
    env_var_refs: set[str] = set()
    for a in args:
        env_var_refs |= _ref_vars(a)

    # Partition env into shell-expanded (has `$`) vs literal.
    shell_env: dict[str, str] = {}
    literal_env: dict[str, str] = {}
    for k, v in env.items():
        if isinstance(v, str) and "$" in v:
            shell_env[k] = v
            env_var_refs |= _ref_vars(v)
        else:
            literal_env[k] = v

    if shell_env:
        # Wrap (or splice into existing `sh -c`) so the shell expands env values.
        if command == "sh" and args and args[0] == "-c" and len(args) >= 2:
            inner = args[1]
            exports = "\n".join(
                f"export {k}={_shell_dquote(v)}" for k, v in shell_env.items()
            )
            command = "sh"
            args = ["-c", exports + "\n" + inner]
        else:
            env_exports = " ".join(
                f"{k}={_shell_dquote(v)}" for k, v in shell_env.items()
            )
            inner_cmd = " ".join([_shell_arg(command)] + [_shell_arg(a) for a in args])
            command = "sh"
            args = ["-c", f"exec env {env_exports} {inner_cmd}"]

    lines: list[str] = [section, f"command = {json.dumps(command)}"]
    if args:
        lines.append("args = [" + ", ".join(json.dumps(a) for a in args) + "]")
    if env_var_refs:
        lines.append(
            "env_vars = [" + ", ".join(json.dumps(v) for v in sorted(env_var_refs)) + "]"
        )
    if literal_env:
        lines.append("")
        lines.append(f"[mcp_servers.{_toml_key(name)}.env]")
        for k, v in literal_env.items():
            lines.append(f"{_toml_key(k)} = {json.dumps(v)}")
    return "\n".join(lines)


def _replace_mcp_servers_and_save_user(current: dict[str, Any],
                                        adk_entries: dict[str, dict[str, Any]]) -> dict[str, str]:
    """Replace the entire `mcpServers` map with adk-only entries.

    The user explicitly asked us to wipe pre-configured (non-adk) MCPs from
    every agent. We stash whatever non-adk entries were present at first
    install under `_adkRemovedMcpServers` so `--uninstall` can put them
    back. Subsequent installs do not overwrite that stash (so re-running
    install can't lose user data).
    """
    existing = current.get("mcpServers", {}) or {}
    if not isinstance(existing, dict):
        existing = {}
    # First install only: snapshot user entries.
    if ADK_REMOVED_MCP_KEY not in current:
        user_entries = {k: v for k, v in existing.items()
                        if not str(k).startswith(ADK_MCP_NAME_PREFIX)}
        if user_entries:
            current[ADK_REMOVED_MCP_KEY] = user_entries
    # Wipe everything; write only adk entries.
    current["mcpServers"] = dict(adk_entries)
    results: dict[str, str] = {}
    removed = [k for k in existing if not str(k).startswith(ADK_MCP_NAME_PREFIX)]
    for name in adk_entries:
        results[name] = "installed"
    if removed:
        results["_removed_user_mcps"] = ", ".join(sorted(removed))
    return results


def _build_adk_mcp_entries(repo_root: Path,
                            translator) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """Build the adk-mcp-* entries map, skipping any that can't be enabled."""
    out: dict[str, dict[str, Any]] = {}
    skipped: dict[str, str] = {}
    for name, cfg in load_mcp_configs(repo_root).items():
        if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
            skipped[name] = "skipped (RAG_MCP_URL unset)"
            continue
        out[name] = translator(cfg)
    return out, skipped


def merge_mcp_into_claude(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Merge mcp/* into ~/.claude.json (the real Claude Code config) under mcpServers.

    NOTE: Claude Code reads MCP servers from `~/.claude.json`, NOT from
    `~/.claude/settings.json`. Writing to settings.json silently does
    nothing — that was the cause of "no MCPs visible after install".
    """
    settings = Path.home() / ".claude.json"
    current = read_json(settings)
    adk_entries, skipped = _build_adk_mcp_entries(repo_root, _translate_mcp_entry_claude)
    results = _replace_mcp_servers_and_save_user(current, adk_entries)
    results.update(skipped)
    write_json(settings, current, dry_run)
    return results


def merge_mcp_into_cursor(repo_root: Path, dry_run: bool) -> dict[str, str]:
    settings = Path.home() / ".cursor" / "mcp.json"
    current = read_json(settings)
    adk_entries, skipped = _build_adk_mcp_entries(repo_root, _translate_mcp_entry_generic)
    results = _replace_mcp_servers_and_save_user(current, adk_entries)
    results.update(skipped)
    write_json(settings, current, dry_run)
    return results


def merge_mcp_into_junie(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Merge mcp/* into ~/.junie/mcp/mcp.json under mcpServers.<name>.

    Junie reads its MCP server list from `~/.junie/mcp/mcp.json`. The shape
    matches Cursor's, so we re-use the same translator + replacement logic.
    """
    settings = Path.home() / ".junie" / "mcp" / "mcp.json"
    ensure_dir(settings.parent, dry_run)
    current = read_json(settings)
    adk_entries, skipped = _build_adk_mcp_entries(repo_root, _translate_mcp_entry_generic)
    results = _replace_mcp_servers_and_save_user(current, adk_entries)
    results.update(skipped)
    write_json(settings, current, dry_run)
    return results


def merge_mcp_into_codex(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Generate `[mcp_servers.NAME]` TOML blocks from mcp/adk-mcp-*.json and
    write them into `~/.codex/config.toml` between the `# adk-marker:start` /
    `:end` markers.

    Idempotent: re-running replaces the block; uninstall strips it via the
    same marker.
    """
    target = Path.home() / ".codex" / "config.toml"
    results: dict[str, str] = {}
    blocks: list[str] = []
    for name, cfg in load_mcp_configs(repo_root).items():
        if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
            results[name] = "skipped (RAG_MCP_URL unset)"
            continue
        blocks.append(_translate_mcp_entry_codex(cfg))
        results[name] = "installed"
    header = (
        "# adk v3 MCP servers — generated by install.py from "
        "mcp/adk-mcp-*.json. Do NOT edit by hand; edit the JSON sources and "
        "re-run install.sh.\n#\n"
        "# Codex requires the map form `[mcp_servers.NAME]` (see openai/codex\n"
        "# codex-rs/config/src/mcp_edit.rs). It does not shell-expand `${VAR}`\n"
        "# in TOML values, so stdio entries with `${VAR}` env values are wrapped\n"
        "# in `sh -c` and the referenced var names are listed under `env_vars`\n"
        "# so Codex forwards them from the host process."
    )
    content = header + "\n\n" + "\n\n".join(blocks)
    status = append_with_marker(
        target, content, MARKER_HASH_START, MARKER_HASH_END, dry_run, repo_root,
    )
    results["_marker_status"] = status
    return results


def _pop_marker_block(text: str, marker_start: str, marker_end: str) -> tuple[str, str | None]:
    """Remove and return a marker block from a text file."""
    start = text.find(marker_start)
    if start == -1:
        return text, None
    end = text.find(marker_end, start)
    if end == -1:
        return text, None
    end += len(marker_end)
    if end < len(text) and text[end] == "\n":
        end += 1
    block = text[start:end].strip()
    return text[:start] + text[end:], block


def _reorder_codex_config_blocks(config_path: Path) -> None:
    """Keep top-level Codex settings before generated MCP tables.

    TOML table headers stay active until the next table header, so top-level
    settings written after the MCP marker would otherwise attach to the final
    `[mcp_servers.*]` section.
    """
    if not config_path.exists():
        return
    original = config_path.read_text(encoding="utf-8")
    without_mcp, mcp_block = _pop_marker_block(original, MARKER_HASH_START, MARKER_HASH_END)
    without_blocks, permissions_block = _pop_marker_block(
        without_mcp, MARKER_PERMS_HASH_START, MARKER_PERMS_HASH_END,
    )
    if not mcp_block and not permissions_block:
        return
    parts = [p for p in (
        without_blocks.strip(),
        permissions_block,
        mcp_block,
    ) if p]
    reordered = "\n\n".join(parts).rstrip() + "\n"
    if reordered != original:
        config_path.write_text(reordered, encoding="utf-8")


# ----------------------------------------------------------------------------
# Per-agent install
# ----------------------------------------------------------------------------

def set_statusline_in_claude(dry_run: bool) -> dict[str, str]:
    """Write the statusLine command into ~/.claude/settings.json.

    Idempotent: re-running replaces the existing statusLine key. Does not
    touch any other key.
    """
    settings_path = Path.home() / ".claude" / "settings.json"
    current = read_json(settings_path)
    current["statusLine"] = {
        "type": "command",
        "command": "bash /Users/sujeet/.claude/statusline-command.sh",
    }
    write_json(settings_path, current, dry_run)
    return {"status": "ok" if not dry_run else "dry-run",
            "script": "/Users/sujeet/.claude/statusline-command.sh"}


def _hook_signature(entry: Any) -> str:
    if isinstance(entry, dict):
        entry = {k: v for k, v in entry.items() if k != "_adk_managed"}
    return json.dumps(entry, sort_keys=True)


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
    # Phase 1: prune adk-managed entries from ALL existing events, so that
    # events removed from hooks.json since the last run get dropped here too.
    for event in list(current["hooks"]):
        existing = current["hooks"][event]
        kept = [e for e in existing if not (isinstance(e, dict) and e.get("_adk_managed"))]
        if kept:
            current["hooks"][event] = kept
        else:
            del current["hooks"][event]
            actions[event] = "pruned (no longer in hooks.json)"
    # Phase 2: append fresh adk-managed entries from src.
    for event, src_entries in src_hooks.items():
        src_sigs = {_hook_signature(e) for e in src_entries}
        current["hooks"].setdefault(event, [])
        # Older installs wrote the same hooks without `_adk_managed`. Drop
        # exact untagged duplicates before appending the fresh managed entries.
        current["hooks"][event] = [
            e for e in current["hooks"][event]
            if _hook_signature(e) not in src_sigs
        ] + src_entries
        actions[event] = f"merged ({len(src_entries)} entries)"
    write_json(settings, current, dry_run)
    return {"status": "ok", "events": actions}


def cleanup_stale_adk_symlinks(dest_dir: Path, dry_run: bool) -> list[str]:
    """Remove adk-prefixed symlinks under `dest_dir` whose target no longer exists.

    Triggered on re-install when a previously-shipped skill / command is removed
    upstream (e.g. /adk-pr-reviews → CLI). Without this, the dead symlinks linger
    in the agent's skill dir and confuse the agent at load time.
    """
    if not dest_dir.exists():
        return []
    removed: list[str] = []
    for p in dest_dir.glob("adk-*"):
        if not p.is_symlink():
            continue
        try:
            target = p.resolve(strict=False)
        except OSError:
            target = None
        if target and target.exists():
            continue
        if dry_run:
            info(f"would remove stale symlink {p} (target missing)")
        else:
            try:
                p.unlink()
                info(f"removed stale symlink {p}")
            except OSError as e:
                warn(f"could not remove stale symlink {p}: {e}")
                continue
        removed.append(p.name)
    return removed


def cleanup_unlisted_adk_entries(dest_dir: Path, expected_names: set[str],
                                 dry_run: bool, reason: str) -> list[dict[str, Any]]:
    """Remove adk-* entries that are no longer emitted by this repo version."""
    if not dest_dir.exists():
        return []
    removed: list[dict[str, Any]] = []
    for p in sorted(dest_dir.glob("adk-*"), key=lambda x: x.name):
        if p.name in expected_names:
            continue
        removed.append(_remove_path(p, dry_run, reason))
    return removed


def _detect_platform() -> str:
    """Return 'mac' | 'linux' | 'other'. Linux detection assumes apt-get if present."""
    if sys.platform == "darwin":
        return "mac"
    if sys.platform.startswith("linux"):
        return "linux"
    return "other"


def _run_capture(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command, capture output, never raise. Used by dep install."""
    try:
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return cp.returncode, cp.stdout, cp.stderr
    except Exception as e:
        return 1, "", str(e)


def install_deps(repo_root: Path, dry_run: bool, results: dict[str, Any],
                 yes: bool = True, allow_curl_bash: bool = False,
                 models: list[str] | None = None) -> None:
    """Detect missing deps and install them. Platform-aware (brew on mac,
    apt-get on linux). Best-effort: a single failure does not bail the run.

    Always:
      - System binaries: git, gh, jq, ollama
      - Python pip packages: slack_sdk, json5, PyYAML, requests, lancedb,
        tree_sitter_language_pack
      - scip-* indexers (npm / pip / go install, each guarded by its toolchain)
      - Ollama models (nomic-embed-text always; opt-in for bge-m3 via --models)

    Linux + ollama: skipped unless `--allow-curl-bash` (uses the upstream
    install.sh which curl-bashes a shell script — gated for safety).
    """
    info("=== dependencies ===")
    platform = _detect_platform()
    out: dict[str, Any] = {"platform": platform, "binaries": {}, "python": {},
                          "scip": {}, "ollama_models": {}}

    if platform == "other":
        warn(f"unsupported platform {sys.platform}; printing required deps but skipping install")
        out["status"] = "platform-unsupported"
        results["deps"] = out
        return

    brew = shutil.which("brew") if platform == "mac" else None
    apt = shutil.which("apt-get") if platform == "linux" else None

    def _install_binary(name: str, mac_args: list[str] | None,
                         apt_args: list[str] | None, fallback_hint: str = "") -> None:
        existing = shutil.which(name)
        if existing:
            out["binaries"][name] = {"status": "present", "path": existing}
            return
        cmd: list[str] | None = None
        if platform == "mac" and brew and mac_args:
            cmd = ["brew"] + mac_args
        elif platform == "linux" and apt and apt_args:
            cmd = (["sudo"] if os.geteuid() != 0 else []) + ["apt-get"] + apt_args
        if cmd is None:
            out["binaries"][name] = {"status": "skipped", "hint": fallback_hint or f"install {name} manually"}
            warn(f"{name} missing; manual install needed ({fallback_hint or 'no package manager'})")
            return
        info(f"$ {' '.join(cmd)}")
        if dry_run:
            out["binaries"][name] = {"status": "would-install", "cmd": " ".join(cmd)}
            return
        code, _stdout, stderr = _run_capture(cmd)
        if code != 0:
            out["binaries"][name] = {"status": "failed", "code": code,
                                      "stderr": stderr.strip()[-300:]}
            warn(f"{name} install failed (rc={code}): {stderr.strip()[-200:]}")
        else:
            out["binaries"][name] = {"status": "installed"}

    _install_binary("git", ["install", "git"], ["install", "-y", "git"],
                    fallback_hint="brew install git OR apt-get install git")
    _install_binary("gh", ["install", "gh"], ["install", "-y", "gh"],
                    fallback_hint="brew install gh OR see cli.github.com")
    _install_binary("jq", ["install", "jq"], ["install", "-y", "jq"],
                    fallback_hint="brew install jq OR apt-get install jq")
    # Ollama: brew on mac is safe; on linux, curl-bash is the upstream path.
    if shutil.which("ollama"):
        out["binaries"]["ollama"] = {"status": "present", "path": shutil.which("ollama")}
    elif platform == "mac" and brew:
        _install_binary("ollama", ["install", "ollama"], None,
                        fallback_hint="brew install ollama")
    elif platform == "linux" and (allow_curl_bash and yes):
        cmd = ["sh", "-c", "curl -fsSL https://ollama.com/install.sh | sh"]
        info(f"$ {' '.join(cmd)}  (curl-bash; gated by --allow-curl-bash)")
        if dry_run:
            out["binaries"]["ollama"] = {"status": "would-install", "via": "curl-bash"}
        else:
            code, _stdout, stderr = _run_capture(cmd)
            out["binaries"]["ollama"] = (
                {"status": "installed", "via": "curl-bash"}
                if code == 0 else {"status": "failed", "code": code,
                                   "stderr": stderr.strip()[-300:]}
            )
    else:
        out["binaries"]["ollama"] = {"status": "skipped",
                                      "hint": "linux ollama install gates behind --allow-curl-bash; "
                                              "or run `curl -fsSL https://ollama.com/install.sh | sh`"}
        warn("ollama not installed (linux); re-run with --allow-curl-bash or install manually")

    # Python pip deps — always pip-install missing ones into the user site.
    # lancedb has a tight upper bound because 0.30 introduced a breaking change
    # to `list_tables()`. Keep in sync with scripts/lib/code_index/requirements.txt.
    py_pkgs = [
        ("slack_sdk", "slack_sdk"),
        ("json5", "json5"),
        ("yaml", "PyYAML"),
        ("requests", "requests"),
        ("lancedb", "lancedb>=0.30,<0.40"),
        ("tree_sitter_language_pack", "tree_sitter_language_pack"),
        # textual: optional at the doctor level (it gracefully falls back to
        # plain text) but cheap to have for `adk doctor --tui`. Auto-installing
        # eliminates the WARN that otherwise shows on every doctor run.
        ("textual", "textual"),
    ]
    for mod, pkg in py_pkgs:
        try:
            __import__(mod)
            out["python"][pkg] = {"status": "present"}
            continue
        except ImportError:
            pass
        cmd = [sys.executable, "-m", "pip", "install", "--user", pkg]
        info(f"$ {' '.join(cmd)}")
        if dry_run:
            out["python"][pkg] = {"status": "would-install"}
            continue
        code, _stdout, stderr = _run_capture(cmd)
        out["python"][pkg] = (
            {"status": "installed"} if code == 0
            else {"status": "failed", "code": code, "stderr": stderr.strip()[-300:]}
        )

    # scip-* indexers (best-effort; each gated by its toolchain).
    if not shutil.which("scip-typescript") and shutil.which("npm"):
        cmd = ["npm", "install", "-g", "@sourcegraph/scip-typescript"]
        info(f"$ {' '.join(cmd)}")
        if dry_run:
            out["scip"]["scip-typescript"] = "would-install"
        else:
            code, _stdout, stderr = _run_capture(cmd)
            out["scip"]["scip-typescript"] = "installed" if code == 0 else f"failed ({code})"
    elif shutil.which("scip-typescript"):
        out["scip"]["scip-typescript"] = "present"
    else:
        out["scip"]["scip-typescript"] = "skipped (no npm)"

    if not shutil.which("scip-python"):
        cmd = [sys.executable, "-m", "pip", "install", "--user", "scip-python"]
        info(f"$ {' '.join(cmd)}")
        if dry_run:
            out["scip"]["scip-python"] = "would-install"
        else:
            code, _stdout, stderr = _run_capture(cmd)
            out["scip"]["scip-python"] = "installed" if code == 0 else f"failed ({code})"
    else:
        out["scip"]["scip-python"] = "present"

    if not shutil.which("scip-go") and shutil.which("go"):
        cmd = ["go", "install", "github.com/sourcegraph/scip-go/cmd/scip-go@latest"]
        info(f"$ {' '.join(cmd)}")
        if dry_run:
            out["scip"]["scip-go"] = "would-install"
        else:
            code, _stdout, stderr = _run_capture(cmd)
            out["scip"]["scip-go"] = "installed" if code == 0 else f"failed ({code})"
    elif shutil.which("scip-go"):
        out["scip"]["scip-go"] = "present"
    else:
        out["scip"]["scip-go"] = "skipped (no go toolchain)"

    if not shutil.which("scip-java") and platform == "mac" and brew:
        cmd = ["brew", "install", "scip-java"]
        info(f"$ {' '.join(cmd)}")
        if dry_run:
            out["scip"]["scip-java"] = "would-install"
        else:
            code, _stdout, stderr = _run_capture(cmd)
            out["scip"]["scip-java"] = "installed" if code == 0 else f"failed ({code})"
    elif shutil.which("scip-java"):
        out["scip"]["scip-java"] = "present"
    else:
        out["scip"]["scip-java"] = "skipped (mac-only auto-install via brew)"

    # Ollama models (only if the binary exists).
    wanted_models = models or ["nomic-embed-text"]
    if shutil.which("ollama"):
        code, list_stdout, _ = _run_capture(["ollama", "list"])
        have = list_stdout if code == 0 else ""
        for model in wanted_models:
            base = model.rsplit(":", 1)[0]
            if base in have:
                out["ollama_models"][model] = "present"
                continue
            info(f"$ ollama pull {model}")
            if dry_run:
                out["ollama_models"][model] = "would-pull"
                continue
            # Pull is interactive (progress bar) — let it stream to the terminal.
            try:
                cp = subprocess.run(["ollama", "pull", model], timeout=900)
                out["ollama_models"][model] = "pulled" if cp.returncode == 0 else f"failed ({cp.returncode})"
            except Exception as e:
                out["ollama_models"][model] = f"error: {e}"
    else:
        out["ollama_models"]["_skipped"] = "ollama binary missing; cannot pull models"

    results["deps"] = out


def _zsh_completion_insert(text: str) -> tuple[str, int | None, str]:
    """Return zshrc text with the managed fpath block inserted before compinit.

    The returned line number is the 1-based insertion point. It is intentionally
    enough for a sanitized diff without surfacing shell-init file contents.
    """
    if ADK_ZSH_COMPLETION_START in text and ADK_ZSH_COMPLETION_END in text:
        return text, None, "present"

    lines = text.splitlines(keepends=True)
    insert_at = 0
    status = "prepended"
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if re.search(r"(?:^|[;&|\s])compinit(?:[\s;&|]|$)", line):
            insert_at = i
            status = "inserted-before-compinit"
            break

    block = ADK_ZSH_COMPLETION_BLOCK
    if lines and insert_at > 0 and not lines[insert_at - 1].endswith("\n"):
        block = "\n" + block
    if lines and insert_at < len(lines) and insert_at > 0:
        block = block + ("\n" if lines[insert_at - 1].strip() else "")

    new_lines = lines[:insert_at] + [block] + lines[insert_at:]
    if not lines:
        return block, 1, "created"
    return "".join(new_lines), insert_at + 1, status


def _zsh_completion_diff(zshrc: Path, line_no: int | None, status: str) -> str:
    if line_no is None:
        return f"{zshrc}: adk completion block already present"
    header = f"@@ {status} at line {line_no} (context redacted) @@"
    added = "".join("+" + line for line in ADK_ZSH_COMPLETION_BLOCK.splitlines(True)).rstrip()
    return f"--- {zshrc}\n+++ {zshrc}\n{header}\n{added}"


def _verify_zsh_completion_registered() -> dict[str, str]:
    if not shutil.which("zsh"):
        return {
            "status": "warn",
            "detail": "zsh not found on PATH; cannot verify `compdef -p adk`",
        }
    cmd = (
        "autoload -Uz compinit; "
        "compinit -u >/dev/null 2>&1; "
        "compdef -p adk >/dev/null 2>&1"
    )
    try:
        cp = subprocess.run(["zsh", "-ic", cmd], capture_output=True, text=True, timeout=8)
    except Exception as e:
        return {"status": "fail", "detail": f"zsh verification failed: {e}"}
    if cp.returncode == 0:
        return {"status": "pass", "detail": "`compdef -p adk` returned a handler"}
    return {
        "status": "fail",
        "detail": (
            "adk completion is not registered in a fresh zsh. Add "
            '`[[ -d "$HOME/.zsh/completions" ]] && fpath=("$HOME/.zsh/completions" $fpath)` '
            "before `compinit` in ~/.zshrc, then open a new shell."
        ),
    }


def _wire_zsh_fpath(*, dry_run: bool) -> dict[str, Any]:
    """Offer to add ~/.zsh/completions to fpath before compinit.

    The prompt shows a context-free diff so secret shell-init content never
    enters stdout/stderr. Non-interactive installs skip the write and print the
    same manual remediation.
    """
    zshrc = Path.home() / ".zshrc"
    existing = zshrc.read_text(encoding="utf-8") if zshrc.exists() else ""
    new_text, line_no, status = _zsh_completion_insert(existing)
    if status == "present":
        return {"status": "present", "verify": _verify_zsh_completion_registered()}

    diff = _zsh_completion_diff(zshrc, line_no, status)
    print("\nProposed zsh completion wiring:")
    print(diff)

    if dry_run:
        return {"status": f"would-{status}", "path": str(zshrc)}
    if not sys.stdin.isatty():
        warn(
            "not modifying ~/.zshrc because install is running non-interactively. "
            "Add the managed block shown above before `compinit`, then run "
            "`adk doctor --completion`."
        )
        return {"status": "skipped-needs-approval", "path": str(zshrc)}

    answer = input("Apply this ~/.zshrc change? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        return {"status": "skipped-by-user", "path": str(zshrc)}

    zshrc.parent.mkdir(parents=True, exist_ok=True)
    zshrc.write_text(new_text, encoding="utf-8")
    verify = _verify_zsh_completion_registered()
    return {"status": status, "path": str(zshrc), "verify": verify}


def bash_completion_warning() -> dict[str, str]:
    shell = Path(os.environ.get("SHELL", "")).name
    if shell != "bash":
        return {"status": "not-bash", "detail": f"SHELL={shell or 'unknown'}"}

    bashrc = Path.home() / ".bashrc"
    text = bashrc.read_text(encoding="utf-8") if bashrc.exists() else ""
    if "bash_completion" in text or "bash-completion" in text:
        return {"status": "present", "detail": f"{bashrc} appears to source bash-completion"}

    detail = (
        "bash completion file was written, but bash-completion@2 is not sourced. "
        "On macOS: `brew install bash-completion@2`, then add "
        '`[[ -r "$(brew --prefix)/etc/profile.d/bash_completion.sh" ]] && '
        'source "$(brew --prefix)/etc/profile.d/bash_completion.sh"` to ~/.bashrc.'
    )
    warn(detail)
    return {"status": "warn", "detail": detail}


def install_completions(dry_run: bool, results: dict[str, Any]) -> None:
    """Install shell completion scripts to the conventional user paths.

    Best-effort: bash + zsh + fish, each only if the dest dir already exists OR
    can be created without sudo. Always uses `bin/adk completion <shell>` via
    subprocess so the static script stays in sync with the CLI module.
    """
    info("=== shell completions ===")
    out: dict[str, Any] = {}
    # During dry-run the symlink hasn't been created yet, so call the source
    # bin/adk directly. Otherwise call through the symlink.
    adk = ADK_BIN_TARGET if ADK_BIN_TARGET.exists() else (
        Path(__file__).resolve().parent / "bin" / "adk"
    )
    if not adk.exists():
        warn("adk binary not found; skipping completion install")
        results["completions"] = {"status": "skipped"}
        return

    targets = [
        ("bash", Path.home() / ".local" / "share" / "bash-completion" / "completions" / "adk"),
        ("zsh",  Path.home() / ".zsh" / "completions" / "_adk"),
        ("fish", Path.home() / ".config" / "fish" / "completions" / "adk.fish"),
    ]
    for shell, dst in targets:
        try:
            cp = subprocess.run([str(adk), "completion", shell],
                                capture_output=True, text=True, check=True, timeout=10)
        except Exception as e:
            out[shell] = {"status": "failed", "error": str(e)}
            continue
        if dry_run:
            out[shell] = {"status": "would-write", "dst": str(dst)}
            continue
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(cp.stdout, encoding="utf-8")
            out[shell] = {"status": "written", "dst": str(dst)}
        except Exception as e:
            out[shell] = {"status": "failed", "error": str(e), "dst": str(dst)}
    out["zsh_fpath"] = _wire_zsh_fpath(dry_run=dry_run)
    out["bash_warning"] = bash_completion_warning()
    results["completions"] = out


def install_adk_bin(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    """Symlink <repo>/bin/adk → ~/.local/bin/adk so the `adk` CLI is on PATH.

    Creates ~/.local/bin if missing. If ~/.local/bin is not on PATH, prints a
    one-line export hint (does not touch shell-init files).
    """
    info("=== adk CLI ===")
    src = repo_root / "bin" / "adk"
    if not src.exists():
        warn(f"bin/adk missing at {src}; skipping CLI symlink")
        results["adk_bin"] = {"status": "skipped-source-missing", "src": str(src)}
        return
    target_dir = ADK_BIN_TARGET.parent
    ensure_dir(target_dir, dry_run)
    sym_result = make_symlink(src, ADK_BIN_TARGET, dry_run)
    info(f"adk CLI: {sym_result} → {ADK_BIN_TARGET}")
    # PATH hint (no shell-init edits).
    path_env = os.environ.get("PATH", "")
    on_path = str(target_dir) in path_env.split(":")
    if not on_path:
        warn(
            f"{target_dir} is not on $PATH. Add this to your shell init:\n"
            f"    export PATH=\"{target_dir}:$PATH\""
        )
    results["adk_bin"] = {
        "status": sym_result,
        "src": str(src),
        "target": str(ADK_BIN_TARGET),
        "on_path": on_path,
    }


def install_claude(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Claude Code ===")
    home_claude = Path.home() / ".claude"
    ensure_dir(home_claude / "skills", dry_run)
    ensure_dir(home_claude / "agents", dry_run)
    ensure_dir(home_claude / "commands", dry_run)
    # Prune stale symlinks from previous installs (e.g. /adk-pr-reviews → CLI).
    stale_skills = cleanup_stale_adk_symlinks(home_claude / "skills", dry_run)
    stale_agents = cleanup_stale_adk_symlinks(home_claude / "agents", dry_run)
    stale_cmds = cleanup_stale_adk_symlinks(home_claude / "commands", dry_run)
    # skills
    skill_results = {}
    skill_sources = [
        p for p in sorted((repo_root / "skills").glob("adk-*"))
        if p.is_dir() and p.name not in NON_SLASH_SKILLS
    ]
    obsolete_skills = cleanup_unlisted_adk_entries(
        home_claude / "skills", {p.name for p in skill_sources}, dry_run,
        "remove obsolete ADK Claude skill",
    )
    for skill_dir in skill_sources:
        if skill_dir.is_dir() and skill_dir.name not in NON_SLASH_SKILLS:
            dst = home_claude / "skills" / skill_dir.name
            skill_results[skill_dir.name] = make_symlink(skill_dir, dst, dry_run)
    # agents
    agent_results = {}
    agent_sources = sorted((repo_root / "agents-claude" / "agents").glob("adk-agent-*.md"))
    obsolete_agents = cleanup_unlisted_adk_entries(
        home_claude / "agents", {p.name for p in agent_sources}, dry_run,
        "remove obsolete ADK Claude agent",
    )
    for agent_file in agent_sources:
        dst = home_claude / "agents" / agent_file.name
        agent_results[agent_file.name] = make_symlink(agent_file, dst, dry_run)
    # commands
    cmd_results = {}
    cmd_sources = sorted((repo_root / "agents-claude" / "commands").glob("adk-*.md"))
    obsolete_cmds = cleanup_unlisted_adk_entries(
        home_claude / "commands", {p.name for p in cmd_sources}, dry_run,
        "remove obsolete ADK Claude command",
    )
    for cmd_file in cmd_sources:
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
    # Permissions merge (allow-most / ask-on-dangerous)
    perms_result = merge_permissions_into_claude(repo_root, dry_run)
    # statusLine
    statusline_result = set_statusline_in_claude(dry_run)
    results["claude"] = {
        "skills": skill_results, "agents": agent_results, "commands": cmd_results,
        "stale_removed": {"skills": stale_skills, "agents": stale_agents, "commands": stale_cmds},
        "obsolete_removed": {"skills": obsolete_skills, "agents": obsolete_agents, "commands": obsolete_cmds},
        "claude_md_append": append_result, "mcp_merge": mcp_results, "hooks": hooks_result,
        "permissions": perms_result, "statusline": statusline_result,
    }


def install_cursor(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Cursor ===")
    rules_dir = Path.home() / ".cursor" / "rules"
    ensure_dir(rules_dir, dry_run)
    stale_rules = cleanup_stale_adk_symlinks(rules_dir, dry_run)
    # Requestable Cursor rules need rendered absolute @ paths. They used to be
    # symlinks, but Cursor does not expand `{{ADK_REPO}}` inside symlinked rule
    # sources.
    rule_results = {}
    rule_sources = sorted((repo_root / "agents-cursor" / "rules").glob("adk-*.mdc"))
    obsolete_rules = cleanup_unlisted_adk_entries(
        rules_dir, {p.name for p in rule_sources}, dry_run,
        "remove obsolete ADK Cursor rule",
    )
    for rule_file in rule_sources:
        dst = rules_dir / rule_file.name
        rule_results[rule_file.name] = write_rendered_file(rule_file, dst, repo_root, dry_run)
    # global always-rule (the AGENTS.md pointer).
    # _adk.mdc is FULLY adk-managed — Cursor needs frontmatter at the file top
    # (not inside HTML comments), so we overwrite rather than merge-by-marker.
    tmpl = (repo_root / "agents-cursor" / "cursor-rules.append.tmpl").read_text(encoding="utf-8")
    rendered = tmpl.replace("{{ADK_REPO}}", str(repo_root))
    _adk_mdc = rules_dir / "_adk.mdc"
    if dry_run:
        append_result = "would-overwrite" if _adk_mdc.exists() else "would-create"
    else:
        _adk_mdc.parent.mkdir(parents=True, exist_ok=True)
        _adk_mdc.write_text(rendered, encoding="utf-8")
        append_result = "overwritten"
    # MCP merge
    mcp_results = merge_mcp_into_cursor(repo_root, dry_run)
    # Permissions merge (allow-most / ask-on-dangerous)
    perms_result = merge_permissions_into_cursor(repo_root, dry_run)
    results["cursor"] = {
        "rules": rule_results, "stale_removed": {"rules": stale_rules},
        "obsolete_removed": {"rules": obsolete_rules},
        "always_rule_append": append_result, "mcp_merge": mcp_results,
        "permissions": perms_result,
    }


def _codex_global_instructions(repo_root: Path) -> str:
    return f"""# ADK global routing

This file is fully managed by agents-devkit. Re-run `{repo_root}/install.sh --target codex` to refresh it.

For every prompt:

1. Read `{repo_root}/AGENTS.md` for intent-to-skill routing.
2. Use only ADK prompt wrappers from `~/.codex/prompts/adk-*.md`.
3. Apply `{repo_root}/shared/constitution.md` and `{repo_root}/shared/question-first.md` before any skill workflow.
4. Use MCP servers generated from `{repo_root}/mcp/adk-mcp-*.json` in `~/.codex/config.toml`.
5. Treat non-ADK Codex plugins, imported skills, prompts, and MCP servers as unavailable unless the user explicitly asks to bypass ADK for this invocation.
6. Log every non-trivial decision to `~/.agents-devkit/improve/learning/decisions.jsonl` via `{repo_root}/scripts/decision_logger.py`.
"""


def install_codex(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Codex ===")
    codex_dir = Path.home() / ".codex"
    ensure_dir(codex_dir / "prompts", dry_run)
    prompt_results = {}
    prompt_sources = sorted((repo_root / "agents-codex" / "prompts").glob("adk-*.md"))
    obsolete_prompts = cleanup_unlisted_adk_entries(
        codex_dir / "prompts", {p.name for p in prompt_sources}, dry_run,
        "remove obsolete ADK Codex prompt",
    )
    for prompt_file in prompt_sources:
        dst = codex_dir / "prompts" / prompt_file.name
        prompt_results[prompt_file.name] = make_symlink(prompt_file, dst, dry_run)
    # MCP merge — generated from mcp/adk-mcp-*.json (single source of truth
    # shared with Claude / Cursor / Junie).
    mcp_results = merge_mcp_into_codex(repo_root, dry_run)
    # Permissions merge (approval_policy / sandbox_mode)
    perms_result = merge_permissions_into_codex(repo_root, dry_run)
    # TOML has no explicit "end of section" — top-level keys written after a
    # `[mcp_servers.NAME]` block silently belong to that section. Reorder so
    # the permissions block (which contains top-level keys) sits before the
    # mcp_servers marker block.
    if not dry_run:
        _reorder_codex_config_blocks(codex_dir / "config.toml")
    # Global instructions pointer
    instructions = codex_dir / "instructions.md"
    pointer = (
        f"For every prompt, follow the routing in @{repo_root}/AGENTS.md. "
        "Use only ADK prompt wrappers (`adk-*`) and ADK MCP servers "
        "(`adk-mcp-*`) unless the user explicitly asks to bypass ADK."
    )
    instructions_append = append_with_marker(
        instructions, pointer, MARKER_MD_START, MARKER_MD_END, dry_run, repo_root,
    )
    agents_md = codex_dir / "AGENTS.md"
    codex_agents_status = "would-overwrite" if dry_run else "overwritten"
    if not dry_run:
        agents_md.parent.mkdir(parents=True, exist_ok=True)
        agents_md.write_text(_codex_global_instructions(repo_root), encoding="utf-8")
    results["codex"] = {
        "prompts": prompt_results,
        "obsolete_removed": {"prompts": obsolete_prompts},
        "mcp_merge": mcp_results,
        "permissions": perms_result,
        "instructions_append": instructions_append,
        "agents_md": codex_agents_status,
        "gaps": "see agents-codex/README.md for the capability table",
    }


def install_junie(repo_root: Path, dry_run: bool, results: dict[str, Any]) -> None:
    info("=== Junie ===")
    junie_dir = Path.home() / ".junie"
    ensure_dir(junie_dir, dry_run)
    ensure_dir(junie_dir / "skills", dry_run)
    ensure_dir(junie_dir / "commands", dry_run)
    tmpl = (repo_root / "agents-junie" / "guidelines.md.append.tmpl").read_text(encoding="utf-8")
    guidelines_append = append_with_marker(
        junie_dir / "guidelines.md", tmpl, MARKER_MD_START, MARKER_MD_END, dry_run, repo_root,
    )
    # Symlink skills/adk-* into ~/.junie/skills/ — Junie auto-discovers skills
    # with a SKILL.md in each subdir, same as Claude Code.
    skill_results: dict[str, str] = {}
    skill_sources = [
        p for p in sorted((repo_root / "skills").glob("adk-*"))
        if p.is_dir() and p.name not in NON_SLASH_SKILLS
    ]
    obsolete_skills = cleanup_unlisted_adk_entries(
        junie_dir / "skills", {p.name for p in skill_sources}, dry_run,
        "remove obsolete ADK Junie skill",
    )
    for skill_dir in skill_sources:
        dst = junie_dir / "skills" / skill_dir.name
        skill_results[skill_dir.name] = make_symlink(skill_dir, dst, dry_run)
    # Slash commands: Junie skills are auto-invoked by description match, not
    # by typing `/adk-…`. To make `/adk-*` appear in the slash menu, write
    # rendered command Markdowns (re-used from agents-claude/commands) into
    # ~/.junie/commands/. Junie command format (YAML frontmatter w/
    # `description:` + body) is compatible with Claude's.
    cmd_results: dict[str, str] = {}
    cmd_sources = sorted((repo_root / "agents-claude" / "commands").glob("adk-*.md"))
    obsolete_cmds = cleanup_unlisted_adk_entries(
        junie_dir / "commands", {p.name for p in cmd_sources}, dry_run,
        "remove obsolete ADK Junie command",
    )
    for cmd_file in cmd_sources:
        dst = junie_dir / "commands" / cmd_file.name
        rendered = cmd_file.read_text(encoding="utf-8").replace("{{ADK_REPO}}", str(repo_root))
        if dry_run:
            cmd_results[cmd_file.name] = "would-write"
            continue
        prev = dst.read_text(encoding="utf-8") if dst.exists() else None
        dst.write_text(rendered, encoding="utf-8")
        cmd_results[cmd_file.name] = "kept" if prev == rendered else ("updated" if prev else "created")
    # MCP merge → ~/.junie/mcp/mcp.json (real config; previously only wrote a
    # paste-this snippet, which is why Junie users saw zero adk MCPs).
    mcp_results = merge_mcp_into_junie(repo_root, dry_run)
    # Keep emitting the paste-this snippet for older Junie versions whose MCP
    # config dir isn't `~/.junie/mcp/`.
    mcp_snippet_path = repo_root / "agents-junie" / "junie-mcp.json.snippet"
    mcp_snippet = {"mcpServers": {}}
    for name, cfg in load_mcp_configs(repo_root).items():
        if name == "adk-mcp-rag" and not os.environ.get("RAG_MCP_URL"):
            continue
        mcp_snippet["mcpServers"][name] = cfg
    if not dry_run:
        mcp_snippet_path.write_text(json.dumps(mcp_snippet, indent=2) + "\n", encoding="utf-8")
    # Permissions allowlist write
    perms_result = merge_permissions_into_junie(repo_root, dry_run)
    results["junie"] = {
        "guidelines_append": guidelines_append,
        "skills": skill_results,
        "commands": cmd_results,
        "obsolete_removed": {"skills": obsolete_skills, "commands": obsolete_cmds},
        "mcp_merge": mcp_results,
        "mcp_snippet_written": str(mcp_snippet_path) if not dry_run else "(dry-run)",
        "permissions": perms_result,
    }


# ----------------------------------------------------------------------------
# Uninstall
# ----------------------------------------------------------------------------

def _restore_scalar(section: dict[str, Any], key: str, book: dict[str, Any], prev_key: str) -> None:
    if prev_key not in book:
        return
    prev_val = book[prev_key]
    if prev_val is None:
        section.pop(key, None)
    else:
        section[key] = prev_val


def strip_permissions_from_claude(dry_run: bool) -> str:
    settings_path = Path.home() / ".claude" / "settings.json"
    if not settings_path.exists():
        return "absent"
    current = read_json(settings_path)
    book = current.get(ADK_PERMS_BOOKKEEPING_KEY, {})
    if not book:
        return "no-bookkeeping"
    perms = current.get("permissions", {})
    for key in ("allow", "ask", "deny"):
        managed = book.get(key, [])
        if managed and key in perms:
            perms[key] = [x for x in perms[key] if x not in managed]
    _restore_scalar(perms, "defaultMode", book, "defaultMode__previous")
    current.pop(ADK_PERMS_BOOKKEEPING_KEY, None)
    write_json(settings_path, current, dry_run)
    return "stripped"


def strip_permissions_from_cursor(dry_run: bool) -> str:
    settings_path = Path.home() / ".cursor" / "cli-config.json"
    if not settings_path.exists():
        return "absent"
    current = read_json(settings_path)
    book = current.get(ADK_PERMS_BOOKKEEPING_KEY, {})
    if not book:
        return "no-bookkeeping"
    perms = current.get("permissions", {})
    for key in ("allow", "deny"):
        managed = book.get(key, [])
        if managed and key in perms:
            perms[key] = [x for x in perms[key] if x not in managed]
    _restore_scalar(current, "approvalMode", book, "approvalMode__previous")
    sandbox_book = book.get("sandbox", {})
    sandbox = current.get("sandbox", {})
    if sandbox_book:
        for skey in ("mode", "networkAccess"):
            _restore_scalar(sandbox, skey, sandbox_book, f"{skey}__previous")
    current.pop(ADK_PERMS_BOOKKEEPING_KEY, None)
    write_json(settings_path, current, dry_run)
    return "stripped"


def restore_mcp_servers(settings_path: Path, dry_run: bool) -> str:
    """Drop adk-mcp-* entries and restore previously-stashed user MCPs.

    Mirror of `_replace_mcp_servers_and_save_user`. If the file doesn't
    exist or has no bookkeeping, we still strip adk-mcp-* names from the
    map.
    """
    if not settings_path.exists():
        return "absent"
    current = read_json(settings_path)
    mcps = current.get("mcpServers", {}) or {}
    if not isinstance(mcps, dict):
        return "skipped (non-dict mcpServers)"
    kept = {k: v for k, v in mcps.items()
            if not str(k).startswith(ADK_MCP_NAME_PREFIX)}
    saved = current.pop(ADK_REMOVED_MCP_KEY, {}) or {}
    if isinstance(saved, dict):
        for k, v in saved.items():
            kept.setdefault(k, v)
    if kept:
        current["mcpServers"] = kept
    else:
        current.pop("mcpServers", None)
    write_json(settings_path, current, dry_run)
    return f"restored ({len(saved)} user mcps put back)" if saved else "stripped"


def strip_permissions_from_junie(dry_run: bool) -> str:
    target = Path.home() / ".junie" / "allowlist.json"
    if not target.exists():
        return "absent"
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "skipped (invalid json)"
    if not data.get("_adk_managed"):
        return "skipped (user-owned)"
    if dry_run:
        return "would-remove"
    target.unlink()
    return "removed"


def uninstall_adk_bin(dry_run: bool) -> dict[str, Any]:
    """Remove the ~/.local/bin/adk symlink if it points to our repo's bin/adk."""
    p = ADK_BIN_TARGET
    if not p.is_symlink() and not p.exists():
        return {"status": "missing", "target": str(p)}
    if not p.is_symlink():
        return {"status": "skipped-not-symlink", "target": str(p)}
    if dry_run:
        info(f"would remove symlink {p}")
        return {"status": "would-remove", "target": str(p)}
    p.unlink()
    info(f"removed symlink {p}")
    return {"status": "removed", "target": str(p)}


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
        # Permissions: drop adk-managed entries, restore previous defaultMode
        results["claude_permissions"] = strip_permissions_from_claude(dry_run)
        # MCPs: strip adk entries from ~/.claude.json and restore stashed user entries
        results["claude_mcps"] = restore_mcp_servers(Path.home() / ".claude.json", dry_run)
        results["claude"] = "uninstalled (symlinks removed; CLAUDE.md marker stripped; adk hooks + permissions stripped; adk MCPs removed; user MCPs restored)"
    elif target == "cursor":
        rules = Path.home() / ".cursor" / "rules"
        for p in rules.glob("adk-*.mdc"):
            if p.is_symlink():
                if dry_run:
                    info(f"would remove {p}")
                else:
                    p.unlink()
        strip_marker(rules / "_adk.mdc", MARKER_MD_START, MARKER_MD_END, dry_run)
        results["cursor_permissions"] = strip_permissions_from_cursor(dry_run)
        results["cursor_mcps"] = restore_mcp_servers(Path.home() / ".cursor" / "mcp.json", dry_run)
        results["cursor"] = "uninstalled (rules removed; _adk.mdc marker stripped; adk permissions + MCPs stripped; user MCPs restored)"
    elif target == "codex":
        prompts = Path.home() / ".codex" / "prompts"
        for p in prompts.glob("adk-*.md"):
            if p.is_symlink():
                if dry_run:
                    info(f"would remove {p}")
                else:
                    p.unlink()
        strip_marker(Path.home() / ".codex" / "config.toml", MARKER_HASH_START, MARKER_HASH_END, dry_run)
        strip_marker(Path.home() / ".codex" / "config.toml", MARKER_PERMS_HASH_START, MARKER_PERMS_HASH_END, dry_run)
        strip_marker(Path.home() / ".codex" / "instructions.md", MARKER_MD_START, MARKER_MD_END, dry_run)
        results["codex"] = "uninstalled (mcp + permissions blocks stripped)"
    elif target == "junie":
        # Remove adk skill symlinks
        junie_skills = Path.home() / ".junie" / "skills"
        skill_removed = 0
        for p in junie_skills.glob("adk-*"):
            if p.is_symlink():
                if dry_run:
                    info(f"would remove {p}")
                else:
                    p.unlink()
                skill_removed += 1
        results["junie_skills_removed"] = skill_removed
        # Remove adk slash-command files (regular files, not symlinks)
        junie_commands = Path.home() / ".junie" / "commands"
        cmd_removed = 0
        if junie_commands.exists():
            for p in junie_commands.glob("adk-*.md"):
                if p.is_file() and not p.is_symlink():
                    if dry_run:
                        info(f"would remove {p}")
                    else:
                        p.unlink()
                    cmd_removed += 1
        results["junie_commands_removed"] = cmd_removed
        strip_marker(Path.home() / ".junie" / "guidelines.md", MARKER_MD_START, MARKER_MD_END, dry_run)
        results["junie_permissions"] = strip_permissions_from_junie(dry_run)
        results["junie_mcps"] = restore_mcp_servers(Path.home() / ".junie" / "mcp" / "mcp.json", dry_run)
        results["junie"] = "uninstalled (skill symlinks + guidelines marker + adk allowlist + adk MCPs removed; user MCPs restored)"


# ----------------------------------------------------------------------------
# Bootstrap user dir
# ----------------------------------------------------------------------------

def bootstrap_user_dir(repo_root: Path, dry_run: bool) -> dict[str, str]:
    """Create adk home dirs v4 skeleton.

    Layout (see shared/paths.md):
      $ADK_CONFIG_HOME/          # core.yaml + repos.md + links.json5 + connectors/*.md
      $ADK_MEMORY_HOME/          # cross-session memory
      $ADK_DATA_HOME/            # machine-local working dirs
        improve/ repos/ skill-*/
    """
    out: dict[str, str] = {}

    config_root = adk_config_home()
    improve_root = adk_improve_home()
    memory = adk_memory_home()
    data_root = adk_data_home()

    learning = improve_root / "learning"
    metadata = improve_root / "metadata"
    sessions = learning / "sessions"
    proposals = learning / "proposals"
    archive = learning / "archive"
    connectors = config_root / "connectors"
    for d in (config_root, connectors, improve_root, learning, metadata, memory,
              sessions, proposals, archive):
        ensure_dir(d, dry_run)

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

    # $ADK_DATA_HOME — working-dir root for global skills.
    for sub in ("repos", "skill-pr-review", "skill-investigate", "skill-review",
                "skill-sync", "skill-setup", "skill-explain"):
        ensure_dir(data_root / sub, dry_run)
    out["adk_data_root"] = str(data_root)
    return out


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="adk installer (ADK-only agent profile)")
    ap.add_argument("--repo-root", required=True, type=Path)
    ap.add_argument("--target", default=None, help="comma-separated; or 'all'")
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-deps", action="store_true",
                    help="skip auto-install of system + python dependencies")
    ap.add_argument("--no-completions", action="store_true",
                    help="skip shell-completion install")
    ap.add_argument("--allow-curl-bash", action="store_true",
                    help="allow upstream curl-bash installer on linux (ollama)")
    ap.add_argument("--models", default="nomic-embed-text",
                    help="comma-separated ollama models to pull (default: nomic-embed-text)")
    ap.add_argument("--statusline", action="store_true",
                    help="only patch the statusLine key in ~/.claude/settings.json; skip full install")
    args = ap.parse_args()

    repo_root: Path = args.repo_root.resolve()
    dry_run: bool = args.dry_run

    # --statusline: surgical patch only — skip all other install steps.
    if args.statusline:
        result = set_statusline_in_claude(dry_run)
        print(json.dumps({"statusline": result}, indent=2))
        return 0

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
        # adk CLI symlink: only remove on full-fleet uninstall (`--target all` or
        # an explicit listing of every supported target). A single-target
        # uninstall leaves the CLI alone — the user may still want `adk pr-scan`.
        if set(targets) >= set(SUPPORTED):
            results["adk_bin"] = uninstall_adk_bin(dry_run)
        print(json.dumps(results, indent=2))
        return 0

    # Enforce the ADK-only machine profile before writing fresh ADK artifacts.
    # This makes install.sh repeatable: every run first removes stale/non-ADK
    # integrations and then recreates the desired state from this repo.
    try:
        results["adk_only_cleanup"] = cleanup_adk_only(repo_root, targets, dry_run)
    except Exception as e:
        err(f"ADK-only cleanup failed: {e}")
        results["adk_only_cleanup"] = {"error": str(e)}

    # Always bootstrap ~/.agents-devkit/config/
    results["user_dir"] = bootstrap_user_dir(repo_root, dry_run)

    # Always install the `adk` CLI (target-agnostic — it's a user-level shell binary).
    try:
        install_adk_bin(repo_root, dry_run, results)
    except Exception as e:
        err(f"adk CLI install failed: {e}")
        results["adk_bin"] = {"error": str(e)}

    # Dependency auto-install (full-auto unless --no-deps).
    if not args.no_deps:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        try:
            install_deps(repo_root, dry_run, results, yes=True,
                         allow_curl_bash=args.allow_curl_bash, models=models)
        except Exception as e:
            err(f"dep install failed: {e}")
            results["deps"] = {"error": str(e)}

    # Shell completions (after adk binary is in place).
    if not args.no_completions:
        try:
            install_completions(dry_run, results)
        except Exception as e:
            err(f"completion install failed: {e}")
            results["completions"] = {"error": str(e)}

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
    print("  1. run /adk-setup --init from your agent to scaffold ~/.agents-devkit/config/{core.yaml,repos.md,connectors/*.md,links.json5}.")
    print("  2. set env vars per SETUP.md.")
    print("  3. restart your agent so it picks up env + MCP changes.")
    print("  4. run /adk-setup --check to verify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
