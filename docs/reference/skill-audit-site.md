---
title: 'audit-site'
description: 'Audit a publicly reachable website or web app across performance, accessibility, SEO, UX, and basic security headers - producing a single severity-tiered report with URL/selector evidence per finding. Use when the deliverable is a multi-dimensional health report on a deployed site, not a code repo. Do not use to audit a checked-out repo (use adk-audit-repo) or to fix the issues found (use adk-build-* / adk-frontend-* skills).'
skill_name: audit-site
category: router
---
# ADK Audit / Site

Standalone task skill under the `@adk:audit` (a.k.a. `adk-audit`) category router. Inspects a deployed website across multiple dimensions and produces one consolidated report with severity-tiered findings, each anchored to a URL or DOM selector.

## When to use

- Pre-launch or post-launch audit of a public website or web app.
- Periodic accessibility / performance / SEO check.
- Comparison audit (this URL vs. a target URL).
- Deliverable is a markdown report at `.temp/reports/<slug>.md`.

## When NOT to use

- Code-repo audit -> `@adk:audit-repo` (a.k.a. `adk-audit-repo`)
- Single PR review -> `@adk:review-pr` (a.k.a. `adk-review-pr`)
- Doc-only review -> `@adk:docs-review` (a.k.a. `adk-docs-review`)
- Building or fixing UI issues -> `@adk:frontend-feature` (a.k.a. `adk-frontend-feature`) / `@adk:frontend-design` (a.k.a. `adk-frontend-design`)

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<url>` | yes | Public starting URL (or list of URLs) |
| `<dimensions>` | optional | Subset of: `performance`, `accessibility`, `seo`, `ux`, `security-headers` (default: all) |
| `<depth>` | optional | `quick` (1 page) / `standard` (default; up to 5 pages) / `deep` (crawl + Core Web Vitals across templates) |
| `<viewport>` | optional | `mobile` / `desktop` / `both` (default `both`) |
| `<output path>` | optional | Defaults to `.temp/reports/audit-site-<slug>-<date>.md` |
| `--auto` | optional | Skip approval gates |

## Workflow

1. **Confirm intent** - restate URL(s), dimensions, depth, viewports, output. Approval gate unless `--auto`.
2. **Inventory** - capture: site type (marketing / app / docs), framework hints (from headers / source), key user flows, third-party scripts, page tree to depth.
3. **Run dimensions in parallel** - each dimension produces its own findings list:
   - **Performance**: Core Web Vitals (LCP, INP, CLS), TTFB, transfer size, render-blocking resources, image strategy.
   - **Accessibility**: WCAG 2.2 AA - landmarks, headings hierarchy, alt text, color contrast, focus management, ARIA misuse, keyboard traps.
   - **SEO**: title/meta, canonical, robots, sitemap, OG/Twitter cards, structured data, internal linking, crawlability.
   - **UX**: layout at 360 / 768 / 1280 viewports, primary CTA visibility, form usability, error states, copy clarity.
   - **Security headers**: HSTS, CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy, Permissions-Policy.
4. **Aggregate** - merge findings; deduplicate; group by dimension under each severity.
5. **Validate** - re-fetch the URL or re-run the analyzer to confirm each finding reproduces.
6. **Report** - findings-first markdown using the template below.

## Severity ladder

| Label | Site meaning |
| --- | --- |
| `Blocker` | Broken core flow, security header missing entirely, accessibility failure that blocks use, page does not load |
| `Critical` | Significant CWV failure, severe a11y / SEO regression, missing meta on the home page |
| `Should Have` | Notable improvement (image optimization, missing alt text in non-critical regions) |
| `May Have` | Minor polish |
| `Nitpick` | Style only |
| `Question` | Auditor unsure (e.g. intentional A/B test variant) |

## Finding template

```markdown
### [<Severity>] <One-line summary> (<dimension>)
- **URL**: <url>
- **Anchor**: <DOM selector / region / response header>
- **Issue**: <2-3 sentence explanation>
- **Evidence**: <measurement / quoted source / screenshot description>
- **Suggested fix**: <concrete recommendation; route to ``@adk:frontend` (a.k.a. `adk-frontend`)-*` / ``@adk:build` (a.k.a. `adk-build`)-*` if implementation needed>
- **Why this severity**: <one sentence>
```

## Report template

```markdown
# Site Audit: <site>

## Summary
- URLs audited: <list>
- Viewports: <list>
- Dimensions: <list>
- Findings: <N> Blocker, <N> Critical, <N> Should Have, <N> May Have, <N> Nitpick, <N> Question

## Top Risks
1. <one-line top risk>
2. <one-line top risk>

## Core Web Vitals (per page)
| URL | LCP | INP | CLS | TTFB | Transfer |
| --- | --- | --- | --- | --- | --- |

## Findings

### Blockers
<finding blocks>

### Critical
<finding blocks>

### Should Have
<finding blocks>

### May Have
<finding blocks>

### Nitpicks
<finding blocks>

### Questions
<finding blocks>

## Per-Dimension Notes
<short per-dimension narrative for context the findings cannot carry>

## Out of Scope
- <items not audited and why (e.g. authenticated flows, third-party iframes)>

## Recommended Next Steps
1. <fix Blockers via `adk-frontend-feature` / `@adk:build-feature` (a.k.a. `adk-build-feature`)>
2. <follow-up audit in <area> after fixes>
```

## Tooling notes

This skill calls whatever site-audit tooling the environment provides (browser MCP for DOM / a11y inspection, Lighthouse-like perf checks, header probes via `curl -I`). When a tool is unavailable, the skill explicitly marks the dimension as `not-measured` rather than guessing.

Tools the skill may use when present:

- Headless browser MCP (page load, DOM snapshot, axe-core, screenshots).
- HTTP probe (`curl -I`, `httpx`) for headers.
- HTML parser for meta, link, structured data.
- Public Lighthouse / PageSpeed API for perf metrics.

## Anti-patterns

- Findings without URL + selector / header anchor.
- Reporting Lighthouse scores without per-metric values - scores hide root cause.
- Mixing fixes into the audit; the audit reports.
- Auditing only one viewport when the site is responsive.
- Calling something a Blocker that is intentional (e.g. a maintenance page).
- Relying on cached results from a previous run; always re-fetch.

## Examples

```
adk-audit-site https://example.com --dimensions performance,accessibility --viewport mobile
```

```
adk-audit-site https://shop.example.com --depth deep --output .temp/reports/audit-site-shop-2026-04.md
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/audit-site-clarifying-questions.md`) and reports the choices.

1. **Which URL(s) to audit? Single page, top N pages, or full crawl?** — _How to pick:_ Single = focused investigation. Top N = sample (home + 5-10 high-traffic pages). Full crawl = comprehensive but slow; only with explicit approval.
2. **Dimensions: performance / accessibility / SEO / UX / security-headers / all?** — _How to pick:_ All by default. Narrow when retesting a specific dimension.
3. **Devices and connection profiles?** — _How to pick:_ Default = desktop + mobile, fast 3G + cable. Match real user distribution if known.

**Default report:** Per-page Lighthouse score table + severity-grouped findings + screenshot references.

**Detailed report (on request or `--verbose`):** Add: full Lighthouse JSON archived, axe full report, network waterfall analysis, page-weight breakdown, contrast-ratio table for any flagged colors.

**Artifact:** `site-audit-report` — Markdown report + screenshots/artifacts in .temp/notes/audit-site-<slug>/.

**Artifact path:** .temp/reports/audit-site-<host>-<date>.md (raw lighthouse JSON + screenshots in .temp/notes/audit-site-<slug>/)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/audit-site-clarifying-questions.md`) and reports the choices.

1. **Which URL(s) to audit? Single page, top N pages, or full crawl?** — _How to pick:_ Single = focused investigation. Top N = sample (home + 5-10 high-traffic pages). Full crawl = comprehensive but slow; only with explicit approval.
2. **Dimensions: performance / accessibility / SEO / UX / security-headers / all?** — _How to pick:_ All by default. Narrow when retesting a specific dimension.
3. **Devices and connection profiles?** — _How to pick:_ Default = desktop + mobile, fast 3G + cable. Match real user distribution if known.

## Default vs detailed output

**Default report:** Per-page Lighthouse score table + severity-grouped findings + screenshot references.

**Detailed report (on request or `--verbose`):** Add: full Lighthouse JSON archived, axe full report, network waterfall analysis, page-weight breakdown, contrast-ratio table for any flagged colors.

**Artifact:** `site-audit-report` — Markdown report + screenshots/artifacts in .temp/notes/audit-site-<slug>/.

**Artifact path:** .temp/reports/audit-site-<host>-<date>.md (raw lighthouse JSON + screenshots in .temp/notes/audit-site-<slug>/)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/audit-site-anti-patterns.md` | Things to avoid when running this skill. |
| `references/audit-site-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/audit-site-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/audit-site-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/audit-site-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/audit-site-persona.md` | The agent persona that drives this skill. |
| `references/audit-site-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/audit-site-review-comment-format.md` | Standard finding format with stable IDs and severities. |
| `references/audit-site-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/audit-site-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
