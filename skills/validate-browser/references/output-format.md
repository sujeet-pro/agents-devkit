# `validate-browser` — output format (per mode)

## Status banner (each turn)

```
[adk:validate-browser] mode=<verify-fix|visual-check|console-audit|interaction-test|a11y-audit> backend=<chrome-devtools-mcp|cursor-ide-browser-mcp|playwright-mcp|npx-playwright> target=<url-or-file>
```

Backend selection priority: `chrome-devtools-mcp` (1st, Claude's built-in) → `cursor-ide-browser-mcp` (2nd, when host is Cursor) → `playwright-mcp` (3rd) → `npx-playwright` (4th, last resort).

## verify-fix/report.md

```markdown
# verify-fix — <task-slug>

**Target:** <url>
**Repro:** <path/to/repro.md>
**Result:** PASS | FAIL

## Steps walked
| # | Action | Expected | Actual | Screenshot | Status |
|---|--------|----------|--------|------------|--------|

## Console — original error signature
- pattern: `<regex>`
- present-before: yes (cited from repro)
- present-after: no  (✓ fix holds)

## Network failures during walk
(none) | (list)
```

## visual-check/report.md

```markdown
# visual-check — <task-slug>

**Target:** <url>
**Viewports:** 360, 768, 1280
**Threshold:** 0.5% pixel diff
**Result:** PASS | FAIL | FIRST_RUN

## Per viewport
| viewport | actual | baseline | diff% | status |
|----------|--------|----------|-------|--------|
| 360 | actual/360.png | baseline/360.png | 0.12% | PASS |
| 768 | actual/768.png | baseline/768.png | 1.84% | FAIL → diff/768.png |
| 1280 | actual/1280.png | baseline/1280.png | 0.31% | PASS |
```

## console-audit/report.md

```markdown
# console-audit — <task-slug>

**Target:** <url>
**Wait idle:** 5s

## Findings (severity-tiered)
- [Blocker]    1 console error: `Uncaught TypeError: x.y is not a function (vendor.js:1234)`
- [Critical]   1 failed network request: 500 GET /api/users
- [Should]     3 console warnings: deprecated React lifecycle
- [Nitpick]    blocked third-party tracker (chrome only)

## Raw
- raw.json (full console + network arrays)
```

## interaction-test/trace.md

```markdown
# interaction-test — <task-slug>

**Target:** <url>
**Script:** <path/to/script.yaml>
**Result:** PASS | FAIL

## Steps
| # | Action | Selector | Expected | Actual | Screenshot | Status |
```

## a11y-audit/report.md

```markdown
# a11y-audit — <task-slug>

**Target:** <url>
**Viewports:** 360, 768, 1280
**Standards:** WCAG 2.0 A/AA, WCAG 2.1 AA, WCAG 2.2 AA
**Result:** PASS | FAIL

## Violations (severity-tiered)
- [Blocker] color-contrast — 4 instances — WCAG 1.4.3 — affected: button.primary, ...
- [Critical] label — 2 instances — WCAG 1.3.1, 4.1.2
- [Should] heading-order — 1 instance — WCAG 1.3.1
```
