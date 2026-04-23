# Accessibility checklist — site audit (WCAG 2.2 AA)

Optional reference loaded by `audit-site` when the audit covers accessibility (default). Each item maps to a WCAG success criterion; cite the SC number in findings.

## Keyboard

- [ ] Every interactive element is reachable by Tab in a sensible order. (WCAG 2.1.1)
- [ ] Tab order matches visual order. (2.4.3)
- [ ] Focus is visible at all times when keyboard is in use. (2.4.7, 2.4.11 in 2.2)
- [ ] No keyboard trap (Esc / Tab can leave any modal / menu). (2.1.2)
- [ ] Custom widgets (combobox, dialog, tabs) follow ARIA Authoring Practices for keyboard. (4.1.2)
- [ ] Skip-to-content link present and works on first Tab. (2.4.1)

## Screen reader

- [ ] Page has a unique, descriptive `<title>`. (2.4.2)
- [ ] One `<h1>` per page; heading levels not skipped. (1.3.1, 2.4.6)
- [ ] Landmarks present (`<main>`, `<nav>`, `<header>`, `<footer>`, `<aside>`). (1.3.1)
- [ ] All `<img>` have meaningful `alt` (or `alt=""` for decorative). (1.1.1)
- [ ] Form inputs have associated labels (`<label for>`, `aria-label`, or `aria-labelledby`). (3.3.2)
- [ ] Buttons have accessible names (text or `aria-label`). (4.1.2)
- [ ] Icons used as buttons have accessible names. (4.1.2)
- [ ] Live regions used for dynamic content (`aria-live` polite/assertive). (4.1.3)
- [ ] Status messages announced (e.g. "Saved", "Error: ..."). (4.1.3)

## Visual design

- [ ] Text contrast ≥ 4.5:1 (normal); ≥ 3:1 (large text ≥ 18px / 14px bold). (1.4.3)
- [ ] Non-text UI contrast ≥ 3:1 (icons, form borders). (1.4.11)
- [ ] Page works at 200% zoom without horizontal scrolling. (1.4.4)
- [ ] Page works at 400% zoom (responsive reflow). (1.4.10)
- [ ] No info conveyed by color alone (icon + label, pattern + color). (1.4.1)
- [ ] Touch targets ≥ 24×24 CSS pixels (2.2 SC 2.5.8) — recommended ≥ 44×44.
- [ ] `prefers-reduced-motion` honored — animations reduced or disabled. (2.3.3)
- [ ] `prefers-color-scheme` honored if dark mode supported.
- [ ] Focus indicator contrast ≥ 3:1 against adjacent colors. (2.4.11 in 2.2)

## Forms

- [ ] Required fields clearly indicated (text, not just `*`). (3.3.2)
- [ ] Error messages are specific and tied to the field. (3.3.1, 3.3.3)
- [ ] Error messages don't disappear before the user can read them.
- [ ] Form completion doesn't time out without warning. (2.2.1)
- [ ] Autocomplete attributes set on common fields (`autocomplete="email"` etc.). (1.3.5)

## Content / structure

- [ ] Language declared on `<html lang="...">`. (3.1.1)
- [ ] Reading order in source matches visual order. (1.3.2)
- [ ] Tables use `<th>` with `scope` for headers. (1.3.1)
- [ ] Lists use `<ul>` / `<ol>`, not `<br>` and `<div>`. (1.3.1)
- [ ] Links have descriptive text (avoid "click here", "read more"). (2.4.4)

## Common HTML patterns (correct vs wrong)

| Need | Correct | Wrong |
| --- | --- | --- |
| Button | `<button type="button">` | `<div onclick>` |
| Link | `<a href>` | `<button>` styled as link |
| Toggle | `<button aria-pressed="false">` | `<div role="button">` with no keyboard support |
| Dialog | `<dialog>` or `role="dialog" aria-modal="true"` + focus management | `<div>` overlay |
| Tooltip | `aria-describedby` on the target → `role="tooltip"` element | `title` attribute on a div |
| Tabs | `role="tablist"` + `tab` / `tabpanel`, arrow-key navigation | unstyled `<a href>` |
| Alert | `role="alert"` for transient | `console.log` |

## Live regions

| Use case | Attribute | Politeness |
| --- | --- | --- |
| Form-level error after submit | `role="alert"` | assertive |
| Status message ("Saved") | `role="status"` / `aria-live="polite"` | polite |
| Loading indicator | `aria-busy="true"` on the region | implicit |
| Search-result count update | `aria-live="polite"` | polite |

Don't overuse `assertive` — it interrupts the user.

## Testing tools

- **Automated** — catches ~30% of issues:
  - `npx @axe-core/cli https://example.com`
  - `npx pa11y https://example.com`
  - Lighthouse Accessibility audit (`npx lighthouse ... --only-categories=accessibility`)
- **Manual** (mandatory):
  - Keyboard-only navigation through every interactive flow.
  - Screen reader test (VoiceOver on macOS, NVDA / JAWS on Windows, TalkBack on Android, Orca on Linux).
  - 200% browser zoom.
  - High-contrast mode.
  - `prefers-reduced-motion` simulation in DevTools.

## Common anti-patterns

- `<div onclick>` instead of `<button>`.
- Custom dropdowns without keyboard support.
- Focus that visually disappears in custom themes (`outline: none` with no replacement).
- Color-only error indication.
- Auto-playing video or audio with no user control. (1.4.2)
- Carousels that auto-rotate without pause control.
- Modals that don't trap focus / don't return focus on close.
- Toasts that disappear in 2 seconds with critical info.
- `placeholder` used as the only label.
- Required marker is just a red asterisk with no text alternative.
