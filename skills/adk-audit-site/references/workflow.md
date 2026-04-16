# ADK Audit Site Workflow

## Phase 1 -- Scope
**Gate: approval unless `--auto`**

1. Confirm the target URL (production, staging, or local)
2. Confirm the focus: `seo`, `performance`, `accessibility`, `security`, `content`, or `all`
3. Confirm scope narrowing: specific routes, pages, or surfaces
4. Clarify whether the user wants audit-only or audit-plus-fix proposals
5. If `--auto`, log the resolved target, focus, and scope, then proceed

**Approval prompt**: "Audit [URL] with [focus] lens. Scope: [routes/pages]. Mode: [audit-only / audit+fix]. Proceed?"

## Phase 2 -- Scan

Run per-dimension checks using the checklists defined in SKILL.md Phase 2.

### Performance
- Core Web Vitals: LCP, CLS, INP thresholds
- Render-blocking resources: undeferred CSS/JS in `<head>`
- Image optimization: lazy loading, compression, WebP/AVIF, missing width/height
- Bundle size: unminified JS/CSS, unused code, code splitting
- Caching: Cache-Control headers, CDN usage
- Network waterfall: sequential requests, preconnect/preload hints

### Accessibility
- Color contrast ratios against WCAG AA (4.5:1 normal, 3:1 large)
- ARIA roles, labels, states on interactive elements
- Keyboard navigation: focus indicators, tab order, keyboard traps
- Semantic HTML: heading hierarchy, landmarks, button vs div
- Alt text presence and quality on images
- Form labeling, error messaging, required indicators
- Touch targets (min 44x44px on mobile)

### SEO
- Meta tags: title, description, og:tags, twitter:cards (missing/duplicate)
- Structured data: JSON-LD/microdata validation against schema.org
- Canonical URLs and hreflang consistency
- Crawlability: robots.txt, sitemap.xml, noindex audit
- URL structure and mobile signals

### Security
- HTTPS: redirect from HTTP, certificate validity
- Security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy
- Mixed content: HTTP resources on HTTPS pages
- Exposed paths: debug endpoints, stack traces, directory listing
- Cookie security: Secure/HttpOnly/SameSite flags
- Subresource integrity on third-party scripts

### Content/UX
- Broken links: internal 404s, external dead links, redirect chains
- Image issues: oversized, missing responsive srcset, broken references
- Responsive design: content overflow, fixed widths on mobile
- User flow integrity: broken forms, dead-end pages, non-functional CTAs
- Loading states and flash of unstyled content

For each checklist item, record: checked/unchecked, evidence found, confidence level.

## Phase 3 -- Browser Check

1. Dispatch browser agent via `cursor-ide-browser` MCP (or equivalent browser automation tool)
2. Browser agent tasks using MCP tools:
   - `browser_navigate` to load each target page
   - `browser_take_screenshot` at mobile (375px), tablet (768px), and desktop (1440px) widths
   - `browser_console_messages` to capture JavaScript errors and warnings
   - `browser_snapshot` to inspect DOM structure, ARIA tree, and element refs
   - `browser_click` / `browser_type` to verify interactive elements (forms, nav, modals)
   - `browser_scroll` to check for overflow and lazy-load behavior
3. Collect browser findings as structured observations with screenshot evidence

**Browser agent contract**: Receives URL, scope, and focus. Returns screenshot evidence, console errors, render observations, and interaction test results. All browser observations carry High confidence since they are live-site evidence.

## Phase 4 -- Score

1. Aggregate findings per dimension from scan and browser phases
2. Calculate health score (0-4) per dimension using SKILL.md criteria:
   - 4 (Excellent): no P0 or P1 findings, at most minor P2/P3
   - 3 (Good): no P0, at most 1-2 P1, minor P2/P3
   - 2 (Fair): no P0, multiple P1 or notable P2 issues
   - 1 (Poor): 1+ P0 or many P1 findings
   - 0 (Critical): multiple P0 findings or systemic failure
3. Record the key finding per dimension (most impactful issue for score card)
4. Calculate aggregate score (sum of 5 dimensions, max 20)
5. Assign rating band: 18-20 Excellent, 14-17 Good, 10-13 Acceptable, 6-9 Poor, 0-5 Critical
6. Calculate before/after targets (expected score after fixing P0/P1 items)
7. If a dimension could not be fully assessed (no browser, auth-gated), cap its max score at 2 and note the gap

## Phase 5 -- Findings

1. Merge all findings from scan phase and browser check
2. Deduplicate overlapping findings across sources
3. Assign severity: P0 (Critical), P1 (High), P2 (Medium), P3 (Low)
4. Organize by dimension, then by severity within each dimension
5. Tag effort: quick-win, planned, strategic
6. Assign stable IDs: F1, F2, F3, ...
7. Include fix commands or specific remediation steps where applicable

## Phase 6 -- Report

1. Render health score card as a table (dimension, score, label, top issue)
2. Present findings grouped by severity, with dimension tags
3. List recommended actions with priority, effort, dimension, and target score impact
4. State before/after targets showing expected improvement
5. State blind spots: dimensions not assessed, auth-gated pages, JS-only content
6. Offer re-audit after fixes, deeper dive into specific dimension, or related skills

## Validation Rules

- Every finding cites a URL, audit output, browser observation, or page evidence
- Static-source claims about runtime behavior are labeled as unverified
- Browser screenshots or observations back visual and render findings
- Before/after comparisons are explicit when re-auditing after fixes
- Scores are traceable to the findings that produced them
- If a dimension could not be assessed (auth-gated, no browser access), it appears in blind spots
