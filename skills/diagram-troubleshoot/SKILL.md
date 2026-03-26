---
name: diagram-troubleshoot
description: Diagnose diagram generation or rendering failures in local and CI engineering workflows
user_invocable: true
arguments:
  - name: issue
    description: "Description of the problem"
    required: true
  - name: environment
    description: "Environment: local, docker, github-actions, gitlab-ci"
    required: false
---

# Diagram Troubleshooting

Use `skills/_references/preflight-validations.md`.

## Preflight

Start by running:

`zsh scripts/check-skill-deps.zsh diagram-troubleshoot format=<format>`

If the failure is dependency-related, show the exact fix command first:

- `npm install -g diagramkit`
- `diagramkit warmup`
- `npm install -g sharp` for raster output

## Required Child Agents

Run at least these child agents in parallel:

- **Source validation agent**: checks the diagram source file for syntax errors, unsupported features, invalid references, and encoding issues. Reports specific line-level errors with fix suggestions.
- **Renderer and dependency agent**: verifies all rendering dependencies are installed and working (diagramkit, Playwright Chromium, sharp). Checks version compatibility, permissions, and PATH configuration. Reports missing or broken dependencies with exact install commands.
- **Environment agent**: diagnoses environment-specific issues based on the `environment` argument. For local: checks Node.js version, npm global paths, display server for headless rendering. For Docker: checks base image, Chromium dependencies, font availability. For CI: checks cache configuration, artifact paths, and runner capabilities.

## Workflow

1. **Reproduce.** Attempt to render the failing diagram to confirm the error.
2. **Launch diagnostic agents.** Run source validation, dependency, and environment passes in parallel.
3. **Identify root cause.** Merge agent findings and determine the primary failure point.
4. **Present findings.** Report in this order:
   - Root cause with specific error
   - Minimal fix command or code change
   - Optional hardening steps to prevent recurrence

## Output

A diagnostic report containing:

- **Root Cause**: the specific failure with file and line references
- **Fix**: exact command or change to resolve the issue
- **Hardening**: optional steps to prevent recurrence (e.g., CI cache configuration, dependency pinning)

## Adjacent Skills

- `/devkit:diagram-render` for rendering after the issue is fixed
- `/devkit:diagram-pipeline` for CI/CD pipeline setup
- `/devkit:diagram` for creating new diagrams
