---
name: manage-improve
description: Audit and upgrade DevKit itself by reviewing skills, agents, guidelines, manifest sources, MCP routing, and packaging against ecosystem leaders (Superpowers, BMAD, GSD) and community best practices
user_invocable: true
arguments:
  - name: scope
    description: "What to improve: all, skills, agents, guidelines, integrations, docs, sources, ecosystem (default: all)"
    required: false
  - name: focus
    description: "Optional specific skill, agent, or area"
    required: false
  - name: depth
    description: "Audit depth: quick (structure only), standard (structure + content), deep (structure + content + ecosystem comparison). Default: standard"
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

- **Catalog auditor**: Scans all skill directories, agent definitions, and documentation files for completeness. Checks that every skill has valid YAML frontmatter, description starting with "Use when...", proper `/devkit:` cross-references, and agentic-teams.md reference for non-trivial skills. Validates no orphaned skill directories exist. Produces a gap report with specific files and missing elements.

- **Quality auditor**: Evaluates skill content quality against ecosystem best practices:
  - Description discoverability: descriptions state triggering conditions, include concrete symptoms and tool names (inspired by Superpowers CSO conventions)
  - Token efficiency: frequently-loaded skills under 200 lines, others under 500 lines
  - Progressive disclosure: SKILL.md as entrypoint with supporting files in subdirectories
  - Quality gates: workflow skills (dev-*, plan-*) enforce explicit gates between phases
  - Review skills follow canonical comment template; write skills produce markdown-first output
  - Adjacent skills sections are present and accurate
  - Produces a quality score per skill and specific improvement suggestions

- **Manifest auditor**: Checks `manifest.json` for sync freshness, validates that all `dest_paths` exist on disk, verifies `last_commit` matches upstream HEAD, and confirms no orphaned files. Produces a manifest health report.

- **MCP and packaging auditor**: Verifies platform adapters (`.claude-plugin`, `.cursor-plugin`, `.codex`, `.opencode`, `GEMINI.md`) are version-consistent and that `settings/base-settings.json` contextInstructions lists all current skills. Checks all platform docs include update instructions. Produces an adapter consistency report.

- **Ecosystem research agent** (`research-agent`): Researches current ecosystem patterns by checking:
  - Upstream sources: Superpowers (obra/superpowers) for new skills or workflow changes
  - Competitor frameworks: BMAD (bmad-code-org/BMAD-METHOD) for agent persona patterns, document sharding, scale-adaptive workflows
  - Competitor frameworks: GSD (gsd-build/get-shit-done) for context engineering, wave-based execution, artifact cascade patterns
  - Community: awesome-claude-code, awesome-agent-skills, anthropics/skills for new patterns
  - Official docs: Claude Code docs, Agent Skills standard (agentskills.io) for spec changes
  - Produces an opportunities brief with specific actionable items

- **Editorial agent**: Converts all findings into a prioritized improvement plan with checkbox steps. Groups by priority (critical, high, medium, nice-to-have). Marks items that require upstream sync vs. local-only changes.

## Audit Checklist

The child agents should collectively cover:

### Structure

- [ ] All skills have valid YAML frontmatter and description starting with "Use when..."
- [ ] All skills that reference other skills use the `/devkit:` prefix
- [ ] All non-trivial skills reference `skills/_references/agentic-teams.md`
- [ ] All skills that need external tools have a preflight section calling `check-skill-deps.zsh`
- [ ] Platform adapters are version-consistent
- [ ] `manifest.json` sources are current and all `dest_paths` exist
- [ ] Guidelines cover all detected repo types
- [ ] `settings/base-settings.json` contextInstructions lists all current skills
- [ ] No broken file references in SKILL.md files
- [ ] All platform docs include update instructions

### Quality (depth=standard or deep)

- [ ] Skill descriptions optimized for agent discoverability (triggering conditions, not workflow summaries)
- [ ] Frequently-loaded skills under 200 lines; all others under 500 lines
- [ ] Skills use progressive disclosure (SKILL.md + supporting files)
- [ ] Workflow skills enforce quality gates between phases
- [ ] Review skills follow canonical comment template
- [ ] Write skills produce markdown-first output
- [ ] Adjacent skills sections are present and accurate

### Ecosystem (depth=deep)

- [ ] DevKit skills cover equivalent functionality to Superpowers core (brainstorm, plan, execute, TDD, review, debug, verify)
- [ ] DevKit workflow patterns incorporate BMAD strengths (scale-adaptive depth, artifact-first development)
- [ ] DevKit context efficiency matches GSD targets (fresh context per subagent, artifact cascade)
- [ ] DevKit platform coverage matches or exceeds competitors
- [ ] No major ecosystem pattern gaps compared to awesome-claude-code and awesome-agent-skills listings

## Output

Save the improvement plan to `.temp/plans/improve-<date>.md` with checkbox steps.

Produce:

- Critical issues: broken references, version mismatches, stale sources
- Quality gaps: skills with poor discoverability, token inefficiency, missing gates
- Ecosystem opportunities: patterns from Superpowers/BMAD/GSD worth adopting
- Missing coverage: skills, guidelines, platform support, agent types
- Recommended edits grouped by priority with estimated effort (small/medium/large)

## Adjacent Skills

- `/devkit:manage-setup` for checking tool and MCP installation
- `/devkit:manage-validate` for validating MCP server connectivity
- `/devkit:manage-skill` for creating or updating individual skills
- `/devkit:manage-update` for pulling updates from upstream
- `/devkit:review-codebase` for non-mutating whole-repo review
