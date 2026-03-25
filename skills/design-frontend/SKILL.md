---
name: design-frontend
description: Create distinctive, production-grade frontend interfaces with high design quality. Generates 5 bold design variations as a visual HTML preview the user can open in a browser, then iterates until the design is finalized.
user_invocable: true
arguments:
  - name: description
    description: "What to design — component, page, application, or interface"
    required: true
  - name: framework
    description: "Target framework for final output: react, nextjs, vue, astro, svelte, vanilla (default: react)"
    required: false
  - name: style
    description: "Styling approach for final output: tailwind, css-modules, styled-components (default: tailwind)"
    required: false
  - name: theme
    description: "Light, dark, or auto (default: auto)"
    required: false
---

# Frontend Design

Use `skills/_references/agentic-teams.md`.

This skill creates distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. It produces **5 visually distinct design variations** as a single HTML preview file the user can open in their browser, then **iterates on feedback** until the design is locked.

> **Important**: The `framework` and `style` arguments define the *final deliverable* format. All preview rounds use **pure HTML/CSS/vanilla JS** so the user can visually compare without any build step.

---

## Phase 1 — Context & Design Thinking

Before any code, understand the brief:

- **Purpose**: What problem does this interface solve? Who uses it?
- **Constraints**: Technical requirements (framework, browser support, performance, accessibility).
- **Differentiation**: What makes this interface *memorable*? What is the one thing someone will remember?

---

## Phase 2 — Generate 5 Design Variations

Run **5 parallel child agents**, one per variation. Each agent must commit to a **different, bold aesthetic direction** and produce a complete, working implementation **in pure HTML and CSS** (with optional vanilla JS for interactions).

### Aesthetic Direction Rules

Each variation MUST choose a distinct aesthetic from a pool like (but not limited to):

1. **Brutally minimal** — extreme whitespace, monochrome or near-monochrome, stark typography, single accent color
2. **Maximalist / expressive** — layered textures, bold gradients, overlapping elements, density, saturated palette
3. **Retro-futuristic** — CRT glow, scan lines, monospace type, neon accents on dark backgrounds
4. **Organic / natural** — earth tones, rounded shapes, hand-drawn feel, soft shadows, natural textures
5. **Luxury / editorial** — serif display type, generous spacing, muted palette with gold or metallic accents, magazine-quality layout
6. **Playful / toy-like** — rounded everything, candy colors, bouncy animations, oversized elements
7. **Brutalist / raw** — system fonts, exposed grids, raw borders, intentionally "undesigned" aesthetic
8. **Art deco / geometric** — strong symmetry, gold lines, geometric patterns, decorative borders
9. **Soft / pastel** — light palette, gentle gradients, rounded cards, airy spacing, warm feel
10. **Industrial / utilitarian** — dark backgrounds, monospace data, LED-style accents, dashboard density
11. **Glassmorphism** — frosted glass, backdrop blur, translucent layers, vibrant backgrounds
12. **Neo-Memphis** — bold shapes, primary colors, asymmetric layouts, pattern fills, 90s-inspired
13. **Dark luxe** — deep blacks, sharp highlights, premium feel, cinematic contrast
14. **Paper / print** — newspaper columns, ink-style type, visible texture, off-white backgrounds

**No two variations may share the same aesthetic family.** Pick 5 that contrast sharply with each other.

### Per-Variation Requirements

Each child agent produces a **self-contained HTML/CSS snippet** (no build tools, no framework imports) that includes:

1. **Variation name & aesthetic label** (e.g., "Variation 3 — Neo-Memphis")
2. **Design rationale** — 2-3 sentences on why this direction fits the brief
3. **Key design choices**:
   - Typography: specific font pairing (display + body). **NEVER** use Inter, Roboto, Arial, or system-ui as display fonts. Use distinctive, characterful choices from Google Fonts or similar.
   - Color palette: 4-6 colors defined as CSS variables. Dominant color with sharp accents outperforms timid, evenly-distributed palettes.
   - Layout strategy: grid, asymmetric, single-column, magazine, dashboard, etc.
   - Signature detail: one memorable micro-interaction, texture, or visual flourish
4. **Complete working HTML/CSS** — fully self-contained:
   - All HTML structure and inline `<style>` blocks
   - CSS variables for theming consistency
   - Responsive design (mobile-first or desktop-first, stated clearly)
   - Animations and micro-interactions using pure CSS transitions/animations and vanilla JS only
   - Google Fonts loaded via `<link>` tags — no other external dependencies
   - Accessibility: semantic HTML, ARIA labels, keyboard navigation, sufficient contrast

### Aesthetic Quality Standards (apply to every variation)

- **Typography**: Beautiful, unique, interesting. Pair a distinctive display font with a refined body font. Never generic.
- **Color & Theme**: Cohesive palette defined in CSS variables. Bold, intentional choices.
- **Motion**: Focus on high-impact moments — a well-orchestrated page load with staggered reveals creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density — match the aesthetic.
- **Backgrounds & Visual Details**: Atmosphere and depth, not flat solid colors. Use gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, or grain overlays as appropriate to the aesthetic.

### What to AVOID across all variations

- Overused font families (Inter, Roboto, Arial, system fonts) as display or primary fonts
- Cliché color schemes — especially purple gradients on white backgrounds
- Predictable, cookie-cutter component layouts with no character
- Identical structural patterns across variations — each must feel like a different designer made it
- Placeholder or lorem ipsum content — use realistic, contextual content

---

## Phase 3 — Build & Open the Preview File

After all child agents complete, **assemble a single HTML preview file** and open it in the browser.

### Preview File Structure

Write a single file to `.design-preview/preview.html` (create the directory if needed). The file must:

1. Be a **complete, self-contained HTML document** — no external dependencies besides Google Fonts CDN links
2. Include a **top-level navigation bar** with buttons labeled "Variation 1", "Variation 2", … "Variation 5" that switch between variations (use vanilla JS to show/hide sections)
3. Each variation section contains:
   - A header strip with the variation name, aesthetic label, and 2-3 sentence rationale
   - The full rendered design below it
4. Include a **comparison strip** at the top or bottom showing key metadata for all 5 side by side (aesthetic, palette swatches, font names, signature detail)
5. Default to showing Variation 1 on load, with smooth transitions when switching

### Open in Browser

After writing the file, **immediately open it**:

```
open .design-preview/preview.html
```

On Linux use `xdg-open`, on macOS use `open`.

Then present the comparison summary to the user in the chat as well:

| # | Name | Aesthetic | Palette | Typography | Signature Detail |
|---|------|-----------|---------|------------|------------------|
| 1 | …    | …         | …       | …          | …                |
| 2 | …    | …         | …       | …          | …                |
| 3 | …    | …         | …       | …          | …                |
| 4 | …    | …         | …       | …          | …                |
| 5 | …    | …         | …       | …          | …                |

Ask the user: **"The preview is open in your browser. Which variation do you want to go with? I can also mix elements from multiple variations, or tweak any specific aspect — just tell me what to change."**

---

## Phase 4 — Iterate (repeat until the user says "done")

This is a **feedback loop**. After the user reviews the preview, they may:

- **Pick a variation** → proceed to Phase 5
- **Request changes** (e.g., "use the typography from 2 but the layout from 4", "make variation 3 darker", "add a sidebar to variation 1")
- **Ask for new variations** to replace ones they don't like

For each round of feedback:

1. Apply the requested changes to the HTML preview file
2. **Re-open the preview** in the browser (or refresh if already open — overwrite the same `.design-preview/preview.html` path so the browser tab can be refreshed)
3. Describe what changed in the chat
4. Ask for further feedback

**Keep iterating until the user explicitly picks a final direction** (e.g., "go with 3", "this is good", "done", "finalize this").

Do NOT move to Phase 5 until the user confirms.

---

## Phase 5 — Finalize to Target Framework

Once the user locks a design direction:

1. **Convert** the chosen pure-HTML variation into the target `framework` and `style` specified in the arguments (e.g., React + Tailwind, Next.js + CSS Modules, Vue + styled-components, or keep as vanilla if that's the target)
2. Add any missing interactive states (loading, empty, error, hover, focus, active, disabled)
3. Ensure full accessibility compliance (WCAG 2.1 AA minimum)
4. Extract reusable tokens and components if the scope warrants it
5. Write the final implementation files to the project (ask the user for the target path if not obvious)
6. Add integration notes: how to install fonts, required dependencies, responsive breakpoints

The `.design-preview/` directory can be kept for reference or deleted — ask the user.

---

## Reference Loading

- Load `skills/_references/guidelines/coding/design-system.md` when the output involves tokens or a component library
- Load `skills/_references/guidelines/coding/frontend-nextjs.md` when framework is Next.js
- Load `skills/_references/guidelines/coding/general.md` for general code quality

## Output

Phase 2-4: a visual HTML preview file opened in the browser, iterated on until the user is satisfied.
Phase 5: production-ready code in the target framework with integration notes.
