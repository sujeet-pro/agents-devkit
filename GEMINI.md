# ADK Repository Guidance -- Gemini CLI

Read `AGENTS.md` first for the full skill catalog and intent mapping.

## Gemini-Specific Notes

Gemini CLI uses a different skill loading mechanism than Claude or Cursor:

- Skills are loaded via `@./GEMINI.<skill-name>.md` import syntax in the root `GEMINI.md`
- There is no `.gemini/skills/` directory; skills are modular root-level files
- ADK does not ship a separate Gemini command wrapper layer; use skills directly

## Installation

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.agents-devkit
cd ~/.agents-devkit
# Gemini requires manual setup -- copy relevant skill content to GEMINI.md imports
```

## Skill Format Differences

| Feature | Claude/Cursor | Gemini |
| --- | --- | --- |
| Skill location | `.claude/skills/*/SKILL.md` | `GEMINI.<name>.md` at root |
| Loading | Auto-discovery | `@./GEMINI.<name>.md` import |
| Command layer in this repo | none | none |
| Arguments | `{{argname}}` placeholders | `{{args}}` (single string) |

## Available Skills

All ADK skills documented in `AGENTS.md` are available. For Gemini CLI, reference the skill content from `skills/adk-*/SKILL.md` and adapt the format as needed.
