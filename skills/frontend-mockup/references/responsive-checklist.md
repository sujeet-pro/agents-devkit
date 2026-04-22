# `frontend-mockup` — responsive checklist

Three viewport widths are mandatory:

- **360** — small mobile (iPhone SE territory)
- **768** — tablet portrait
- **1280** — laptop / desktop

Each sample must render correctly at each width. No horizontal scroll at 360. Touch targets ≥ 44×44 CSS pixels at mobile widths.

Use `@media` queries at exactly those breakpoints (or use `min-width` / `max-width` ranges that contain them).

Test by:
1. Opening `sample-N.html` in a browser
2. DevTools → device toolbar → set viewport to 360, 768, 1280 in turn
3. Or run `@adk:validate-browser --mode visual-check --target file://.../sample-N.html` which captures all three automatically.
