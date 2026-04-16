---
name: prj-refresh-skills
description: Refresh repo-maintained ADK skills from ai-guidelines. Use when shared guidance, provenance, or the public skill catalog changes.
compatibility: Repository-maintenance skill for this repo. Reads ai-guidelines directly and uses local helper scripts.
metadata:
  internal: true
---
# Refresh Skills

## Read First
- `ai-guidelines/README.md`
- `ai-guidelines/constitution.md`
- `ai-guidelines/skill-architecture.md`
- `ai-guidelines/update-scope-policy.md`
- `ai-guidelines/shared-files-map.json`
- `ai-guidelines/sources/registry.json`

## Tools
- `python3 ai-guidelines/scripts/refresh_adk_skills.py status`
- `python3 ai-guidelines/scripts/refresh_adk_skills.py scope --changed-path <path>`
- `python3 ai-guidelines/scripts/refresh_adk_skills.py scope --source-id <source-id>`
- `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared --dry-run`
- `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared`

## Workflow
1. Read the relevant `ai-guidelines/` sources.
2. Decide whether the change affects one skill, one family, or all public skills.
3. Refresh copied shared guidance into `skills/adk-*`.
4. Regenerate manifest or docs if the public catalog changed.
5. Validate before closing the task.
