---
name: review-ui
description: "Use when you need a structured visual and UX review of frontend code covering layout, typography, color, responsiveness, accessibility, and interaction states"
user_invocable: true
arguments:
  - name: scope
    description: "Files, components, or pages to review (comma-separated paths or 'all')"
    required: true
  - name: framework
    description: "Frontend framework: react, vue, svelte, html, angular (auto-detected if omitted)"
    required: false
  - name: publish
    description: "Output format: markdown, source, both (default: markdown)"
    required: false
  - name: mode
    description: "Workflow mode: interactive (default), standard, auto-approve"
    required: false
---

# UI Review

Use the shared contracts in `skills/_references/agentic-teams.md`, `skills/_references/review-comment-template.md`, and `skills/_references/output-formats.md`.

**All review findings must follow the canonical format in `skills/_references/review-comment-template.md`.** This applies to findings presented interactively and to the final markdown review artifact.

This skill is review-only. It does not modify source files. It produces a markdown review artifact and optionally posts findings through a source MCP.

## Preflight

1. Resolve the `scope` argument into a concrete file list. When `scope=all`, discover all frontend files in the project (templates, components, stylesheets, layout files).
2. Detect the `framework` when not provided. Inspect `package.json`, file extensions, and import patterns to determine whether the project uses React, Vue, Svelte, Angular, or plain HTML/CSS.
3. Verify at least one scoped file exists and is readable before launching child agents.

## Guideline Loading

Always load when available:

- `skills/_references/guidelines/coding/frontend-nextjs.md`
- `skills/_references/guidelines/coding/design-system.md`

Also load repo-local coding guidance when present (e.g., `.cursorrules`, `AGENTS.md`, project-level style guides, or design token definitions).

Scan the project for design-token files, theme configuration, Tailwind config, or CSS custom-property definitions and make them available to all child agents so findings reference actual project values rather than generic defaults.

## The 6 Pillars

The review is organized around six pillars. Each pillar has a dedicated child agent that reviews every scoped file through its lens.

### Pillar 1: Layout & Spacing

- Grid alignment and consistent use of the project's grid system
- Spacing consistency — margin and padding values pulled from the design-token scale, not arbitrary values
- Visual hierarchy — primary, secondary, and tertiary content areas are clearly differentiated
- Density — information density is appropriate for the context (dashboard vs. marketing page vs. form)
- Container widths and max-width constraints
- Alignment of sibling elements across different viewport sizes

### Pillar 2: Typography

- Font scale adherence — sizes follow the project's type scale, not ad-hoc pixel values
- Line height and letter spacing — readable body text (1.4-1.6 line height) and appropriate heading spacing
- Heading hierarchy — `h1` through `h6` used in correct document order, no skipped levels
- Font weight and style consistency across similar elements
- Text truncation and overflow handling — long strings, dynamic content, and internationalization
- Readability — sufficient contrast between text and background, appropriate measure (line length)

### Pillar 3: Color & Contrast

- WCAG AA compliance — minimum 4.5:1 contrast ratio for normal text, 3:1 for large text
- WCAG AAA compliance — flag opportunities to reach 7:1 contrast for critical content
- Consistent palette usage — colors reference design tokens or theme variables, not hardcoded hex values
- Dark mode support — verify dark mode styles exist and maintain contrast ratios when the project supports a dark theme
- Color as sole indicator — ensure color is never the only means of conveying information (e.g., error states should also use icons or text)
- Focus indicator contrast — focus rings and outlines meet contrast requirements against all backgrounds

### Pillar 4: Responsiveness

- Breakpoint coverage — components render correctly at standard breakpoints (mobile, tablet, desktop, wide)
- Mobile-first patterns — styles build upward from the smallest viewport rather than overriding desktop styles
- Viewport handling — no horizontal scroll at any standard viewport, content reflows appropriately
- Touch targets — interactive elements are at least 44x44px on mobile
- Image and media handling — responsive images, appropriate aspect ratios, no layout shift on load
- Container query readiness — note components that would benefit from container queries over media queries

### Pillar 5: Accessibility

- ARIA labels and roles — interactive elements have accessible names, landmarks are correctly annotated
- Keyboard navigation — all interactive elements are reachable and operable via keyboard alone
- Focus indicators — visible focus rings on all focusable elements, logical focus order
- Screen reader support — meaningful alt text, aria-live regions for dynamic content, correct heading structure
- Reduced motion — `prefers-reduced-motion` respected for animations and transitions
- Semantic HTML — prefer native elements (`<button>`, `<nav>`, `<main>`) over generic `<div>` with ARIA roles

### Pillar 6: Interaction States

- Empty states — components handle zero-data scenarios with helpful messaging and calls to action
- Loading states — skeleton screens, spinners, or progressive loading indicators for async content
- Error states — user-facing error messages are clear, actionable, and appropriately styled
- Hover states — visual feedback on interactive elements (buttons, links, cards)
- Active and pressed states — distinct styling for the pressed/active moment
- Disabled states — visually distinct, not just reduced opacity; cursor and ARIA state correctly set
- Transition states — smooth transitions between states without layout shift or flicker

## Required Child Agents

Follow the contract in `skills/_references/agentic-teams.md`. Launch **6 child agents in parallel**, one per pillar:

- `layout-reviewer` — Pillar 1: Layout & Spacing
- `typography-reviewer` — Pillar 2: Typography
- `color-reviewer` — Pillar 3: Color & Contrast
- `responsiveness-reviewer` — Pillar 4: Responsiveness
- `accessibility-reviewer` — Pillar 5: Accessibility
- `interaction-state-reviewer` — Pillar 6: Interaction States

Each child agent receives:

1. The full list of scoped files to review.
2. The detected framework and its conventions.
3. The loaded guidelines and design-token definitions.
4. The checklist for its assigned pillar (from the section above).

Each child agent returns a list of findings. Each finding must include:

- The pillar name
- Severity: `critical`, `high`, `medium`, or `low`
- The file path and line number
- A confidence score (0-100)
- A description of the issue
- A concrete suggested fix with code

## Consolidation

After all child agents complete:

1. Collect findings from all 6 agents.
2. Deduplicate findings that reference the same file and line with overlapping issues (e.g., a color contrast finding and an accessibility finding about the same element — keep both but link them).
3. Assign a final severity to each finding. Child-agent severity is authoritative unless two agents disagree, in which case use the higher severity.
4. Sort findings by severity (critical first), then by pillar order, then by file path.
5. Filter findings below the confidence threshold (default: 70).

---

## Standard Flow

Used when `mode=standard`.

1. Run preflight, guideline loading, and child agents.
2. Consolidate findings.
3. Produce the markdown review artifact with all findings and the summary table.
4. If `publish` includes source posting, post findings through the matching MCP.

---

## Interactive Flow

Used when `mode=interactive` (the default).

### Phase 1: Review

1. Run preflight, guideline loading, and child agents.
2. Consolidate findings.

### Phase 2: Interactive Loop

Present each finding to the user one at a time in this format:

```text
## Finding [N/total] - [pillar] - [severity: critical|high|medium|low]

File: path/to/file.ext:LINE
Confidence: NN%

Issue: <what is wrong visually or from a UX perspective>

Suggested Fix:
<concrete code change showing the before/after or the addition needed>

Action: [A]ccept | [E]dit | [R]eject | [S]kip
```

#### Actions

- **Accept**: queue the finding for the final report as-is.
- **Edit**: let the user revise the finding description or suggested fix before queuing.
- **Reject**: discard the finding entirely.
- **Skip**: defer to the end. After all other findings are processed, return to skipped items for a final decision.

#### Loop Rules

1. Process findings in severity order (critical -> high -> medium -> low).
2. Within the same severity, group by pillar so the user reviews related findings together.
3. If the user says "accept all remaining", queue all unprocessed findings.
4. If the user says "reject all remaining", discard all unprocessed findings.
5. If the user says "accept all [pillar]", queue all remaining findings for that pillar.

### Phase 3: Summary and Output

After the loop finishes, display the interactive summary:

```text
## Interactive Review Summary

Accepted: N
Edited: N
Rejected: N
Skipped: N
```

Then produce the full review artifact containing only accepted and edited findings.

---

## Auto-Approve Flow

Used when `mode=auto-approve`.

1. Run preflight, guideline loading, and child agents.
2. Consolidate findings.
3. Accept all findings automatically — no interactive loop.
4. Produce the markdown review artifact with all findings and the summary table.
5. If `publish` includes source posting, post all findings through the matching MCP.

---

## Output

Always produce a markdown review artifact with:

- Severity-ordered findings using the canonical comment template from `skills/_references/review-comment-template.md`
- Confidence scores on every finding
- The pillar label on every finding
- The summary table (below)
- Top 3 priority fixes
- An overall score

### Summary Table

```text
## UI Review Summary

| Pillar             | Critical | High | Medium | Low |
|--------------------|----------|------|--------|-----|
| Layout & Spacing   |        N |    N |      N |   N |
| Typography         |        N |    N |      N |   N |
| Color & Contrast   |        N |    N |      N |   N |
| Responsiveness     |        N |    N |      N |   N |
| Accessibility      |        N |    N |      N |   N |
| Interaction States |        N |    N |      N |   N |

Total Findings: N (after deduplication and confidence filtering)
Overall Score: NN/100
```

### Overall Score Calculation

Start at 100 and deduct points based on accepted findings:

- Critical: -15 per finding
- High: -8 per finding
- Medium: -3 per finding
- Low: -1 per finding

Floor the score at 0. The score reflects the visual and UX quality of the scoped code.

### Top Priority Fixes

List the top 3 findings by impact. For each, include the pillar, file, and a one-sentence description of the fix. These are the highest-leverage changes the team should make first.

```text
## Top Priority Fixes

1. [Pillar] path/to/file.ext:LINE — <one-sentence fix description>
2. [Pillar] path/to/file.ext:LINE — <one-sentence fix description>
3. [Pillar] path/to/file.ext:LINE — <one-sentence fix description>
```

## Adjacent Skills

- `review-code-pr` — for full code review beyond visual and UX concerns
- `design-frontend` — for generating or refactoring frontend components
- `audit-performance` — for frontend performance profiling and optimization
