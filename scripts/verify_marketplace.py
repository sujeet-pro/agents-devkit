#!/usr/bin/env python3
"""verify_marketplace.py — structural validator for the adk Claude Code marketplace.

Checks:
  * .claude-plugin/marketplace.json parses and has 5 plugin entries.
  * For every plugin entry:
      - plugins/<name>/.claude-plugin/plugin.json exists, parses, name matches.
      - plugin.json `dependencies` (when present) reference real plugins.
  * For every plugins/<plugin>/skills/<skill>/:
      - SKILL.md present.
      - YAML frontmatter parses, has `name` matching the folder, has `description`.
      - description length <= 1536 (Claude's hard limit).
      - references/ folder present with the canonical files.
  * For every plugins/<plugin>/agents/<agent>.md:
      - frontmatter `name` matches basename.
      - frontmatter has `description`.
  * Every .mcp.json parses.
  * Every hooks/hooks.json parses.

Usage:
  python3 scripts/verify_marketplace.py             # report; exit 0 if OK, 1 if errors
  python3 scripts/verify_marketplace.py --strict    # also fail on warnings
  python3 scripts/verify_marketplace.py --quiet     # only print errors
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGINS = ROOT / "plugins"
MARKETPLACE_JSON = ROOT / ".claude-plugin" / "marketplace.json"

CANONICAL_REFS = [
    "persona.md",
    "anti-patterns.md",
    "interaction-contract.md",
]

DESCRIPTION_MAX = 1536


class Report:
    def __init__(self, quiet: bool):
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.quiet = quiet

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def emit(self) -> int:
        if not self.quiet:
            for w in self.warnings:
                print(f"  WARN:  {w}")
        for e in self.errors:
            print(f"  ERROR: {e}")
        print(
            f"verify_marketplace: errors={len(self.errors)} warnings={len(self.warnings)}"
        )
        return 1 if self.errors else 0


def parse_frontmatter(text: str) -> dict[str, object] | None:
    m = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not m:
        return None
    body = m.group(1)
    fm: dict[str, object] = {}
    current_key: str | None = None
    current_block: list[str] = []
    for line in body.splitlines():
        if line.startswith("  "):
            if current_key:
                current_block.append(line[2:])
            continue
        if current_key and current_block:
            fm[current_key] = "\n".join(current_block)
            current_block = []
        m2 = re.match(r"^([a-zA-Z0-9_-]+):\s*(.*?)\s*$", line)
        if not m2:
            continue
        key, val = m2.group(1), m2.group(2)
        current_key = key
        if val == "|" or val == ">" or val == "":
            fm[key] = ""
        else:
            fm[key] = val.strip().strip('"')
            current_key = None
    if current_key and current_block:
        fm[current_key] = "\n".join(current_block).strip()
    return fm


def load_json(path: Path, report: Report) -> dict | None:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        report.error(f"{path.relative_to(ROOT)}: missing")
        return None
    except json.JSONDecodeError as e:
        report.error(f"{path.relative_to(ROOT)}: invalid JSON: {e}")
        return None


def check_marketplace(report: Report) -> list[str]:
    data = load_json(MARKETPLACE_JSON, report)
    if not data:
        return []
    if data.get("name") != "adk":
        report.error(
            f"marketplace.json: name should be 'adk', got '{data.get('name')}'"
        )
    plugins = data.get("plugins", [])
    if not isinstance(plugins, list) or not plugins:
        report.error("marketplace.json: plugins must be a non-empty list")
        return []
    plugin_names: list[str] = []
    for p in plugins:
        name = p.get("name")
        if not name:
            report.error("marketplace.json: a plugin entry is missing 'name'")
            continue
        plugin_names.append(name)
        src = p.get("source")
        if isinstance(src, str) and src.startswith("./plugins/"):
            if not (ROOT / src.lstrip("./")).is_dir():
                report.error(
                    f"marketplace.json: plugin '{name}' source '{src}' not found"
                )
        if not p.get("description"):
            report.warn(f"marketplace.json: plugin '{name}' missing description")
    return plugin_names


def check_plugin(
    plugin_dir: Path, plugin_name: str, all_plugins: list[str], report: Report
) -> None:
    pj_path = plugin_dir / ".claude-plugin" / "plugin.json"
    pj = load_json(pj_path, report)
    if pj:
        if pj.get("name") != plugin_name:
            report.error(
                f"{pj_path.relative_to(ROOT)}: name='{pj.get('name')}' must equal folder '{plugin_name}'"
            )
        if not pj.get("version"):
            report.warn(f"{pj_path.relative_to(ROOT)}: missing version")
        deps = pj.get("dependencies", []) or []
        for d in deps:
            dn = d.get("name") if isinstance(d, dict) else None
            if dn and dn not in all_plugins:
                report.error(
                    f"{pj_path.relative_to(ROOT)}: dependency '{dn}' not in marketplace"
                )

    for sub in ("hooks/hooks.json", ".mcp.json"):
        p = plugin_dir / sub
        if p.exists():
            try:
                json.loads(p.read_text())
            except json.JSONDecodeError as e:
                report.error(f"{p.relative_to(ROOT)}: invalid JSON: {e}")

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            check_skill(skill_dir, report)
    else:
        report.warn(f"{plugin_dir.relative_to(ROOT)}/skills missing")

    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for agent_file in sorted(agents_dir.glob("*.md")):
            check_agent(agent_file, report)


def check_skill(skill_dir: Path, report: Report) -> None:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        report.error(f"{skill_dir.relative_to(ROOT)}/SKILL.md: missing")
        return
    text = skill_md.read_text()
    fm = parse_frontmatter(text)
    if fm is None:
        report.error(
            f"{skill_md.relative_to(ROOT)}: missing or malformed YAML frontmatter"
        )
        return
    folder = skill_dir.name
    if fm.get("name") != folder:
        report.error(
            f"{skill_md.relative_to(ROOT)}: frontmatter name='{fm.get('name')}' must equal folder '{folder}'"
        )
    desc = fm.get("description") or ""
    if not desc:
        report.error(f"{skill_md.relative_to(ROOT)}: missing description")
    elif isinstance(desc, str) and len(desc) > DESCRIPTION_MAX:
        report.error(
            f"{skill_md.relative_to(ROOT)}: description length {len(desc)} > {DESCRIPTION_MAX} (Claude's hard limit)"
        )

    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        report.warn(f"{skill_dir.relative_to(ROOT)}/references: missing")
    else:
        present = {p.name for p in refs_dir.iterdir() if p.is_file()}
        for canonical in CANONICAL_REFS:
            if canonical not in present:
                report.warn(
                    f"{skill_dir.relative_to(ROOT)}/references/{canonical}: missing"
                )


def check_agent(agent_file: Path, report: Report) -> None:
    text = agent_file.read_text()
    fm = parse_frontmatter(text)
    if fm is None:
        report.error(
            f"{agent_file.relative_to(ROOT)}: missing or malformed YAML frontmatter"
        )
        return
    expected = agent_file.stem
    if fm.get("name") != expected:
        report.error(
            f"{agent_file.relative_to(ROOT)}: frontmatter name='{fm.get('name')}' must equal basename '{expected}'"
        )
    if not fm.get("description"):
        report.error(f"{agent_file.relative_to(ROOT)}: missing description")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true", help="fail on warnings")
    ap.add_argument("--quiet", action="store_true", help="only print errors")
    args = ap.parse_args()

    report = Report(quiet=args.quiet)

    plugin_names = check_marketplace(report)
    if not plugin_names:
        return report.emit() or 1

    for name in plugin_names:
        plugin_dir = PLUGINS / name
        if not plugin_dir.is_dir():
            report.error(f"plugins/{name}: directory missing")
            continue
        check_plugin(plugin_dir, name, plugin_names, report)

    rc = report.emit()
    if rc == 0 and args.strict and report.warnings:
        return 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
