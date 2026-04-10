---
title: 'workspace-conventions'
description: 'Workspace file conventions — temp files, diagram output, artifact locations, and .gitignore management'
skill_name: workspace-conventions
category: guideline
workflow_tier: helper
user_invocable: false
---

# workspace-conventions

`workspace-conventions` is a shared helper that keeps cross-cutting rules and expectations consistent across the skills that invoke it. Most users meet it indirectly when another skill loads it to resolve a shared rule set or a reusable contract.

## Overview

`workspace-conventions` belongs to the `guideline` layer and is declared at the `helper` tier. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The key design trade-off is indirection. This skill rarely owns an interactive workflow on its own, but it keeps cross-cutting behavior consistent so task skills do not each reinvent the same policy, formatting rule, or detection logic.

## Parameters

This helper does not expose a broad user-facing parameter surface beyond the narrow controls in `SKILL.md`. In practice, task skills load it indirectly and supply the context it needs.

## Output

Helper skills usually return a rule set, a resolved reference list, or a normalized contract back to the calling skill rather than a standalone report.


## Additional Reference

### Core Rule

**All generated artifacts live inside the project workspace.** Agents never write files outside the repo root unless explicitly instructed by the user.

---

### Temporary Files

Intermediate artifacts (plans, drafts, research notes, intent files, proposals) go in `.temp/` at the project root. Each skill or task creates its own subfolder using a task slug.

```
<project-root>/
└── .temp/
    ├── review-auth-module/
    │   ├── intent.json
    │   ├── plan.md
    │   └── findings.md
    ├── diagram-system-arch/
    │   └── draft.excalidraw
    └── docs-write-adr-caching/
        ├── outline.md
        └── draft.md
```

### .gitignore Management

Before creating the `.temp/` directory for the first time in a project:

1. Check if `.gitignore` exists at the project root
2. If it exists, check if `.temp/` is already listed
3. If not listed, append `.temp/` to `.gitignore`
4. If `.gitignore` does not exist, create it with `.temp/` as the first entry

```bash
# Check and add .temp/ to .gitignore
if [ ! -f .gitignore ]; then
  echo '.temp/' > .gitignore
elif ! grep -qx '.temp/' .gitignore 2>/dev/null; then
  echo '.temp/' >> .gitignore
fi
mkdir -p .temp
```

### Task Slug Convention

The subfolder name follows: `<skill-short-name>-<kebab-case-topic>`

| Skill | Example Slug |
|-------|-------------|
| code-review-pr | `review-pr-42` |
| docs-write | `docs-write-adr-caching` |
| diagram-mermaid | `diagram-auth-flow` |
| plan | `plan-api-redesign` |
| dev-build | `dev-auth-middleware` |

---

### Diagram Output Location

Diagrams (source files and rendered images) follow these rules in priority order:

### 1. Project diagramkit Configuration

If a `diagramkit.config.json` exists at the project root, **obey its `outputDir` setting** for rendered output. Use the project's local `diagramkit` (`npx diagramkit`) rather than a global install.

```json
{
  "outputDir": "docs/assets/diagrams",
  "defaultFormat": "svg",
  "defaultTheme": "both",
  "scale": 2
}
```

When this file is present:
- Source files go to the directory specified in the config (or alongside rendered output)
- Rendered output goes to `outputDir`
- Use `defaultFormat` and `defaultTheme` as defaults unless overridden by the user

### 2. Doc-Sibling Diagrams

When a diagram is created as part of documentation (invoked by `/adk:docs-write`, `/adk:docs-repo`, `/adk:docs-crud`, or any doc skill), place both source and rendered files in a `diagrams/` folder **sibling to the document**:

```
docs/
├── architecture/
│   ├── README.md              ← the document
│   └── diagrams/              ← sibling diagrams/ folder
│       ├── system-overview.mermaid
│       ├── system-overview-light.svg
│       ├── system-overview-dark.svg
│       ├── system-overview-light.png
│       └── system-overview-dark.png
```

### 3. Default: Project `diagrams/` Folder

For standalone diagram creation (not part of a doc), place outputs in a `diagrams/` folder at the project root:

```
<project-root>/
└── diagrams/
    ├── dependency-graph.dot
    ├── dependency-graph-light.svg
    ├── dependency-graph-dark.svg
    ├── dependency-graph-light.png
    └── dependency-graph-dark.png
```

---

### Diagram Rendering Conventions

All diagram skills must produce **two theme variants** by default:

| Variant | Suffix | Background |
|---------|--------|------------|
| Light | `-light` | White or transparent for light surfaces |
| Dark | `-dark` | Dark surface with adjusted colors |

All diagram skills must produce **both vector and raster** output:

| Format | Extension | Use Case |
|--------|-----------|----------|
| SVG | `.svg` | Web embedding, READMEs, documentation (scales cleanly) |
| PNG | `.png` | PDFs, slides, platforms that mishandle SVG |

Default output for a diagram named `system-overview`:
- `system-overview-light.svg`
- `system-overview-dark.svg`
- `system-overview-light.png`
- `system-overview-dark.png`

### File Naming

- **Source files**: `<kebab-case-name>.<engine-ext>` (e.g., `auth-flow.mermaid`, `deps.dot`)
- **Rendered files**: `<name>-<theme>.<format>` (e.g., `auth-flow-light.svg`, `auth-flow-dark.png`)
- Use **kebab-case** for all diagram file names

### Source File Extensions

| Engine | Primary Extension | Alternatives |
|--------|-------------------|-------------|
| Mermaid | `.mermaid` | `.mmd`, `.mmdc` |
| Excalidraw | `.excalidraw` | — |
| Draw.io | `.drawio` | `.drawio.xml`, `.dio` |
| Graphviz | `.dot` | `.gv` |

**Always commit the source file alongside rendered images** so diagrams remain editable.

---

### Rendering Pipeline

Every diagram skill follows this pipeline after generating the source file:

### Step 1: Check for Project diagramkit Config

```bash
if [ -f diagramkit.config.json ]; then
  # Use project-local diagramkit — it reads config automatically
  npx diagramkit render <source-file>
fi
```

### Step 2: Render with diagramkit (Primary)

```bash
# SVG — both themes
diagramkit render <source-file> --format svg --theme both

# PNG — both themes, 2x scale for retina
diagramkit render <source-file> --format png --theme both --scale 2
```

### Step 3: Fallback to Engine CLI

If diagramkit is not installed or rendering fails, use the engine's native CLI. See each diagram skill for engine-specific fallback commands.

### Step 4: Verify Outputs

Confirm that all expected output files exist:
- `<name>-light.svg` and `<name>-dark.svg`
- `<name>-light.png` and `<name>-dark.png`

---

### Other Generated Artifacts

| Artifact Type | Location |
|---------------|----------|
| Plans, drafts, research | `.temp/<task-slug>/` |
| Diagrams (standalone) | `diagrams/` at project root |
| Diagrams (for docs) | `diagrams/` sibling to the document |
| Generated documentation | Where the doc skill specifies (usually `docs/`) |
| Test reports | `.temp/<task-slug>/` |
| Handoff context | `.temp/handoff/` |

---

### Summary for Inline Fallback

> All work inside the project repo. Temp files in `.temp/<task-slug>/` (gitignored). Diagrams in `diagrams/` (sibling to doc, or project root). Both light+dark SVG and PNG. Respect `diagramkit.config.json` when present. Always commit source files with rendered output.

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.
