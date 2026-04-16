# ADK Repository Guidance

Read `AGENTS.md` first.

Claude-specific notes:
- repo-maintenance skills live in `.claude/skills/prj-*`
- canonical shared guidance lives in `ai-guidelines/`
- public installable skills live in `skills/adk-*`
- reusable agent personas live in `agent-personas/adk-*`
- Claude installable agent source files live in `agents-claude/*.md` and are generated from `agent-personas/adk-*/AGENT.md`
- Claude installable hook source lives in `hooks/settings.json`
- file-to-skill mapping lives in `ai-guidelines/shared-files-map.json`

When shared guidance changes (constitution, brainstorming-workflow, output-format, research-protocol, or personas):
1. read `ai-guidelines/update-scope-policy.md`
2. run `python3 ai-guidelines/scripts/refresh_adk_skills.py scope --changed-path <path>`
3. run `python3 ai-guidelines/scripts/refresh_adk_skills.py copy-shared`
4. run `python3 scripts/generate-skills-manifest.py`
5. run `python3 tests/test_skills.py`

Symlink management:
- run `./scripts/sync-links.sh` after adding or removing skills
- run `python3 scripts/generate_agent_projections.py` after changing canonical agent personas
- run `python3 scripts/generate_hook_projections.py` after changing runtime hook behavior
- run `./scripts/install-mcp.sh --agent claude-code` to install MCP configs

Suggested user-level prompt snippet:

```md
When a task involves design, trade-offs, ambiguity, or meaningful risk, start with the ADK brainstorming workflow.

1. Prefer the brainstorming MCP if available.
2. If it is missing, warn once with install guidance and continue using the fallback workflow.
3. Capture current state, target state, acceptable blast radius, desired confidence, and preferred artifact output.
4. Research unknowns, present options, and ask follow-up questions until confidence is high enough for the task.
5. Route into the right skill: brainstorm, spec, plan, write-docs, build, refactor, migrate, or design.
```
