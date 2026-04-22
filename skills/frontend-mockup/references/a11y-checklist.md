# `frontend-mockup` — a11y checklist (WCAG 2.2 AA)

Required for every sample:

- [ ] Color contrast: text ≥ 4.5:1, large text & UI components ≥ 3:1
- [ ] Visible focus ring on every interactive element (do not `outline: none` without replacing)
- [ ] All interactive elements keyboard reachable (Tab, Enter/Space, Arrow keys for menus)
- [ ] Skip-link to main if there's a long header
- [ ] Semantic HTML: use `<button>`, `<a>`, `<nav>`, `<main>`, `<header>`, `<footer>` per role; avoid `<div onclick>`
- [ ] ARIA only where semantic HTML doesn't cover it; never duplicate native semantics
- [ ] `prefers-reduced-motion` respected (disable transitions/animations)
- [ ] `prefers-color-scheme` supported if dark mode is in scope
- [ ] Form fields: associated `<label>`, `aria-describedby` for help text, `aria-invalid` + `aria-errormessage` on error
- [ ] Lang attribute on `<html lang="en">` (or per content)
- [ ] All images have alt text (empty `alt=""` if decorative)

Validate with `axe-core` via `@adk:validate-browser --mode a11y-audit`.
