---
title: 'frontend'
description: 'Category router for frontend and UI work - UI/UX design, building or extending frontend components and pages, and bootstrapping React 19 client-side sample apps on a fixed Vite + TanStack + Radix + GitHub Pages stack.'
artifact_kind: skill
skill_name: frontend
category: frontend
---
# frontend

Category router for frontend and UI work - UI/UX design, building or extending frontend components and pages, and bootstrapping React 19 client-side sample apps on a fixed Vite + TanStack + Radix + GitHub Pages stack. Use when the deliverable is a UI artifact, a frontend code change, or a new frontend project. Picks one of adk-frontend-design, adk-frontend-feature, adk-frontend-react-csr.

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-frontend` form via `agents-skills/`.

```text
/adk:frontend            # interactive run (Claude Code)
/adk:frontend --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-frontend` (resolved through the
`agents-skills/adk-frontend/` symlink).

## Source

Direct from `skills/frontend/SKILL.md` — this page is auto-generated.

Routes any "frontend / UI" intent to the right frontend task. Activate one of the listed task skills below; do not implement directly from this router.

## When to use this category

- Designing a UI surface (mockup, layout, interaction, component spec) before code.
- Implementing or extending a frontend component, page, route, or interaction.
- Bootstrapping a new React 19 client-side sample app on the locked ADK stack.

## When NOT to use this category

- Backend / non-UI code -> `@adk:build` (a.k.a. `adk-build`)
- Pure visualization (single diagram, chart) -> `@adk:visualize` (a.k.a. `adk-visualize`)
- Marketing copy / docs site content -> `@adk:docs-write` (a.k.a. `adk-docs-write`)
- Reviewing existing UI code -> `@adk:review-local` (a.k.a. `adk-review-local`) / `@adk:review-pr` (a.k.a. `adk-review-pr`)

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
| `@adk:frontend-design` (a.k.a. `adk-frontend-design`) | Mockup, layout, interaction, or component spec is the deliverable - before code | Code is the deliverable - use feature |
| `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`) | Implement or extend a frontend component, page, route, or interaction | A whole new app from scratch - use react-csr |
| `@adk:frontend-react-csr` (a.k.a. `adk-frontend-react-csr`) | Bootstrap a new React 19 + Vite/Rolldown + TanStack + Radix + GitHub Pages client-side app | Existing app - use feature |

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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-clarifying-questions.md`) and reports the choices.

1. **Is the work UI/UX design (decisions, mocks, copy) or implementation (code)?** — _How to pick:_ Design → adk-frontend-design. Implementation → frontend-feature or frontend-react-csr.
2. **If implementation: is the project on the locked React 19 + Vite + TanStack stack, or another stack?** — _How to pick:_ Locked stack → adk-frontend-react-csr. Other → adk-frontend-feature.

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `frontend-routing-decision` — Inline message.

**Artifact path:** (none)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-clarifying-questions.md`) and reports the choices.

1. **Is the work UI/UX design (decisions, mocks, copy) or implementation (code)?** — _How to pick:_ Design → adk-frontend-design. Implementation → frontend-feature or frontend-react-csr.
2. **If implementation: is the project on the locked React 19 + Vite + TanStack stack, or another stack?** — _How to pick:_ Locked stack → adk-frontend-react-csr. Other → adk-frontend-feature.

## Default vs detailed output

**Default report:** Routed task + why.

**Detailed report (on request or `--verbose`):** (n/a — small router)

**Artifact:** `frontend-routing-decision` — Inline message.

**Artifact path:** (none)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/frontend-anti-patterns.md` | Things to avoid when running this skill. |
| `references/frontend-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/frontend-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/frontend-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/frontend-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/frontend-persona.md` | The agent persona that drives this skill. |
| `references/frontend-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->


## Related skills

- [`build`](./skill-build.md) — `@adk:build` (a.k.a. `adk-build`)
- [`docs-write`](./skill-docs-write.md) — `@adk:docs-write` (a.k.a. `adk-docs-write`)
- [`frontend-design`](./skill-frontend-design.md) — `@adk:frontend-design` (a.k.a. `adk-frontend-design`)
- [`frontend-feature`](./skill-frontend-feature.md) — `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`)
- [`frontend-react-csr`](./skill-frontend-react-csr.md) — `@adk:frontend-react-csr` (a.k.a. `adk-frontend-react-csr`)
- [`review-local`](./skill-review-local.md) — `@adk:review-local` (a.k.a. `adk-review-local`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
- [`visualize`](./skill-visualize.md) — `@adk:visualize` (a.k.a. `adk-visualize`)
