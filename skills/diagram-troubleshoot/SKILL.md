---
name: troubleshoot
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

Run in parallel:

- a source validation pass
- a renderer and dependency pass
- an environment-specific pass

Return the likely root cause first, then the minimal fix, then optional hardening steps.
