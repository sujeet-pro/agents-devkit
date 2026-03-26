---
name: manage-improve
description: Audit and upgrade DevKit itself by reviewing skills, agents, guidelines, manifest sources, MCP routing, and packaging against current software-development workflows
user_invocable: true
arguments:
  - name: scope
    description: "What to improve: all, skills, agents, guidelines, integrations, docs, sources (default: all)"
    required: false
  - name: focus
    description: "Optional specific skill, agent, or area"
    required: false
---

# Improve DevKit

Use `skills/_references/agentic-teams.md`, `skills/_references/preflight-validations.md`, and `skills/_references/guidelines/README.md`.

## Manifest-Driven Sync

Before making any edits, check `manifest.json` at the repo root:

### Copy Sources (diagramkit, superpowers)

1. Read the `last_sync` timestamp for each copy source
2. If stale (older than 7 days), pull the latest from the upstream repo
3. Diff the upstream files against the current local copies
4. For changed files: update the local copy and record the new `last_commit`
5. Update `last_sync` in `manifest.json`

### Ref Sources (pagesmith)

1. Read the `last_sync` timestamp for each ref source
2. If stale, pull the latest from the upstream repo
3. Compare upstream content against current skill files listed in `ref_skills`
4. Do NOT auto-apply changes — present a summary of what changed upstream and let the user decide
5. If the user approves, edit the skill files and update `last_sync`

## Sync Rules

- First compare against the canonical GitHub source before making local edits
- Refresh mirrored diagram references from `../diagramkit/agent_skills/_references/`
- Keep active coding and document guidance loaded from `skills/_references/guidelines/`

## Required Child Agents

Run at least these child agents in parallel:

- **Catalog auditor**: scans all skill directories, agent definitions, and documentation files for completeness. Checks that every skill has valid YAML frontmatter, description starting with "Use when...", proper `/devkit:` cross-references, and agentic-teams.md reference for non-trivial skills. Produces a gap report with specific files and missing elements.
- **Manifest auditor**: checks `manifest.json` for sync freshness, validates that all `dest_paths` exist on disk, verifies `last_commit` matches upstream HEAD, and confirms no orphaned files. Produces a manifest health report.
- **MCP and packaging auditor**: verifies platform adapters (`.claude-plugin`, `.cursor-plugin`, `.codex`, `.opencode`, gemini) are version-consistent and that `settings/base-settings.json` contextInstructions lists all current skills. Produces an adapter consistency report.
- **Research agent** (`research-agent`): researches current ecosystem patterns, new tools, official docs updates, and community best practices relevant to DevKit's skill categories. Produces an opportunities brief.
- **Editorial agent**: converts all findings into a prioritized improvement plan with checkbox steps. Groups by priority (critical, high, medium, nice-to-have). Produces the final plan file.

## Audit Checklist

The child agents should collectively cover:

- [ ] All skills have valid YAML frontmatter and description starting with "Use when..."
- [ ] All skills that reference other skills use the `/devkit:` prefix
- [ ] All non-trivial skills reference `skills/_references/agentic-teams.md`
- [ ] All skills that need external tools have a preflight section calling `check-skill-deps.zsh`
- [ ] Platform adapters are version-consistent
- [ ] `manifest.json` sources are current and all `dest_paths` exist
- [ ] Guidelines cover all detected repo types
- [ ] `settings/base-settings.json` contextInstructions lists all current skills
- [ ] No broken file references in SKILL.md files

## Output

Save the improvement plan to `.temp/plans/improve-<date>.md` with checkbox steps.

Produce:

- current-state gaps with file paths and line references
- stale or broken manifest sources
- missing or outdated skill references
- platform adapter inconsistencies
- recommended edits grouped by priority

## Adjacent Skills

- `/devkit:manage-setup` for checking tool and MCP installation
- `/devkit:manage-validate` for validating MCP server connectivity
- `/devkit:manage-skill` for creating or updating individual skills
- `/devkit:manage-update` for pulling updates from upstream
