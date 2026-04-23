# Accessibility checklist — frontend design

Optional reference loaded by `frontend-design` to enforce WCAG 2.2 AA defaults at design time, not as a fix-later afterthought. Same rigor as `@adk:audit-site`'s a11y checklist, scoped to design choices instead of audit findings.

## Design-time decisions to lock in

- **Color palette has accessible pairs.** Every (text, background) pair meets ≥ 4.5:1 contrast (normal) / ≥ 3:1 (large text). Document the accessible pairs in the design system.
- **Touch targets ≥ 44×44 CSS px** (24×24 minimum per WCAG 2.2 SC 2.5.8). Spacing between targets ≥ 8 px.
- **Focus indicator** is part of the visual design, not "the browser default if we forget". Contrast ≥ 3:1 against background; ≥ 2 px thick.
- **Typography** scales correctly at 200% zoom; no fixed-px font sizes for body copy.
- **Component states** designed for: default, hover, focus, focus-visible (keyboard), active, disabled, loading, empty, error.
- **No info conveyed by color alone.** Status badges have icon + text + color.
- **Reduced motion variant** designed for any animation > 200 ms.
- **Dark mode pair** for any non-illustrative color.
- **Form errors** designed inline (next to the field) AND summarized at the top.

## Component-by-component minimums

### Button

- Solid hit area; min 44×44.
- Visible focus ring (≥ 3:1).
- Disabled: not just "lighter color" — also explicit `aria-disabled` semantic.
- Loading: announces "Loading..." via live region; doesn't lose focus.

### Input / textarea

- Persistent visible label (NOT just placeholder).
- Required indicator: text + symbol, not symbol alone.
- Error message: red border + icon + text; tied to field with `aria-describedby`.
- Inline validation announces only after blur (or after first submit).

### Modal / dialog

- Focus trapped inside while open.
- Esc closes (and returns focus to trigger).
- First focusable element receives focus on open (or the dialog itself with `tabindex="-1"` for screen-reader announcement).
- Background scroll locked.

### Menu / dropdown

- Arrow keys to navigate items.
- Enter/Space to select.
- Esc to close.
- Trigger has `aria-haspopup` + `aria-expanded`.

### Tooltip

- Triggered by hover AND keyboard focus.
- Persistent until dismissed (don't disappear on cursor move when content is important).
- `aria-describedby` from target to tooltip.

### Tabs

- `role="tablist"`, `role="tab"`, `role="tabpanel"`.
- Arrow-key navigation between tabs.
- Active tab has `aria-selected="true"`.
- Tab and panel linked via `aria-controls` / `aria-labelledby`.

### Toast / snackbar

- Persistent if action is required (don't auto-dismiss).
- Auto-dismiss only for confirmations; min 5 s.
- Live region (`role="status"` polite, `role="alert"` for errors).

### Skeleton / loading state

- Doesn't shift layout when real content loads (CLS).
- `aria-busy="true"` on the loading region.
- Provides at least an "idle" state announcement (optional, polite).

## Responsive breakpoints (defaults)

| Size | Width | Notes |
| --- | --- | --- |
| Small mobile | 320 px | Default; design must work here. |
| Mobile | 375 px | iPhone class. |
| Large mobile | 414 px | iPhone Pro Max class. |
| Tablet portrait | 768 px | iPad. |
| Tablet landscape / small laptop | 1024 px | |
| Desktop | 1280 px | |
| Large desktop | 1440 px+ | |

Design at 360 / 768 / 1280 minimum (per `@adk:frontend-feature` constitution). Verify at the others.

## Accessibility-related design tokens

Recommended token shape:

```ts
{
  color: {
    text: { primary: '#0F172A', secondary: '#475569', inverse: '#F8FAFC' },
    background: { default: '#FFFFFF', subtle: '#F8FAFC', inverse: '#0F172A' },
    border: { default: '#CBD5E1', strong: '#475569', focus: '#1D4ED8' },
    state: { error: '#B91C1C', warning: '#A16207', success: '#15803D', info: '#1D4ED8' },
  },
  motion: {
    duration: { fast: '150ms', normal: '250ms', slow: '400ms' },
    easing: { in: 'cubic-bezier(0.4, 0, 1, 1)', out: 'cubic-bezier(0, 0, 0.2, 1)' },
    reducedMotion: { duration: '0ms' },
  },
  size: {
    target: { min: '44px' },
    space: { focusRing: '2px' },
  },
}
```

## Anti-patterns

- "We'll fix a11y after launch" — far more expensive after the design is shipped.
- Designing only the default state — focus, hover, disabled, loading, empty, error are part of the design.
- Insufficient contrast in the brand palette — fix the palette, not the page-by-page exception list.
- Removing focus rings to "look cleaner" — restores the bug at speed.
- `placeholder`-as-label patterns — placeholder disappears on input.
- Modal that doesn't trap focus — keyboard users get lost in the underlying page.
- Tooltips on touch screens with no equivalent — content is invisible.
- Carousels that auto-rotate — moving content is hostile.
- Toasts with critical info that disappear in 2 s — unreadable for slow readers.
