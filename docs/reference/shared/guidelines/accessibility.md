---
title: 'guidelines/accessibility'
description: '1. **Hold to WCAG 2.2 AA** for new UI. AAA where required by domain (healthcare, gov).'
source: 'shared/guidelines/accessibility.md'
group: 'shared-guidelines'
order: 6300
---
# shared/guidelines/accessibility

> Source: `shared/guidelines/accessibility.md`

# guideline: accessibility

> Loaded when the task touches UI components, forms, navigation, or anything keyboard / screen-reader / contrast.

## Hard rules

1. **Hold to WCAG 2.2 AA** for new UI. AAA where required by domain (healthcare, gov).
2. **Every interactive element has**: a name (visible label or aria-label), a role (semantic HTML or aria-role), a keyboard path (focusable + activatable).
3. **Color is never the only signal**. Pair color with text or icon. Error red + ✗ icon + "Error: ...".
4. **Contrast ratio**: 4.5:1 for normal text, 3:1 for large text (≥18pt or bold ≥14pt), 3:1 for UI components and graphical objects.
5. **Focus is visible**. Don't remove the outline; restyle if you must.
6. **Forms have labels**, not just placeholders. Placeholder is hint, not name.

## Keyboard

- **Tab order matches reading order**. Don't use `tabindex > 0`; use 0 or -1 only.
- **Escape closes** modals / popovers / dropdowns; returns focus to the trigger.
- **Arrow keys** for compound widgets (menubar, tabs, listbox, grid). Use a vetted lib (Radix, Headless UI).
- **Skip-to-content** link at the top of every page.

## Screen readers

- **Use semantic HTML**: `<button>` not `<div onClick>`; `<nav>` not `<div class="nav">`; `<h1>`-`<h6>` not `<div class="heading">`.
- **Headings form an outline**: one h1 per page; don't skip levels.
- **Lists are lists**: `<ul>` / `<ol>`, not styled divs.
- **Live regions** for dynamic content: `aria-live="polite"` for non-urgent, `aria-live="assertive"` for urgent (sparingly).
- **Hidden ≠ display:none**. Use `aria-hidden="true"` to hide from AT while keeping visible, `visually-hidden` class to hide visually but keep for AT, `display:none` to hide from both.

## Forms

- Every input has a `<label for>` or `<label>` wrapping. Required marker (✱) has a text equivalent in the label.
- Error messages: associated with the field via `aria-describedby`; announced via live region; not just color.
- Submit failures move focus to the first error.

## Anti-patterns

- `<div role="button">` instead of `<button>`. Use the button.
- Modal that traps focus but doesn't return it.
- Image without `alt`. Decorative: `alt=""`. Informative: describe what it conveys. Functional (icon button): name the action.
- `onclick` on a `<div>` without keyboard handler.
- Skip-to-content link styled `display:none` until focus — works, but use `position:absolute; left:-9999px` so it stays in tab order.
- Auto-playing media without controls.

## Test

- Tab through the page. Every interactive element reachable, focus visible.
- Use a screen reader (VoiceOver / NVDA) on a critical flow per change.
- Run axe-core or similar against the rendered DOM.
- Check at 200% zoom and at 320px viewport.

## Cite when reviewing

- Specific WCAG criterion violated (e.g., 1.4.3 Contrast Minimum, 2.1.1 Keyboard).
- The component's existing accessibility tests (if any).
- `frontend-design.md` for the broader UI rules.
