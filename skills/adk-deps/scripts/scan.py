#!/usr/bin/env python3
"""Dependency scanner for adk-deps skill.

Detects the package manager in a project and runs basic dependency analysis.
Outputs structured results as JSON or human-readable text.

Usage:
    python3 scan.py [--path <project-root>] [--format json|text]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Package manager detection
# ---------------------------------------------------------------------------

MANIFEST_MAP: list[tuple[str, str, str]] = [
    # (filename, manager_key, display_name)
    ("package.json", "npm", "npm / yarn / pnpm"),
    ("requirements.txt", "pip", "pip"),
    ("pyproject.toml", "pyproject", "pip / poetry"),
    ("Pipfile", "pipenv", "pipenv"),
    ("Cargo.toml", "cargo", "cargo"),
    ("go.mod", "go", "go modules"),
    ("pom.xml", "maven", "maven"),
    ("build.gradle", "gradle", "gradle"),
    ("build.gradle.kts", "gradle", "gradle (Kotlin DSL)"),
    ("Gemfile", "bundler", "bundler"),
    ("composer.json", "composer", "composer"),
]


def detect_managers(project: Path) -> list[dict[str, str]]:
    """Return a list of detected package managers with their manifest files."""
    found: list[dict[str, str]] = []
    seen_keys: set[str] = set()
    for filename, key, label in MANIFEST_MAP:
        manifest = project / filename
        if manifest.exists() and key not in seen_keys:
            seen_keys.add(key)
            found.append({
                "manager": key,
                "label": label,
                "manifest": str(manifest),
            })
    return found


# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------


def _run_json_cmd(cmd: list[str], cwd: Path) -> dict[str, Any] | list[Any] | None:
    """Run a command and parse its stdout as JSON, returning None on failure."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
        # npm audit exits non-zero when vulnerabilities found, but still outputs JSON
        if result.stdout.strip():
            return json.loads(result.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
        pass
    return None


def _run_text_cmd(cmd: list[str], cwd: Path) -> str | None:
    """Run a command and return its stdout as text, or None on failure."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


# ---------------------------------------------------------------------------
# Per-manager analysis
# ---------------------------------------------------------------------------


def _count_npm_deps(project: Path) -> dict[str, Any]:
    """Count dependencies from package.json."""
    info: dict[str, Any] = {"direct": 0, "dev": 0}
    pkg_path = project / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            info["direct"] = len(pkg.get("dependencies", {}))
            info["dev"] = len(pkg.get("devDependencies", {}))
        except (json.JSONDecodeError, OSError):
            pass
    return info


def analyze_npm(project: Path) -> dict[str, Any]:
    """Run npm audit and npm outdated."""
    result: dict[str, Any] = {
        "manager": "npm",
        "counts": _count_npm_deps(project),
        "audit": None,
        "outdated": None,
        "commands_available": {},
    }

    # Determine which npm-compatible tool to use
    for tool in ("npm", "yarn", "pnpm"):
        if shutil.which(tool):
            result["commands_available"][tool] = True
        else:
            result["commands_available"][tool] = False

    npm_cmd = None
    for tool in ("npm", "pnpm", "yarn"):
        if shutil.which(tool):
            npm_cmd = tool
            break

    if not npm_cmd:
        result["error"] = "No npm-compatible CLI found. Install node/npm to enable scanning."
        return result

    # npm audit
    audit_data = _run_json_cmd([npm_cmd, "audit", "--json"], project)
    if audit_data and isinstance(audit_data, dict):
        vulnerabilities = audit_data.get("vulnerabilities", {})
        metadata = audit_data.get("metadata", {})
        if vulnerabilities:
            severity_counts: dict[str, int] = {}
            for _name, info in vulnerabilities.items():
                sev = info.get("severity", "unknown")
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            result["audit"] = {
                "total_vulnerabilities": len(vulnerabilities),
                "by_severity": severity_counts,
            }
        elif metadata:
            vuln_meta = metadata.get("vulnerabilities", {})
            total = sum(v for v in vuln_meta.values() if isinstance(v, int))
            result["audit"] = {
                "total_vulnerabilities": total,
                "by_severity": {k: v for k, v in vuln_meta.items() if isinstance(v, int) and v > 0},
            }
        else:
            result["audit"] = {"total_vulnerabilities": 0, "by_severity": {}}

    # npm outdated
    outdated_data = _run_json_cmd([npm_cmd, "outdated", "--json"], project)
    if outdated_data and isinstance(outdated_data, dict):
        outdated_list = []
        for pkg_name, info in outdated_data.items():
            outdated_list.append({
                "package": pkg_name,
                "current": info.get("current", "?"),
                "wanted": info.get("wanted", "?"),
                "latest": info.get("latest", "?"),
            })
        result["outdated"] = {
            "total": len(outdated_list),
            "packages": outdated_list,
        }
    elif outdated_data is not None:
        result["outdated"] = {"total": 0, "packages": []}

    return result


def _count_pip_deps(project: Path) -> dict[str, Any]:
    """Count dependencies from requirements.txt or pyproject.toml."""
    info: dict[str, Any] = {"direct": 0}
    req_path = project / "requirements.txt"
    if req_path.exists():
        try:
            lines = req_path.read_text(encoding="utf-8").splitlines()
            info["direct"] = sum(
                1 for line in lines
                if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("-")
            )
        except OSError:
            pass
    pyproject = project / "pyproject.toml"
    if pyproject.exists() and not req_path.exists():
        try:
            text = pyproject.read_text(encoding="utf-8")
            # Simple count of dependencies lines under [project.dependencies]
            in_deps = False
            count = 0
            for line in text.splitlines():
                if line.strip() == "dependencies = [" or line.strip().startswith("dependencies"):
                    in_deps = True
                    continue
                if in_deps:
                    if line.strip() == "]":
                        break
                    if line.strip().startswith('"') or line.strip().startswith("'"):
                        count += 1
            if count > 0:
                info["direct"] = count
        except OSError:
            pass
    return info


def analyze_pip(project: Path) -> dict[str, Any]:
    """Run pip outdated check."""
    result: dict[str, Any] = {
        "manager": "pip",
        "counts": _count_pip_deps(project),
        "audit": None,
        "outdated": None,
    }

    pip_cmd = None
    for tool in ("pip3", "pip"):
        if shutil.which(tool):
            pip_cmd = tool
            break

    if not pip_cmd:
        result["error"] = "pip not found. Install Python/pip to enable scanning."
        return result

    # pip list --outdated
    outdated_data = _run_json_cmd([pip_cmd, "list", "--outdated", "--format=json"], project)
    if outdated_data and isinstance(outdated_data, list):
        outdated_list = []
        for pkg in outdated_data:
            outdated_list.append({
                "package": pkg.get("name", "?"),
                "current": pkg.get("version", "?"),
                "latest": pkg.get("latest_version", "?"),
                "type": pkg.get("latest_filetype", "?"),
            })
        result["outdated"] = {
            "total": len(outdated_list),
            "packages": outdated_list,
        }

    # pip-audit if available
    if shutil.which("pip-audit"):
        audit_data = _run_json_cmd(["pip-audit", "--format=json", "--desc"], project)
        if audit_data and isinstance(audit_data, dict):
            deps = audit_data.get("dependencies", [])
            vulns = [d for d in deps if d.get("vulns")]
            result["audit"] = {
                "total_vulnerabilities": sum(len(d.get("vulns", [])) for d in vulns),
                "affected_packages": len(vulns),
            }
    else:
        result["audit_hint"] = "Install pip-audit for vulnerability scanning: pip install pip-audit"

    return result


def analyze_generic(manager: str, label: str, manifest: str) -> dict[str, Any]:
    """Provide detection info and suggest native commands for other managers."""
    suggestions: dict[str, dict[str, str]] = {
        "cargo": {
            "audit": "cargo audit",
            "outdated": "cargo outdated",
            "install_hint": "cargo install cargo-audit cargo-outdated",
        },
        "go": {
            "audit": "govulncheck ./...",
            "outdated": "go list -m -u all",
            "install_hint": "go install golang.org/x/vuln/cmd/govulncheck@latest",
        },
        "maven": {
            "audit": "mvn org.owasp:dependency-check-maven:check",
            "outdated": "mvn versions:display-dependency-updates",
            "install_hint": "Maven plugins are fetched automatically",
        },
        "gradle": {
            "audit": "gradle dependencyCheckAnalyze (requires OWASP plugin)",
            "outdated": "gradle dependencyUpdates (requires ben-manes/gradle-versions-plugin)",
            "install_hint": "Add plugins to build.gradle",
        },
        "bundler": {
            "audit": "bundle audit",
            "outdated": "bundle outdated",
            "install_hint": "gem install bundler-audit",
        },
        "composer": {
            "audit": "composer audit",
            "outdated": "composer outdated --direct",
            "install_hint": "Composer 2.4+ includes audit natively",
        },
        "pipenv": {
            "audit": "pipenv check",
            "outdated": "pipenv update --outdated",
            "install_hint": "pip install pipenv",
        },
        "pyproject": {
            "audit": "pip-audit",
            "outdated": "pip list --outdated",
            "install_hint": "pip install pip-audit",
        },
    }

    result: dict[str, Any] = {
        "manager": manager,
        "label": label,
        "manifest": manifest,
        "counts": None,
        "audit": None,
        "outdated": None,
    }

    # Try to count deps from manifest
    manifest_path = Path(manifest)
    if manifest_path.exists():
        try:
            text = manifest_path.read_text(encoding="utf-8")
            result["manifest_lines"] = len(text.splitlines())
        except OSError:
            pass

    if manager in suggestions:
        result["suggested_commands"] = suggestions[manager]
    else:
        result["note"] = f"No built-in scanner for {label}. Run the manager's native audit commands."

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def scan(project: Path) -> dict[str, Any]:
    """Run the full scan and return structured results."""
    managers = detect_managers(project)

    results: dict[str, Any] = {
        "project": str(project),
        "managers_detected": [m["label"] for m in managers],
        "manager_count": len(managers),
        "analyses": [],
    }

    if not managers:
        results["error"] = "No supported package manager manifest files found."
        return results

    for mgr in managers:
        key = mgr["manager"]
        if key == "npm":
            results["analyses"].append(analyze_npm(project))
        elif key in ("pip", "pyproject"):
            results["analyses"].append(analyze_pip(project))
        elif key == "pipenv":
            results["analyses"].append(analyze_generic("pipenv", mgr["label"], mgr["manifest"]))
        else:
            results["analyses"].append(analyze_generic(key, mgr["label"], mgr["manifest"]))

    return results


def format_text(data: dict[str, Any]) -> str:
    """Format scan results as human-readable text."""
    lines: list[str] = []
    lines.append(f"Project: {data['project']}")
    lines.append(f"Package managers detected: {data['manager_count']}")
    for label in data.get("managers_detected", []):
        lines.append(f"  - {label}")
    lines.append("")

    if data.get("error"):
        lines.append(f"Error: {data['error']}")
        return "\n".join(lines)

    for analysis in data.get("analyses", []):
        mgr = analysis.get("manager", "unknown")
        lines.append(f"--- {mgr} ---")

        if analysis.get("error"):
            lines.append(f"  Error: {analysis['error']}")
            lines.append("")
            continue

        counts = analysis.get("counts")
        if counts:
            parts = []
            for k, v in counts.items():
                parts.append(f"{k}={v}")
            lines.append(f"  Dependencies: {', '.join(parts)}")

        audit = analysis.get("audit")
        if audit:
            total = audit.get("total_vulnerabilities", 0)
            lines.append(f"  Vulnerabilities: {total}")
            by_sev = audit.get("by_severity", {})
            if by_sev:
                for sev, count in sorted(by_sev.items()):
                    lines.append(f"    {sev}: {count}")

        audit_hint = analysis.get("audit_hint")
        if audit_hint:
            lines.append(f"  Audit hint: {audit_hint}")

        outdated = analysis.get("outdated")
        if outdated:
            lines.append(f"  Outdated packages: {outdated['total']}")
            for pkg in outdated.get("packages", [])[:10]:
                current = pkg.get("current", "?")
                latest = pkg.get("latest", pkg.get("wanted", "?"))
                lines.append(f"    {pkg['package']}: {current} -> {latest}")
            if outdated["total"] > 10:
                lines.append(f"    ... and {outdated['total'] - 10} more")

        suggested = analysis.get("suggested_commands")
        if suggested:
            lines.append("  Suggested commands:")
            for action, cmd in suggested.items():
                if action != "install_hint":
                    lines.append(f"    {action}: {cmd}")
            hint = suggested.get("install_hint")
            if hint:
                lines.append(f"    install: {hint}")

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan project dependencies for security, freshness, and health."
    )
    parser.add_argument(
        "--path",
        default=".",
        help="Project root directory (default: current directory)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    project = Path(args.path).resolve()
    if not project.is_dir():
        print(f"Error: {project} is not a directory", file=sys.stderr)
        raise SystemExit(1)

    data = scan(project)

    if args.format == "json":
        print(json.dumps(data, indent=2))
    else:
        print(format_text(data))


if __name__ == "__main__":
    main()
