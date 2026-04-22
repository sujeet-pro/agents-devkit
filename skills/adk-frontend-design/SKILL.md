---
name: adk-frontend-design
description: Produce UI/UX design artifacts - mockups, layouts, interaction specs, component specs - before code. Covers desktop + mobile + tablet viewports, default + hover + focus + active + disabled + loading + empty + error states, accessibility-first defaults (WCAG 2.2 AA, keyboard, prefers-reduced-motion, prefers-color-scheme), and a design rationale for every non-trivial choice. Use when the deliverable is a design (markdown spec + sketch / wireframe / mockup), not code. Do not use for backend or non-UI work (use adk-build) or for implementing the design (use adk-frontend-feature).
---

# ADK Frontend / Design

Standalone task skill under the `adk-frontend` category router. Produces a UI design artifact: layout, interaction spec, component spec, with intentional aesthetic choices and explicit accessibility / responsive defaults.

## When to use

- A new UI surface (page, screen, component, modal) needs design before code.
- An existing surface needs a redesign or an interaction refresh.
- A component spec is needed so multiple engineers can implement consistently.
- The deliverable is a design markdown (with an embedded mockup, ASCII layout, or linked image), not running code.

## When NOT to use

- The design is settled; just implement -> `adk-frontend-feature`
- Architecture / system design write-up -> `adk-plan-design`
- Backend or non-UI design -> `adk-build` family
- Single diagram only -> `adk-visualize-diagram`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<surface>` | yes | What is being designed (page, component, flow) |
| `<user goal>` | yes | What the user accomplishes here |
| `<existing system>` | optional | Repo path, design tokens file, component library to align with |
| `<viewports>` | optional | Default `mobile, tablet, desktop` |
| `<output path>` | optional | Defaults to `.temp/drafts/design-<slug>.md` |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate surface, user goal, viewports, system constraints. Approval gate unless `--auto`.
2. **Gather** - read existing component library, design tokens, accessibility constraints, prior versions, related screens.
3. **Load / generate design system** - read `design-system/MASTER.md` (and any `design-system/pages/<page>.md` override) per `frontend-design-design-system-master.md`. If no design system exists yet, draft one from product type + industry + audience + style keywords. Industry-anti-patterns from `frontend-design-industry-anti-patterns.md` filter out no-go choices.
4. **Decide direction** - pick an intentional aesthetic and information density (no AI-slop defaults). Capture rationale. Cross-check against the loaded MASTER and industry anti-patterns.
5. **Layout** - sketch responsive layout for each viewport (mobile, tablet, desktop) using ASCII / mermaid / linked image.
6. **States** - enumerate every state for every interactive element: default, hover, focus-visible, active, disabled, loading, empty, error.
7. **Interaction spec** - keyboard map, focus order, error recovery, loading/skeleton strategy, motion (with `prefers-reduced-motion` fallback).
8. **Accessibility check** - WCAG 2.2 AA: contrast, target size (44 CSS px), focus visibility, ARIA only when needed, content meaning preserved without color.
9. **Pre-delivery checklist** - walk every item in `frontend-design-pre-delivery-checklist.md`; surface unfinished items in the report.
10. **Validate (per `frontend-design-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/frontend-design-<slug>-validator.md` before the final report.
11. **Self-review** - run the validation list below.
12. **Report** - return the file path, 3-bullet TL;DR, viewports covered, follow-up questions for the user.

## Design template

```markdown
# Design: <surface>

## TL;DR
- <bullet>
- <bullet>
- <bullet>

## User Goal
<one paragraph>

## Direction & Rationale
- Aesthetic: <e.g. "editorial / quiet / spacious">
- Density: <comfortable | compact>
- Why this fits: <one paragraph>
- Rejected alternatives: <bullets - what we tried and why we did not pick it>

## Layout

### Mobile (<= 480px)
<ASCII / mermaid / image link>

### Tablet (~768px)
<...>

### Desktop (>= 1280px)
<...>

## Components Used
- `Component` - role, props of interest, source (Radix / repo lib / new)

## Interactive Elements & States
| Element | Default | Hover | Focus-visible | Active | Disabled | Loading | Empty | Error |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `Submit button` | label | bg shift | 2px ring | press | 50% opacity | spinner inline | n/a | inline error text |
| `Search input` | placeholder | n/a | 2px ring | n/a | 50% opacity | spinner trailing | "no results yet" | error text below |

## Keyboard Map
- Tab: focus order = <list>
- Enter / Space: <activation>
- Esc: <dismissal>
- Arrow keys: <navigation if any>

## Motion
- Defaults: <durations, easings>
- `prefers-reduced-motion`: <reduce / remove>

## Accessibility Checklist
- [ ] Contrast: text >= 4.5:1, large text >= 3:1, UI / icons >= 3:1
- [ ] Target size: 44 CSS px min
- [ ] Focus-visible state for every interactive element
- [ ] Meaning preserved without color (status uses icon + label)
- [ ] ARIA only where needed; native semantics first
- [ ] Skip links if multiple landmarks

## Copy
- Microcopy with character / word count where space matters

## Edge Cases
- <bullet>

## Open Questions
- <question>
```

## Validation list

- Every interactive element has all required states.
- Every viewport has a layout (or an explicit "same as desktop" note).
- Color is never the only encoding for meaning.
- Motion has a `prefers-reduced-motion` answer.
- Direction has rationale + at least one rejected alternative.

## Output format

```
## Design ready: <surface>
- File: `<path>`
- Viewports: <list>
- States covered: <count> elements x <count> states
- TL;DR:
  - <bullet>
  - <bullet>
  - <bullet>
- Open questions: <count>

Want a deeper look at any section?
```

## Anti-patterns

- AI-slop aesthetics: purple-cyan gradients, generic Inter, card-grid soup with no hierarchy.
- Designs with only the "happy" state. Real users hit empty / error / loading first.
- Using ARIA where native semantics would do.
- Color-only differentiation (status, charts).
- "Mobile is the same" without checking the layout actually works at 360px.
- Direction with no rejected alternatives - the choice is not justified.

## Examples

```
adk-frontend-design "Settings page with profile, security, notifications"
```

```
adk-frontend-design "Empty + loading + error states for the dashboard widgets" --viewports mobile,desktop
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-design-clarifying-questions.md`) and reports the choices.

1. **What is the surface (page, component, feature flow)?** — _How to pick:_ Page → screen-level. Component → reusable primitive. Flow → multi-step user journey.
2. **What is the design source-of-truth (existing design system, Figma file, sibling components)?** — _How to pick:_ Existing design system always wins. Figma if a designer is involved. Sibling components when extending a pattern.
3. **Constraints: brand, accessibility, performance budget, internationalization?** — _How to pick:_ List as hard constraints. Brand = colors/fonts/voice. A11y = WCAG level, language support. Perf = LCP/CLS/INP targets. i18n = locale list + LTR/RTL.

**Default report:** Component/page spec + interaction states table + accessibility notes + token usage.

**Detailed report (on request or `--verbose`):** Add: low-fi sketch (mermaid/excalidraw), copy table per state, motion spec (duration + easing + reduced-motion fallback), responsive breakpoints, content-overflow rules.

**Artifact:** `design-spec` — Markdown spec + optional sketch (excalidraw) + optional theme-grid screenshot pairs.

**Artifact path:** .temp/drafts/design-fe-<slug>.md (spec) + .temp/drafts/diagrams/<slug>.excalidraw (sketch).

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-design-clarifying-questions.md`) and reports the choices.

1. **What is the surface (page, component, feature flow)?** — _How to pick:_ Page → screen-level. Component → reusable primitive. Flow → multi-step user journey.
2. **What is the design source-of-truth (existing design system, Figma file, sibling components)?** — _How to pick:_ Existing design system always wins. Figma if a designer is involved. Sibling components when extending a pattern.
3. **Constraints: brand, accessibility, performance budget, internationalization?** — _How to pick:_ List as hard constraints. Brand = colors/fonts/voice. A11y = WCAG level, language support. Perf = LCP/CLS/INP targets. i18n = locale list + LTR/RTL.

## Default vs detailed output

**Default report:** Component/page spec + interaction states table + accessibility notes + token usage.

**Detailed report (on request or `--verbose`):** Add: low-fi sketch (mermaid/excalidraw), copy table per state, motion spec (duration + easing + reduced-motion fallback), responsive breakpoints, content-overflow rules.

**Artifact:** `design-spec` — Markdown spec + optional sketch (excalidraw) + optional theme-grid screenshot pairs.

**Artifact path:** .temp/drafts/design-fe-<slug>.md (spec) + .temp/drafts/diagrams/<slug>.excalidraw (sketch).

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/frontend-design-anti-patterns.md` | Things to avoid when running this skill. |
| `references/frontend-design-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/frontend-design-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/frontend-design-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/frontend-design-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/frontend-design-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/frontend-design-persona.md` | The agent persona that drives this skill. |
| `references/frontend-design-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/frontend-design-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/frontend-design-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |
| `references/frontend-design-design-system-master.md` | The MASTER + page-overrides pattern for the app's design system (colors, typography, spacing, components). |
| `references/frontend-design-pre-delivery-checklist.md` | Mandatory checklist (visual, interaction, accessibility, light/dark, layout, performance) before "ready for review". |
| `references/frontend-design-industry-anti-patterns.md` | Industry-specific design no-gos (fintech / healthcare / e-commerce / etc.) used to filter aesthetic choices. |

<!-- adk:references:end -->
