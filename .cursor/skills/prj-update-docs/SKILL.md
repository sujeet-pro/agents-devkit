---
name: prj-update-docs
description: Refresh ADK documentation pages from the current repository state. Use when public skills, repo-maintenance skills, or guidance docs change.
compatibility: Repository-maintenance skill for this repo. Uses local docs sync and build commands.
metadata:
  internal: true
---
# Update Docs

## Read First
- `README.md`
- `CONTRIBUTING.md`
- `docs/README.md`
- `docs/reference/skills/README.md`
- `docs/reference/agents/README.md`

## Tools
- `python3 scripts/sync-skill-docs.py`
- `python3 scripts/generate-skills-manifest.py --check`
- `npm run docs:build`

## Workflow
1. Review the changed skills or guidance docs.
2. Update the human-authored overview pages when architecture text changed.
3. Run `python3 scripts/sync-skill-docs.py` when public skill reference pages need refresh.
4. Run `npm run docs:build`.
5. Report what changed and any remaining doc gaps.
