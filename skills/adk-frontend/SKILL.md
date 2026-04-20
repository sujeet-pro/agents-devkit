---
name: adk-frontend
description: Category router for frontend and UI work - UI/UX design, building or extending frontend components and pages, and bootstrapping React 19 client-side sample apps on a fixed Vite + TanStack + Radix + GitHub Pages stack. Use when the deliverable is a UI artifact, a frontend code change, or a new frontend project. Picks one of adk-frontend-design, adk-frontend-feature, adk-frontend-react-csr.
---

# ADK Frontend (Category Router)

Routes any "frontend / UI" intent to the right frontend task. Activate one of the listed task skills below; do not implement directly from this router.

## When to use this category

- Designing a UI surface (mockup, layout, interaction, component spec) before code.
- Implementing or extending a frontend component, page, route, or interaction.
- Bootstrapping a new React 19 client-side sample app on the locked ADK stack.

## When NOT to use this category

- Backend / non-UI code -> `adk-build`
- Pure visualization (single diagram, chart) -> `adk-visualize`
- Marketing copy / docs site content -> `adk-docs-write`
- Reviewing existing UI code -> `adk-review-local` / `adk-review-pr`

## Shared workflow

Every task in this category honors the same six steps. The task skills tailor the content of each step.

1. **Confirm intent** - identify the surface (page / component / app), the user goal, the design system in play, and the device targets.
2. **Gather** - read the existing component library, design tokens, routing layout, and accessibility constraints. Pull repo evidence first.
3. **Plan** - lay out the structure (component tree, state, data shape, routes, interactions). Approval gate unless `--auto`.
4. **Execute** - design (mockup + spec) or implement (typed React 19 components, accessible by default, responsive by default).
5. **Validate** - run repo-native checks: type-check, lint, unit tests, axe / a11y check, lighthouse / web-vitals if perf is in scope.
6. **Report** - changed files / mockup paths; validation evidence; remaining UX risk; offer depth on request.

## Task selection

| Task skill | Use when | Do NOT use when |
| --- | --- | --- |
| `adk-frontend-design` | Mockup, layout, interaction, or component spec is the deliverable - before code | Code is the deliverable - use feature |
| `adk-frontend-feature` | Implement or extend a frontend component, page, route, or interaction | A whole new app from scratch - use react-csr |
| `adk-frontend-react-csr` | Bootstrap a new React 19 + Vite/Rolldown + TanStack + Radix + GitHub Pages client-side app | Existing app - use feature |

## Stack defaults (when ADK chooses for you)

| Layer | Default |
| --- | --- |
| Bundler | Vite (with Rolldown when stable) |
| Framework | React 19 |
| Routing | TanStack Router (file-based) |
| Data | TanStack Query for async, Zustand for local app state |
| UI primitives | Radix UI |
| Styling | Tailwind v4 |
| Forms | React Hook Form + Zod |
| Tests | Vitest + React Testing Library + Playwright |
| Hosting | GitHub Pages (CSR) |

Override only when the project's existing code already uses something else; never mix stacks in one app.

## Accessibility / responsive defaults

- All interactive elements use Radix primitives or have explicit ARIA roles.
- All images and icons have alt text or `aria-hidden` when decorative.
- Focus states are visible.
- Layouts work at 360px, 768px, and 1280px widths by default.

## Activation

Once you have picked a task, load `adk-frontend-<task>` and follow it. Each task skill is fully standalone - everything it needs is in its own folder.

## Anti-patterns

- Implementing inside this router. Always hand off to a task skill.
- Mixing two design systems in one component tree.
- Ignoring keyboard / screen-reader accessibility because "we'll add it later".
- Hard-coding colors instead of using the design tokens.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |

<!-- adk:references:end -->
