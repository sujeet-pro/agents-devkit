---
name: prj-audit-skills
description: Audit repo-maintained ADK skills for architecture drift, attribution gaps, and validation issues. Use when changing the skill system itself.
compatibility: Repository-maintenance skill for this repo. Reads ai-guidelines directly and uses local validation scripts.
metadata:
  internal: true
---
# Audit Skills

## Read First
- `ai-guidelines/README.md`
- `ai-guidelines/constitution.md`
- `ai-guidelines/skill-architecture.md`
- `ai-guidelines/update-scope-policy.md`
- `ai-guidelines/sources/registry.json`

## Tools
- `python3 ai-guidelines/scripts/refresh_adk_skills.py status`
- `python3 tests/test_skills.py`
- `python3 scripts/generate-skills-manifest.py --check`
- `npm run docs:build`

## Workflow
1. Inspect the changed public or project-only skills.
2. Check scope and shared-guidance impact.
3. Review self-containment, naming, copied references, and attribution.
4. Run validation.
5. Report findings in severity order.
