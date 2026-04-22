# Pre-delivery Checklist

Mandatory checklist before declaring any page or component "ready for review". Adapted from the UI-UX Pro Max pre-delivery checklist (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), expanded with ADK's accessibility-first defaults.

Every item below is enforceable: if a check fails, the work is NOT done. The validator's Phase 3 (`<task>-validator.md`) treats unfinished checklist items as BLOCKER.

## Visual quality

- [ ] No emojis used as structural icons (use SVG: Phosphor `@phosphor-icons/react`, Heroicons `@heroicons/react`, or Lucide).
- [ ] All icons come from a single icon family with consistent stroke width and fill style.
- [ ] Icons sized via design tokens (e.g., `icon.sm` = 16px, `icon.md` = 20px, `icon.lg` = 24px). No arbitrary 18 / 22 / 26 mixing.
- [ ] All text uses tokens from the modular scale defined in `<task>-design-system-master.md`.
- [ ] All colors use semantic tokens (`color.bg`, `color.text`, `color.primary`). No raw hex inside components.
- [ ] Brand assets (logos, illustrations) use official sources with correct proportions and clear-space.
- [ ] Pressed-state visuals do not shift layout bounds (no jitter on tap).

## Interaction

- [ ] All tappable elements provide pressed feedback within 80-150ms (ripple / opacity / elevation).
- [ ] Touch targets meet platform minimum: >= 44x44pt (iOS) or >= 48x48dp (Android). Web: >= 44x44px or use `hitSlop`-equivalent padding.
- [ ] Micro-interaction timing in 150-300ms range with platform-native easing (`cubic-bezier(0.4, 0, 0.2, 1)` or platform default).
- [ ] Disabled states are visually clear AND non-interactive (cursor `not-allowed` on web; `disabled` attribute set; no tap action).
- [ ] Loading states are visible and respect timing (skeletons preferred for >300ms loads; spinners for <300ms).
- [ ] Empty states have informative content + clear next-step CTA.
- [ ] Error states explain what failed AND how to recover.
- [ ] No layout-shifting hover states (transforms that move neighbors).
- [ ] Gesture regions avoid nested/conflicting interactions (tap/drag/back-swipe conflicts).

## Accessibility (WCAG 2.2 AA mandatory)

- [ ] All meaningful images / icons have `alt` text or `aria-label`.
- [ ] Form fields have associated labels (`<label for>` / `aria-label` / `aria-labelledby`).
- [ ] Form fields have hint text + clear error messages with `aria-describedby` and `aria-invalid="true"` on error.
- [ ] Color is NEVER the only indicator (icons / text / patterns supplement color cues).
- [ ] Focus visible on all interactive elements (custom focus ring or `:focus-visible`).
- [ ] Tab order matches visual order; no tab traps outside modals.
- [ ] Modals trap focus AND restore focus to the trigger on close. ESC closes.
- [ ] Live regions (`role=status` / `role=alert`) announce dynamic changes (toasts, validation errors).
- [ ] Reduced motion supported: animations skip or simplify when `prefers-reduced-motion: reduce`.
- [ ] Dynamic Type supported: layout doesn't break at 200% font-size.
- [ ] Keyboard shortcuts documented and don't conflict with browser / screen reader defaults.
- [ ] Form errors are associated with their fields, NOT just shown in a summary far from the field.

## Light / Dark mode

- [ ] Primary text contrast >= 4.5:1 in both light and dark mode.
- [ ] Secondary text contrast >= 3:1 in both light and dark mode.
- [ ] Dividers, borders, and separators visible in BOTH themes (not just light).
- [ ] Modal scrim opacity strong enough to preserve foreground legibility (typically 40-60% black).
- [ ] Pressed / focused / disabled states equally distinguishable in light AND dark.
- [ ] Both themes tested before delivery — NOT inferred from a single theme.
- [ ] System theme follows `prefers-color-scheme`; user override available and persisted.

## Layout & Spacing

- [ ] Safe areas respected for headers, tab bars, bottom CTA bars (use `env(safe-area-inset-*)` on web; platform APIs on mobile).
- [ ] Scroll content not hidden behind fixed/sticky bars (apply `padding-bottom` matching the bar height).
- [ ] Verified at all required viewports: 360 (small phone), 768 (tablet portrait), 1024 (tablet landscape), 1280 (desktop), 1440 (wide).
- [ ] Verified in landscape orientation on mobile.
- [ ] Horizontal insets / gutters adapt by device size (16px mobile, 24px tablet, 32px desktop).
- [ ] 4 / 8dp spacing rhythm maintained across component / section / page levels.
- [ ] Long-form text remains readable on tablet / desktop (no edge-to-edge paragraphs over 70-80 chars per line).
- [ ] No `100vh` — use `100svh` (or `100dvh`) to handle mobile browser chrome.

## Performance

- [ ] First Contentful Paint < 1.5s on mid-tier mobile (CWV Good).
- [ ] Largest Contentful Paint < 2.5s.
- [ ] Cumulative Layout Shift < 0.1.
- [ ] Interaction to Next Paint < 200ms.
- [ ] Images use `loading="lazy"` for below-the-fold; `srcset` / `sizes` for responsive sources.
- [ ] Web fonts use `font-display: swap` (or `optional` for non-critical).
- [ ] No render-blocking JS in `<head>`.
- [ ] List virtualization for >50 items (Vue: virtual-scroller; React: TanStack Virtual; native: FlatList / RecyclerView).

## Code quality

- [ ] Component file is < 300 lines (split before this).
- [ ] No inline styles for design tokens (use the design system).
- [ ] Props are typed and documented.
- [ ] Component handles all 8 states from the design system: default / hover / focus / active / disabled / loading / empty / error.
- [ ] Tests cover at minimum: render-with-default-props, error state, loading state, accessibility (axe-core or equivalent).

## Stack-specific

Reference the relevant section in `<task>-design-system-master.md` "Components" for component-level requirements.

| Stack | Extra checks |
| --- | --- |
| React 19 | Server components used where data fetching is the only concern; client components only when hooks / events are needed. |
| Next.js | Metadata API used for SEO; `Image` component for all images. |
| SwiftUI | `Dynamic Type` scaling tested; `accessibilityLabel` / `accessibilityHint` set. |
| Jetpack Compose | `contentDescription` on icons; `Modifier.semantics` for custom controls. |
| React Native | `accessibilityLabel` / `accessibilityRole`; safe-areas via `react-native-safe-area-context`. |
| Flutter | `Semantics` widget; `MediaQuery.textScalerOf(context)` respected. |

## Final gate

When EVERY box above is checked AND the validator's Phase 3 + Phase 4 pass, the work is "ready for review". Until then it is "in progress" — surface the unfinished items in the report so the user knows what remains.
