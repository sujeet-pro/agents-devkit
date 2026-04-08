---
title: "design"
description: Frontend UI/UX design with bold variations, visual previews, and iterative refinement
skill_name: design
category: task
workflow_tier: full
user_invocable: true
---

# design

Unified design skill that creates distinctive, production-grade frontend interfaces. Generates 5 bold design variations as visual HTML previews, iterates on feedback in a loop, and converts the chosen direction to the target framework. Also handles auditing existing UI via `--action audit` (delegates to `/adk:code-review-pr --focus ui`).

## When to Use

- Design a new frontend component, page, or layout from scratch
- Generate multiple bold aesthetic directions for comparison
- Iterate on visual design with live HTML previews
- Convert finalized designs to a target framework (React, Next.js, Vue, etc.)
- Audit existing frontend UI for visual/UX issues
- Explore different typography, color palette, and layout strategies
- Build production-ready, accessible UI components

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `<task>` | design brief or description | (required) | What to design — component, page, or layout description |
| `--focus` | `ui`, `ux`, `visual`, `accessibility` | auto-detect | Focus area for the design task |
| `--framework` | `react`, `nextjs`, `vue`, `vanilla`, etc. | `vanilla` | Target framework for final deliverable (previews always use pure HTML/CSS) |
| `--style` | `tailwind`, `css-modules`, `styled-components`, etc. | `css` | Target styling approach for final deliverable |
| `--theme` | `<theme-name>` | none | Theme or aesthetic direction hint (e.g., "dark luxe", "brutalist") |
| `--action` | `design`, `audit` | auto-detect | Whether to create new designs or audit existing UI |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--auto` | flag | off | Skip all confirmations and approval gates |
| `--help` | flag | — | Show parameter reference and exit |

## Behavior Variations

| Context | Behavior |
|---------|----------|
| **Default** (`--action design`) | Full 6-phase workflow. Generates 5 bold design variations as an HTML preview, iterates on feedback, then converts to the target framework |
| **Audit** (`--action audit`) | Routes to `/adk:code-review-pr --focus ui` for 6-pillar review (layout, typography, color, responsiveness, accessibility, interaction states) |
| **Framework specified** (`--framework react`) | Preview rounds still use pure HTML/CSS; final deliverable is converted to the target framework |
| **Theme hint** (`--theme "dark luxe"`) | Influences the aesthetic direction of generated variations while maintaining diversity |
| `--verbosity short` | Status line only (e.g., "5 variations generated, preview opened") |
| `--verbosity detailed` | Full design rationale, accessibility audit results, and all child agent outputs |

## Priorities

Design variations are evaluated across five quality dimensions:

1. **Typography** — distinctive, characterful font pairings (display + body); never generic fonts (Inter, Roboto, Arial, system-ui as display)
2. **Color & Theme** — cohesive palette defined in CSS variables; bold, intentional choices; dominant color with sharp accents
3. **Motion** — high-impact moments (staggered page load, scroll-triggered reveals, surprising hover states) over scattered micro-interactions
4. **Spatial Composition** — unexpected layouts; asymmetry, overlap, diagonal flow, grid-breaking elements; generous negative space or controlled density
5. **Backgrounds & Visual Details** — atmosphere and depth through gradient meshes, noise textures, geometric patterns, layered transparencies, decorative borders

## Key Behaviors

- **5 parallel child agents**: each commits to a different bold aesthetic direction (brutally minimal, maximalist, retro-futuristic, organic, luxury, etc.) — no two variations share the same aesthetic family
- **Pure HTML/CSS previews**: all preview rounds use self-contained HTML/CSS/vanilla JS with no build tools, regardless of target framework
- **Live browser preview**: assembles a single `.design-preview/preview.html` file with navigation between variations and opens it in the browser
- **Iterative feedback loop**: keeps iterating until the user explicitly picks a direction — supports mixing elements, tweaking, or requesting replacement variations
- **Framework conversion**: on finalize, converts the chosen HTML variation to the target `--framework` and `--style` with interactive states, WCAG 2.1 AA accessibility, and reusable tokens
- **Audit routing**: `--action audit` delegates to `/adk:code-review-pr --focus ui` for existing UI review

## Workflow

Follows the 6-phase workflow for design creation. Audit mode routes externally.

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm goal, constraints, target framework, and success criteria |
| 1. Research & Options | yes | Analyze design requirements, scan existing patterns |
| 2. Approach Selection | yes | Present 2-3 approaches, user picks or mixes |
| 3. Planning | yes | Break into tasks/waves for parallel child agents |
| 4. Execute | yes | Generate 5 variations, build preview, iterate on feedback, finalize to framework |
| 5. Validate & Learn | yes | Review design against requirements and accessibility standards |

## Design Workflow

| Phase | Activity | Output |
|-------|----------|--------|
| Context & Design Thinking | Understand brief, purpose, constraints, differentiation | Design brief document |
| Generate 5 Variations | 5 parallel child agents, each a distinct aesthetic | 5 self-contained HTML/CSS snippets |
| Build & Open Preview | Assemble single HTML file with variation switcher | `.design-preview/preview.html` opened in browser |
| Iterate | Apply feedback, re-open preview, repeat until user confirms | Updated preview file |
| Finalize to Framework | Convert chosen variation to target framework with full states | Production-ready component files |

## Shared Skills

| Skill | Load When | Fallback |
|-------|-----------|----------|
| `workflow` | always | 6-phase: intent → research → approach → plan → execute → validate |
| `communication` | always | Lead with conclusion, bullet points, no preamble |
| `preflight-check` | before work | Run preflight.py, detect source, validate MCP |
| `output-format` | producing output | short/standard/detailed verbosity; priority labels |
| `principal-engineer` | complexity >= medium | Five PE questions: need? simplest? alternatives? maintenance? clarity? |
| `agentic-teams` | parallel work needed | Launch child agents with distinct roles |
| `interaction` | NOT --auto | Inline protocols for confirmations and approvals |

## Output Format

All output is markdown in the chat, plus a visual HTML preview opened in the browser.

- **Phase 2-4**: `.design-preview/preview.html` with variation navigation, comparison strip, and per-variation design rationale
- **Phase 5**: production-ready code in the target framework with integration notes (font installation, required dependencies, responsive breakpoints)
- **Comparison table** in chat showing aesthetic, palette, typography, and signature detail per variation

## Adjacent Skills

| Skill | When to use instead |
|-------|-------------------|
| `/adk:code-review-pr --focus ui` | Audit existing frontend code for visual/UX issues (6-pillar review) |
| `/adk:dev-build` | Implement the finalized design as working code |
| `/adk:docs-write` | Document design decisions and component usage |

## Examples

```
/adk:design a landing page for a developer tools SaaS product
/adk:design --framework react --style tailwind a settings dashboard
/adk:design --theme "dark luxe" a pricing page with toggle
/adk:design --focus accessibility audit the signup flow
/adk:design --action audit review the main navigation component
```
