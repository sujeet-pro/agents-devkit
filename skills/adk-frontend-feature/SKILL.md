---
name: adk-frontend-feature
description: Implement or extend a frontend component, page, route, or interaction in an existing app - typed React 19 with accessibility-first defaults, responsive layout at 360/768/1280, all interactive states (default/hover/focus/active/disabled/loading/empty/error), and repo-native validation (typecheck, lint, unit tests, axe). Use when the deliverable is frontend code in an existing app. Do not use to design from scratch (use adk-frontend-design first), to bootstrap a new app (use adk-frontend-react-csr), or for backend work (use adk-build-feature).
---

# ADK Frontend / Feature

Standalone task skill under the `adk-frontend` category router. Builds or extends a frontend feature with typed code, accessibility defaults, responsive layout, and repo-native validation.

## When to use

- Add a new page, route, component, or interaction to an existing frontend app.
- Extend an existing component (new prop, new state, new variant) without redesigning it.
- Fix a frontend bug with a regression-test slice.
- Adopt a design produced by `adk-frontend-design`.

## When NOT to use

- Design first; no code yet -> `adk-frontend-design`
- Bootstrap a brand-new React 19 + CSR sample app -> `adk-frontend-react-csr`
- Backend / non-UI feature -> `adk-build-feature`
- Restructure with no behavior change -> `adk-build-refactor`
- Frontend deps upgrade only -> `adk-build-deps`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task>` | yes | What to build / extend / fix |
| `<scope>` | optional | Path to limit reads and changes |
| `<design>` | optional | Path to design markdown (from `adk-frontend-design`) |
| `<viewports>` | optional | Default `360, 768, 1280` |
| `--auto` | optional | Skip approval gates (still validates) |

## Workflow

1. **Confirm intent** - restate task, scope, design ref, viewports, success criteria. Approval gate unless `--auto`.
2. **Discover stack** - read `package.json`, framework, router, state library, styling, test framework, lint/typecheck commands. Match what is already there.
3. **Read context** - read the existing component library, design tokens, accessibility helpers, route layout, and tests near the change. Repo evidence over guessing.
4. **Plan** - list components / files / routes to add or change; map states to elements; identify new design tokens needed (prefer reusing existing). Approval gate unless `--auto` or change is trivial.
5. **Implement** - apply the smallest correct change. Typed, accessible, responsive by default. Use existing patterns, not invented ones.
6. **Validate** - run repo-native checks: type-check, lint, unit tests for changed code, axe / a11y check for changed UI, build (catches CSS / asset issues).
7. **Report** - changed files, new components, new tokens (if any), validation evidence, screenshots / preview link if available.

## Implementation defaults (override only when the repo already differs)

- Components: function components + hooks. No class components.
- Types: TypeScript with strict on. Props typed; no `any`.
- Styling: match repo (Tailwind v4, CSS Modules, vanilla-extract, etc.). Use design tokens, not hardcoded colors / spacing.
- State: local component state for component-local concerns; existing app store for shared state. Never introduce a new state library mid-feature.
- Forms: React Hook Form + a schema (Zod / Yup) when forms exist; otherwise match repo.
- Async data: TanStack Query (or repo equivalent) with explicit `loading`, `error`, `empty` UI states.
- Routing: file-based or config-based as the repo already uses; do not switch routers.
- Icons: existing icon set; do not pull in a new icon library.
- Images: responsive `srcset` and `loading="lazy"` for non-LCP images.

## Accessibility checklist (per UI change)

- [ ] Every interactive element is reachable and operable by keyboard.
- [ ] Focus-visible state is present and not hidden by `outline: none` without replacement.
- [ ] Color contrast meets WCAG 2.2 AA (text 4.5:1, large text 3:1, UI 3:1).
- [ ] Status conveyed by icon / text + color (never color alone).
- [ ] Form fields have programmatic labels.
- [ ] Live regions used for async status messages (`aria-live="polite"`).
- [ ] Modals trap focus and restore on close.
- [ ] Motion respects `prefers-reduced-motion`.
- [ ] Touch targets >= 44 CSS px.

## Responsive checklist

- [ ] Layout works at 360px (mobile), 768px (tablet), 1280px (desktop).
- [ ] No horizontal scroll at any default viewport.
- [ ] Type ramp scales legibly; line lengths < ~75 characters.

## Output format

```
## Frontend feature: <task>

## Changed Files
- `src/components/Foo.tsx` - <one-line description>
- `src/routes/__settings.tsx` - <one-line description>

## New Components / Tokens
- `<Component>`: <purpose>
- token `<name>`: <value>

## Validation
- Type-check: <command> - PASS
- Lint: <command> - PASS / FAIL
- Tests: <command> - PASS / FAIL (changed-files: PASS)
- Axe / a11y: <command or summary> - PASS
- Build: <command> - PASS / FAIL

## Screenshots / Preview
- <path or URL if available>

## Remaining Risk
- <bullet>

Need more detail on any section?
```

## Hard rules

- Do not introduce a new state, style, router, or component library mid-feature.
- Use existing design tokens; if the design needs a new token, add it to the central tokens file (call it out in the report).
- All interactive elements must have all states (default/hover/focus-visible/active/disabled/loading/empty/error).
- Validation must run before claiming the feature is done; never claim "looks right" without proof.
- Do not ship UI gated only by mouse interactions.

## Anti-patterns

- Hardcoding colors, spacing, fonts.
- Disabling lint or type errors to "ship faster".
- Removing focus styles without replacement.
- Implementing only the happy path; ignoring loading / empty / error.
- Reaching for a new dependency where an existing one (or a small custom hook) would do.
- Over-abstracting: adding a base `<FormField>` for one form.

## Examples

```
adk-frontend-feature "Add the Settings page from .temp/drafts/design-settings.md" --design .temp/drafts/design-settings.md --scope src/routes/
```

```
adk-frontend-feature "Fix mobile dropdown trapping focus after Esc" --scope src/components/Dropdown/
```

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/working-artifacts.md` | The .temp/ rule for intermediate artifacts. |

<!-- adk:references:end -->
