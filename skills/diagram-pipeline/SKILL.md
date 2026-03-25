---
name: ci-cd
description: Set up free, repo-native diagram rendering in CI or hooks for engineering documentation workflows
user_invocable: true
arguments:
  - name: platform
    description: "Platform: github-actions, gitlab-ci, docker, pre-commit"
    required: false
  - name: format
    description: "Rendered format: svg, png, jpeg, webp (default: svg)"
    required: false
  - name: strategy
    description: "Strategy: commit-output, artifact, on-demand (default: commit-output)"
    required: false
---

# Diagram Pipeline

Use `skills/_references/preflight-validations.md`.

## Preflight

Before designing or debugging CI automation, run:

`zsh scripts/check-skill-deps.zsh diagram-pipeline format=<format>`

Validate the same local prerequisites the pipeline will need:

- global `diagramkit`
- Playwright Chromium readiness
- global `sharp` when the pipeline emits raster output

Use free, local, or CI-native rendering only. Do not require paid documentation tooling.

Run in parallel:

- a pipeline design pass
- a cache and performance pass
- a documentation pass so contributors know how rendered assets are produced
