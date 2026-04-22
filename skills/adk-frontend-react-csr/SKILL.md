---
name: adk-frontend-react-csr
description: Bootstrap or extend an opinionated React 19 client-side sample app on a fixed Vite (rolldown) + Vitest + oxc + TanStack (router/query/hotkeys) + Radix UI stack, with a self-contained themeable design system (paper + high-contrast, light/dark, three text sizes), full WCAG 2.2 AA + keyboard accessibility, performance-first defaults, and GitHub Pages deploy on push to main. Use to scaffold a new sample app, add a feature to one already on this stack, or audit one for stack conformance. Do not use for SSR/Next/Remix, non-React frontends, or production multi-tenant apps with auth/payments.
---

# ADK Frontend / React CSR

Standalone task skill under the `adk-frontend` category router. Bootstraps and maintains opinionated React 19 client-side sample apps on a fixed performance-first stack, with a polished accessible themeable design system, ready to deploy to GitHub Pages.

This skill **does not** ship a frozen template. On every run it instructs the agent to research current stable versions of every pinned library so sample apps always start from current state.

## When to use

- Scaffolding a brand-new client-side React 19 sample app intended to live on GitHub Pages.
- Adding a feature, page, or component to an existing app already on this stack.
- Auditing an existing app for stack conformance, accessibility, or performance regressions.
- Migrating a sample app onto this stack from a different React/CRA/Webpack baseline.

## When NOT to use

- SSR / Next.js / Remix work -> different routing, data, and deploy concerns. Use `adk-frontend-feature` (or `adk-build-feature`) on the SSR stack.
- Non-React frontends (Vue, Svelte, Angular, Astro) -> `adk-frontend-feature` on that stack.
- Backend services or full-stack APIs -> `adk-build-feature`.
- Production multi-tenant apps with auth, payments, or persistent backends -> this skill assumes a public, static, single-tenant sample.

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task>` | yes | What to build / extend / audit |
| `<mode>` | optional | `new` (bootstrap) / `feature` (extend) / `audit` (read-only) - inferred when omitted |
| `<target>` | optional | Repo root for `feature` / `audit`, or directory to create the app in for `new` (default `.`) |
| `<repo-name>` | optional | Used for `base` path and Pages URL when `mode=new` (defaults from `target`) |
| `<base-path>` | optional | Vite `base` and TanStack Router `basepath`. Defaults to `/<repo-name>/`. Override for custom domains. |
| `<no-research>` | optional | Suppress the *user-facing report* of the research step. Lookups still happen. |
| `--auto` | optional | Skip user confirmation gates. Use defaults at every choice. |

## Workflow

1. **Confirm intent** - restate task, mode, target, base path, and constraints. Approval gate unless `--auto`.
2. **Research** - look up current stable versions of every pinned library (table below). Capture the result to `.temp/notes/adk-frontend-react-csr-versions-<date>.md`. **Mandatory every run.** No version is known a priori.
3. **Load / generate design system** - for `new`: generate `design-system/MASTER.md` per `frontend-react-csr-design-system-master.md` from product type + industry + audience. For `feature` / `audit`: read the existing `design-system/MASTER.md` (and any `pages/<page>.md` overrides). Industry anti-patterns from `frontend-react-csr-industry-anti-patterns.md` filter out no-go choices.
4. **Plan** - for `new` or any multi-file change, write `.temp/plans/adk-frontend-react-csr-<slug>.md` with file list, design direction, and validation gates. Approval gate unless `--auto`.
5. **Setup or extend**:
   - `new`: create the repo skeleton (config, theme system, fonts, router, sample accessible page, CI, `design-system/MASTER.md`). Reach for the stack defaults below.
   - `feature`: implement the smallest correct change behind the existing tokens, themes, and patterns. Surface stack drift if you find it.
   - `audit`: read-only - produce findings only.
6. **Pre-delivery checklist** - walk every item in `frontend-react-csr-pre-delivery-checklist.md`; surface unfinished items in the report.
7. **Validate (per `frontend-react-csr-validator.md`)** - `npm run check` (lint + format + typecheck), `npm test`, `npm run build`, automated `axe` pass, manual keyboard pass, theme-grid screenshot pass (paper x high-contrast x light x dark x small/base/large = 12 cells), Lighthouse on `dist/` via a browser MCP. Run the four-phase validator gate; capture evidence in `.temp/notes/frontend-react-csr-<slug>-validator.md`.
8. **Report** - changed files, version table from research, validation matrix with per-row evidence, design notes, deploy URL, remaining risk, next steps.

## Locked stack

Do not reach for a library outside this list. New deps require explicit user approval and a `.temp/reports/` justification with measured trade-off.

| Layer | Library | Notes |
| --- | --- | --- |
| Bundler | `vite` (rolldown channel when stable) | research confirms current rolldown integration status |
| Compiler / format / lint | `oxc`, `oxlint`, `oxfmt` | |
| Type checker | `@typescript/native-preview` (ts-go) when available | fall back to `typescript` for editor tooling |
| Tests | `vitest` | |
| Framework | `react`, `react-dom` | 19+ |
| React Compiler | `babel-plugin-react-compiler` (beta channel) | |
| Routing | `@tanstack/react-router` (file-based) | basepath derived from `import.meta.env.BASE_URL` |
| Data | `@tanstack/react-query` | |
| Hotkeys | `@tanstack/react-hotkeys` | |
| UI primitives | `radix-ui` (meta) or `@radix-ui/*` per primitive | no other component library |
| Styles | CSS custom properties + `light-dark()` + `data-theme` + `data-text-size` | no CSS-in-JS for theming |
| Fonts | Open Sans + JetBrains Mono | self-hosted variable woff2; never Google Fonts CDN |
| CI | GitHub Actions -> GitHub Pages on push to `main` | |

## Design system contract

The generated app ships with a self-contained, themeable design system. Every component must render correctly across the 12-cell matrix:

- Themes: `theme-paper`, `theme-high-contrast`.
- Color modes: `light`, `dark` (driven by `light-dark()` and `data-theme`).
- Text sizes: `small`, `base`, `large` (driven by `data-text-size`).

Every interactive state must be implemented: default, hover, focus-visible, active, disabled, loading, empty, error.

Tokens (color, spacing, type ramp, radii, shadows, motion) live in a single `tokens.css` (or equivalent). No hardcoded values in components.

## Research checklist (run every time)

Before changing any file, gather current stable versions and one-line risk per library:

```markdown
| Library                       | Latest stable | Notes |
| ---                           | ---           | ---   |
| vite                          | <x.y.z>       | rolldown integration status |
| @vitejs/plugin-react          | <x.y.z>       |  |
| react / react-dom             | <x.y.z>       | confirm 19+ |
| babel-plugin-react-compiler   | <x.y.z>       | beta channel |
| @tanstack/react-router        | <x.y.z>       |  |
| @tanstack/react-query         | <x.y.z>       |  |
| @tanstack/react-hotkeys       | <x.y.z>       |  |
| radix-ui                      | <x.y.z>       | meta-package vs @radix-ui/* primitives |
| oxlint / oxfmt                | <x.y.z>       |  |
| @typescript/native-preview    | <x.y.z>       | ts-go preview channel |
| typescript                    | <x.y.z>       | fallback for editor tooling |
| vitest                        | <x.y.z>       |  |
```

## Validation matrix

Definition of done - every box must be ticked or explicitly waived.

- [ ] `npm run check` passes (oxlint, oxfmt --check, tsgo --noEmit)
- [ ] `npm test -- --run` passes (or no tests applicable, with justification)
- [ ] `npm run build` produces `dist/` under the configured `base`
- [ ] Bundle: largest single chunk under 200 KB gzip; route chunks split per-route
- [ ] `axe` automated pass on every route - zero violations of `serious` or `critical`
- [ ] Manual keyboard pass on every interactive surface - Tab, Shift+Tab, Enter, Space, Esc, Arrow keys behave per WAI-ARIA APG
- [ ] Theme matrix renders correctly across 12 cells
- [ ] `prefers-reduced-motion` honored - no involuntary motion
- [ ] Lighthouse on `dist/` via browser MCP - Performance >= 95, Accessibility = 100, Best Practices >= 95, SEO >= 90
- [ ] GitHub Actions workflow exists and is well-formed
- [ ] If a check could not run, say so and explain why

## Output format

Sections in this exact order:

```
## Summary
<one sentence on what was done>

## Mode + Target
<what was bootstrapped, extended, or audited>

## Versions
<the research table>

## Plan
<link to .temp/plans/adk-frontend-react-csr-<slug>.md if one was written>

## Changes
<file list grouped by area: config / styles / components / routes / ci>

## Validation
<the matrix above with per-row evidence>

## Design Notes
<short rationale for non-trivial visual choices>

## Deploy
<final URL or steps to enable Pages>

## Remaining Risk
<open items, untested edges, browser-MCP unavailability>

## Next Steps
<concrete follow-ups, numbered list>
```

## Hard rules

- Latest-version research is mandatory every run. `--no-research` only suppresses the *report*, not the lookups.
- Performance is the first non-negotiable: target `<200ms` interaction latency on a mid-tier laptop, `<2s` LCP on a fast 3G profile, Lighthouse 100 / 100 / 100 / 100 before declaring done.
- Accessibility is a build gate: WCAG 2.2 AA + complete keyboard + `prefers-reduced-motion` + `prefers-color-scheme` are part of definition-of-done.
- Stack lock is real: no Tailwind, Chakra, MUI, Mantine, styled-components, or any non-Radix component library. New deps need explicit user approval.
- Self-contained: tokens, fonts, themes, accessibility helpers, and CI live inside the generated repo. No private packages, no shared design system, no CDN fonts.
- Plan before any non-trivial change.

## Anti-patterns

- Skipping the research step and pinning versions from memory.
- Pulling in Tailwind / Chakra / MUI / Mantine / styled-components.
- CSS-in-JS for theming - themes are CSS-custom-property driven via `light-dark()` + `data-theme` + `data-text-size`.
- Loading fonts from a CDN.
- AI-slop visuals: purple-cyan gradients, generic Inter, card-grid soup with no hierarchy.
- Hard-coding `/` as the router basepath - always derive from `import.meta.env.BASE_URL`.
- Pushing without per-route code splitting and `manualChunks` for vendor libs.
- Marking work done without a Lighthouse run on the produced `dist/`.
- Treating the design system as optional polish - it is the contract that lets every page satisfy a11y + theme requirements with no per-page work.

## Examples

```
adk-frontend-react-csr "scaffold a recipes-finder sample app" --mode new --target ../recipes --repo-name recipes
```

```
adk-frontend-react-csr "add a per-user theme picker (paper / high-contrast / system) with a hotkey" --mode feature
```

```
adk-frontend-react-csr "audit accessibility and bundle size" --mode audit
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-react-csr-clarifying-questions.md`) and reports the choices.

1. **Mode: new (bootstrap), feature (extend existing), audit (read-only)?** — _How to pick:_ Inferred from the request when omitted. New = create dir + scaffold. Feature = inside an existing app on the stack. Audit = read-only findings.
2. **Target directory + repo name + base path?** — _How to pick:_ Repo name → Pages URL `/<repo-name>/`. Custom domain → base = `/`. Subpath hosting → explicit base.
3. **Should the agent suppress the user-facing version-research report (--no-research)?** — _How to pick:_ Default = show the report. Suppress only when output noise is unwanted; the lookups still run.

**Default report:** Result + version table + changed files (config / styles / components / routes / ci) + validation matrix + deploy URL + remaining risk + next steps.

**Detailed report (on request or `--verbose`):** Add: per-route Lighthouse breakdown, axe full report, theme-grid screenshots (12 cells), bundle visualization, suggested follow-ups numbered.

**Artifact:** `react-csr-codebase` — Working app in the repo + GitHub Actions workflow + version-research note in .temp/.

**Artifact path:** .temp/notes/adk-frontend-react-csr-versions-<date>.md (research). Code lives in target repo.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/frontend-react-csr-clarifying-questions.md`) and reports the choices.

1. **Mode: new (bootstrap), feature (extend existing), audit (read-only)?** — _How to pick:_ Inferred from the request when omitted. New = create dir + scaffold. Feature = inside an existing app on the stack. Audit = read-only findings.
2. **Target directory + repo name + base path?** — _How to pick:_ Repo name → Pages URL `/<repo-name>/`. Custom domain → base = `/`. Subpath hosting → explicit base.
3. **Should the agent suppress the user-facing version-research report (--no-research)?** — _How to pick:_ Default = show the report. Suppress only when output noise is unwanted; the lookups still run.

## Default vs detailed output

**Default report:** Result + version table + changed files (config / styles / components / routes / ci) + validation matrix + deploy URL + remaining risk + next steps.

**Detailed report (on request or `--verbose`):** Add: per-route Lighthouse breakdown, axe full report, theme-grid screenshots (12 cells), bundle visualization, suggested follow-ups numbered.

**Artifact:** `react-csr-codebase` — Working app in the repo + GitHub Actions workflow + version-research note in .temp/.

**Artifact path:** .temp/notes/adk-frontend-react-csr-versions-<date>.md (research). Code lives in target repo.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/frontend-react-csr-anti-patterns.md` | Things to avoid when running this skill. |
| `references/frontend-react-csr-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/frontend-react-csr-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/frontend-react-csr-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/frontend-react-csr-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/frontend-react-csr-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/frontend-react-csr-persona.md` | The agent persona that drives this skill. |
| `references/frontend-react-csr-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/frontend-react-csr-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/frontend-react-csr-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |
| `references/frontend-react-csr-design-system-master.md` | The MASTER + page-overrides pattern for the app's design system (colors, typography, spacing, components). |
| `references/frontend-react-csr-pre-delivery-checklist.md` | Mandatory checklist (visual, interaction, accessibility, light/dark, layout, performance) before "ready for review". |
| `references/frontend-react-csr-industry-anti-patterns.md` | Industry-specific design no-gos used to filter aesthetic + implementation choices. |

<!-- adk:references:end -->
