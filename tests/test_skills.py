#!/usr/bin/env python3
"""
DevKit Skill Validation Test Suite
====================================

Validates all skills for structural integrity, frontmatter correctness,
propagation consistency, script syntax, and cross-reference validity.

Usage:
    python3 tests/test_skills.py          # run all tests
    python3 -m pytest tests/test_skills.py -v   # verbose with pytest
"""

import ast
import filecmp
import re
import subprocess
import sys
from pathlib import Path

# ── Locate project root ─────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
TEMPLATES_DIR = ROOT / "templates" / "skill"

# ── Add preflight parser to path so we can reuse it ─────────────────
sys.path.insert(0, str(TEMPLATES_DIR / "scripts"))
from preflight import parse_frontmatter  # noqa: E402

# ── Discover all skills ─────────────────────────────────────────────
SKILL_DIRS = sorted(
    d for d in SKILLS_DIR.iterdir()
    if d.is_dir() and not d.name.startswith("_") and (d / "SKILL.md").exists()
)

SKILL_NAMES = [d.name for d in SKILL_DIRS]

# ── Required frontmatter fields ─────────────────────────────────────
REQUIRED_FM_FIELDS = {"name", "description", "user-invocable", "workflow-tier", "maturity"}
VALID_TIERS = {"full", "abbreviated", "helper", "orchestrator"}
VALID_MATURITY = {"experimental", "stable", "battle-tested"}

# ── Canonical propagated files (templates/skill/common → skills/*/references/) ──
# Note: common/ files (help-format.md, project-guidelines.md, inline-interaction.md)
# were removed — shared knowledge is now accessed via helper skill invocations.
_common_dir = TEMPLATES_DIR / "common"
CANONICAL_COMMON = sorted(
    f.relative_to(_common_dir)
    for f in (_common_dir.rglob("*") if _common_dir.exists() else [])
    if f.is_file()
)

# ── Skills with custom preflight.py (allowed to differ from template) ──
CUSTOM_PREFLIGHT_SKILLS = {"github", "bitbucket", "confluence", "jira"}


# ═══════════════════════════════════════════════════════════════════
# Test helpers
# ═══════════════════════════════════════════════════════════════════

class TestResult:
    def __init__(self, name: str):
        self.name = name
        self.passed: list[str] = []
        self.failed: list[str] = []
        self.warnings: list[str] = []

    def ok(self, msg: str):
        self.passed.append(msg)

    def fail(self, msg: str):
        self.failed.append(msg)

    def warn(self, msg: str):
        self.warnings.append(msg)

    @property
    def success(self) -> bool:
        return len(self.failed) == 0


class TestSuite:
    def __init__(self):
        self.results: list[TestResult] = []

    def run(self, name: str, fn):
        r = TestResult(name)
        try:
            fn(r)
        except Exception as e:
            r.fail(f"Exception: {e}")
        self.results.append(r)
        return r

    def summary(self) -> tuple[int, int, int]:
        p = sum(len(r.passed) for r in self.results)
        f = sum(len(r.failed) for r in self.results)
        w = sum(len(r.warnings) for r in self.results)
        return p, f, w

    def print_report(self):
        print("\n" + "=" * 70)
        print("DevKit Skill Validation Report")
        print("=" * 70)

        for r in self.results:
            status = "PASS" if r.success else "FAIL"
            icon = "✓" if r.success else "✗"
            print(f"\n{icon} [{status}] {r.name}")
            for msg in r.failed:
                print(f"    ✗ {msg}")
            for msg in r.warnings:
                print(f"    ⚠ {msg}")
            if r.success and not r.warnings:
                print(f"    ✓ {len(r.passed)} check(s) passed")

        p, f, w = self.summary()
        print("\n" + "-" * 70)
        print(f"Total: {p} passed, {f} failed, {w} warnings")
        print("=" * 70)
        return f == 0


# ═══════════════════════════════════════════════════════════════════
# Test: Structural Integrity
# ═══════════════════════════════════════════════════════════════════

def test_structure(r: TestResult):
    """Every skill must have SKILL.md, references/, scripts/ with preflight.py."""
    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        for required in ["SKILL.md", "references", "scripts"]:
            path = skill_dir / required
            if path.exists():
                r.ok(f"{name}/{required} exists")
            else:
                r.fail(f"{name}/{required} MISSING")

        if not (skill_dir / "scripts" / "preflight.py").exists():
            r.fail(f"{name}/scripts/preflight.py MISSING")
        else:
            r.ok(f"{name}/scripts/preflight.py exists")


# ═══════════════════════════════════════════════════════════════════
# Test: Frontmatter Validity
# ═══════════════════════════════════════════════════════════════════

def _expected_frontmatter_name(dirname: str) -> str:
    return f"adk-{dirname}"


def test_frontmatter(r: TestResult):
    """Every SKILL.md must have valid, parseable frontmatter with required fields."""
    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        fm = parse_frontmatter(str(skill_dir))

        if not fm:
            r.fail(f"{name}: frontmatter is empty or unparseable")
            continue

        # Check required fields
        for field in REQUIRED_FM_FIELDS:
            if field in fm:
                r.ok(f"{name}: has '{field}'")
            else:
                r.fail(f"{name}: missing required field '{field}'")

        # name should match directory (adk-<dir> convention) or legacy bare dirname
        raw_name = fm.get("name")
        expected = _expected_frontmatter_name(name)
        if raw_name in (name, expected):
            r.ok(f"{name}: name matches directory / adk- convention")
        else:
            r.fail(f"{name}: frontmatter name '{raw_name}' != '{name}' or '{expected}'")

        # workflow-tier should be valid
        tier = fm.get("workflow-tier", "")
        if tier in VALID_TIERS:
            r.ok(f"{name}: valid tier '{tier}'")
        else:
            r.fail(f"{name}: invalid workflow-tier '{tier}' (expected one of {VALID_TIERS})")

        # maturity should be valid
        maturity = fm.get("maturity", "")
        if maturity in VALID_MATURITY:
            r.ok(f"{name}: valid maturity '{maturity}'")
        else:
            r.fail(f"{name}: invalid maturity '{maturity}' (expected one of {VALID_MATURITY})")

        # allowed-tools optional (e.g. connector helpers); if present must be a non-empty list
        tools = fm.get("allowed-tools")
        if tools is None:
            r.ok(f"{name}: allowed-tools omitted (optional for some helpers)")
        elif isinstance(tools, list) and len(tools) > 0:
            r.ok(f"{name}: allowed-tools is a non-empty list")
        else:
            r.fail(f"{name}: allowed-tools should be omitted or a non-empty list, got {tools!r}")

        # dependencies should be a dict if present
        deps = fm.get("dependencies", {})
        if isinstance(deps, dict):
            r.ok(f"{name}: dependencies is a dict")
        else:
            r.fail(f"{name}: dependencies should be a dict, got {type(deps).__name__}")


# ═══════════════════════════════════════════════════════════════════
# Test: Propagation Consistency
# ═══════════════════════════════════════════════════════════════════

def test_propagation(r: TestResult):
    """Propagated common reference files and preflight.py must match canonical templates."""
    for skill_dir in SKILL_DIRS:
        name = skill_dir.name

        for rel in CANONICAL_COMMON:
            src = TEMPLATES_DIR / "common" / rel
            dst = skill_dir / "references" / rel
            if not dst.exists():
                r.fail(f"{name}/references/{rel} MISSING (not propagated)")
            elif filecmp.cmp(src, dst, shallow=False):
                r.ok(f"{name}/references/{rel} matches template common/")
            else:
                r.fail(f"{name}/references/{rel} DIFFERS from template (run propagate.py)")

        src = TEMPLATES_DIR / "scripts" / "preflight.py"
        dst = skill_dir / "scripts" / "preflight.py"
        has_custom_preflight = name in CUSTOM_PREFLIGHT_SKILLS or name.startswith("adk-")
        if has_custom_preflight:
            if dst.exists():
                r.ok(f"{name}/scripts/preflight.py has allowed custom preflight")
        elif dst.exists() and not filecmp.cmp(src, dst, shallow=False):
            r.fail(f"{name}/scripts/preflight.py DIFFERS from template")
        elif dst.exists():
            r.ok(f"{name}/scripts/preflight.py matches template")


# ═══════════════════════════════════════════════════════════════════
# Test: Python Script Syntax
# ═══════════════════════════════════════════════════════════════════

def test_python_syntax(r: TestResult):
    """All .py files under skills/ must be valid Python syntax."""
    for py_file in SKILLS_DIR.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        rel = py_file.relative_to(SKILLS_DIR)
        try:
            source = py_file.read_text(encoding="utf-8")
            ast.parse(source, filename=str(py_file))
            r.ok(f"{rel}: valid syntax")
        except SyntaxError as e:
            r.fail(f"{rel}: syntax error at line {e.lineno}: {e.msg}")


# ═══════════════════════════════════════════════════════════════════
# Test: Cross-References in SKILL.md
# ═══════════════════════════════════════════════════════════════════

def test_cross_references(r: TestResult):
    """Backticked paths under this skill (references/, stages/) cited in SKILL.md must exist."""
    ref_pattern = re.compile(r"`references/([^`]+)`")

    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        refs_found = ref_pattern.findall(skill_md)
        for ref in refs_found:
            if "<" in ref and ">" in ref:
                continue
            ref_path = skill_dir / "references" / ref
            if ref_path.exists():
                r.ok(f"{name}: references/{ref} exists")
            else:
                r.fail(f"{name}: references/{ref} referenced in SKILL.md but MISSING")

    stage_pattern = re.compile(r"`stages/([^`]+)`")
    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        stages_found = stage_pattern.findall(skill_md)
        for stage in stages_found:
            if "<" in stage and ">" in stage:
                continue
            stage_path = skill_dir / "stages" / stage
            if stage_path.exists():
                r.ok(f"{name}: stages/{stage} exists")
            else:
                r.fail(f"{name}: stages/{stage} referenced in SKILL.md but MISSING")


# ═══════════════════════════════════════════════════════════════════
# Test: Preflight Script Runs
# ═══════════════════════════════════════════════════════════════════

def test_preflight_runs(r: TestResult):
    """preflight.py must execute without crashing for each skill."""
    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        preflight = skill_dir / "scripts" / "preflight.py"
        if not preflight.exists():
            r.warn(f"{name}: no preflight.py to test")
            continue

        try:
            result = subprocess.run(
                [sys.executable, str(preflight), str(skill_dir)],
                capture_output=True, text=True, timeout=30
            )
            # Exit code 0 = all deps met, exit code 1 = missing deps (still valid)
            if result.returncode in (0, 1):
                r.ok(f"{name}: preflight.py executed (exit {result.returncode})")
            else:
                r.fail(f"{name}: preflight.py crashed (exit {result.returncode}): {result.stderr[:200]}")
        except subprocess.TimeoutExpired:
            r.fail(f"{name}: preflight.py timed out")
        except Exception as e:
            r.fail(f"{name}: preflight.py error: {e}")


# ═══════════════════════════════════════════════════════════════════
# Test: No Stale __pycache__ Directories
# ═══════════════════════════════════════════════════════════════════

def test_no_pycache(r: TestResult):
    """Skills should not have committed __pycache__ directories."""
    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        pycache_dirs = list(skill_dir.rglob("__pycache__"))
        if pycache_dirs:
            r.warn(f"{name}: has __pycache__ dirs (run propagate.py to clean)")
        else:
            r.ok(f"{name}: no __pycache__")


# ═══════════════════════════════════════════════════════════════════
# Test: No Cross-Skill File References
# ═══════════════════════════════════════════════════════════════════

def _skill_md_without_fenced_blocks(text: str) -> str:
    """Remove fenced code blocks so example paths in samples do not trip cross-skill checks."""
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def test_no_cross_skill_refs(r: TestResult):
    """SKILL.md should not reference files from other skill directories (outside fenced examples)."""
    cross_pattern = re.compile(r"(?:skills|\.\.)/(\w[\w-]*)/(?:references|scripts|stages)/")

    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        skill_md = _skill_md_without_fenced_blocks(
            (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        )

        matches = cross_pattern.findall(skill_md)
        violations = [m for m in matches if m != name]
        if violations:
            r.fail(f"{name}: cross-skill file references found: {set(violations)}")
        else:
            r.ok(f"{name}: no cross-skill file references")


# ═══════════════════════════════════════════════════════════════════
# Test: Propagate Script Dry Run
# ═══════════════════════════════════════════════════════════════════

def test_propagate_dry_run(r: TestResult):
    """propagate.py --dry-run should succeed and report current state."""
    propagate = TEMPLATES_DIR / "scripts" / "propagate.py"
    try:
        result = subprocess.run(
            [sys.executable, str(propagate), "--dry-run"],
            capture_output=True, text=True, timeout=30,
            cwd=str(ROOT)
        )
        if result.returncode == 0:
            r.ok("propagate.py --dry-run succeeded")
            if "Files changed:" in result.stdout:
                for line in result.stdout.splitlines():
                    if "Files changed:" in line:
                        count = line.strip().split(":")[-1].strip()
                        if int(count) > 0:
                            r.warn(f"propagate.py reports {count} files need updating")
                        else:
                            r.ok("All propagated files are up to date")
        else:
            r.fail(f"propagate.py --dry-run failed: {result.stderr[:300]}")
    except Exception as e:
        r.fail(f"propagate.py error: {e}")


# ═══════════════════════════════════════════════════════════════════
# Test: SKILL.md Script Paths Are Valid
# ═══════════════════════════════════════════════════════════════════

def test_script_paths_in_skillmd(r: TestResult):
    """Script invocations in SKILL.md (python3 .../scripts/...) should reference existing files."""
    script_pattern = re.compile(r"python3\s+\$\{CLAUDE_SKILL_DIR\}/scripts/(\S+)")

    for skill_dir in SKILL_DIRS:
        name = skill_dir.name
        skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")

        for match in script_pattern.finditer(skill_md):
            script_rel = match.group(1)
            script_file = script_rel.split()[0]
            script_path = skill_dir / "scripts" / script_file
            if script_path.exists():
                r.ok(f"{name}: scripts/{script_file} exists")
            else:
                r.fail(f"{name}: scripts/{script_file} referenced in SKILL.md but MISSING")


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    print(f"Discovered {len(SKILL_DIRS)} skills: {', '.join(SKILL_NAMES)}")

    suite = TestSuite()

    suite.run("Structural Integrity", test_structure)
    suite.run("Frontmatter Validity", test_frontmatter)
    suite.run("Propagation Consistency", test_propagation)
    suite.run("Python Syntax", test_python_syntax)
    suite.run("Cross-References", test_cross_references)
    suite.run("Script Paths in SKILL.md", test_script_paths_in_skillmd)
    suite.run("Preflight Runs", test_preflight_runs)
    suite.run("No __pycache__", test_no_pycache)
    suite.run("No Cross-Skill File Refs", test_no_cross_skill_refs)
    suite.run("Propagate Dry Run", test_propagate_dry_run)

    all_passed = suite.print_report()
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
