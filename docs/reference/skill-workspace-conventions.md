---
title: "workspace-conventions"
description: "Workspace file conventions for temp files, diagram output, artifact locations, and .gitignore management"
skill_name: workspace-conventions
category: guideline
workflow_tier: helper
user_invocable: false
---

# workspace-conventions

Standard conventions for where agents create files, diagrams, images, charts, and temporary artifacts. All work happens within the user's project repository — never in the home directory or outside the workspace.

## Purpose

- Define consistent output paths for all generated artifacts (temp files, diagrams, docs, reports)
- Ensure `.temp/` directories are gitignored automatically
- Standardize diagram rendering conventions (dual theme, dual format)
- Establish file naming conventions for source files and rendered output

## Key Behaviors

### Core Rule

All generated artifacts live inside the project workspace. Agents never write files outside the repo root unless explicitly instructed by the user.

### Temporary Files

Intermediate artifacts (plans, drafts, research notes, intent files, proposals) go in `.temp/` at the project root. Each skill or task creates its own subfolder using a task slug.

```
<project-root>/
└── .temp/
    ├── review-auth-module/
    │   ├── intent.json
    │   ├── plan.md
    │   └── findings.md
    └── docs-write-adr-caching/
        ├── outline.md
        └── draft.md
```

**Task slug convention**: `<skill-short-name>-<kebab-case-topic>` (e.g., `review-pr-42`, `docs-write-adr-caching`, `diagram-auth-flow`, `dev-auth-middleware`).

### .gitignore Management

Before creating `.temp/` for the first time in a project:

1. Check if `.gitignore` exists at the project root
2. If it exists, check if `.temp/` is already listed
3. If not listed, append `.temp/` to `.gitignore`
4. If `.gitignore` does not exist, create it with `.temp/` as the first entry

### Diagram Output Location (Priority Order)

1. **Project diagramkit config**: if `diagramkit.config.json` exists, obey its `outputDir` for rendered output. Use project-local `npx diagramkit` rather than global install.
2. **Doc-sibling diagrams**: when a diagram is part of documentation, place source and rendered files in a `diagrams/` folder sibling to the document.
3. **Default**: standalone diagrams go in `diagrams/` at the project root.

### Diagram Rendering Conventions

All diagram skills produce **two theme variants** by default:

| Variant | Suffix | Background |
|---------|--------|------------|
| Light | `-light` | White or transparent for light surfaces |
| Dark | `-dark` | Dark surface with adjusted colors |

All diagram skills produce **both vector and raster** output:

| Format | Extension | Use Case |
|--------|-----------|----------|
| SVG | `.svg` | Web embedding, READMEs, documentation |
| PNG | `.png` | PDFs, slides, platforms that mishandle SVG |

Default output for a diagram named `system-overview`: `system-overview-light.svg`, `system-overview-dark.svg`, `system-overview-light.png`, `system-overview-dark.png`.

### File Naming Conventions

- **Source files**: `<kebab-case-name>.<engine-ext>` (e.g., `auth-flow.mermaid`, `deps.dot`)
- **Rendered files**: `<name>-<theme>.<format>` (e.g., `auth-flow-light.svg`, `auth-flow-dark.png`)
- Use kebab-case for all diagram file names
- Always commit source files alongside rendered images

**Source file extensions**:

| Engine | Primary Extension | Alternatives |
|--------|-------------------|-------------|
| Mermaid | `.mermaid` | `.mmd`, `.mmdc` |
| Excalidraw | `.excalidraw` | — |
| Draw.io | `.drawio` | `.drawio.xml`, `.dio` |
| Graphviz | `.dot` | `.gv` |

### Rendering Pipeline

1. Check for project `diagramkit.config.json` — use project-local diagramkit if present
2. Render with diagramkit: SVG (both themes) + PNG (both themes, 2x scale)
3. Fallback to engine's native CLI if diagramkit unavailable
4. Verify all expected output files exist

### Artifact Location Summary

| Artifact Type | Location |
|---------------|----------|
| Plans, drafts, research | `.temp/<task-slug>/` |
| Diagrams (standalone) | `diagrams/` at project root |
| Diagrams (for docs) | `diagrams/` sibling to the document |
| Generated documentation | Where the doc skill specifies (usually `docs/`) |
| Test reports | `.temp/<task-slug>/` |
| Handoff context | `.temp/handoff/` |

## What It Provides

- Output path resolution logic for all artifact types
- Automatic `.gitignore` management for `.temp/`
- Diagram rendering conventions (dual theme, dual format)
- File naming standards for source and rendered files
- Rendering pipeline with diagramkit primary and engine-native fallback
- Inline fallback summary for skills that embed conventions directly

## Invoked By

| Skill | Load Condition |
|-------|---------------|
| `diagram-mermaid` | always (diagram output paths and rendering conventions) |
| `diagram-excalidraw` | always |
| `diagram-drawio` | always |
| `diagram-graphviz` | always |
| `docs-write` | always (temp files and doc-sibling diagram paths) |
| `docs-repo` | always |
| `docs-crud` | always |
| `plan` | always (temp file paths) |
| `spec` | always |
| `research` | always |
| `handoff` | always (handoff context paths) |
| `chart` | always (diagram output conventions apply to charts) |
