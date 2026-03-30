# UI Review Stage

Structured visual and UX review of frontend code covering 6 pillars: layout, typography, color, responsiveness, accessibility, and interaction states.

This stage is triggered by `--focus ui`. It does not modify source files. It produces a markdown review artifact and optionally posts findings through a source MCP.

**All review findings must follow the canonical format in `references/review-comment-template.md`.**

---

## Parameters (inherited from parent)

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<scope>` | `all`, file path, glob pattern, component name | `all` | Which frontend files to review |
| `--framework` | `react`, `vue`, `svelte`, `angular`, `html` | auto-detect | Override framework detection |
| `--publish` | flag | off | Post findings to PR source |
| `--mode` | `interactive`, `auto-approve` | `interactive` | Whether to present findings one-by-one or auto-accept all |

---

## Preflight

1. Resolve the `scope` argument into a concrete file list. When `scope=all`, discover all frontend files in the project (templates, components, stylesheets, layout files).
2. Detect the `framework` when not provided. Inspect `package.json`, file extensions, and import patterns to determine whether the project uses React, Vue, Svelte, Angular, or plain HTML/CSS.
3. Verify at least one scoped file exists and is readable before launching child agents.

## Review Pillars

Each finding must be tagged with one of these pillars:

1. **Layout & Spacing** -- grid alignment, padding/margin consistency, visual hierarchy, whitespace
2. **Typography** -- font pairing, size scale, line height, readability, font loading
3. **Color & Contrast** -- palette consistency, contrast ratios, dark/light mode, color blindness
4. **Responsiveness** -- breakpoint coverage, mobile-first or desktop-first, fluid layouts, touch targets
5. **Accessibility** -- semantic HTML, ARIA labels, keyboard navigation, screen reader, WCAG compliance
6. **Interaction States** -- hover, focus, active, disabled, loading, empty, error states

## Interactive Flow

### Phase 1: Review Execution

Launch child agents (one per pillar or grouped) to review the scoped files. Each agent produces findings in the canonical review comment template format, tagged with the pillar label and severity.

### Phase 2: Interactive Loop

Present findings one at a time, grouped by severity then by pillar:

```text
## Finding [N/total] - [severity] - [pillar]

File: <path:line>
Confidence: NN%

Issue: <description>

Suggested fix: <recommendation>

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

## Auto-Approve Flow

Used when `mode=auto-approve`.

1. Run preflight, guideline loading, and child agents.
2. Consolidate findings.
3. Accept all findings automatically -- no interactive loop.
4. Produce the markdown review artifact with all findings and the summary table.
5. If `publish` is set, post all findings through the matching MCP.

## Output

Always produce a markdown review artifact with:

- Severity-ordered findings using the canonical comment template from `references/review-comment-template.md`
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

1. [Pillar] path/to/file.ext:LINE -- <one-sentence fix description>
2. [Pillar] path/to/file.ext:LINE -- <one-sentence fix description>
3. [Pillar] path/to/file.ext:LINE -- <one-sentence fix description>
```
