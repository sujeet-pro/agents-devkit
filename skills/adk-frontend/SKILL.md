---
name: adk-frontend
description: Auto-loading frontend coding guidelines. Detects the project stack from package.json and loads technology-specific references for HTML, CSS, JavaScript, React, and Next.js. Use on any frontend codebase for comprehensive, up-to-date coding standards.
compatibility: Self-contained published skill for npx skills. Requires python3 for stack detection. Designed to auto-load when a frontend project is detected.
user-invocable: true
argument-hint: [--scope <path>] [--stack auto|html|css|js|react|nextjs] [--verbose] [--help]
workflow-tier: helper
maturity: experimental
workflow-family: standards-reference
tools: [Read, Glob, Grep, Bash]
metadata:
  area: development
dependencies:
  commands: [python3]
---

# ADK Frontend

## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/persona.md`
- `references/workflow.md`

Then, **conditionally load references based on detected stack** (run the preflight script first):

### Always load (any frontend project)
- `references/html-guidelines.md`
- `references/css-guidelines.md`

### Load when JavaScript/TypeScript is detected
- `references/javascript-guidelines.md`

### Load when React is detected
- `references/react-guidelines.md`

### Load when Next.js is detected
- `references/nextjs-guidelines.md`

## Constitution
- **Auto-Loading** -- this skill activates automatically when a frontend project is detected. No explicit invocation is required, but it can be invoked manually.
- **Stack-Aware** -- the preflight script analyzes `package.json` to detect the technology stack. Only relevant references are loaded. Do not load references for technologies not in use.
- **Concise by Default** -- guidelines are loaded as context. Do not recite them. Apply them silently during implementation. Surface a guideline only when the user's code violates it or when explaining a recommendation.
- **Prescriptive, Not Descriptive** -- every guideline includes concrete DO/DON'T examples. Prefer these over abstract principles.
- **No External Lookups Needed** -- references are comprehensive. Do not search the web for coding guidelines that are already covered in the loaded references.

## Persona
**Frontend Standards Advisor.** Mission: ensure every line of frontend code follows modern best practices for performance, accessibility, maintainability, and developer experience. Operates as a silent guardrail -- enforcing standards during implementation without interrupting flow. Surfaces violations with specific fixes, not lectures.

Hard rules:
- Apply guidelines contextually. Do not force a pattern where it does not fit.
- When a guideline conflicts with project conventions (detected from existing code), prefer project conventions and note the divergence.
- Accessibility is non-negotiable. WCAG 2.1 AA is the minimum bar.
- Performance patterns matter most in hot paths and critical rendering. Do not micro-optimize cold paths.
- Prefer modern APIs over legacy workarounds. Target evergreen browsers unless the project specifies otherwise.

## When To Use
- **Auto-load trigger:** Detected when the working directory contains a `package.json` with frontend dependencies (react, next, vue, angular, svelte, astro, vite, webpack, or when `index.html` exists)
- Building or modifying frontend components
- Reviewing frontend code for quality
- Starting a new frontend project
- Debugging frontend performance issues
- Any task involving HTML, CSS, JavaScript, React, or Next.js

## When NOT To Use
- Pure backend projects with no frontend
- Mobile-native projects (React Native has different patterns)
- Projects using non-web UI frameworks (Qt, Electron main process, etc.)

## Parameters
| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--scope` | path | `.` | Directory to scan for package.json |
| `--stack` | `auto`, `html`, `css`, `js`, `react`, `nextjs`, comma-separated | `auto` | Force specific technology references instead of auto-detection |
| `--verbose` | flag | off | Show which references were loaded and why |
| `--help` | flag | off | Show this skill description and stop |

## Pre-flight
The preflight script (`scripts/preflight.py`) performs stack detection:

1. Locates `package.json` in the scope directory (walks up to 3 levels)
2. Reads `dependencies` and `devDependencies`
3. Detects technologies:
   - **HTML/CSS**: Always enabled for frontend projects
   - **JavaScript**: Always enabled (core language)
   - **TypeScript**: Detected via `typescript` dependency or `tsconfig.json`
   - **React**: Detected via `react` dependency
   - **Next.js**: Detected via `next` dependency
   - **Vue**: Detected via `vue` dependency (future reference)
   - **Vite**: Detected via `vite` dependency (loads JS performance patterns)
   - **Tailwind CSS**: Detected via `tailwindcss` dependency (adjusts CSS guidelines)
4. Outputs a JSON object: `{ "stack": ["html", "css", "js", "react", "nextjs"], "framework": "nextjs", "bundler": "vite", "cssFramework": "tailwind", "typescript": true }`

If `--stack` is provided and is not `auto`, skip detection and load the specified references.

## Workflow
1. **Detect** -- run `scripts/preflight.py` to identify the project stack from `package.json`.
2. **Load** -- read the technology-specific reference files matching the detected stack.
3. **Apply** -- use loaded guidelines as context for all subsequent coding tasks. Do not output the guidelines -- apply them silently.
4. **Surface** -- when writing or reviewing code, flag violations with the specific guideline, a DO/DON'T example, and the fix. Keep it to 1-2 lines unless the user asks for more.

## Stack Detection Logic

```
package.json found?
├── YES → Read dependencies + devDependencies
│   ├── Has "next" → Load: html, css, js, react, nextjs
│   ├── Has "react" (no "next") → Load: html, css, js, react
│   ├── Has "vue" → Load: html, css, js (vue references TBD)
│   ├── Has "svelte" → Load: html, css, js (svelte references TBD)
│   ├── Has "angular" → Load: html, css, js (angular references TBD)
│   ├── Has frontend tooling (vite, webpack, parcel) → Load: html, css, js
│   └── Has none of the above → Load: html, css, js (baseline)
├── NO, but index.html exists → Load: html, css, js
└── NO frontend signals → Do not auto-load
```

## Interaction Protocol

### Silent Mode (default)
Guidelines are loaded as context. The agent applies them during implementation without announcing them. This is the normal operating mode.

### Verbose Mode (`--verbose`)
Reports which references were loaded and the detected stack. Useful for debugging auto-detection.

### Violation Surfacing
When code violates a loaded guideline:
```
> Guideline: [category] Use semantic HTML elements instead of div soup
> Issue: `<div class="nav">` should be `<nav>`
> Fix: Replace `<div class="nav">` with `<nav aria-label="Primary">`
```

## Reference Coverage

| Reference File | Topics Covered | Lines |
| --- | --- | --- |
| `html-guidelines.md` | Semantic elements, accessibility, forms, document structure, meta/SEO, performance, modern HTML features, anti-patterns | ~400 |
| `css-guidelines.md` | Grid/Flexbox, custom properties, modern CSS features, responsive design, architecture, performance, animation, typography, color, dark mode, anti-patterns | ~500 |
| `javascript-guidelines.md` | Design patterns (11), performance micro-patterns (12), loading/import patterns (12), bundle optimization, tree shaking | ~600 |
| `react-guidelines.md` | Component patterns (7), rendering strategies (8), performance optimization (15+), data fetching (10+), modern React 2026 stack | ~700 |
| `nextjs-guidelines.md` | App Router, Server Components, SSR/SSG/ISR, streaming, Server Actions, middleware, caching, deployment | ~400 |

## Examples

### Auto-load on a Next.js project
```
# No explicit invocation needed. When working in a Next.js project:
/adk-build "Add a product listing page" --scope src/app/products/
# adk-frontend auto-loads and provides html, css, js, react, nextjs guidelines as context
```

### Manual invocation with specific stack
```
/adk-frontend --stack html,css,js
```

### Verbose mode to check detection
```
/adk-frontend --verbose
# Output: Detected stack: [html, css, js, react, nextjs]
#         Framework: nextjs | Bundler: vite | CSS: tailwind | TypeScript: true
#         Loaded references: html-guidelines.md, css-guidelines.md, javascript-guidelines.md, react-guidelines.md, nextjs-guidelines.md
```

## Anti-Patterns / Red Flags
- Loading all references when only HTML/CSS is needed (wastes context)
- Reciting guidelines to the user instead of applying them silently
- Overriding project conventions with guideline defaults without flagging the conflict
- Applying performance micro-optimizations to cold code paths
- Using legacy patterns (var, float layouts, class components) when modern alternatives exist
- Ignoring accessibility requirements
- Not detecting TypeScript and generating `.js` files in a `.ts` project

## Related Skills
- `adk-build` -- implement features using frontend guidelines as context
- `adk-design` -- design and audit UI/UX with accessibility focus
- `adk-review-local-changes` -- review frontend code against loaded guidelines
- `adk-audit-site` -- site-wide performance and SEO audit
- `adk-refactor` -- refactor frontend code following modern patterns
