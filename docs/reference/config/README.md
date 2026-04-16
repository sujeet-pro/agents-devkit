---
title: Configuration Reference
description: Public skill packaging, ai-guidelines, repo-only skill locations, and validation surfaces
order: 3
---

# Configuration Reference

ADK configuration is now split across public packaging, shared guidance, and repo-only maintenance surfaces.

## Public Packaging

- `skills/adk-*`: public installable skills
- `skills-manifest.json`: generated public catalog
- `package.json`: repository version used by the public manifest

## Shared Guidance

- `ai-guidelines/README.md`
- `ai-guidelines/constitution.md`
- `ai-guidelines/brainstorming-workflow.md`
- `ai-guidelines/skill-architecture.md`
- `ai-guidelines/research-protocol.md`
- `ai-guidelines/update-scope-policy.md`
- `ai-guidelines/personas/`
- `ai-guidelines/sources/registry.json`

## Repo-Only Maintenance Surfaces

- `.claude/skills/prj-*`
- `.cursor/skills/prj-*`
- `.agents/skills/prj-*`
- `.cursor/rules/`
- `.codex/` as compatibility-only output

## Validation

```bash
python3 ai-guidelines/scripts/refresh_adk_skills.py status
python3 scripts/generate-skills-manifest.py --check
python3 tests/test_skills.py
npm run docs:build
npx skills add . --list
```

## MCP

MCP remains optional and is configured per runtime rather than through plugin packaging. See `settings/mcp-setup.md` for the current project guidance.

ADK intentionally does not publish public connector or setup skills whose only job is to wrap MCP wiring or runtime configuration. Prefer direct runtime MCP use, config docs, and existing built-in runtime skills for that work.

The one workflow-specific exception is the `brainstorming` MCP server: ADK skills can prefer it for design closure, but they must still warn once and fall back to the shared manual workflow when it is not configured.
