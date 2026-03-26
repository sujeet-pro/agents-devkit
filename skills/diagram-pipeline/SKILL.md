---
name: diagram-pipeline
description: Set up free, repo-native diagram rendering in CI or hooks for engineering documentation workflows
user_invocable: true
arguments:
  - name: platform
    description: "Platform: github-actions, gitlab-ci, docker, pre-commit (default: github-actions)"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
  - name: strategy
    description: "Strategy: commit-output (commit rendered assets), artifact (store as CI artifacts), on-demand (render only on request) (default: commit-output)"
    required: false
---

# Diagram Pipeline

Use `skills/_references/agentic-teams.md`, `skills/_references/preflight-validations.md`, and `skills/_references/output-formats.md`.

## Preflight

Before designing or debugging CI automation, run:

`zsh scripts/check-skill-deps.zsh diagram-pipeline format=<format>`

Validate the same local prerequisites the pipeline will need:

- global `diagramkit`
- Playwright Chromium readiness
- global `sharp` when the pipeline emits raster output

Use free, local, or CI-native rendering only. Do not require paid documentation tooling.

## Required Child Agents

Run at least these child agents in parallel:

- **Pipeline designer**: analyzes the repository structure to find diagram source files (`.mmd`, `.excalidraw`, `.drawio`, `.dot`). Designs the CI workflow or hook configuration for the target platform. Specifies trigger conditions (on push, on PR, on tag), caching strategy, and output paths.
- **Cache and performance agent**: optimizes the pipeline for speed. Configures dependency caching (npm, Playwright browsers), incremental rendering (only re-render changed diagrams), and parallel execution where the platform supports it.
- **Documentation agent**: writes contributor documentation explaining how rendered diagram assets are produced, how to add new diagrams, and how to test rendering locally.

## Workflow

1. **Scan repository.** Identify all diagram source files and their types.
2. **Design pipeline.** Launch the pipeline designer for the target platform.
3. **Optimize.** Launch the cache and performance agent to add caching and incremental rendering.
4. **Document.** Launch the documentation agent to write contributor docs.
5. **Generate configuration.** Produce the CI configuration file:
   - **github-actions**: `.github/workflows/diagrams.yml`
   - **gitlab-ci**: `.gitlab-ci.yml` diagram stage
   - **docker**: `Dockerfile` for diagram rendering
   - **pre-commit**: `.pre-commit-config.yaml` hook entry
6. **Test locally.** Run the pipeline locally to verify it produces correct output.

## Output

- CI configuration file for the target platform
- Contributor documentation for diagram rendering workflow
- List of diagram sources found and their rendering status

## Adjacent Skills

- `/devkit:diagram` for creating individual diagrams
- `/devkit:diagram-render` for rendering diagram sources locally
- `/devkit:diagram-troubleshoot` for diagnosing pipeline failures
