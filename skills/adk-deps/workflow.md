# Dependency Analyst Workflow

## Phase 1: Scan

**Goal**: Inventory current dependencies and detect package managers.

1. Run `python3 scripts/scan.py` against the project (or `--scope` path) to auto-detect and inventory dependencies
2. Scan the project for package manager manifest files:
   - `package.json` (npm/yarn/pnpm)
   - `requirements.txt`, `pyproject.toml`, `Pipfile` (pip/poetry/pipenv)
   - `Cargo.toml` (cargo)
   - `go.mod` (go)
   - `pom.xml` (maven)
   - `build.gradle`, `build.gradle.kts` (gradle)
   - `Gemfile` (ruby/bundler)
3. Parse manifest files to extract direct dependencies and their declared versions
4. Parse lock files when available to extract resolved versions and transitive dependencies
5. Report the inventory: total dependency count, managers detected, manifest locations

## Phase 2: Analyze

**Goal**: Check for vulnerabilities, outdated packages, unused deps, and license issues.

1. **Security** (`--focus security` or `all`):
   - Run package manager audit tools (`npm audit`, `pip-audit`, `cargo audit`, etc.)
   - Research known CVEs for detected vulnerabilities
   - Classify by severity: critical, high, moderate, low
2. **Outdated** (`--focus outdated` or `all`):
   - Compare current versions against latest available versions
   - Classify updates: major (breaking risk), minor, patch
   - Check changelogs for major updates to identify breaking changes
3. **Licenses** (`--focus licenses` or `all`):
   - Extract license information from package metadata
   - Flag copyleft licenses (GPL, AGPL) if the project uses a permissive license
   - Flag packages with unknown or missing license information
4. **Unused**: identify dependencies declared in manifests but not imported in source code

## Phase 3: Plan

**Goal**: Propose updates with risk assessment.

1. Prioritize findings by severity and impact:
   - Critical security vulnerabilities first
   - High-severity vulnerabilities second
   - Outdated packages with known issues third
   - Minor version bumps last
2. For each proposed update:
   - Current version -> proposed version
   - Risk level (breaking changes, deprecations, behavior changes)
   - Dependencies affected (other packages that depend on the updated one)
3. Present the plan as a ranked table
4. **Gate**: User approves the plan (or modifies it) before execution (skip if `--auto` for non-breaking updates only)

## Phase 4: Execute

**Goal**: Apply approved updates and verify the result.

1. Apply updates using the appropriate package manager commands
2. Regenerate lock files
3. Run the project's test suite to verify nothing breaks
4. If tests fail: revert the update, report the failure, suggest investigation
5. If tests pass: confirm the update and move to the next one

## Phase 5: Report

**Goal**: Produce the final dependency health summary.

1. Updated inventory with new version numbers
2. Security status: vulnerabilities resolved vs. remaining
3. Remaining risks: unfixed vulnerabilities, unverified updates, packages with no test coverage
4. Blind spots: transitive dependencies not covered by audit tools, packages without CVE databases
5. Next steps: remaining updates, manual review items, scheduled re-audit recommendation

## Validation Rules

- Lock file is consistent after every update
- Tests pass after every update (revert if not)
- No new vulnerabilities introduced by updates
- Removed dependencies have no remaining import references in source
- Breaking changes are only applied with explicit approval
