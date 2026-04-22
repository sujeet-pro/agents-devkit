# `frontend-mockup` — sample HTML scaffold

Each `sample-N.html` MUST be self-contained:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sample N — <surface name></title>
  <style>
    /* All styles inline. No external CSS. */
    /* Use CSS custom properties at :root for the chosen palette + type ramp. */
    :root {
      --bg: #...;
      --fg: #...;
      --accent: #...;
      --font-display: '...', serif;
      --font-body: '...', sans-serif;
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { transition: none !important; animation: none !important; }
    }
    @media (max-width: 767px)  { /* mobile (360-767) */ }
    @media (min-width: 768px) and (max-width: 1279px) { /* tablet */ }
    @media (min-width: 1280px) { /* desktop */ }
  </style>
</head>
<body>
  <main>
    <!-- Real content from requirements.md, NOT lorem ipsum -->
  </main>
  <!-- All state demos: default, hover, focus, active, disabled, loading, empty, error -->
  <section aria-label="State variants">
    <!-- one preview per state -->
  </section>
</body>
</html>
```

## Hard requirements

- Self-contained: open `sample-N.html` directly in a browser, must render fully.
- No JS framework imports. Vanilla JS only if needed for an interaction demo.
- Real example data (from `requirements.md`) — no lorem ipsum.
- All applicable states demonstrated.
- WCAG 2.2 AA: contrast 4.5:1 (text), 3:1 (large/UI), keyboard reachable, focus visible.
- `prefers-reduced-motion` respected.
- Works at 360, 768, 1280 (test in browser-dev-tools or via `@adk:validate-browser`).
