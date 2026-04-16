# adk-deps

Analyze, audit, and update project dependencies for security, licensing, and freshness.

## Quick Start

```bash
npx adk-deps --action audit --focus security
```

## What This Skill Does

Manages the dependency lifecycle: audit for vulnerabilities, check for outdated packages, verify license compliance, and plan or execute safe updates. Detects package managers present in the project, inventories dependencies, and generates findings ordered by severity with CVE references for security issues and version comparisons for outdated packages.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--action` | `audit`, `update`, `check`, `plan` | `audit` | Primary action to perform |
| `--scope` | path | `.` | Limit analysis to a specific directory |
| `--focus` | `security`, `outdated`, `licenses`, `all` | `all` | Narrow the analysis lens |
| `--auto` | flag | off | Skip confirmations and execute with defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | CLI command | yes |
| `python3` | CLI command | yes |
| Package manager(s) | runtime | at least one (npm, pip, cargo, go, etc.) |

### Supported Package Managers

| Manager | Manifest File |
| --- | --- |
| npm / yarn / pnpm | `package.json` |
| pip / poetry / pipenv | `requirements.txt`, `pyproject.toml`, `Pipfile` |
| cargo | `Cargo.toml` |
| go | `go.mod` |
| maven | `pom.xml` |
| gradle | `build.gradle`, `build.gradle.kts` |
| ruby / bundler | `Gemfile` |

## Skill Layout

```
skills/adk-deps/
  SKILL.md                              # Skill definition and frontmatter
  README.md                             # This file
  scripts/
    preflight.py                        # Pre-flight checks and package manager detection
  references/
    persona.md                          # Skill-specific persona
    workflow.md                         # Skill-specific workflow detail
    _shared/
      ai-guidelines-overview.md         # Shared ADK guidance
      constitution.md                   # Shared constitution
      output-format.md                  # Shared output format
      research-protocol.md              # Shared research protocol
```

## Workflow

1. Detect package managers present in the project.
2. Inventory all direct and transitive dependencies where possible.
3. Run analysis based on the selected action and focus.
4. Generate findings ordered by severity.
5. Propose an action plan for any issues found.
6. Execute approved updates if the action is `update`.
7. Validate: lock file integrity, tests pass, no new vulnerabilities.

## Interaction Protocol

- **Confirm action and scope** -- before running, confirm which action and scope the user wants.
- **Present findings with severity** -- vulnerabilities include CVE references; outdated packages show current vs. available version.
- **Show update plan before applying** -- for `--action update`, present planned changes with risk assessment and wait for approval.
- **Separate blocking from advisory** -- critical security vulnerabilities are blocking; minor version bumps are advisory.
- **Report lock file integrity** -- after any update, confirm lock file consistency and test status.

## Output Format

- Dependency count and manager(s) detected
- Vulnerabilities found (count and severity breakdown)
- Outdated packages (count with available versions)
- Update plan with risk assessment
- Remaining risk and blind spots

## Examples

Security audit of all dependencies:
```
/adk-deps --action audit --focus security
```

Check for outdated packages:
```
/adk-deps --action check --focus outdated
```

Plan a major version update for a specific package scope:
```
/adk-deps --action plan --scope packages/core
```

## What Success Looks Like

- [ ] Package managers are detected and reported
- [ ] Action and scope are confirmed before execution
- [ ] Vulnerabilities include CVE references where available
- [ ] Outdated packages show current vs. available version
- [ ] Update plan is presented and approved before applying
- [ ] Lock file integrity is verified after updates
- [ ] Tests pass after dependency changes
- [ ] No new vulnerabilities introduced by updates
