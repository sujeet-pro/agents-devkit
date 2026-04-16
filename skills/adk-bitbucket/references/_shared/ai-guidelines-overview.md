# AI Guidelines

`ai-guidelines/` is the source of truth for shared ADK behavior.

Use it for:
- core constitution and operating rules
- shared brainstorming and design-closure workflow
- published skill architecture
- structured research method
- update-scope decisions
- focused persona briefs
- provenance and attribution

Read order:
1. `constitution.md`
2. `brainstorming-workflow.md`
3. `skill-architecture.md`
4. `output-format.md`
5. `research-protocol.md`
6. `update-scope-policy.md`
7. `sources/README.md`

Model:
- published skills live in `skills/adk-*`
- project-only skills live in `.claude/skills/prj-*`, `.cursor/skills/prj-*`, and `.agents/skills/prj-*`
- compatibility-only outputs can live in `.codex/`
- shared guidance is written here first
- published skills receive copied or generated local references from this folder
- project-only skills refer here directly instead of duplicating long instructions

Key rules:
- optimize for technical accuracy over speed
- keep humans in the loop for non-trivial work
- plan before implementation
- validate every meaningful change
- prefer concise bullet-first output
- keep the published skill catalog small and use-case driven
- keep published skills self-contained
- avoid plugin-specific packaging assumptions in the canonical guidance

Directory map:
- `constitution.md`: non-negotiable behavior rules
- `brainstorming-workflow.md`: MCP-first brainstorming and design-closure protocol
- `skill-architecture.md`: published skill vs project skill contract
- `output-format.md`: shared result shape, verbosity, and severity rules
- `research-protocol.md`: deep research workflow
- `update-scope-policy.md`: decide one-skill vs many-skill updates
- `published-skill-catalog.md`: target public catalog
- `personas/`: focused role briefs
- `sources/`: provenance, attribution, and upstream registry

Maintenance:
- update this folder first
- use the repo-maintenance updater skill to copy applicable content into published skills
- record new inspirations in `sources/registry.json`
- update attribution when new borrowed patterns become user-facing
