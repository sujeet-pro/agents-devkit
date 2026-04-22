---
name: frontend-feature
description: Implement or extend a frontend component, page, route, or interaction in an existing app - typed React 19 with accessibility-first defaults, responsive layout at 360/768/1280, all interactive states (default/hover/focus/active/disabled/loading/empty/error), and repo-native validation (typecheck, lint, unit tests, axe). Use when the deliverable is frontend code in an existing app. Do not use to design from scratch (use adk-frontend-design first), to bootstrap a new app (use adk-frontend-react-csr), or for backend work (use adk-build-feature).
metadata:
  category: frontend
  kind: task
  layer: 3
  modes: [auto]
---

# ADK Frontend / Feature

Standalone task skill under the `@adk:frontend` (a.k.a. `adk-frontend`) category router. Builds or extends a frontend feature with typed code, accessibility defaults, responsive layout, and repo-native validation.

## When to use

- Add a new page, route, component, or interaction to an existing frontend app.
- Extend an existing component (new prop, new state, new variant) without redesigning it.
- Fix a frontend bug with a regression-test slice.
- Adopt a design produced by `@adk:frontend-design` (a.k.a. `adk-frontend-design`).

## When NOT to use

- Design first; no code yet -> `adk-frontend-design`
- Bootstrap a brand-new React 19 + CSR sample app -> `@adk:frontend-react-csr` (a.k.a. `adk-frontend-react-csr`)
- Backend / non-UI feature -> `@adk:build-feature` (a.k.a. `adk-build-feature`)
- Restructure with no behavior change -> `@adk:build-refactor` (a.k.a. `adk-build-refactor`)
- Frontend deps upgrade only -> `@adk:build-deps` (a.k.a. `adk-build-deps`)

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
3. **Load design system** - read `design-system/MASTER.md` (and `design-system/pages/<page>.md` if applicable) per `frontend-feature-design-system-master.md`. Pick tokens / patterns from there, not from memory. If the app has no design system, recommend running `adk-frontend-design` first or use the universal anti-patterns from `frontend-feature-industry-anti-patterns.md` as guard rails.
4. **Read context** - read the existing component library, design tokens, accessibility helpers, route layout, and tests near the change. Repo evidence over guessing.
5. **Plan** - list components / files / routes to add or change; map states to elements; identify new design tokens needed (prefer reusing existing). Approval gate unless `--auto` or change is trivial.
6. **Implement** - apply the smallest correct change. Typed, accessible, responsive by default. Use existing patterns + the loaded design system, not invented ones.
7. **Pre-delivery checklist** - walk every item in `frontend-feature-pre-delivery-checklist.md`; surface unfinished items in the report.
8. **Validate (per `frontend-feature-validator.md`)** - run repo-native checks: type-check, lint, unit tests for changed code, axe / a11y check for changed UI, build (catches CSS / asset issues). Run the four-phase validator gate; capture evidence in `.temp/notes/frontend-feature-<slug>-validator.md`.
9. **Report** - changed files, new components, new tokens (if any), validation evidence, screenshots / preview link if available.

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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-feature-clarifying-questions.md`) and reports the choices.

1. **What framework and meta-framework (React/Next, Vue/Nuxt, Svelte/SvelteKit, Astro, Solid, Angular, ...)?** — _How to pick:_ Detect from package.json. State explicitly so the agent uses the right idioms.
2. **Is this a new component, a feature on an existing component, or a screen/route?** — _How to pick:_ New component → in components/ with story + test. Feature on existing → minimal diff, preserve API. Screen/route → in routes/ + data hooks.
3. **Design source-of-truth (Figma, design spec, sibling component)?** — _How to pick:_ Figma → reference frame URL. Spec → adk-frontend-design output path. Sibling → call out the pattern being matched.

**Default report:** Result + changed-files + tests added + a11y notes + bundle delta.

**Detailed report (on request or `--verbose`):** Add: per-component prop table, story coverage, e2e test plan, design-spec deviations with reason.

**Artifact:** `frontend-code-change` — Code committed to the repo + tests + (optional) story files. Working notes in .temp/.

**Artifact path:** .temp/plans/fe-feature-<slug>.md (plan). Code lands in src/ matching repo conventions.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-feature-clarifying-questions.md`) and reports the choices.

1. **What framework and meta-framework (React/Next, Vue/Nuxt, Svelte/SvelteKit, Astro, Solid, Angular, ...)?** — _How to pick:_ Detect from package.json. State explicitly so the agent uses the right idioms.
2. **Is this a new component, a feature on an existing component, or a screen/route?** — _How to pick:_ New component → in components/ with story + test. Feature on existing → minimal diff, preserve API. Screen/route → in routes/ + data hooks.
3. **Design source-of-truth (Figma, design spec, sibling component)?** — _How to pick:_ Figma → reference frame URL. Spec → adk-frontend-design output path. Sibling → call out the pattern being matched.

## Default vs detailed output

**Default report:** Result + changed-files + tests added + a11y notes + bundle delta.

**Detailed report (on request or `--verbose`):** Add: per-component prop table, story coverage, e2e test plan, design-spec deviations with reason.

**Artifact:** `frontend-code-change` — Code committed to the repo + tests + (optional) story files. Working notes in .temp/.

**Artifact path:** .temp/plans/fe-feature-<slug>.md (plan). Code lands in src/ matching repo conventions.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/frontend-feature-anti-patterns.md` | Things to avoid when running this skill. |
| `references/frontend-feature-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/frontend-feature-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/frontend-feature-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/frontend-feature-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/frontend-feature-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/frontend-feature-persona.md` | The agent persona that drives this skill. |
| `references/frontend-feature-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/frontend-feature-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/frontend-feature-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |
| `references/frontend-feature-design-system-master.md` | The MASTER + page-overrides pattern for the app's design system (colors, typography, spacing, components). |
| `references/frontend-feature-pre-delivery-checklist.md` | Mandatory checklist (visual, interaction, accessibility, light/dark, layout, performance) before "ready for review". |
| `references/frontend-feature-industry-anti-patterns.md` | Industry-specific design no-gos (fintech / healthcare / e-commerce / etc.) used to filter implementation choices. |

<!-- adk:references:end -->
