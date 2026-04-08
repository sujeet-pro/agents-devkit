---
title: "docs-repo"
description: Generate comprehensive repository documentation using pagesmith
skill_name: docs-repo
category: task
workflow_tier: full
user_invocable: true
---

# docs-repo

Generate comprehensive, AI-first documentation for a repository using @pagesmith/docs conventions. Produces a complete `docs/` directory tree covering architecture, API reference, guides, and configuration — written for both humans and AI agents.

## When to Use

- Generate documentation for an entire repository from scratch
- Scaffold a complete docs site with pagesmith or plain markdown
- Document a specific package in a monorepo
- Initialize @pagesmith/docs and generate content in one pass

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--scope` | `full` \| `package <name>` | `full` | Generate docs for the entire repo or a specific package/module |
| `--format` | `pagesmith` \| `markdown` | auto-detect | Output format. Auto-detects from `pagesmith.config.json5` presence |
| `--init` | flag | off | Run `npx pagesmith init` to set up @pagesmith/docs before generating |
| `--verbosity` | `short` \| `standard` \| `detailed` | `standard` | Output detail level |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Auto-detect (default)** | Checks for `pagesmith.config.json5`. If found, uses pagesmith format with frontmatter and folder/README.md conventions. If absent, generates plain markdown |
| **`--init`** | Runs `npx pagesmith init` to scaffold @pagesmith/docs, then generates docs using pagesmith format |
| **`--scope package <name>`** | Limits documentation to a single package in a monorepo. Generates a focused doc tree for that package only |
| **`--format pagesmith`** | Forces pagesmith conventions: folder/README.md structure, YAML frontmatter, meta.json5 files |
| **`--format markdown`** | Forces plain markdown: no frontmatter, no meta.json5, flat file structure |

## Key Behaviors

- **Format auto-detection**: detects pagesmith from `pagesmith.config.json5` presence and adapts output conventions
- **Parallel generation**: launches child agents in waves — reference pages first (factual), then guides (narrative), then home page and metadata
- **AI-first writing**: uses precise language, complete code examples, consistent heading hierarchy, and parameter tables
- **Cross-reference validation**: verifies all internal links resolve and code examples match actual source
- **Three structure options**: presents Minimal, Standard, and Comprehensive doc structures with trade-offs

## Doc Structure

### Pagesmith Format

```
docs/
├── README.md                    # Home page (hero layout)
├── guide/
│   ├── meta.json5               # Section: order 1
│   ├── README.md                # Getting Started
│   ├── concepts/
│   │   └── README.md            # Core Concepts
│   └── configuration/
│       └── README.md            # Configuration Guide
└── reference/
    ├── meta.json5               # Section: order 2
    ├── README.md                # Reference Overview
    ├── api/
    │   └── README.md            # API Reference
    ├── cli/
    │   └── README.md            # CLI Reference
    └── config/
        └── README.md            # Config Reference
```

### Markdown Format

```
docs/
├── README.md
├── getting-started.md
├── concepts.md
├── configuration.md
├── api-reference.md
├── cli-reference.md
└── config-reference.md
```

## Workflow

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm scope, format, target audience, and what sections to generate |
| 1. Research & Options | yes | Analyze codebase: architecture, public APIs, CLI commands, config schema |
| 2. Approach Selection | yes | Present 2-3 doc structure options (Minimal, Standard, Comprehensive) |
| 3. Planning | yes | Define section plan, assign child agents, set generation order |
| 4. Execute | yes | Generate all doc pages using parallel child agents in waves |
| 5. Validate & Learn | yes | Cross-reference docs with code, check internal links, verify examples |

### Generation Waves

**Wave 1 — Reference pages** (factual, code-derived): API documenter, CLI documenter, Config documenter

**Wave 2 — Guide pages** (narrative, cross-referencing): Getting-started writer, Concepts writer, Configuration writer

**Wave 3 — Home page and metadata**: Home page writer, Metadata generator (meta.json5 and frontmatter)

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py for MCP validation |
| `output-format` | producing output | short/standard/detailed verbosity |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents: source analyst, outline editor, fact checker, code/diagram specialist, publisher |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

The primary output is a complete `docs/` directory tree. After generation, prints a summary:

```
## Documentation Generated

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

## Adjacent Skills

| Skill | When to use instead |
|-------|---------------------|
| `/adk:docs-review` | Review existing documentation for quality |
| `/adk:docs-crud` | Manage individual doc pages (create, update, improve) |
| `/adk:docs-write` | Write formal documents (ADRs, RFCs, specs) |
| `/adk:diagram` | Generate architecture and flow diagrams for docs |

## Examples

```
/adk:docs-repo
/adk:docs-repo --init
/adk:docs-repo --scope package auth-service
/adk:docs-repo --format pagesmith
/adk:docs-repo --format markdown --verbosity detailed
```
