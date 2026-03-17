---
name: frontend-design
description: Create distinctive frontend designs with 5 variations, interactive selection, and production-ready code
user_invocable: true
arguments:
  - name: description
    description: "What to design (e.g., 'dashboard for analytics app', 'landing page for SaaS')"
    required: true
  - name: framework
    description: "Target framework: react, nextjs, astro, vanilla (default: react)"
    required: false
  - name: style
    description: "CSS approach: tailwind, css-modules, styled-components (default: tailwind)"
    required: false
---

# Frontend Design Skill

Create distinctive, production-grade frontend interfaces with 5 unique design variations, an interactive preview system, and final production-ready code output.

## Instructions

You MUST follow each phase in order. Do not skip phases or combine them.

---

## Phase 1: Design Framework

Before writing ANY code, establish a design framework.

### 1.1 Understand the Request

- Identify the **purpose** of the interface (what problem does it solve?)
- Identify the **audience** (developers? executives? consumers? general public?)
- Identify the **context** (standalone page? part of a larger app? marketing site?)
- Read the project's `package.json`, `tsconfig.json`, and any existing style configuration to understand conventions

### 1.2 Define 5 Distinct Aesthetic Directions

Create 5 variations, each with a **name** and **1-sentence description**:

1. **Bold/Dramatic** — e.g., brutalist, maximalist, dark luxury, high contrast
2. **Clean/Minimal** — e.g., Swiss design, Apple-like minimalism, whitespace-heavy
3. **Warm/Organic** — e.g., soft gradients, rounded corners, warm earth tones, gentle shadows
4. **Playful/Creative** — e.g., illustrated elements, vibrant colors, animated, hand-drawn feel
5. **Professional/Corporate** — e.g., enterprise SaaS, data-dense, structured grid, formal

### 1.3 Define Design Tokens for Each Variation

For EACH of the 5 variations, define:

- **Typography**: Font pairings (heading + body), sizes, weights, line-heights. Use real fonts from Google Fonts or system font stacks.
- **Color Palette**: Primary, secondary, accent, success, warning, error, and neutral scale (50-950). Express as CSS custom properties.
- **Spacing & Layout**: Grid system, spacing scale, max-width constraints, layout philosophy (dense vs. airy).
- **Motion & Animation**: Transition durations, easing functions, entrance/exit patterns, hover effects, micro-interactions.
- **Key Visual Elements**: Borders, shadows, border-radius, gradients, textures, icons style, imagery approach.

### 1.4 Present to User

Present all 5 directions to the user in a table or structured list with:
- Variation number and name
- 1-sentence aesthetic description
- Font pairing
- Primary/accent color swatches (use color names or hex)
- One distinguishing visual characteristic

Ask the user: "Would you like me to generate all 5 variations, or would you like to adjust any direction before I proceed?"

---

## Phase 2: Generate Variations

Generate a **complete, working component** for each of the 5 variations.

### 2.1 File Structure

Create the following structure in the project:

```
designs/
├── variation-1-bold/
│   ├── index.tsx (or .astro, .html based on framework argument)
│   └── styles.css (if not using Tailwind)
├── variation-2-minimal/
│   ├── index.tsx
│   └── styles.css
├── variation-3-warm/
│   ├── index.tsx
│   └── styles.css
├── variation-4-playful/
│   ├── index.tsx
│   └── styles.css
├── variation-5-professional/
│   ├── index.tsx
│   └── styles.css
└── preview.html
```

Use the appropriate file extension based on the `framework` argument:
- `react` or `nextjs` → `.tsx`
- `astro` → `.astro`
- `vanilla` → `.html`

### 2.2 Component Requirements

Each variation MUST include:

- **Full component code** with all markup, styles, and logic
- **Responsive design** using a mobile-first approach (test at 320px, 768px, 1024px, 1440px breakpoints)
- **Dark mode support** via `prefers-color-scheme` media query AND a manual toggle using a `data-theme` attribute
- **Accessibility**:
  - Semantic HTML elements (`<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`)
  - ARIA labels and roles where appropriate
  - Keyboard navigation support (focus-visible, tab order)
  - Focus management for interactive elements
  - Color contrast ratios meeting WCAG 2.1 AA
  - Screen reader announcements for dynamic content
- **Realistic placeholder content** — use believable names, numbers, descriptions. NEVER use "Lorem ipsum" or "John Doe".
- **Loading states**, **empty states**, and **error states** where applicable
- **Micro-interactions**: hover effects, button press feedback, smooth transitions

### 2.3 CSS Approach

Based on the `style` argument:

- **tailwind**: Use Tailwind utility classes. Include a `<script src="https://cdn.tailwindcss.com">` tag in preview for standalone rendering. Define custom theme values in a `<script>` block.
- **css-modules**: Generate `.module.css` files alongside components. For preview, inline the styles.
- **styled-components**: Use styled-components with a ThemeProvider. For preview, include the styled-components CDN.

Default to **tailwind** if not specified.

### 2.4 Design Quality Rules

- NEVER use generic AI-generated aesthetics (avoid the typical "gradient purple-to-blue hero with rounded cards" pattern)
- Each variation MUST be **distinctly different** — not just color swaps. Different layouts, typography hierarchies, visual metaphors, and interaction patterns.
- Use real typography from Google Fonts (include `<link>` tags)
- Include meaningful micro-interactions and animations (CSS transitions, keyframe animations)
- Consider loading states, empty states, error states
- Code must be **production-ready**, not prototype quality
- All components should be self-contained and work independently

---

## Phase 3: Preview System

Generate a `preview.html` file in the `designs/` directory.

### 3.1 Preview Requirements

The preview file MUST be:

- A **single, self-contained HTML file** (no external dependencies except CDN links for fonts/Tailwind)
- Openable directly in a browser via `open designs/preview.html`
- Contains all 5 variations embedded as separate sections

### 3.2 Preview Structure

```html
<!-- Navigation bar at the top -->
<nav> Tabs for: Variation 1 | Variation 2 | Variation 3 | Variation 4 | Variation 5 </nav>

<!-- Each variation in its own section, shown/hidden by tabs -->
<section id="variation-1"> ... full rendered variation ... </section>
<section id="variation-2"> ... full rendered variation ... </section>
<!-- etc. -->
```

### 3.3 Preview Features

- **Tab navigation** at the top to switch between variations (only one visible at a time)
- Each tab shows the variation name and 1-line description
- A **"Select this design"** button for each variation (logs selection to console and shows an alert)
- **Responsive preview**: Include buttons to simulate mobile (375px), tablet (768px), and desktop (1440px) widths using an iframe resize approach
- **Dark mode toggle** that applies to the currently viewed variation
- The navigation bar itself should be minimal and not distract from the designs

### 3.4 Inform the User

After generating the preview, tell the user:

```
Preview generated! Open it in your browser:
  open designs/preview.html

Review all 5 variations and let me know:
  - "Pick variation 3" to use that design
  - "Iterate on 2 and 4" to refine those
  - "Take the colors from 1 but the layout from 3" to create a hybrid
```

---

## Phase 4: Interactive Selection

Wait for user feedback and respond accordingly.

### 4.1 Handle Selection Commands

- **"Pick variation N"** → Proceed to Phase 5 with that variation
- **"Iterate on N"** → Create 2-3 new sub-variations of that design with refinements, update preview.html
- **"Iterate on N and M"** → Create new variations blending elements from both, update preview.html
- **"Take X from N but Y from M"** → Create a hybrid variation combining specific elements, update preview.html
- **"Change the colors to..."** → Apply color changes to the selected variation
- **"Make it more..."** → Adjust the design in the specified direction
- **Free-form feedback** → Interpret and apply changes, show updated preview

### 4.2 Iteration Rules

- Each iteration round updates `preview.html` with the new variations
- Keep previous variations accessible (add them as additional tabs)
- Label iterations clearly (e.g., "Variation 3 — Iteration 2")
- Maximum 3 iteration rounds before encouraging a final pick

---

## Phase 5: Apply Design

Once the user selects a final design, apply it to the project.

### 5.1 Project Integration

Read the project structure and conventions, then:

- **Next.js project**: Create components in the appropriate directory (`app/`, `components/`, `src/`), use the project's existing patterns (server components, client components, layouts)
- **React project**: Create components following existing structure, match existing state management patterns
- **Astro project**: Create `.astro` files with proper frontmatter, use existing layout patterns
- **Vanilla**: Create clean HTML/CSS/JS files

### 5.2 Code Organization

- Extract **design tokens** into CSS custom properties in a shared file (e.g., `tokens.css` or `theme.ts`)
- Create **reusable sub-components** from repeated patterns (buttons, cards, inputs, etc.)
- Separate **layout components** from **content components**
- Follow existing project naming conventions (PascalCase, kebab-case, etc.)

### 5.3 Final Checklist

Before finishing, verify:
- [ ] All components render without errors
- [ ] Responsive at all breakpoints
- [ ] Dark mode works
- [ ] Keyboard navigation works
- [ ] No hardcoded values that should be tokens
- [ ] No placeholder content that should be dynamic
- [ ] File structure matches project conventions
- [ ] All imports are correct

### 5.4 Cleanup

- Optionally remove the `designs/` preview directory (ask user)
- Provide a summary of all files created/modified

---

## Code Block Formatting

When showing code in conversation (not in files), use expressive-code properties:
- `file=filename.tsx` to show the filename
- `{3-5}` to highlight important lines
- `collapse={1-5}` for collapsible boilerplate (imports, etc.)

Example:
````
```tsx file=components/Hero.tsx {7-12} collapse={1-3}
import React from 'react';
import { motion } from 'framer-motion';
import styles from './Hero.module.css';

export function Hero({ title, subtitle }) {
  return (
    <section className={styles.hero}>
      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {title}
      </motion.h1>
    </section>
  );
}
```
````
