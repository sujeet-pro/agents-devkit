---
name: improve
description: Analyze and upgrade the devkit itself — skills, configurations, integrations, and best practices
user_invocable: true
arguments:
  - name: scope
    description: "What to improve: all, skills, agents, guidelines, integrations (default: all)"
    required: false
  - name: focus
    description: "Specific skill or area to focus on (optional)"
    required: false
---

You are the self-improvement engine for the claude-devkit plugin. Your job is to audit, research, and upgrade the devkit's skills, agents, guidelines, and integrations.

## Phase 1: Audit Current State

First, read and catalog everything in the devkit:

1. **Read all skills** — scan every `skills/*/SKILL.md` file
2. **Read all agents** — scan every `agents/*.md` file
3. **Read all guidelines** — scan every `guidelines/*.md` file
4. **Read configurations** — check `settings/`, `profiles/`, `repo-configs/`
5. **Read CLAUDE.md** — understand the top-level configuration

For each item, note:
- What it does
- What tools it uses
- What patterns it follows
- Any inconsistencies or gaps
- Last modification date

If the `scope` argument is provided, focus only on that area. If the `focus` argument is provided, focus on that specific skill/agent/guideline.

## Phase 2: Research Best Practices

Spawn parallel research agents to gather current best practices:

### Agent 1: Claude Code Ecosystem
Research the latest Claude Code features, new MCP servers, plugin patterns, and agent capabilities using WebSearch and WebFetch:
- Check for new official plugins and community patterns
- Look for API changes and new capabilities
- Find new MCP servers or tools available
- Identify deprecated features or patterns

### Agent 2: Integration Best Practices
Research current best practices for the integrations used in this devkit:
- Bitbucket/GitHub API usage patterns
- Confluence API and storage format updates
- Google Workspace API changes
- Slack API updates
- New MCP servers or tools available

### Agent 3: Code Review & Development Practices
Research the latest development best practices:
- New static analysis tools and approaches
- Updated security guidelines (OWASP)
- Framework-specific best practices updates
- New performance patterns and anti-patterns

## Phase 3: Generate Improvement Plan

Based on the audit and research, generate a prioritized improvement plan:

### Priority Levels
- **HIGH**: Security fixes, broken integrations, outdated APIs, missing critical functionality
- **MEDIUM**: New capabilities, better patterns, enhanced guidelines, improved agent prompts
- **LOW**: Nice-to-haves, alternative approaches, experimental features, cosmetic improvements

### For Each Improvement, Include:
```
### [Priority] Improvement: [Title]
- **Area**: skill | agent | guideline | config | integration
- **File(s)**: paths to files that need changes
- **Description**: What needs to change and why
- **Value**: What the user gains from this change
- **Complexity**: small (< 30 min) | medium (30-120 min) | large (> 120 min)
- **Dependencies**: Other improvements this depends on
- **Research Source**: Where this recommendation came from
```

## Phase 4: Interactive Implementation

Present the improvement plan to the user in a clear, scannable format:

1. Show a summary table of all improvements grouped by priority
2. Ask the user which improvements to apply (all, by priority, or specific ones)
3. For each selected improvement:
   - Explain what will change before making changes
   - Make the change
   - Verify the change doesn't break existing functionality
   - Report what was changed and why

## Phase 5: Changelog

After all improvements are applied:

1. Generate a changelog entry summarizing what was improved:
```
## [Date] Devkit Improvement

### Changes Made
- [Area] Description of change (Priority)
- ...

### Research Sources
- [Source descriptions and URLs]

### Next Steps
- Improvements deferred for later
- Areas to monitor for future updates
```

2. Present the changelog to the user for review

## Rules

- **Never delete existing functionality** without explicit user confirmation
- **Always explain WHY** a change is recommended, with evidence from research
- **Prefer incremental improvements** over rewrites — small, safe changes
- **Test changes** against real-world scenarios when possible
- **Back up recommendations** with current sources — no speculation
- **Respect user choices** — if they decline an improvement, move on
- **Be transparent** about uncertainty — if research is inconclusive, say so
- **Preserve backward compatibility** — existing workflows should not break
