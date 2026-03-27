---
name: improve
description: Use when contributing to DevKit itself — reviews and updates skills, agents, guidelines, manifest sources, and platform packaging against ecosystem leaders (Superpowers, BMAD, GSD) and community best practices
user_invocable: true
arguments:
  - name: scope
    description: "What to improve: all, skills, agents, guidelines, integrations, docs, sources, ecosystem (default: all)"
    required: false
  - name: focus
    description: "Optional specific skill, agent, or area to focus on"
    required: false
  - name: depth
    description: "Audit depth: quick (structure only), standard (structure + content), deep (structure + content + ecosystem comparison). Default: standard"
    required: false
---

# Improve DevKit (Contributor)

This is the contributor version of `/devkit:manage-improve`. It runs inside this repository and modifies files directly.

## References

Use `skills/_references/agentic-teams.md`, `skills/_references/preflight-validations.md`, and `skills/_references/guidelines/README.md`.

## Before You Start

1. Ensure you are on the `main` branch or a feature branch
2. Ensure the working tree is clean (`git status`)
3. Read `manifest.json` at the repo root
4. Read `AGENTS.md` and `CONTRIBUTING.md` for current conventions

## Manifest Sync

### Copy Sources

For each source with `"type": "copy"` in `manifest.json`:

1. Check if the upstream repo is available at `../<repo-name>/` (local sibling) or clone to a temp dir
2. For local siblings, prefer reading directly (avoids network)
3. Compare upstream files against local copies using the `mapping` in manifest.json
4. For each changed file: show the diff and apply the update
5. Update `last_sync` and `last_commit` in `manifest.json`

### Ref Sources

For each source with `"type": "ref"` in `manifest.json`:

1. Check the upstream repo for changes to the `source_path`
2. Read the upstream content and compare with the current skill files listed in `ref_skills`
3. Present a summary of what changed upstream
4. Do NOT auto-apply — let the contributor decide what to incorporate
5. If approved, update the skill files and `last_sync`

## Audit Checklist

### Skills Audit (Structure)

- [ ] All `skills/*/SKILL.md` files have valid YAML frontmatter
- [ ] All descriptions start with "Use when..." and state **triggering conditions** (not workflow summaries)
- [ ] All cross-references use `/devkit:` prefix
- [ ] All non-trivial skills reference `skills/_references/agentic-teams.md`
- [ ] All skills with external deps have preflight calling `check-skill-deps.zsh`
- [ ] `settings/base-settings.json` contextInstructions lists every skill
- [ ] No orphaned skill directories (skill dir exists but no SKILL.md)
- [ ] No broken file references in SKILL.md files

### Skills Audit (Quality — inspired by Superpowers CSO and BMAD patterns)

- [ ] Skill descriptions are optimized for agent discoverability (concrete triggers, error symptoms, tool names)
- [ ] Frequently-loaded skills (use, manage-*) are under 200 lines; all others under 500 lines
- [ ] Skills use progressive disclosure (SKILL.md as entrypoint, supporting files in subdirectories for reference material)
- [ ] Skills specify appropriate tool restrictions where applicable
- [ ] Review skills follow the canonical comment template from `skills/_references/review-comment-template.md`
- [ ] Write skills produce markdown-first output with optional publishing
- [ ] Dev workflow skills (dev-*, plan-*) enforce explicit quality gates between phases
- [ ] Adjacent skills section is present and accurate on all skills

### Agents Audit

- [ ] All `agents/*.md` files have valid YAML frontmatter
- [ ] All agent descriptions are clear and specific
- [ ] Tool lists are realistic and minimal
- [ ] Agent coverage matches workflow needs (review, research, documentation, diagram, security, migration teams)

### Guidelines Audit

- [ ] `skills/_references/guidelines/coding/` covers all repo types in `profiles/detect.md`
- [ ] `skills/_references/guidelines/document/` covers all document types
- [ ] No outdated framework versions or deprecated API references
- [ ] Guidelines cite authoritative sources (official docs, specs) over blog posts

### Platform Audit

- [ ] `.claude-plugin/plugin.json` version matches across all platform adapters
- [ ] `.cursor-plugin/plugin.json` is consistent
- [ ] `.codex/INSTALL.md` references and instructions are current
- [ ] `.opencode/INSTALL.md` references and instructions are current
- [ ] `GEMINI.md` references are current
- [ ] All platform docs include update instructions

### Scripts Audit

- [ ] All scripts use `#!/usr/bin/env zsh` and `set -euo pipefail`
- [ ] `check-skill-deps.zsh` has cases for all skills that need them
- [ ] `install.zsh --list` shows all skills correctly
- [ ] Scripts are portable across macOS and Linux

## Required Child Agents

Run at least these in parallel:

- **Catalog auditor**: Scans all skill directories, agent definitions, and documentation files for completeness. Checks structure audit items (frontmatter, descriptions, cross-references, agentic-teams references). Produces a gap report with specific files and line numbers.

- **Quality auditor**: Evaluates skill content quality — description discoverability (CSO), token efficiency (line counts), progressive disclosure patterns, tool restrictions, quality gates in workflow skills, and adherence to shared contracts (review pipeline, output formats, source routing). Produces a quality score per skill and specific improvement suggestions.

- **Manifest auditor**: Checks `manifest.json` for sync freshness, validates that all `dest_paths` exist on disk, verifies `last_commit` against upstream, and confirms no orphaned files from removed mappings. Produces a manifest health report.

- **Platform auditor**: Verifies all platform adapters (`.claude-plugin`, `.cursor-plugin`, `.codex`, `.opencode`, `GEMINI.md`) are version-consistent, have current references, and include update instructions. Checks `settings/base-settings.json` contextInstructions lists all skills. Produces an adapter consistency report.

- **Ecosystem research agent**: Use `subagent_type: devkit:research-agent` (NOT `devkit:research-quick`). This agent must do actual deep web research — fetch GitHub repos, read READMEs, check changelogs, compare architectures. Spawn multiple research agents in parallel, one per topic:
  - **Upstream tracker**: Check Superpowers (obra/superpowers) for new skills, workflow changes, version updates
  - **BMAD analyst**: Check BMAD (bmad-code-org/BMAD-METHOD) for agent persona patterns, document sharding, scale-adaptive workflows
  - **GSD analyst**: Check GSD (gsd-build/get-shit-done) for context engineering, wave-based execution, artifact cascade patterns
  - **Community scanner**: Check awesome-claude-code, awesome-agent-skills, anthropics/skills for new patterns and emerging tools
  - **Docs tracker**: Check Claude Code docs, Agent Skills standard (agentskills.io) for spec changes
  - Each produces an opportunities brief with specific actionable items and links to sources

- **Editorial agent**: Converts all findings into a prioritized improvement plan with checkbox steps. Groups by priority (critical, high, medium, nice-to-have). Marks items that require upstream sync vs. local-only changes.

## Ecosystem Comparison (depth=deep only)

When `depth=deep`, the research agent should produce a comparison matrix:

| Dimension | DevKit | Superpowers | BMAD | GSD |
|-----------|--------|-------------|------|-----|
| Skill count | Count skills/ | 14 core | 34+ workflows | 37+ commands |
| Workflow enforcement | Check gate patterns | Hard gates, TDD deletion | 4-phase artifact gates | Discuss-Plan-Execute-Verify |
| Agent orchestration | agentic-teams.md | Coordinator + subagents | Persona-based agents | Thin orchestrator + waves |
| Context efficiency | Check line counts | CSO + <200 word targets | Document sharding | Fresh context per task |
| Code review | review pipeline | Two-stage (spec + quality) | Three-layer parallel | Goal-backward verification |
| Platform support | 5 platforms | 5 platforms | 3 platforms + npm | 8 runtimes via npm |

Flag gaps where DevKit is behind and propose specific improvements.

## Output

Save the improvement plan to `.temp/plans/improve-<date>.md` with checkbox steps grouped by priority.

Produce a summary with:
- Critical issues (broken references, version mismatches, stale sources)
- Quality gaps (skills with poor discoverability, token inefficiency, missing gates)
- Ecosystem opportunities (patterns from Superpowers/BMAD/GSD worth adopting)
- Missing coverage (skills, guidelines, platform support, agent types)
- Recommended improvements by priority with estimated effort (small/medium/large)

## Adjacent Skills

- `/devkit:manage-setup` for checking tool and MCP installation
- `/devkit:manage-validate` for validating MCP server connectivity
- `/devkit:manage-skill` for creating or updating individual skills
- `/devkit:manage-update` for pulling updates from upstream
- `/devkit:review-codebase` for non-mutating whole-repo review
