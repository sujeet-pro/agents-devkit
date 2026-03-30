# DevKit

Use skills from `skills/` directory. Route general prompts through `/use` first. Invoke a specific skill directly only when the user explicitly names that skill or clearly wants that exact workflow.

Every skill supports `--help` to see parameters and behavior variations.

Shared templates live in `templates/skill/`. After editing templates, run `python3 templates/skill/scripts/propagate.py` to push changes to all skills.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills, guidelines, agents, and test locally.

## Skill Architecture Rules

- **Self-sufficient**: Each skill references only files within its own `skill-name/` directory. No cross-skill file references.
- **Delegation, not file sharing**: When a skill needs another skill's capability, it invokes that skill (e.g., "invoke `/research`"), never references its sub-files. The invoking skill specifies the output format it needs, not how to do the work.
- **All reference material lives under `references/`**, with subfolders when grouping aids readability.
- **Consistent structure**: Every skill follows the same directory layout (`SKILL.md`, `references/`, `stages/`, `scripts/`).

## Cross-Skill Update Dependencies

When updating shared concepts, these skills need coordinated updates:

| What Changed | Skills to Update |
|---|---|
| **Coding guidelines** (`coding/references/coding-guidelines/`) | `review`, `develop`, `design`, `audit` — all invoke `/coding` |
| **Doc-writing guidelines** (`doc-writing/references/doc-guidelines/`) | `write`, `review-doc`, `spec` — all invoke `/doc-writing` |
| **Research methodology** (`research/references/research-methodology.md`) | `write`, `plan`, `spec`, `design` — all may invoke `/research` |
| **Review comment format** (`templates/skill/references/review-comment-template.md`) | `review`, `audit` — all produce review comments |
| **6-phase workflow** (`templates/skill/references/workflow-6phase.md`) | All full-tier skills — propagate via `propagate.py` |
| **Agentic teams contract** (`templates/skill/references/agentic-teams.md`) | All skills that spawn child agents — propagate via `propagate.py` |
| **Principal Engineer lens** (`templates/skill/references/principal-engineer.md`) | All full-tier skills — propagate via `propagate.py` |
| **Communication style** (`templates/skill/references/communication-style.md`) | All full-tier skills — propagate via `propagate.py` |
| **Interactive TUI** | Each skill owns its copy under `scripts/tui/` |
