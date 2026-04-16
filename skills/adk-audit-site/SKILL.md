---
name: adk-audit-site
description: Audit a live site or webapp for SEO, performance, accessibility, security signals, metadata, and broken-user-flow issues. Use when the job is site health rather than repo health.
compatibility: Self-contained published skill for npx skills. Works best when web access is available and when browser tooling is available locally.
user-invocable: true
argument-hint: <url> [--focus seo|performance|accessibility|security|content|all] [--scope <path-or-surface>] [--auto] [--help]
workflow-tier: full
maturity: experimental
workflow-family: standard-task
tools: [Read, Glob, Grep, Bash, Agent, WebSearch, WebFetch]
metadata:
  area: audits-quality
dependencies:
  commands: [git, python3]
---

# ADK Audit Site


## Read In This Order
- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/persona.md`
- `references/review-comment-format.md`
- `references/workflow.md`

## Constitution

- **Human-in-the-Loop** -- Decisions interactive, execution automatic. Confirm the target URL and audit dimensions before scanning. `--auto` skips confirmations but still reports everything.
- **Plan First** -- Show the audit plan (URL, dimensions, scope) and get approval before executing any checks.
- **Brainstorm After Findings, Not Before Scanning** -- use only a light brainstorming handoff when the user wants remediation planning or route selection after the audit.
- **Concise by Default** -- Health score card and top findings first. Offer to elaborate per dimension.
- **Parallel Agentic Teams** -- Dispatch a browser agent for visual verification and render checks. Run performance, accessibility, and SEO scans in parallel where possible.
- **Principal Engineer Lens** -- Run the smallest useful audit pass first, then deepen only where evidence says it matters. Prioritize high-traffic pages over exhaustive crawls.

## Persona

See `references/persona.md` for the full Web Quality Auditor persona.

- **Mission**: Audit live sites and webapps for discoverability, quality, performance, accessibility, and user-facing defects, producing a scored health report with actionable fixes.
- **Voice**: Evidence-first, dimension-organized, severity-ordered. Leads with scores, follows with proof.
- **Hard rules**: Live-site evidence over source-only guesses. Separate site findings from code-fix proposals. Re-audit after approved fixes.
- **Evidence expectations**: Every finding cites a URL, tool output, browser observation, or screenshot. Runtime claims from static source inspection are labeled as unverified.

## When To Use

- Auditing a production or staging site for quality
- Checking technical SEO, crawlability, metadata, or structured content issues
- Finding accessibility, performance, or broken-link problems
- Comparing before/after site health after deployments or changes
- Visual verification of render behavior across viewports

## When NOT To Use

- Source-only repository audits with no live target -- use `adk-audit-repo`
- Writing or fixing code -- use `adk-build`
- PR or diff review -- use `adk-review-pr`
- Test execution -- use `adk-test`

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<url>` | live URL | required | Site or webapp to audit |
| `--focus` | `seo`, `performance`, `accessibility`, `security`, `content`, `all` | `all` | Primary audit lens |
| `--scope` | path, route group, or page hint | none | Limit the audit to one surface |
| `--auto` | flag | off | Skip confirmations and execute with defaults |
| `--help` | flag | off | Show the skill and stop |

## Pre-flight

Run `python3 scripts/preflight.py` before any audit work.
If the script reports a missing dependency, stop and tell the user.

## Workflow

See `references/workflow.md` for full phase details.

### Phase 1 -- Scope (gate: approval unless `--auto`)
Confirm the target URL, audit dimensions, and whether the user wants audit-only or audit-plus-fix proposals. Clarify scope narrowing (specific routes or pages).

### Phase 2 -- Scan
Run comprehensive checks across 5 dimensions. Score each dimension 0-4 using the criteria below.

#### 1. Performance
**Check for**:
- Core Web Vitals: LCP > 2.5s, CLS > 0.1, INP > 200ms
- Render-blocking resources: undeferred CSS/JS in `<head>`, large synchronous scripts
- Image optimization: missing lazy loading, uncompressed images, no WebP/AVIF fallback, missing width/height causing layout shift
- Bundle size: unminified JS/CSS, unused code shipped, no code splitting
- Caching: missing or short Cache-Control headers, no CDN usage
- Network waterfall: excessive sequential requests, no preconnect/preload hints

**Score 0-4**: 0=Unusable (LCP > 8s, layout thrash, unoptimized everything), 1=Major problems (LCP > 4s, no lazy loading, render-blocking resources), 2=Partial (some optimization, Core Web Vitals partially met), 3=Good (Core Web Vitals mostly green, minor improvements possible), 4=Excellent (all vitals green, lean assets, proper caching)

#### 2. Accessibility
**Check for**:
- Color contrast: text contrast ratios < 4.5:1 normal text, < 3:1 large text (WCAG AA)
- Missing ARIA: interactive elements without proper roles, labels, or states
- Keyboard navigation: missing focus indicators, illogical tab order, keyboard traps
- Semantic HTML: improper heading hierarchy (h1 → h3 skip), missing landmarks, divs as buttons
- Alt text: missing or decorative descriptions on informational images
- Form issues: inputs without associated labels, missing error messaging, no required indicators
- Touch targets: interactive elements < 44x44px on mobile

**Score 0-4**: 0=Inaccessible (fails WCAG A, no keyboard nav, no alt text), 1=Major gaps (few ARIA labels, broken keyboard nav, poor contrast), 2=Partial (some a11y effort, significant gaps in forms or navigation), 3=Good (WCAG AA mostly met, minor gaps), 4=Excellent (WCAG AA fully met, approaches AAA)

#### 3. SEO
**Check for**:
- Meta tags: missing or duplicate title/description, missing og:tags and twitter:cards
- Structured data: missing JSON-LD/microdata, schema.org validation errors
- Canonical URLs: missing canonical tags, conflicting canonicals, self-referencing errors
- Crawlability: pages blocked by robots.txt, missing sitemap.xml, noindex on important pages
- URL structure: non-descriptive URLs, missing trailing-slash consistency
- Mobile signals: missing viewport meta, content wider than screen, no mobile-friendly indicators

**Score 0-4**: 0=Invisible (no meta tags, blocked by robots.txt, no sitemap), 1=Major gaps (missing titles/descriptions on key pages, no structured data), 2=Partial (basic meta present, gaps in structured data or canonicals), 3=Good (meta complete, structured data present, minor canonical issues), 4=Excellent (full meta coverage, valid structured data, clean sitemap, proper canonicals)

#### 4. Security
**Check for**:
- HTTPS: missing redirect from HTTP, expired or misconfigured certificate
- Security headers: missing CSP, HSTS (min 1-year max-age), X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- Mixed content: HTTP resources loaded on HTTPS pages (scripts, images, stylesheets)
- Exposed paths: accessible debug endpoints, stack traces in error pages, directory listing enabled
- Cookie security: missing Secure/HttpOnly/SameSite flags on session cookies
- Subresource integrity: third-party scripts without SRI hashes

**Score 0-4**: 0=Critical exposure (no HTTPS, credentials in plaintext, accessible debug endpoints), 1=Major gaps (HTTPS present but missing key headers, mixed content), 2=Partial (HTTPS + some headers, notable gaps in CSP or cookie flags), 3=Good (solid HTTPS, most headers present, minor gaps), 4=Excellent (full header suite, no mixed content, SRI on third-party, clean cookies)

#### 5. Content/UX
**Check for**:
- Broken links: internal 404s, external dead links, redirect chains > 2 hops
- Image issues: oversized images, missing responsive srcset, broken image references
- Responsive design: content overflow on mobile, fixed widths that break on narrow viewports
- Duplicate content: same content on multiple URLs without canonicals
- User flow integrity: broken forms, non-functional CTAs, dead-end pages
- Loading states: no feedback during async operations, flash of unstyled content

**Score 0-4**: 0=Broken (multiple dead links, forms non-functional, layout breaks on mobile), 1=Major issues (broken user flows, significant responsive failures), 2=Partial (mostly functional, broken links or responsive gaps), 3=Good (functional flows, minor broken links or image optimization gaps), 4=Excellent (clean links, responsive everywhere, optimized images, smooth flows)

### Phase 3 -- Browser Check
Dispatch the browser agent (via `cursor-ide-browser` MCP or equivalent browser automation tool) for visual verification:
- Screenshot key pages at mobile (375px), tablet (768px), and desktop (1440px) widths
- Verify render behavior: layout shifts, missing assets, JS errors in console
- Check interactive elements: forms, navigation, modals, dropdowns
- Validate responsive breakpoints and overflow detection
- Record console errors and network failures as evidence

**Browser agent dispatch**: Use `browser_navigate` to load each page, `browser_snapshot` for structure, `browser_take_screenshot` for visual evidence, and `browser_console_messages` for JS errors. All browser observations become findings evidence.

### Phase 4 -- Score
Score each dimension 0-4 using the criteria defined in Phase 2.

| Score | Label | Meaning |
| --- | --- | --- |
| 4 | Excellent | No significant issues |
| 3 | Good | Minor issues only |
| 2 | Fair | Notable issues requiring attention |
| 1 | Poor | Serious issues affecting users |
| 0 | Critical | Immediate action required |

**Rating bands** (sum of 5 dimensions):
- 18-20 Excellent -- minor polish only
- 14-17 Good -- address weak dimensions
- 10-13 Acceptable -- significant work needed
- 6-9 Poor -- major overhaul required
- 0-5 Critical -- fundamental issues across the board

Dimensions scored: **performance**, **accessibility**, **SEO**, **security**, **content/UX**.

If a dimension could not be fully assessed (auth-gated pages, no browser access), cap its max score at 2 and note the gap.

### Phase 5 -- Findings
Severity-ordered with P0-P3 ratings, organized by dimension:
- **P0** -- Critical: broken functionality, security vulnerabilities, total accessibility failures
- **P1** -- High: significant UX degradation, major SEO blockers, performance bottlenecks
- **P2** -- Medium: improvement opportunities with clear user impact
- **P3** -- Low: polish items, minor optimization opportunities

### Phase 6 -- Report
Deliver:
1. Health score card (dimension scores table)
2. Detailed findings (severity-ordered, grouped by dimension)
3. Recommended fix commands or actions (effort-tagged)
4. Before/after targets (what scores should be after fixes)
5. Blind spots and areas needing manual verification

## Interaction Protocol

### Intent Confirmation
Unless `--auto` is set, confirm before starting:
- Target URL and whether audit-only or audit-plus-fix planning
- Focus area(s) to audit
- Scope narrowing (specific routes or pages)

### Findings Presentation
Each finding uses the format:

```
F<n> [Type][Severity]: Title
Confidence: High|Medium|Low | Dimension: <dim> | Scope: <URL, route, or page>

**Issue Summary** -- What is wrong.
**Why This Matters** -- Impact on users, SEO, or compliance.
**Suggested Fix** -- Actionable remediation with commands where applicable.
**Verify** -- How to confirm the fix (optional).
```

Types: **Bug**, **Risk**, **Improvement**, **Nitpick**, **Question**
Severity: **P0** (Critical) > **P1** (High) > **P2** (Medium) > **P3** (Low)
Dimensions: **performance**, **accessibility**, **seo**, **security**, **content**

### Post-Fix Re-audit
When fixes are applied, offer to re-audit affected pages. State what improved and what still fails.

## Parallel Agents

| Agent | Role | Dispatched When |
| --- | --- | --- |
| Browser agent (`cursor-ide-browser` MCP) | Visual verification via `browser_navigate`, `browser_snapshot`, `browser_take_screenshot`, `browser_console_messages` | Always (Phase 3) -- screenshots at 375px, 768px, 1440px |
| Performance scanner | Core Web Vitals measurement, resource analysis, waterfall inspection | `--focus performance` or `--focus all` |

Each agent receives the target URL, scope, and focus. Returns structured findings with evidence (screenshots, console output, network data). The orchestrator merges, deduplicates, and scores.

## Validation

- Findings cite URLs, audit output, browser evidence, or direct page observations
- Static-source claims about runtime behavior are labeled when not fully verified
- Before/after comparisons are explicit when fixes were applied
- Browser screenshots or observations back visual findings
- Scores are justified by the findings within each dimension

## Output Format

```markdown
## Health Score Card
| # | Dimension | Score | Label | Key Finding |
| --- | --- | --- | --- | --- |
| 1 | Performance | 2 | Fair | 4.2s LCP on mobile, 3 render-blocking scripts |
| 2 | Accessibility | 1 | Poor | 23 images missing alt text, h1 → h3 skip |
| 3 | SEO | 3 | Good | Minor meta description gaps on 2 pages |
| 4 | Security | 3 | Good | Missing CSP header, no SRI on 3rd-party scripts |
| 5 | Content/UX | 2 | Fair | 12 broken links, form submit fails on mobile |
| **Total** | | **11/20** | **Acceptable** | |

## Findings (N total: X P0, Y P1, Z P2, W P3)
### P0 -- Critical
<findings using F<n> format from review-comment-format.md>

### P1 -- High
<findings by dimension>

### P2 -- Medium / P3 -- Low
<findings>

## Recommended Actions
| Priority | Action | Effort | Dimension | Target Score |
| --- | --- | --- | --- | --- |
| 1 | Add alt text to hero images | quick-win | accessibility | 1 → 3 |

## Before/After Targets
| Dimension | Current | Target | Key Action |
| --- | --- | --- | --- |
| Accessibility | 1 | 3 | Alt text + heading structure |

## Blind Spots
- <areas not covered or needing manual verification>

## Next Steps
- <re-audit after fixes, deeper dive, related skills>
- Re-run audit after fixes to see score improve
```

## Examples

### Full site audit
```
/adk-audit-site https://example.com
```
Audits all dimensions. Produces health score card, prioritized findings, and fix recommendations.

### Performance-focused audit
```
/adk-audit-site https://example.com --focus performance
```
Deep performance scan: Core Web Vitals, resource loading, render-blocking assets. Score and fix commands.

### Scoped accessibility audit
```
/adk-audit-site https://example.com/contact --focus accessibility --scope /contact
```
Accessibility audit of the contact page. WCAG compliance check, heading structure, form labeling.

## Anti-Patterns / Red Flags

- **Source-only guessing**: Saying "LCP is likely slow" from looking at HTML source without loading the page. Use `browser_navigate` + measurement, not static inference.
- **Exhaustive crawl**: Spidering 200 pages when the user asked about `/contact`. Confirm scope first; default to the target URL and its linked pages only.
- **Fix without ask**: Editing server config or HTML during the audit. The audit skill reports findings; it does not apply fixes unless explicitly asked.
- **Stale screenshots**: Reusing a screenshot from a previous audit or cached browser state. Every screenshot must come from a fresh `browser_navigate` + `browser_take_screenshot` in this session.
- **Hidden dimensions**: Scoring accessibility at 3/4 when the browser agent could not load the page (auth-gated). Unassessed dimensions must appear in Blind Spots with their max capped score.
- **Score inflation**: Giving performance 4/4 when Core Web Vitals were not measured because no browser was available. No measurement = max score of 2.
- **Generic findings**: Saying "improve SEO" instead of "page `/about` has no `<title>` tag, og:description is missing, and JSON-LD structured data is absent." Be specific with URLs and elements.

## Related Skills

- `adk-audit-repo` -- source-code repository audit
- `adk-test` -- test execution and verification
- `adk-design` -- design review and UX feedback
- `adk-review-docs` -- documentation review
