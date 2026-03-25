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
3. Compare the upstream content against the current skill files listed in `ref_skills`
4. Do NOT auto-apply changes — present a summary of what changed upstream and let the user decide
5. If the user approves updates, edit the skill files to reflect new capabilities and update `last_sync`

## Sync Rules

When improving DevKit itself:

- first compare against the canonical GitHub source of truth at `https://github.com/sujeet-pro/agents-devkit` for skill definitions, references, and packaging docs before making local edits
- refresh the mirrored diagram references from `../diagramkit/agent_skills/_references/`, for example with `rsync -a ../diagramkit/agent_skills/_references/ skills/_references/`
- keep active coding and document guidance loaded from `skills/_references/guidelines/`

## Required Child Agents

Run at least these child agents in parallel:

- a **catalog auditor** for skills, agents, and docs completeness
- a **manifest auditor** that checks sync freshness and source consistency
- an **MCP and packaging auditor** that verifies platform adapters are consistent
- a **research pass** for current ecosystem patterns, new tools, and official docs
- an **editorial pass** that converts findings into a prioritized improvement plan

## Audit Checklist

The child agents should collectively cover:

- [ ] All skills have valid YAML frontmatter and description starting with "Use when..."
- [ ] All skills that reference other skills use the `/devkit:` prefix
- [ ] All non-trivial skills reference `skills/_references/agentic-teams.md`
- [ ] All skills that need external tools have a preflight section calling `check-skill-deps.zsh`
- [ ] Platform adapters (.claude-plugin, .cursor-plugin, .codex, .opencode, gemini) are version-consistent
- [ ] `manifest.json` sources are current and all `dest_paths` exist
- [ ] Guidelines cover all detected repo types in `profiles/detect.md`
- [ ] `settings/base-settings.json` contextInstructions lists all current skills
- [ ] No broken file references in SKILL.md files

## Output

Save the improvement plan to `.temp/plans/improve-<date>.md` with checkbox steps.

Produce:

- current-state gaps
- stale or broken manifest sources
- missing or outdated skill references
- platform adapter inconsistencies
- opportunities to simplify skill design
- recommended edits grouped by priority (critical → nice-to-have)
