# CSS Coding Guidelines

Comprehensive reference for modern CSS best practices. Covers layout, custom properties, modern features, responsive design, architecture, performance, animation, typography, color, and dark mode.

---

## 1. Layout: CSS Grid and Flexbox

### When to Use Each

| Use Case | Tool |
|---|---|
| Page-level layout (header, sidebar, main, footer) | Grid |
| Card grids, image galleries | Grid |
| Aligning items in a single row/column | Flexbox |
| Navigation bars, toolbars | Flexbox |
| Complex 2D layouts | Grid |
| Content reflow that wraps | Flexbox |
| Overlapping elements | Grid |
| Centering | Either (Grid is simpler) |

### Grid Patterns

```css
/* Page layout */
.layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: auto 1fr auto;
  grid-template-areas:
    "header header"
    "sidebar main"
    "footer footer";
  min-height: 100dvh;
}
.header  { grid-area: header; }
.sidebar { grid-area: sidebar; }
.main    { grid-area: main; }
.footer  { grid-area: footer; }

/* Responsive card grid (no media queries) */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(300px, 100%), 1fr));
  gap: 1.5rem;
}

/* Subgrid for aligned children */
.card {
  display: grid;
  grid-template-rows: subgrid;
  grid-row: span 3; /* header, body, footer */
}
```

### Flexbox Patterns

```css
/* Navbar */
.navbar {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.navbar-spacer { flex: 1; } /* push items to edges */

/* Center anything */
.centered {
  display: grid;
  place-items: center;
}

/* Holy grail with flexbox */
.container {
  display: flex;
  flex-wrap: wrap;
}
.sidebar { flex: 0 0 250px; }
.main    { flex: 1; min-width: 0; } /* min-width: 0 prevents overflow */
```

### DON'T: Float-based layouts

```css
/* BAD: floats for layout (legacy) */
.sidebar { float: left; width: 250px; }
.main { margin-left: 260px; }
.clearfix::after { content: ""; display: table; clear: both; }

/* GOOD: Grid or Flexbox (modern) */
.layout { display: grid; grid-template-columns: 250px 1fr; }
```

---

## 2. CSS Custom Properties (Variables)

### Token Architecture

```css
/* Layer 1: Primitive tokens (raw values) */
:root {
  --color-blue-500: oklch(0.55 0.2 250);
  --color-blue-600: oklch(0.45 0.2 250);
  --color-gray-100: oklch(0.95 0.01 250);
  --color-gray-900: oklch(0.15 0.02 250);
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
}

/* Layer 2: Semantic tokens (purpose) */
:root {
  --color-text: var(--color-gray-900);
  --color-text-muted: oklch(0.55 0.02 250);
  --color-bg: white;
  --color-bg-surface: var(--color-gray-100);
  --color-primary: var(--color-blue-500);
  --color-primary-hover: var(--color-blue-600);
  --space-section: var(--space-8);
  --space-element: var(--space-4);
  --radius-card: var(--radius-md);
}

/* Layer 3: Component tokens */
.card {
  --card-padding: var(--space-6);
  --card-radius: var(--radius-card);
  --card-bg: var(--color-bg-surface);
  padding: var(--card-padding);
  border-radius: var(--card-radius);
  background: var(--card-bg);
}
```

### DON'T: Scattered magic values

```css
/* BAD: hardcoded values repeated everywhere */
.header { background: #3b82f6; padding: 16px; border-radius: 8px; }
.button { background: #3b82f6; padding: 8px 16px; border-radius: 4px; }
.card   { background: #f1f5f9; padding: 24px; border-radius: 8px; }
```

---

## 3. Modern CSS Features

### Container Queries

```css
/* Size-based container queries */
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card { flex-direction: row; }
  .card-image { width: 40%; }
}

@container card (max-width: 399px) {
  .card { flex-direction: column; }
  .card-image { width: 100%; }
}

/* Style queries (check custom property values) */
@container style(--theme: dark) {
  .card { background: var(--color-bg-dark); }
}
```

### :has() Selector

```css
/* Style parent based on child state */
.form-group:has(input:invalid) {
  border-color: var(--color-error);
}

/* Card with image vs without */
.card:has(img) {
  grid-template-rows: 200px 1fr;
}
.card:not(:has(img)) {
  grid-template-rows: 1fr;
}

/* Navigation with active link */
nav:has(.active) .nav-indicator {
  opacity: 1;
}

/* Empty state */
.list:has(:not(li)) {
  display: none;
}
```

### :is() and :where()

```css
/* :is() -- groups selectors, takes HIGHEST specificity */
:is(h1, h2, h3, h4, h5, h6) {
  line-height: 1.2;
  text-wrap: balance;
}

/* :where() -- groups selectors, ZERO specificity (great for resets) */
:where(ul, ol) { list-style: none; padding: 0; }
:where(a) { color: inherit; text-decoration: none; }
```

### CSS Nesting

```css
/* Native CSS nesting (no preprocessor needed) */
.card {
  padding: var(--space-4);
  background: var(--color-bg-surface);

  & .title {
    font-size: 1.25rem;
    font-weight: 600;
  }

  &:hover {
    box-shadow: var(--shadow-md);
  }

  @media (width >= 768px) {
    padding: var(--space-6);
  }
}
```

### @layer (Cascade Layers)

```css
/* Control cascade order explicitly */
@layer reset, base, components, utilities;

@layer reset {
  *, *::before, *::after { box-sizing: border-box; }
  * { margin: 0; }
}

@layer base {
  body { font-family: system-ui, sans-serif; line-height: 1.6; }
  h1 { font-size: 2rem; }
}

@layer components {
  .card { /* component styles */ }
  .button { /* component styles */ }
}

@layer utilities {
  .sr-only { /* screen reader only */ }
  .visually-hidden { /* visually hidden */ }
}
```

---

## 4. Responsive Design

### Intrinsic Design (No Media Queries)

```css
/* Fluid typography with clamp() */
h1 { font-size: clamp(1.75rem, 1rem + 2.5vw, 3rem); }
h2 { font-size: clamp(1.375rem, 1rem + 1.5vw, 2.25rem); }
body { font-size: clamp(1rem, 0.9rem + 0.5vw, 1.125rem); }

/* Fluid spacing */
.section { padding: clamp(1.5rem, 1rem + 3vw, 4rem); }
.gap { gap: clamp(1rem, 0.75rem + 1.5vw, 2rem); }

/* Responsive grid without breakpoints */
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: clamp(1rem, 0.5rem + 2vw, 2rem);
}

/* Responsive flex wrap */
.flex-responsive {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.flex-responsive > * {
  flex: 1 1 min(300px, 100%);
}
```

### Container Queries for Component-Level Responsiveness

```css
/* Component adapts to its container, not the viewport */
.widget-container {
  container-type: inline-size;
}

.widget {
  display: flex;
  flex-direction: column;
}

@container (min-width: 500px) {
  .widget {
    flex-direction: row;
    gap: 2rem;
  }
}
```

### When You Need Media Queries

```css
/* Viewport units: use dynamic viewport (dvh/dvw) */
.hero { min-height: 100dvh; }

/* Logical properties for internationalization */
.card {
  margin-inline: auto;    /* left/right in LTR, right/left in RTL */
  padding-block: 1rem;    /* top/bottom */
  border-inline-start: 3px solid var(--color-primary);
}

/* User preference media queries */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

@media (prefers-color-scheme: dark) {
  :root { /* dark mode tokens */ }
}

@media (prefers-contrast: more) {
  :root { /* high contrast tokens */ }
}

/* Range syntax (modern) */
@media (768px <= width < 1024px) {
  /* tablet styles */
}
```

---

## 5. CSS Architecture

### BEM (Block Element Modifier)

```css
/* Use when: custom CSS, no utility framework */
.card { }                     /* Block */
.card__title { }              /* Element */
.card__title--highlighted { } /* Modifier */
.card--featured { }           /* Block modifier */

/* DO */
.search-form { }
.search-form__input { }
.search-form__button { }
.search-form__button--disabled { }

/* DON'T: deeply nested BEM */
.search-form__input__icon__svg { } /* too deep, flatten */
```

### CSS Modules

```css
/* Use when: React/Vue with component-scoped styles */
/* styles.module.css */
.card { padding: 1rem; }
.title { font-weight: 600; }
```

```tsx
import styles from './Card.module.css'
function Card() {
  return <div className={styles.card}><h2 className={styles.title}>Title</h2></div>
}
```

### Utility-First (Tailwind)

When Tailwind is detected, adjust guidelines:
- Use utility classes for most styling
- Extract components for repeated patterns (not `@apply` for everything)
- Use `@apply` sparingly (only in base layer or repeated patterns)
- Prefer Tailwind's design tokens over custom values

```html
<!-- DO: Tailwind utilities -->
<div class="flex items-center gap-4 rounded-lg bg-white p-6 shadow-md">
  <h2 class="text-lg font-semibold text-gray-900">Title</h2>
</div>

<!-- DON'T: @apply everything (defeats the purpose) -->
<style>
.card { @apply flex items-center gap-4 rounded-lg bg-white p-6 shadow-md; }
</style>
```

---

## 6. CSS Performance

### content-visibility

```css
/* Skip rendering for off-screen content */
.below-fold-section {
  content-visibility: auto;
  contain-intrinsic-size: 0 500px; /* estimated height */
}
```

### contain

```css
/* Tell the browser this element's internals won't affect outside layout */
.card {
  contain: layout style; /* or contain: content for stricter */
}
```

### will-change

```css
/* Hint to browser about upcoming changes (use sparingly) */
.animated-element {
  will-change: transform;
}

/* DON'T: will-change on everything */
* { will-change: transform, opacity; } /* BAD: wastes GPU memory */

/* DO: Add dynamically, remove after animation */
.card:hover { will-change: transform; }
```

### Minimize Reflows

```css
/* DO: Use transform for visual changes (compositing only, no reflow) */
.modal-enter { transform: translateY(20px); opacity: 0; }
.modal-active { transform: translateY(0); opacity: 1; }

/* DON'T: Animate layout properties (triggers reflow) */
.modal-enter { top: 20px; height: 0; } /* BAD */
```

---

## 7. Animation

### Prefer transform and opacity

```css
/* Only transform and opacity can be GPU-accelerated without reflow */
.card {
  transition: transform 200ms ease, opacity 200ms ease;
}
.card:hover {
  transform: translateY(-4px);
  opacity: 0.95;
}

/* DON'T animate: width, height, top, left, margin, padding, border */
```

### Respect Motion Preferences

```css
/* Always provide reduced motion fallback */
@media (prefers-reduced-motion: no-preference) {
  .animate-in {
    animation: slide-up 300ms ease-out;
  }
}

@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to   { transform: translateY(0); opacity: 1; }
}

/* Or disable all animations globally */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Scroll-Driven Animations

```css
/* Modern scroll-linked animations (no JS needed) */
.progress-bar {
  animation: grow-bar linear;
  animation-timeline: scroll(root);
}

@keyframes grow-bar {
  from { transform: scaleX(0); }
  to   { transform: scaleX(1); }
}
```

---

## 8. Typography

### Fluid Type Scale

```css
:root {
  /* Major Third scale (1.25 ratio) with fluid sizing */
  --text-xs:  clamp(0.75rem, 0.7rem + 0.25vw, 0.8rem);
  --text-sm:  clamp(0.875rem, 0.825rem + 0.25vw, 0.9375rem);
  --text-base: clamp(1rem, 0.925rem + 0.375vw, 1.125rem);
  --text-lg:  clamp(1.125rem, 1rem + 0.625vw, 1.375rem);
  --text-xl:  clamp(1.25rem, 1.05rem + 1vw, 1.75rem);
  --text-2xl: clamp(1.5rem, 1.15rem + 1.75vw, 2.5rem);
  --text-3xl: clamp(1.875rem, 1.3rem + 2.875vw, 3.5rem);
}

body {
  font-size: var(--text-base);
  line-height: 1.6;
}

h1 { font-size: var(--text-3xl); line-height: 1.1; }
h2 { font-size: var(--text-2xl); line-height: 1.2; }
h3 { font-size: var(--text-xl);  line-height: 1.3; }
```

### Font Loading

```css
/* Preload critical fonts */
/* In <head>: <link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin> */

@font-face {
  font-family: 'Inter';
  src: url('/fonts/inter.woff2') format('woff2');
  font-weight: 100 900;
  font-display: swap; /* Show fallback immediately, swap when loaded */
  font-style: normal;
}

/* Size-adjust for minimal layout shift */
@font-face {
  font-family: 'Inter-fallback';
  src: local('Arial');
  size-adjust: 107%;
  ascent-override: 90%;
  descent-override: 22%;
  line-gap-override: 0%;
}

body {
  font-family: 'Inter', 'Inter-fallback', system-ui, sans-serif;
}
```

### Text Wrapping

```css
/* Balance headings (equal line lengths) */
h1, h2, h3 { text-wrap: balance; }

/* Pretty body text (avoid orphans) */
p { text-wrap: pretty; }
```

---

## 9. Color

### Modern Color Spaces

```css
:root {
  /* OKLCH: perceptually uniform, great for palettes */
  --color-primary: oklch(0.55 0.2 250);
  --color-primary-light: oklch(0.75 0.15 250);
  --color-primary-dark: oklch(0.35 0.2 250);

  /* color-mix() for variations */
  --color-primary-hover: color-mix(in oklch, var(--color-primary) 85%, black);
  --color-primary-subtle: color-mix(in oklch, var(--color-primary) 15%, white);

  /* Relative color syntax for alpha */
  --color-primary-overlay: oklch(from var(--color-primary) l c h / 0.1);
}
```

### Dark Mode

```css
/* Method 1: color-scheme + light-dark() (simplest) */
:root {
  color-scheme: light dark;
  --color-text: light-dark(#1a1a1a, #e5e5e5);
  --color-bg: light-dark(#ffffff, #121212);
  --color-surface: light-dark(#f5f5f5, #1e1e1e);
}

/* Method 2: Semantic token swap */
:root {
  --color-text: var(--color-gray-900);
  --color-bg: white;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-text: var(--color-gray-100);
    --color-bg: var(--color-gray-900);
  }
}

/* Method 3: Class-based (user toggle) */
.dark {
  --color-text: var(--color-gray-100);
  --color-bg: var(--color-gray-900);
}
```

### DON'T: Pure black/white

```css
/* BAD: harsh contrast */
body { background: #000; color: #fff; }

/* GOOD: tinted darks and lights */
body { background: oklch(0.13 0.02 250); color: oklch(0.92 0.01 250); }
```

---

## 10. Modern CSS Reset

```css
@layer reset {
  *, *::before, *::after {
    box-sizing: border-box;
  }

  * {
    margin: 0;
  }

  html {
    color-scheme: light dark;
    hanging-punctuation: first last;
  }

  body {
    min-height: 100dvh;
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
  }

  img, picture, video, canvas, svg {
    display: block;
    max-width: 100%;
  }

  input, button, textarea, select {
    font: inherit;
    color: inherit;
  }

  p, h1, h2, h3, h4, h5, h6 {
    overflow-wrap: break-word;
  }

  h1, h2, h3 {
    text-wrap: balance;
  }

  p {
    text-wrap: pretty;
  }

  a {
    color: inherit;
    text-underline-offset: 0.15em;
  }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      animation-duration: 0.01ms !important;
      animation-iteration-count: 1 !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }
  }
}
```

---

## 11. Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| `float` for layout | CSS Grid or Flexbox |
| Vendor prefixes for well-supported features | Drop `-webkit-transform`, `-moz-border-radius`, etc. |
| `px` for font sizes | Use `rem` for font sizes, `em` for component-relative |
| `!important` everywhere | Fix specificity with layers, :where(), or restructure selectors |
| Over-qualified selectors `div.card ul.list > li.item > a` | Simplify: `.item > a` or `.item-link` |
| Magic numbers `margin-top: 37px` | Use design tokens |
| Hardcoded colors `#3b82f6` scattered | Use custom properties |
| `height: 100vh` on mobile (scrollbar issue) | Use `100dvh` |
| `z-index: 9999` | Use a z-index scale: `--z-dropdown: 100; --z-modal: 200; --z-toast: 300` |
| Styling with IDs `#header` | Use classes (IDs have highest specificity) |
| `*` selector for animation/transform | Too broad, wastes GPU memory |
| No `prefers-reduced-motion` | Always add motion fallbacks |
| CSS-in-JS with runtime (styled-components) in new projects | Prefer zero-runtime: CSS Modules, Tailwind, vanilla-extract |
| Duplicated property declarations | Use custom properties or shared tokens |
