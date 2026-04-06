# DevKit

Use skills from `skills/` directory. Route general prompts through `/adk:use` first. Invoke a specific skill directly only when the user explicitly names that skill or clearly wants that exact workflow.

Every skill supports `--help` to see parameters and behavior variations.

Shared templates live in `templates/skill/`. After editing templates, run `python3 templates/skill/scripts/propagate.py` to push changes to all skills.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for how to add skills, guidelines, agents, and test locally.

## Skill Categories

Skills are organized into three categories:

| Category | Purpose | Example |
|----------|---------|---------|
| **Guideline** (helper) | Reusable knowledge and standards, auto-invoked by task skills | `workflow`, `communication`, `coding` |
| **Connector** (helper) | Platform API wrappers with MCP fallback, auto-invoked by task skills | `github`, `bitbucket`, `confluence`, `jira` |
| **Task** (user-facing) | Specific engineering tasks with self-sufficient inline fallbacks | `code-review-pr`, `dev-build`, `docs-write` |
| **Routing** (orchestrator) | Coordinate and route work across other skills | `use`, `team`, `code-review`, `docs`, `dev`, `diagram` |

## Skill Architecture Rules

- **Self-sufficient**: Each task skill includes inline fallback summaries for all shared knowledge. Works even if guideline skills are not installed.
- **Delegation, not file sharing**: When a skill needs another skill's capability, it invokes that skill (e.g., "invoke `/adk:coding`"), never references its sub-files. The invoking skill specifies the output format it needs, not how to do the work.
- **All reference material lives under `references/`**, with subfolders when grouping aids readability.
- **Consistent structure**: Every skill has `SKILL.md`, `references/`, and `scripts/`. Multi-mode skills also have `stages/` for conditional stage files.
- **No interactive scripts**: All interactivity is via the agent itself.
- **Human-in-the-loop**: All non-trivial skills confirm intent, present options, and get plan approval before executing.
- **Plan first**: Execution only starts after an approved plan exists. Pass `--auto` to skip confirmations.

## Skill Naming

- **Claude plugin**: Skills use the namespace `adk:` — invoked as `/adk:<skill-name>`
- **skills.sh**: Skills use the `name` field with `adk-` prefix — invoked as `/adk-<skill-name>`
- **`name` field**: Set to `adk-<skill-name>` in SKILL.md frontmatter (used by skills.sh for namespacing)
- **`description` field**: Starts with `adk -` followed by bracket tags and the description

## Cross-Skill Update Dependencies

When updating shared concepts, these skills need coordinated updates:

| What Changed | Skills to Update |
|---|---|
| **Workflow framework** (`skills/workflow/`) | All full-tier task skills invoke `/adk:workflow` |
| **Communication style** (`skills/communication/`) | All task skills invoke `/adk:communication` |
| **Principal Engineer lens** (`skills/principal-engineer/`) | All full-tier task skills invoke `/adk:principal-engineer` |
| **Agentic teams contract** (`skills/agentic-teams/`) | All skills that spawn child agents invoke `/adk:agentic-teams` |
| **Output format standards** (`skills/output-format/`) | All skills that produce output invoke `/adk:output-format` |
| **Interaction protocols** (`skills/interaction/`) | All interactive skills invoke `/adk:interaction` |
| **Preflight validations** (`skills/preflight-check/`) | All skills with tool/MCP dependencies invoke `/adk:preflight-check` |
| **Review standards** (`skills/review-standards/`) | `code-review-pr`, `code-review-repo`, `code-review-fix`, `docs-review`, `audit` |
| **Coding guidelines** (`skills/coding/references/coding-guidelines/`) | `code-review-pr`, `code-review-repo`, `code-review-fix`, `dev-build`, `dev-refactor`, `dev-migrate`, `audit` |
| **Doc-writing guidelines** (`skills/docs-guidelines/references/doc-guidelines/`) | `docs-write`, `docs-review`, `docs-repo`, `docs-crud`, `spec` |
| **Markdown guidelines** (`skills/docs-md/`) | `docs-write`, `docs-repo`, `docs-review`, `docs-crud` |
| **Architecture guidelines** (`skills/architecture/`) | `code-review-pr`, `code-review-repo`, `audit`, `design`, `dev-build`, `dev-refactor` |
| **GitHub connector** (`skills/github/`) | `code-review-pr`, `code-review-fix` |
| **Bitbucket connector** (`skills/bitbucket/`) | `code-review-pr`, `code-review-fix` |
| **Confluence connector** (`skills/confluence/`) | `docs-review`, `docs-crud`, `docs-write`, `docs-confluence` |
| **Jira connector** (`skills/jira/`) | `docs-crud`, `code-review-pr` (context reading) |
