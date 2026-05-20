---
title: 'guidelines/frontend-design'
description: '1. **Component boundary = data + behavior + appearance** for one purpose. Split when any of the three doesn''t fit.'
source: 'shared/guidelines/frontend-design.md'
group: 'shared-guidelines'
order: 6304
---
# shared/guidelines/frontend-design

> Source: `shared/guidelines/frontend-design.md`

# guideline: frontend design

> Loaded when the task touches `*.{tsx,jsx,vue,svelte,astro,html,css,scss}` or the user mentions UI / component / page / layout / design.

## Hard rules

1. **Component boundary = data + behavior + appearance** for one purpose. Split when any of the three doesn't fit.
2. **Server-rendered first** (SSR / RSC / static) unless interactivity is essential. Client JS is a cost paid by every visit.
3. **No new global state without naming the boundary**. Pages own routes; features own user-flow state; shared state needs justification.
4. **No prop drilling >2 levels**. Compose, context, or co-locate.
5. **Accessibility is non-optional**. Every interactive element has a name, role, and keyboard path. Hold to WCAG 2.2 AA; see `accessibility.md`.
6. **Performance budget is per-route**. JS ≤ 200KB gzipped initial route; LCP ≤ 2.5s on 4G; CLS < 0.1. Track regressions.
7. **Design tokens > magic numbers**. Pull from the design system or `tailwind.config`; never hex-code-in-jsx.

## Decision frames

- **Class component vs hooks**: hooks always (React 16.8+). Class only to extend legacy.
- **CSS-in-JS vs utility classes vs CSS modules**: match repo convention. If new repo: utility classes (Tailwind) for speed, CSS modules for componentized teams.
- **Form library**: native `<form>` + minimal validation lib for simple; `react-hook-form` for complex multi-step.
- **State manager**: TanStack Query for server state; Zustand / Jotai for client state; Redux only if the team already uses it.
- **Date / time**: dayjs / date-fns over Moment. Never roll your own.

## Anti-patterns

- `useEffect` to fetch data on mount. Use a query lib (TanStack Query / SWR).
- `useEffect` that watches multiple deps with conditional setState inside — usually means the derivation belongs above, not in effects.
- Wrapping every component in `React.memo`. Memo only the ones with measurable re-render cost.
- `dangerouslySetInnerHTML` on user content. Use a sanitizer if you must.
- Reaching into a child component's DOM via `ref` to mutate. Lift state instead.
- Building a custom modal / popover when the headless lib (Radix, Headless UI) exists.

## Cite when reviewing

- Repo's design system (Storybook URL if present in `package.json` or `~/.agents-devkit/config/overrides.yaml.repos[*].design_system_url`).
- Repo's existing component patterns (grep before suggesting "add a new component").
- `accessibility.md` for keyboard / contrast / aria.
- `performance.md` for budget violations.
