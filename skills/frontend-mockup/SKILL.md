---
name: frontend-mockup
description: |
  Standalone 5-sample HTML mockup generator. Produces 5 distinct visual variants of a UI surface (component / page / flow) as self-contained HTML files at `.temp/task-<slug>/preview/sample-{1..5}.html`. Each sample is a different aesthetic direction (NOT five copies of the same design with color tweaks). Use during plan mode for any UI work, called by `@adk:frontend-design` (a.k.a. `adk-frontend-design`) and `@adk:auto` (a.k.a. `adk-auto`) before any implementation. Do not use to write production component code (use `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`)).
metadata:
  category: frontend
  kind: task
  layer: 3
  modes: [auto]
---

# frontend-mockup — 5 distinct UI variants

A hard-rule "always 5, always distinct" mockup generator. The user picks ONE of the five before any implementation begins.

## When to use

- Any UI work — called by `@adk:auto` and `@adk:frontend-design`.
- The user wants to compare options before locking design direction.

## When NOT to use

- The user provided a Figma / mockup PNG / explicit reference design (use that as ground truth instead).
- Production component code (`@adk:frontend-feature`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<surface description>` | yes | What's being designed (component / page / flow) |
| `<requirements.md>` | yes | From `@adk:requirements`; used to constrain functional content |
| `<scope.md>` | optional | From `@adk:scoping`; for blast-radius hints |
| `<aesthetic-hints>` | optional | Free-text "feels modern", "looks like Stripe dashboard", etc. |

## Workflow

1. Read `requirements.md`. Extract: target audience, primary action, content shape, accessibility / responsive constraints.
2. Decide **5 distinct aesthetic directions** (per `references/aesthetic-directions.md`). Examples:
   - Sample 1: brutalist / raw / mono
   - Sample 2: refined minimal / generous whitespace
   - Sample 3: editorial / typography-led
   - Sample 4: maximalist / dense / colorful
   - Sample 5: retro-futuristic / geometric
   - (Pick 5 from a wider menu; ensure they're meaningfully different.)
3. For each direction, generate one self-contained HTML file:
   - Inline `<style>` (no external CSS).
   - Real working example data (no Lorem Ipsum).
   - All states needed: default, hover, focus, active, disabled, loading, empty, error (where applicable).
   - Responsive: works at 360, 768, 1280 widths (use `@media`).
   - Accessibility: WCAG 2.2 AA, keyboard navigable, `prefers-reduced-motion` respected.
4. Write to `.temp/task-<slug>/preview/sample-1.html` ... `sample-5.html`.
5. Generate an **index** at `.temp/task-<slug>/preview/index.html` with thumbnails + links.
6. Show the user 5 thumbnails (or describe + open paths). Ask: "which sample, or 5 more variants?"
7. On pick, write `.temp/task-<slug>/preview/PICKED.md` with the chosen sample number + rationale.
8. Phase 4 validator: 5 files exist, index works, picked sample recorded.

## Output

```
.temp/task-<slug>/preview/
├── index.html
├── sample-1.html  (direction A)
├── sample-2.html  (direction B)
├── sample-3.html  (direction C)
├── sample-4.html  (direction D)
├── sample-5.html  (direction E)
└── PICKED.md      (only after user picks)
```

## Mode

`auto` only.

## Anti-patterns

- 5 samples that are 5 color variants of the same layout. Each must be a different aesthetic direction.
- Lorem Ipsum content. Use real example data (from `requirements.md`).
- Skipping any of the responsive widths.
- Skipping any state (default/hover/focus/active/disabled/loading/empty/error where applicable).
- Generic AI-slop fonts (Inter, Roboto, Arial). Use distinctive font choices per sample.
- Not running `@adk:validate-browser --mode visual-check` on the picked sample before claiming done.

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Pick-5-directions decision tree |
| `references/aesthetic-directions.md` | The menu of 12+ aesthetic directions to pick 5 from |
| `references/sample-html-template.md` | Bare-minimum HTML scaffold per sample |
| `references/state-checklist.md` | All states to cover |
| `references/responsive-checklist.md` | 360 / 768 / 1280 requirements |
| `references/a11y-checklist.md` | WCAG 2.2 AA defaults |
| `references/modes.md` | auto only |
| `references/persona.md` | The mockup designer |
| `references/workflow.md` | Detailed steps |
| `references/clarifying-questions.md` | Aesthetic hints, viewport priorities |
| `references/output-format.md` | Pick + rationale |
| `references/artifact-format.md` | preview/ folder layout |
| `references/validator.md` | Four-phase gate |
| `references/anti-patterns.md` | What NOT to do |
| `references/examples.md` | Worked examples |
| `references/interaction-contract.md` | Synced from canonical |
