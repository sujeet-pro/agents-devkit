---
title: 'docs-repo'
description: 'Generate comprehensive repository documentation using pagesmith'
skill_name: docs-repo
category: task
workflow_tier: full
user_invocable: true
---

# docs-repo

Use `docs-repo` to generate comprehensive repository documentation using pagesmith. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`docs-repo` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `--scope` | `full`, `package <name>` | `full` | Generate docs for the entire repo or a specific package/module |
| `--format` | `pagesmith`, `markdown` | auto-detect | Output format. Auto-detects from `pagesmith.config.json5` presence |
| `--init` | flag | off | Run `npx pagesmith init` to set up @pagesmith/docs before generating |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section and exit |

### Parameter Notes

- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--verbosity` changes presentation depth, not the fundamental workflow. It is safe to increase when you want more evidence or rationale.
- `--format` controls the artifact shape, which can also change embedding rules or publishing behavior.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before work | Run preflight.py for MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Markdown default, Confluence/Google Docs when requested. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents. Standard doc team: source analyst, outline editor, fact checker, code/diagram specialist, publisher. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |
| `/adk:docs-md` | when writing markdown | Markdown formatting: headings, lists, code blocks, tables, links. |
| `/adk:workspace-conventions` | when setting output paths | Check .adk/context.yaml and repo conventions for output directory, naming, and format. |

### Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

### Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

After dependency checks, detect the documentation format:

1. Check for `pagesmith.config.json5` in the project root. If found, read it to understand the content directory (`docs/` or `content/`), site title, and navigation structure.
2. If `--init` was passed and no config exists, run `npx pagesmith init` and re-read the generated config.
3. Scan for existing documentation in `docs/`, `content/`, or `README.md` to understand current state.

### Format Detection

| Condition | Format | Frontmatter | Structure |
|-----------|--------|-------------|-----------|
| `pagesmith.config.json5` exists | pagesmith | Yes — title, description, navLabel, sidebarLabel, order, draft, layout | folder/README.md with meta.json5 |
| `--format pagesmith` forced | pagesmith | Yes | folder/README.md with meta.json5 |
| No config, no flag | markdown | No | Flat files, single directory |
| `--format markdown` forced | markdown | No | Flat files, single directory |

### Pagesmith Frontmatter

When using pagesmith format, every page gets YAML frontmatter:

```yaml
---
title: "Page Title"
description: "Brief description for SEO and link previews"
order: 1
---
```

The home page (`docs/README.md`) uses the hero layout:

```yaml
---
title: "Project Name"
description: "Project tagline"
layout: hero
---
```

### Section Metadata

Each section folder gets a `meta.json5` file for ordering and labels:

```json5
{
  label: "Guide",
  order: 1,
}
```

## Modes & Variations

Use this section when you want to force a deterministic path instead of relying on the skill's auto-detection rules.


### Behavior Variations

- **Auto-detect (default)**: Checks for `pagesmith.config.json5` in the project root. If found, uses pagesmith format with frontmatter and folder/README.md conventions. If absent, generates plain markdown without frontmatter.
- **`--init`**: Runs `npx pagesmith init` to scaffold @pagesmith/docs, then generates docs using the pagesmith format.
- **`--scope package <name>`**: Limits documentation to a single package in a monorepo. Generates a focused doc tree for that package only.
- **`--format pagesmith`**: Forces pagesmith conventions regardless of config file presence. Creates folder/README.md structure, adds frontmatter, generates meta.json5 files.
- **`--format markdown`**: Forces plain markdown. No frontmatter, no meta.json5, flat file structure.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

The primary output is a complete `docs/` directory tree. After generation, print a summary:

```

## Related Skills

### Adjacent Skills

- `/adk:docs-review` — review existing documentation for quality
- `/adk:docs-crud` — manage individual doc pages (create, update, improve)
- `/adk:docs-write` — write formal documents (ADRs, RFCs, specs)
- `/adk:diagram` — generate architecture and flow diagrams for docs

## Additional Reference

### Doc Structure

The generated documentation tree follows this structure:

### Pagesmith Format

```
docs/
├── README.md                    # Home page (hero layout)
├── guide/
│   ├── meta.json5               # Section: order 1
│   ├── README.md                # Getting Started
│   ├── concepts/
│   │   ├── meta.json5
│   │   └── README.md            # Core Concepts
│   └── configuration/
│       ├── meta.json5
│       └── README.md            # Configuration Guide
└── reference/
    ├── meta.json5               # Section: order 2
    ├── README.md                # Reference Overview
    ├── api/
    │   ├── meta.json5
    │   └── README.md            # API Reference
    ├── cli/
    │   ├── meta.json5
    │   └── README.md            # CLI Reference
    └── config/
        ├── meta.json5
        └── README.md            # Config Reference
```

### Markdown Format

```
docs/
├── README.md                    # Home page
├── getting-started.md
├── concepts.md
├── configuration.md
├── api-reference.md
├── cli-reference.md
└── config-reference.md
```

### Common Workflow

### 1. Confirm

- Confirm the repository to document and target audience
- Detect pagesmith config and determine format
- Identify scope: full repo or specific package
- Surface assumptions about what to document (public API only? internal architecture? both?)

### 2. Research

Launch research agents to analyze the codebase in parallel:

- **Architecture analyst**: reads directory structure, entry points, module boundaries, dependency graph. Produces a high-level architecture summary.
- **API surface scanner**: extracts exported functions, classes, types, REST endpoints, CLI commands. Produces a raw API inventory.
- **Existing docs scanner**: reads any existing README, docs/, CHANGELOG, inline JSDoc/docstrings. Identifies what's already documented.

End with a structured codebase summary that informs the doc plan.

### 3. Execute

Launch child agents in parallel waves:

**Wave 1 — Reference pages** (factual, code-derived):
- **API documenter**: generates API reference from extracted types, functions, endpoints. Includes parameter tables, return types, examples.
- **CLI documenter**: generates CLI reference from command definitions, help text, argument parsing.
- **Config documenter**: generates config reference from schema, defaults, validation rules.

**Wave 2 — Guide pages** (narrative, cross-referencing):
- **Getting-started writer**: creates a quickstart guide with install, configure, first-use flow.
- **Concepts writer**: explains core abstractions, data flow, key design decisions.
- **Configuration writer**: practical guide to configuring the project, referencing the config reference.

**Wave 3 — Home page and metadata**:
- **Home page writer**: generates the landing page with project overview, feature highlights, navigation to sections.
- **Metadata generator**: creates all meta.json5 files, verifies frontmatter consistency.

### 4. Validate

Run validation checks:

- Cross-reference every code example with actual source — flag any invented APIs
- Verify all internal links resolve to actual pages
- Check frontmatter consistency (required fields present, order values unique per section)
- Run a completeness check: every public API should appear in the reference, every concept should have a guide entry
- Produce a validation summary with pass/fail counts

### Markdown Guidelines

Use the full @pagesmith/core feature set when generating documentation:

- **GFM**: tables, strikethrough, task lists, autolinks, footnotes
- **GitHub alerts**: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`
- **Math**: `$inline$` and `$$display$$` where relevant (algorithms, formulas)
- **Expressive Code**: syntax highlighting with language tags, line numbers for long blocks, titles for named examples, `mark` / `ins` / `del` for highlighting changes, `collapse` for long outputs
- **Smart typography**: use standard quotes and dashes — the renderer handles curly quotes, em dashes, and ellipses automatically
- **Heading IDs**: use descriptive headings — anchors are auto-generated

### AI-First Documentation Principles

Documentation generated by this skill is written for both humans and AI agents:

- Use precise, unambiguous language — avoid "simply" and "just"
- Include complete code examples that can be copy-pasted without modification
- Structure with consistent heading hierarchy for programmatic navigation
- Use tables for parameter/option documentation — they parse cleanly
- Include type information in API docs — AI agents rely on it
- Cross-reference related sections with relative links

### Documentation Generated

Format: pagesmith | markdown
Pages created: <count>
Structure:

<tree listing>

### Validation
- API coverage: <n>/<total> public APIs documented
- Internal links: <n> verified, <n> broken
- Code examples: <n> verified against source

### Next Steps
- Review generated pages for accuracy
- Run `npx pagesmith dev` to preview (if pagesmith format)
- Use `/adk:docs-review` to get detailed feedback
```

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
/adk:docs-repo
/adk:docs-repo --init
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
/adk:docs-repo --scope package auth-service
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
/adk:docs-repo --format pagesmith
/adk:docs-repo --format markdown --verbosity detailed
```
