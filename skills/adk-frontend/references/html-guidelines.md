# HTML Coding Guidelines

Comprehensive reference for modern HTML best practices. Covers semantic markup, accessibility, forms, document structure, performance, and modern HTML features.

---

## 1. Semantic HTML5 Elements

Semantic elements convey meaning to browsers and assistive technologies. Use them instead of generic `<div>` and `<span>`.

### Element Reference

| Element | Purpose | Use When |
|---------|---------|----------|
| `<header>` | Introductory content or navigation | Page banner, article intro |
| `<nav>` | Navigation links | Primary nav, breadcrumbs, TOC |
| `<main>` | Dominant content | One per page, central content |
| `<article>` | Self-contained distributable content | Blog posts, product cards, comments |
| `<section>` | Thematic grouping with heading | Chapters, tab panels, grouped content |
| `<aside>` | Tangentially related content | Sidebars, related links, glossary |
| `<footer>` | Footer for nearest sectioning ancestor | Copyright, contact, related links |
| `<figure>` / `<figcaption>` | Self-contained with caption | Images, diagrams, code listings |
| `<time>` | Machine-readable date/time | Dates, times, durations |
| `<address>` | Contact info | Author/org contact details |
| `<mark>` | Highlighted text | Search highlights, attention |
| `<details>` / `<summary>` | Collapsible content | FAQ, expandable sections |
| `<dialog>` | Modal or non-modal dialog | Confirmations, forms, alerts |
| `<search>` | Search functionality container | Search forms |

### DO: Semantic structure

```html
<body>
  <header>
    <nav aria-label="Primary">
      <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/about">About</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <article>
      <header>
        <h1>Article Title</h1>
        <time datetime="2025-01-15">January 15, 2025</time>
      </header>
      <section>
        <h2>Introduction</h2>
        <p>Content here...</p>
      </section>
      <footer>
        <address>Written by Jane Doe</address>
      </footer>
    </article>

    <aside aria-label="Related articles">
      <h2>Related</h2>
      <ul><li><a href="/post-2">Related Post</a></li></ul>
    </aside>
  </main>

  <footer>
    <p>&copy; 2025 Company Name</p>
  </footer>
</body>
```

### DON'T: Div soup

```html
<!-- BAD: no semantic meaning, inaccessible -->
<div class="header">
  <div class="nav">
    <div class="nav-item"><a href="/">Home</a></div>
  </div>
</div>
<div class="main">
  <div class="article">
    <div class="title">Article Title</div>
  </div>
</div>
```

**Why:** Screen readers use semantic elements to build navigable document outlines. Divs are invisible to assistive technology.

---

## 2. Accessibility (A11y)

WCAG 2.1 AA is the minimum bar. Accessibility is a requirement, not polish.

### ARIA Rules

**First rule of ARIA:** Don't use ARIA if a native HTML element does the job.

```html
<!-- BAD: ARIA on a native element -->
<div role="button" tabindex="0" onclick="submit()">Submit</div>

<!-- GOOD: Native element with built-in semantics -->
<button type="submit">Submit</button>
```

### Landmarks

Every page needs these landmarks:
```html
<header role="banner">       <!-- implicit with <header> as direct child of <body> -->
<nav role="navigation">       <!-- implicit with <nav> -->
<main role="main">            <!-- implicit with <main> -->
<footer role="contentinfo">   <!-- implicit with <footer> as direct child of <body> -->
```

Add `aria-label` when multiple landmarks of the same type exist:
```html
<nav aria-label="Primary">...</nav>
<nav aria-label="Footer">...</nav>
```

### Labels and Descriptions

```html
<!-- Every interactive element MUST have an accessible name -->

<!-- Method 1: Visible label (preferred) -->
<label for="email">Email address</label>
<input id="email" type="email" />

<!-- Method 2: aria-label (when no visible label) -->
<button aria-label="Close dialog">
  <svg><!-- X icon --></svg>
</button>

<!-- Method 3: aria-labelledby (label from another element) -->
<h2 id="section-title">Settings</h2>
<form aria-labelledby="section-title">...</form>

<!-- Method 4: aria-describedby (supplementary description) -->
<input id="password" type="password" aria-describedby="pw-hint" />
<p id="pw-hint">Must be at least 8 characters</p>
```

### Keyboard Navigation

```html
<!-- All interactive elements must be keyboard accessible -->

<!-- DO: Use native interactive elements (keyboard support built in) -->
<button>Click me</button>
<a href="/page">Link</a>
<input type="text" />
<select>...</select>

<!-- DON'T: Custom interactive elements without keyboard support -->
<div class="button" onclick="doSomething()">Click me</div>

<!-- If you MUST use a div, add full keyboard support -->
<div role="button" tabindex="0"
     onclick="doSomething()"
     onkeydown="if(event.key==='Enter'||event.key===' ')doSomething()">
  Click me
</div>
```

### Focus Management

```html
<!-- Skip link for keyboard users -->
<a href="#main-content" class="skip-link">Skip to main content</a>

<!-- Focus trap for modals -->
<dialog>
  <!-- Focus is automatically trapped in native <dialog> -->
  <h2>Confirm Action</h2>
  <button autofocus>Confirm</button>
  <button>Cancel</button>
</dialog>
```

### Images

```html
<!-- Informative image: descriptive alt text -->
<img src="chart.png" alt="Sales increased 25% from Q1 to Q2 2025" />

<!-- Decorative image: empty alt -->
<img src="divider.png" alt="" />

<!-- Complex image: long description -->
<figure>
  <img src="org-chart.png" alt="Organization chart" aria-describedby="org-desc" />
  <figcaption id="org-desc">
    CEO reports to Board. VP Engineering and VP Product report to CEO...
  </figcaption>
</figure>

<!-- Icon with text: hide the icon -->
<button>
  <svg aria-hidden="true"><!-- icon --></svg>
  Save
</button>

<!-- Icon without text: label the icon -->
<button aria-label="Save">
  <svg aria-hidden="true"><!-- icon --></svg>
</button>
```

### Live Regions

```html
<!-- Announce dynamic content changes to screen readers -->
<div aria-live="polite" aria-atomic="true">
  <!-- Updated content is announced after current speech -->
  3 items in cart
</div>

<div role="alert">
  <!-- Immediately announced (assertive) -->
  Form submitted successfully!
</div>

<div role="status">
  <!-- Politely announced -->
  Loading... 45% complete
</div>
```

### Color and Contrast

- Text contrast ratio: at least 4.5:1 for normal text, 3:1 for large text (WCAG AA)
- Never convey information by color alone (add icons, text, or patterns)
- Test with Windows High Contrast Mode and forced-colors media query

---

## 3. Forms

### Structure

```html
<form>
  <!-- Group related fields -->
  <fieldset>
    <legend>Shipping Address</legend>

    <div>
      <label for="street">Street address</label>
      <input id="street" type="text" autocomplete="street-address" required />
    </div>

    <div>
      <label for="city">City</label>
      <input id="city" type="text" autocomplete="address-level2" required />
    </div>

    <div>
      <label for="state">State</label>
      <select id="state" autocomplete="address-level1" required>
        <option value="">Select...</option>
        <!-- options -->
      </select>
    </div>
  </fieldset>

  <button type="submit">Place Order</button>
</form>
```

### Validation

```html
<!-- Native validation with custom messages -->
<input type="email" required
       pattern="[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"
       title="Enter a valid email address" />

<!-- Inline error with aria -->
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error" />
<p id="email-error" role="alert" class="error">Please enter a valid email address</p>
```

### Input Types

Use the most specific type for mobile keyboard optimization:
```html
<input type="email" />     <!-- email keyboard -->
<input type="tel" />       <!-- phone keyboard -->
<input type="url" />       <!-- URL keyboard -->
<input type="number" />    <!-- numeric keyboard (use for countable values only) -->
<input type="search" />    <!-- search with clear button -->
<input type="date" />      <!-- native date picker -->
<input type="time" />      <!-- native time picker -->
<input type="color" />     <!-- color picker -->
<input type="range" />     <!-- slider -->
<input type="file" accept="image/*" />  <!-- file with filter -->
```

### Autocomplete

Add `autocomplete` attributes for autofill support:
```html
<input type="text" autocomplete="name" />
<input type="email" autocomplete="email" />
<input type="tel" autocomplete="tel" />
<input type="text" autocomplete="address-line1" />
<input type="text" autocomplete="cc-number" />
<input type="password" autocomplete="new-password" />
<input type="password" autocomplete="current-password" />
<input type="text" autocomplete="one-time-code" />
```

---

## 4. Document Structure

### Head

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="Concise page description under 160 chars" />

  <!-- Preconnect to external origins -->
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />

  <!-- Critical CSS inline, rest async -->
  <style>/* critical above-the-fold CSS */</style>
  <link rel="stylesheet" href="/styles.css" media="print" onload="this.media='all'" />

  <!-- Favicon -->
  <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
  <link rel="apple-touch-icon" href="/apple-touch-icon.png" />

  <!-- Open Graph -->
  <meta property="og:title" content="Page Title" />
  <meta property="og:description" content="Page description" />
  <meta property="og:image" content="https://example.com/og-image.jpg" />
  <meta property="og:url" content="https://example.com/page" />
  <meta property="og:type" content="website" />

  <title>Page Title - Site Name</title>
</head>
```

### Heading Hierarchy

```html
<!-- DO: Logical heading hierarchy (h1 > h2 > h3, no skips) -->
<h1>Page Title</h1>
  <h2>Section</h2>
    <h3>Subsection</h3>
    <h3>Subsection</h3>
  <h2>Section</h2>

<!-- DON'T: Skip heading levels or use headings for styling -->
<h1>Title</h1>
<h4>This is not a subsection, just styled smaller</h4>  <!-- BAD -->
<h2>Section</h2>
```

---

## 5. Performance

### Lazy Loading

```html
<!-- Images below the fold -->
<img src="photo.jpg" alt="Description" loading="lazy" decoding="async" />

<!-- Never lazy-load LCP image -->
<img src="hero.jpg" alt="Hero" fetchpriority="high" />

<!-- Iframes -->
<iframe src="https://example.com" loading="lazy" title="Embed description"></iframe>
```

### Resource Hints

```html
<!-- Preconnect: establish early connection -->
<link rel="preconnect" href="https://api.example.com" />

<!-- DNS Prefetch: resolve DNS early (fallback for preconnect) -->
<link rel="dns-prefetch" href="https://api.example.com" />

<!-- Preload: fetch critical resources early -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/hero.webp" as="image" />

<!-- Prefetch: fetch resources for next navigation -->
<link rel="prefetch" href="/next-page.html" />

<!-- Modulepreload: preload ES modules -->
<link rel="modulepreload" href="/app.js" />
```

### Responsive Images

```html
<!-- Art direction with <picture> -->
<picture>
  <source media="(min-width: 800px)" srcset="wide.webp" type="image/webp" />
  <source media="(min-width: 800px)" srcset="wide.jpg" />
  <source srcset="narrow.webp" type="image/webp" />
  <img src="narrow.jpg" alt="Description" />
</picture>

<!-- Resolution switching with srcset -->
<img src="photo-400.jpg"
     srcset="photo-400.jpg 400w, photo-800.jpg 800w, photo-1200.jpg 1200w"
     sizes="(min-width: 800px) 50vw, 100vw"
     alt="Description" />
```

### Script Loading

```html
<!-- Critical: inline small scripts -->
<script>/* critical inline JS */</script>

<!-- Defer: non-critical, execute after parsing (preserves order) -->
<script src="/app.js" defer></script>

<!-- Async: independent scripts, execute ASAP (no order guarantee) -->
<script src="/analytics.js" async></script>

<!-- Module: deferred by default -->
<script type="module" src="/app.mjs"></script>
```

---

## 6. Modern HTML Features

### Dialog

```html
<!-- Native modal dialog (focus trap, Escape to close, backdrop) -->
<dialog id="confirm-dialog">
  <h2>Confirm Action</h2>
  <p>Are you sure you want to delete this item?</p>
  <form method="dialog">
    <button value="cancel">Cancel</button>
    <button value="confirm" autofocus>Confirm</button>
  </form>
</dialog>

<button onclick="document.getElementById('confirm-dialog').showModal()">
  Delete Item
</button>
```

### Details/Summary

```html
<!-- Native collapsible content (no JS needed) -->
<details>
  <summary>View advanced options</summary>
  <div>
    <label><input type="checkbox" /> Enable feature X</label>
    <label><input type="checkbox" /> Enable feature Y</label>
  </div>
</details>

<!-- Exclusive accordion (name attribute) -->
<details name="faq">
  <summary>Question 1?</summary>
  <p>Answer 1.</p>
</details>
<details name="faq">
  <summary>Question 2?</summary>
  <p>Answer 2.</p>
</details>
```

### Popover

```html
<!-- Native popover (no JS for show/hide, light-dismiss) -->
<button popovertarget="menu">Open Menu</button>
<div id="menu" popover>
  <ul>
    <li><a href="/settings">Settings</a></li>
    <li><a href="/logout">Log out</a></li>
  </ul>
</div>
```

### Template and Slots

```html
<!-- Template for reusable markup (not rendered until cloned) -->
<template id="card-template">
  <article class="card">
    <h3></h3>
    <p></p>
  </article>
</template>
```

---

## 7. Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| `<div>` for everything | Use semantic elements (`<nav>`, `<main>`, `<article>`, etc.) |
| `<br>` for spacing | Use CSS margin/padding |
| `<table>` for layout | Use CSS Grid/Flexbox |
| `<b>` / `<i>` for meaning | Use `<strong>` / `<em>` (semantic) or CSS (visual only) |
| Empty `<a href="#">` | Use `<button>` for actions, real URLs for links |
| `onclick` on non-interactive elements | Use `<button>` or add `role="button"` + `tabindex="0"` + keyboard handler |
| Missing `alt` on `<img>` | Always provide alt text (empty `alt=""` for decorative) |
| `<div class="btn">` | Use `<button>` |
| Inline styles | Use CSS classes or custom properties |
| Missing `lang` on `<html>` | Always set `<html lang="en">` (or appropriate language) |
| `<input>` without `<label>` | Always associate a label with every form control |
| Heading levels for size | Use CSS for sizing, headings for hierarchy |
| Auto-playing media | Add `muted` attribute and never autoplay audio without user consent |
