# Contributing to DevKit

## Quick Start

```bash
git clone https://github.com/sujeet-pro/agents-devkit.git ~/.devkit
cd ~/.devkit
```

## Project Structure

```
agents-devkit/
├── templates/skill/         # Canonical templates and shared references
│   ├── SKILL-TEMPLATE.md    # Boilerplate for new skills
│   ├── references/          # Master copies of shared reference docs
│   ├── common/              # Cross-skill guidelines and conventions
│   │   ├── project-guidelines.md
│   │   └── help-format.md
│   └── scripts/             # Master copy of preflight.py, propagate.py, and shared Textual TUI scripts
├── agents/                  # Shared agent definitions (one .md per agent)
├── settings/                # MCP configuration guide
├── skills/                  # Skill library (each skill is self-contained)
│   ├── use/                 # Orchestrator — analyzes prompts, routes to skills
│   ├── coding/              # Helper — detects stack, loads coding guidelines
│   │   ├── SKILL.md
│   │   └── guidelines/      # 16 coding guideline files
│   ├── doc-writing/         # Helper — detects doc type, loads writing guidelines
│   │   ├── SKILL.md
│   │   └── guidelines/      # 24 document guideline files
│   ├── <skill>/             # Multi-stage skills (unified entry points)
│   │   ├── SKILL.md         # Entry point with stage selection logic
│   │   ├── stages/          # Conditional stage files loaded based on context
│   │   ├── references/      # Copied from templates/skill/references/
│   │   └── scripts/         # Copied from templates/skill/scripts/
│   └── ...
├── .claude-plugin/          # Claude Code plugin metadata
├── manifest.json            # Upstream source tracking
└── README.md
```

## Skill Architecture

### Workflow Tiers

Every skill declares a `workflow-tier` in its YAML frontmatter:

| Tier | Description | Skills |
|------|-------------|--------|
| `full` | Uses the full 6-phase framework, often with stage-specific skipping rules | review, review-doc, write, develop, plan, diagram, spec, project, audit, research, design, handoff, team |
| `abbreviated` | Uses the framework but permanently skips some middle phases (e.g., approach selection, planning) | test, setup |
| `helper` | Auto-invoked by other skills, does not own the workflow | coding, doc-writing |
| `orchestrator` | Multi-skill pipeline manager | use |

### The 6-Phase Workflow

Individual skills follow a standardized 6-phase workflow (defined in each skill's `references/workflow-6phase.md`):

1. **Intent Expansion** — Expand the prompt, show concise visible reasoning, identify skills/tools/MCPs, and confirm direction early
2. **Research & Options** — Research the problem, scan the codebase, and end with 2-3 viable approaches
3. **Approach Selection** — Interactive session where the user picks, mixes, or simplifies the approach
4. **Planning** — Produce an executable plan with sequencing, file targets, and verification
5. **Execute** — Run the approved plan
6. **Validate & Learn** — Verify the result, simplify when needed, and capture the key takeaway

Phases are complexity-adaptive — trivial tasks use abbreviated forms, while larger tasks use the full workflow.

### Self-Sufficiency Rule

**Every skill must be fully self-contained.** A skill must NOT reference files outside its own directory. All shared references (`agentic-teams.md`, `preflight.md`, `output-formats.md`, `workflow-6phase.md`, `principal-engineer.md`, `communication-style.md`) and shared Textual scripts under `scripts/tui/` are **copied into** each skill's local folders. This ensures skills work when installed individually via `npx`.

The `templates/skill/` directory holds **canonical master copies** of shared files. When adding a new skill, copy from `templates/skill/references/` into your skill's `references/` directory. When updating a shared reference, edit the file in `templates/skill/references/` or `templates/skill/common/`, then run:

```bash
python3 templates/skill/scripts/propagate.py
```

This propagates changes to all skill directories. Use `--dry-run` to preview changes first.

### Helper Skills (auto-invoked, not user-facing)

| Skill | Purpose |
|---|---|
| `/coding` | Detects repo stack (languages, frameworks), loads matching coding guidelines from `coding/references/coding-guidelines/` |
| `/doc-writing` | Detects document type, loads matching writing guidelines from `doc-writing/references/doc-guidelines/` |

These are invoked automatically by other skills. `/use` should be the default route for general prompts and includes them when needed.

### Core Skills

Multi-mode skills contain conditional `stages/*.md` files loaded based on context. Simpler skills embed all logic directly in SKILL.md. Routing logic is always in the main SKILL.md — there are no separate router skills.

| Skill | Area | Description |
|---|---|---|
| `/review` | Review | Code review: PR, local, branch + fix/comment/interactive |
| `/develop` | Dev | Implement features, fix bugs, enhance code, TDD |
| `/write` | Docs | Create/update any document (ADR, RFC, blog, changelog, etc.) |
| `/plan` | Plan | Brainstorm, write, execute, and track implementation plans |
| `/spec` | Spec | Write specs, analyze consistency, generate checklists |
| `/research` | Research | Multi-agent research with citations |
| `/diagram` | Diagram | Create diagrams (Mermaid, Excalidraw, draw.io, Graphviz) |
| `/design` | Design | UI/UX design direction + visual audit |
| `/audit` | Quality | Audit: codebase, security, performance, dependencies |
| `/review-doc` | Review | Review documents (local, Confluence, Google Docs) |
| `/test` | QA | User acceptance testing with interactive verification |
| `/project` | Project | Initialize projects, manage milestones and ideas |
| `/handoff` | Session | Pause/resume work sessions, context threads |
| `/setup` | Setup | Configure CLI tools and MCP servers |

### Meta Skills

| Skill | Description |
|---|---|
| `/team` | Multi-model review, agent team dispatch |
| `/use` | Orchestrator: auto-select and execute skill pipeline |

## Adding a Skill

1. **Create the skill directory**: `skills/<skill-name>/`

2. **Create `SKILL.md`** with frontmatter (see `templates/skill/SKILL-TEMPLATE.md` for the full template):
   ```yaml
   ---
   name: skill-name
   description: "Use when..."
   user-invocable: true
   argument-hint: "<required-arg> [--optional-arg]"
   allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, Agent]
   workflow-tier: full
   dependencies:
     commands: [git]
   ---
   ```

3. **Create `references/`** — copy shared references from `templates/skill/references/`:
   - `workflow-6phase.md` (required for all skills)
   - `agentic-teams.md` (required for all skills)
   - `principal-engineer.md` (required for all full-tier skills)
   - `communication-style.md` (required for all full-tier skills)
   - `preflight.md` (required for all skills)
   - `output-formats.md` (required for output-producing skills)
   - `source-routing.md` (required for MCP-backed skills)
   - `review-pipeline.md` (required for review skills)
   - Add any skill-specific reference files

4. **Create `scripts/preflight.py`** — copy from `templates/skill/scripts/preflight.py`

5. **Add the Phase Applicability table** to SKILL.md showing which of the 6 phases apply

6. **Add the Output Format section** defining the markdown output structure

7. **Add the Adjacent Skills section** listing related skills

8. Use `${CLAUDE_SKILL_DIR}` to reference files within the skill directory

9. Use `review-*` naming for read-only review skills, `write-*` for drafting skills

10. **Test**: `python3 skills/<skill-name>/scripts/preflight.py skills/<skill-name>`

## Adding a Guideline

1. **Coding guidelines**: Add to `skills/coding/references/coding-guidelines/<name>.md`
2. **Document guidelines**: Add to `skills/doc-writing/references/doc-guidelines/<name>.md`
3. Cite authoritative sources (specs, official docs) over blog posts

## Adding an Agent

1. Create `agents/<agent-name>.md` with YAML frontmatter:
   ```yaml
   ---
   name: agent-name
   description: "..."
   model: opus | sonnet
   allowed-tools:
     - Glob
     - Grep
     - Read
   ---
   ```
2. Keep tool lists minimal and realistic
3. Skills reference agents by name via the host's native agent system

## Testing Changes

```bash
# Check a skill's dependencies
python3 skills/<skill-name>/scripts/preflight.py skills/<skill-name>

# Verify all skills have required structure
for d in skills/*/; do
  skill=$(basename "$d")
  [ "$skill" = "_shared" ] && continue
  [ ! -f "$d/SKILL.md" ] && echo "MISSING SKILL.md: $skill"
  [ ! -d "$d/references" ] && echo "MISSING references/: $skill"
  [ ! -f "$d/scripts/preflight.py" ] && echo "MISSING preflight.py: $skill"
done
```

## Conventions

- **Skill descriptions**: start with "Use when..."
- **Workflow tier**: declare in frontmatter (`full`, `abbreviated`, `helper`, `orchestrator`)
- **Scripts**: prefer Python (`#!/usr/bin/env python3`), then shell, then JavaScript
- **Skill cross-references**: use `/<skill-name>` format (mention by name, don't reference files)
- **Skill file references**: use `${CLAUDE_SKILL_DIR}/references/` or `${CLAUDE_SKILL_DIR}/scripts/`
- **Self-sufficiency**: never reference files outside the skill's own directory
- **Git**: use system identity
- **Intermediary artifacts**: `.temp/` directory (gitignored)
- **Proposals**: `./temp/proposal/<proposal-name>.md` (mutable during Phase 4)
- **Task tracking**: `.temp/<task-slug>/` with phase files (01-brainstorm.md, 02-plan.md, 03-progress.md, 04-summary.md)
- **Output**: markdown by default for all skill outputs

## Upstream Sources

DevKit tracks upstream sources in `manifest.json`:

- **Copy sources** (diagramkit, superpowers): Files are copied into this repo. When updating DevKit-added content in these skills, add a `<!-- DevKit addition -->` marker so upstream syncs can preserve it.
- **Ref sources** (pagesmith): Skills reference upstream content but are authored in DevKit.
