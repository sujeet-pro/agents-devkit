---
name: improve
description: Use when contributing to DevKit itself — reviews and updates skills, agents, guidelines, manifest sources, and platform packaging
user_invocable: true
arguments:
  - name: scope
    description: "What to improve: all, skills, agents, guidelines, integrations, docs, sources (default: all)"
    required: false
  - name: focus
    description: "Optional specific skill, agent, or area to focus on"
    required: false
---

# Improve DevKit (Contributor)

This is the contributor version of `/devkit:manage-improve`. It runs inside this repository and modifies files directly.

## Before You Start

1. Ensure you are on the `main` branch or a feature branch
2. Ensure the working tree is clean (`git status`)
3. Read `manifest.json` at the repo root

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

Run these checks against the current state of the repo:

### Skills Audit
- [ ] All `skills/*/SKILL.md` files have valid YAML frontmatter
- [ ] All descriptions start with "Use when..."
- [ ] All cross-references use `/devkit:` prefix
- [ ] All non-trivial skills reference `skills/_references/agentic-teams.md`
- [ ] All skills with external deps have preflight calling `check-skill-deps.zsh`
- [ ] `settings/base-settings.json` contextInstructions lists every skill
- [ ] No orphaned skill directories (skill dir exists but no SKILL.md)

### Agents Audit
- [ ] All `agents/*.md` files have valid YAML frontmatter
- [ ] All agent descriptions are clear and specific
- [ ] Tool lists are realistic and minimal

### Guidelines Audit
- [ ] `skills/_references/guidelines/coding/` covers all repo types in `profiles/detect.md`
- [ ] `skills/_references/guidelines/document/` covers all document types
- [ ] No outdated framework versions or deprecated API references

### Platform Audit
- [ ] `.claude-plugin/plugin.json` version matches across all platform adapters
- [ ] `.cursor-plugin/plugin.json` is consistent
- [ ] `.codex/INSTALL.md` references are current
- [ ] `.opencode/INSTALL.md` references are current
- [ ] `gemini-extension.json` version matches

### Scripts Audit
- [ ] All scripts use `#!/usr/bin/env zsh` and `set -euo pipefail`
- [ ] `check-skill-deps.zsh` has cases for all skills
- [ ] `install.zsh --list` shows all skills correctly

## Required Child Agents

Run at least these in parallel:

- **catalog auditor**: checks skills, agents, docs for completeness and consistency
- **manifest auditor**: checks sync freshness and source consistency
- **platform auditor**: verifies all platform adapters are consistent
- **research agent**: checks for new patterns, tools, or best practices in the ecosystem
- **editorial agent**: converts findings into a prioritized improvement plan

## Output

Save the improvement plan to `.temp/plans/improve-<date>.md` with checkbox steps grouped by priority.

Produce a summary with:
- Critical issues (broken references, version mismatches)
- Stale sources that need syncing
- Missing coverage (skills, guidelines, platform support)
- Recommended improvements by priority
