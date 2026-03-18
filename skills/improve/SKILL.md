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

## Phase 2: Validate Configuration Consistency

Run a systematic consistency check across the entire devkit. Report each check as PASS, WARN, or FAIL.

### 2a. Skill Registry Consistency

Check that **every skill directory** in `skills/` is registered in all required locations:

| Source of Truth | Files to Check |
|------|------|
| `skills/*/SKILL.md` | Ground truth — every directory with a SKILL.md is a skill |
| `.claude-plugin/marketplace.json` | Must list all user-installable skills (internal sub-skills like mermaid, excalidraw, image-transform, markdown may be excluded) |
| `settings/base-settings.json` | contextInstructions entry 1 must mention every user-invocable skill |
| `settings/mcp-instructions.md` | Skill Routing tables must include every user-invocable skill |
| `README.md` | Skills tables must include every user-invocable skill |

For each skill found in `skills/`, read its SKILL.md frontmatter. If `user_invocable: true`:
- **FAIL** if missing from `README.md` skills tables
- **FAIL** if missing from `settings/base-settings.json` contextInstructions
- **WARN** if missing from `.claude-plugin/marketplace.json` (some internal skills are OK to exclude)
- **WARN** if missing from `settings/mcp-instructions.md` routing tables

### 2b. Agent Registry Consistency

Check that **every agent** in `agents/` is documented:

| Source of Truth | Files to Check |
|------|------|
| `agents/*.md` | Ground truth — every .md file is an agent |
| `README.md` | Agents table must list all agents |
| `settings/mcp-instructions.md` | Agent Routing table must list all agents |
| `settings/base-settings.json` | contextInstructions entry 4 must reference all agents |

For each agent:
- **FAIL** if missing from `README.md` agents table
- **WARN** if missing from `settings/mcp-instructions.md` agent routing table
- **WARN** if missing from `settings/base-settings.json` contextInstructions

### 2c. Guideline Registry Consistency

Check that `README.md` guideline tables match what exists in `guidelines/coding/` and `guidelines/document/`:
- **FAIL** if a guideline file exists but is not listed in README
- **FAIL** if README lists a guideline that doesn't exist

### 2d. MCP Configuration Consistency

Check that MCP server configs are synchronized:

| Check | Sources |
|------|------|
| `claude.json` template servers | Must match `README.md` MCP table rows |
| `claude.json` env var placeholders | Must match `scripts/check-env.zsh` checks |
| `claude.json` env var placeholders | Must match `README.md` env var docs |
| `claude.json` env var placeholders | Must match `SETUP.md` Phase 4 env check |
| `settings/mcp-instructions.md` MCP sections | Must cover every server in `claude.json` |
| `settings/mcp-setup.md` setup instructions | Must cover every server in `claude.json` |

For each MCP server in `claude.json`:
- **FAIL** if not documented in `README.md` MCP table
- **FAIL** if its env vars aren't checked in `check-env.zsh`
- **WARN** if not covered in `mcp-instructions.md`
- **WARN** if not covered in `mcp-setup.md`

### 2e. Script and JSON Validation

Run syntax checks on all shell scripts and JSON files:

```bash
# Validate all shell scripts
for f in scripts/*.zsh install.zsh uninstall.zsh; do
  zsh -n "$f" && echo "PASS: $f" || echo "FAIL: $f"
done

# Validate all JSON files
for f in claude.json settings/base-settings.json .claude-plugin/marketplace.json scripts/model-config.json; do
  jq empty "$f" && echo "PASS: $f" || echo "FAIL: $f"
done
```

### 2f. Model Version Check

Run `scripts/update-models.zsh --dry-run` to check if model versions in `scripts/model-config.json` are current. Report any outdated versions as WARN.

### 2g. Cross-Reference: Skill Delegation Tables

For each skill that has an "Agent & Skill Delegation" table, verify:
- Every agent referenced actually exists in `agents/`
- Every skill delegation target (e.g., `/research`, `/diagram`) actually exists in `skills/`
- **FAIL** if a referenced agent or skill doesn't exist

### 2h. README Structure Validation

Check that README.md sections are internally consistent:
- Skills in the "Task -> Skill Mapping" table match the categorized skills tables
- Agents in the agents table match those referenced in the Task -> Skill Mapping table
- Selective Plugin Install table entries match `marketplace.json` plugins
- No broken internal links (section references like `#heading-name`)

### 2i. Report

Present all findings in a table:

```
## Configuration Consistency Report

| # | Check | Status | Details |
|---|-------|--------|---------|
| 1 | Skills in marketplace.json | PASS | 22/22 skills registered |
| 2 | Skills in README | WARN | missing: /improve |
| 3 | Agents in README | PASS | 9/9 agents documented |
| 4 | MCP servers documented | PASS | 3/3 servers in README |
| 5 | Env vars synced | FAIL | CONFLUENCE_URL missing from SETUP.md |
| ... | ... | ... | ... |

**Summary**: X PASS, Y WARN, Z FAIL
```

If any FAILs are found, add them as HIGH priority items in the improvement plan (Phase 4).
If any WARNs are found, add them as MEDIUM priority items.

---

## Phase 3: Research Best Practices

Spawn parallel research agents to gather current best practices. Also include model version research.

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

### Agent 4: Model Versions & CLI Tools
Research current model versions for all supported CLIs:
- Latest Claude model IDs (Opus, Sonnet, Haiku families)
- Latest OpenAI model IDs (o-series, GPT series)
- Latest Google Gemini model IDs
- Latest Cursor CLI supported models
- Update `scripts/model-config.json` if versions are outdated

## Phase 4: Generate Improvement Plan

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

## Phase 5: Interactive Implementation

Present the improvement plan to the user in a clear, scannable format.

**Consistency FAILs from Phase 2 are auto-included as HIGH priority items.**
**Consistency WARNs from Phase 2 are auto-included as MEDIUM priority items.**

1. Show a summary table of all improvements grouped by priority
2. Ask the user which improvements to apply (all, by priority, or specific ones)
3. For each selected improvement:
   - Explain what will change before making changes
   - Make the change
   - Verify the change doesn't break existing functionality
   - Report what was changed and why

## Phase 6: Changelog

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
