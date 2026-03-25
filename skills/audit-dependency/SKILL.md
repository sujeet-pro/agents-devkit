---
name: audit-dependency
description: Use when you need to audit project dependencies for outdated versions, known vulnerabilities, and license issues with a prioritized remediation plan
user_invocable: true
arguments:
  - name: scope
    description: "Dependency scope to audit: all, production, development (default: all)"
    required: false
  - name: format
    description: "Output format: markdown, pr (default: markdown)"
    required: false
---

# Dependency Audit

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before scanning any package files or launching child agents, run:

`zsh scripts/check-skill-deps.zsh audit-dependency`

## Package File Discovery

Scan the repository root and subdirectories for dependency manifests:

- **Node.js**: `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
- **Python**: `requirements.txt`, `requirements-dev.txt`, `pyproject.toml`, `Pipfile`, `Pipfile.lock`
- **Java/Kotlin**: `pom.xml`, `build.gradle`, `build.gradle.kts`
- **Go**: `go.mod`, `go.sum`
- **Rust**: `Cargo.toml`, `Cargo.lock`
- **Ruby**: `Gemfile`, `Gemfile.lock`
- **.NET**: `*.csproj`, `packages.config`

Report which files were found and which ecosystems are present before proceeding.

## Required Child Agents

Run at least these child agents in parallel:

- **Vulnerability scanner**: for each ecosystem, check dependencies against known CVE databases and advisory sources. Classify findings by severity (Critical, High, Medium, Low). Use `/devkit:research` with `depth=standard` for any CVE that needs additional context.
- **Update compatibility checker**: for each outdated dependency, research the changelog between the current and latest version. Identify breaking changes, required migration steps, and peer dependency conflicts. Flag major version bumps that need careful review.
- **Remediation planner**: synthesize vulnerability and compatibility findings into a prioritized action plan. Group remediations by effort (drop-in update, minor migration, major migration) and risk (security-critical, quality-of-life, optional).

## Workflow

1. **Discover manifests.** Locate all dependency files and determine the ecosystems in use.
2. **Parse dependencies.** Extract dependency names, current versions, and version constraints. Filter by `scope` when set to `production` or `development`.
3. **Check for vulnerabilities.** The vulnerability scanner searches for known CVEs, GitHub Security Advisories, and ecosystem-specific advisory databases for each dependency.
4. **Check for outdated versions.** Compare current versions against latest stable releases. Categorize: up-to-date, patch available, minor available, major available.
5. **Analyze licenses.** Identify the license for each dependency. Flag copyleft licenses (GPL, AGPL) in production dependencies, unknown licenses, and license conflicts with the project's own license.
6. **Build remediation plan.** The remediation planner produces a prioritized list of actions:
   - **Immediate** (Critical/High CVEs): exact commands or version bumps to apply
   - **Short-term** (Medium CVEs, major outdated): migration steps with effort estimates
   - **Backlog** (Low CVEs, license cleanup, optional updates): tracked but not urgent
7. **Generate report.** Merge all findings into the output document.

Save intermediary artifacts to `.temp/dependency-audit/`.

## Output

A dependency audit report containing:

- **Summary**: ecosystem breakdown, total dependencies, vulnerability counts by severity
- **Vulnerability findings**: each CVE with affected package, severity, description, and fix
- **Outdated dependencies**: table of current vs. latest versions grouped by update type
- **License issues**: flagged dependencies with problematic or unknown licenses
- **Remediation plan**: prioritized actions with effort estimates (hours/days) and exact update commands where possible
- **Risk notes**: dependencies with no maintainer activity, deprecated packages, or known instability

When `format=pr`, structure the output as a PR description with a checklist of remediation tasks suitable for tracking progress.
