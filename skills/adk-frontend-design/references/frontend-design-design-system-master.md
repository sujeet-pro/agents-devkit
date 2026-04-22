# Design System Master

A repo-local source of truth for the visual + interaction language of the app being designed / built. Adapted from the UI-UX Pro Max master + page-overrides pattern (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), trimmed to ADK's "no Python, no embedded reasoning engine" constraint.

The design system lives in the TARGET app's repo, not under `.temp/`. It is itself a deliverable.

## Layout

```text
design-system/
├── MASTER.md           # Global source of truth (colors, typography, spacing, components, effects, anti-patterns)
└── pages/
    ├── landing.md      # Page-specific overrides (only deviations from MASTER)
    ├── checkout.md
    ├── dashboard.md
    └── ...
```

## Hierarchical retrieval

When implementing or designing a specific page:

1. First read `design-system/pages/<page-name>.md` if it exists.
2. If the page file exists, its rules override `MASTER.md`.
3. If the page file does not exist, use `MASTER.md` exclusively.

This pattern keeps the MASTER short and scannable while letting individual pages document their deliberate divergences (e.g., a checkout page that uses a stricter color palette than the rest of the app).

## `MASTER.md` template

```md
# Design System: <App Name>

## 1. Pattern

- **Type**: <Hero-Centric | Conversion-Optimized | Feature-Showcase | Minimal | Data-Dense Dashboard | Real-Time Monitoring | ...>
- **Conversion focus**: <emotion-driven | data-driven | trust-driven | exploration-driven>
- **Primary CTA placement**: <above fold | repeated after sections | sticky bottom>
- **Section order**: <Hero -> Services -> Testimonials -> CTA | Hero -> Features -> Pricing -> CTA | ...>

## 2. Style

- **Name**: <Soft UI Evolution | Glassmorphism | Brutalism | Bento Grid | AI-Native | Minimalism & Swiss | ...>
- **Keywords**: <3-5 short adjectives capturing the visual mood>
- **Best for**: <industry / product type>
- **Performance budget**: <Excellent | Good | Heavy>
- **Accessibility target**: WCAG 2.2 AA (mandatory)

## 3. Colors

| Token | Light | Dark | Notes |
| --- | --- | --- | --- |
| `color.bg` | `#FFFFFF` | `#0A0A0A` | App background |
| `color.surface` | `#F8F8F8` | `#1A1A1A` | Card / panel surface |
| `color.text` | `#1A1A1A` | `#F5F5F5` | Body text — contrast >= 4.5:1 |
| `color.text.secondary` | `#525252` | `#A3A3A3` | Secondary text — contrast >= 3:1 |
| `color.primary` | `#3B82F6` | `#60A5FA` | Primary actions |
| `color.cta` | `#10B981` | `#34D399` | Conversion-critical CTAs |
| `color.danger` | `#DC2626` | `#F87171` | Destructive actions |
| `color.border` | `#E5E5E5` | `#2A2A2A` | Dividers, borders |

## 4. Typography

- **Body**: `<font name>` (Google Fonts URL: <link>)
- **Heading**: `<font name>` (Google Fonts URL: <link>)
- **Mono** (when needed): `<font name>`
- **Mood**: <Elegant | Playful | Professional | Editorial | Tech>
- **Scale** (modular, base 16px):
  - `text.xs`: 12 / 1.4
  - `text.sm`: 14 / 1.5
  - `text.base`: 16 / 1.6
  - `text.lg`: 18 / 1.5
  - `text.xl`: 20 / 1.4
  - `text.2xl`: 24 / 1.3
  - `text.3xl`: 30 / 1.2
  - `text.4xl`: 36 / 1.1

## 5. Spacing & Layout

- **Spacing rhythm**: 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96
- **Container max widths**: mobile 100%, tablet 720px, desktop 1280px
- **Gutters**: 16px mobile, 24px tablet, 32px desktop
- **Section vertical rhythm**: 16 / 24 / 32 / 48 by hierarchy
- **Breakpoints**: 360 (small phone), 768 (tablet portrait), 1024 (tablet landscape), 1280 (desktop), 1440 (wide)

## 6. Effects

- **Shadows**: <flat | soft | strong>; ramp `shadow.sm` / `shadow.md` / `shadow.lg`
- **Transitions**: 150-300ms with platform-native easing (`cubic-bezier(0.4, 0, 0.2, 1)`)
- **Hover states**: <opacity shift | color shift | elevation shift>
- **Focus rings**: 2px outline, `color.primary` at 60% opacity, 2px offset
- **Loading**: skeleton (preferred) > spinner > shimmer; never blank

## 7. Components

For each component used in the app, document: shape, sizes, states (default/hover/focus/active/disabled/loading/empty/error), accessibility role, content rules.

| Component | Variants | States | Accessibility |
| --- | --- | --- | --- |
| Button | primary, secondary, ghost, destructive | default/hover/focus/active/disabled/loading | role=button; keyboard activated; aria-busy when loading |
| Card | flat, elevated | default/hover/active | semantic landmark when grouping |
| Input | text, password, email, number | default/focus/error/disabled | label always associated; aria-invalid on error |
| Modal | small, medium, large | open/closing | focus trap; ESC closes; aria-modal; restore focus on close |
| Toast | info, success, warning, error | enter/visible/leave | role=status (info) / role=alert (error); auto-dismiss respects reduced-motion |

## 8. Pre-delivery checklist (mandatory)

See `<task>-pre-delivery-checklist.md`. Every page / component must pass before "ready for review".

## 9. Anti-patterns

See `<task>-industry-anti-patterns.md` for industry-specific anti-patterns. Plus universal:

- No emojis as structural icons (use SVG: Phosphor / Heroicons / Lucide).
- No layout-shifting hover states.
- No `100vh` (use `100svh` to handle mobile browser chrome).
- No raw hex colors in components — use tokens.
- No font sizes outside the modular scale.
- No motion that ignores `prefers-reduced-motion`.
- No focus styles removed without replacement.

## 10. References

- `<task>-pre-delivery-checklist.md`
- `<task>-industry-anti-patterns.md`
- WCAG 2.2: https://www.w3.org/TR/WCAG22/
```

## `pages/<page>.md` template

Pages document ONLY the deviations from MASTER. Keep them short.

```md
# Design System Override: <Page Name>

## What this page overrides

- **Pattern section order**: deviates from MASTER section 1 because <reason>.
  - This page: Hero -> Pricing -> Testimonials -> CTA.
- **Color**: `color.cta` is `#FF6B35` here (instead of `#10B981`) because A/B test 2026-Q1 showed +12% conversion on this page.
- **Typography**: Heading uses `text.5xl` here (not in MASTER scale) because <reason>.

## What this page inherits unchanged

- All other tokens from MASTER.
- All component states from MASTER.
- The pre-delivery checklist still applies.
```

## When to use the master + overrides pattern

- The app has more than ~3 pages with meaningfully different visual language.
- Different teams own different pages and need to coordinate.
- The codebase has accumulated per-page hacks that should be formalized.

## When NOT to use it

- Single-page app or marketing landing — just have a `MASTER.md` and skip the `pages/` folder.
- Component library / design system shipped as a separate package — that has its own docs.
- Prototype / spike — too much overhead.

## Generation strategy

For a NEW app: generate `MASTER.md` from the user's stated product type, industry, audience, and style keywords. The `<task>-industry-anti-patterns.md` reference lists the no-go patterns per industry that the generated MASTER should avoid.

For an EXISTING app: extract the de-facto design system from the codebase first (read 5-10 representative components, list every color / font / spacing value used, identify the dominant pattern), then write `MASTER.md` to formalize the dominant patterns and explicitly call out inconsistencies that should be fixed.

## Validation

The pre-delivery checklist (`<task>-pre-delivery-checklist.md`) and the validator (`frontend-design-validator.md`) both reference this file. A page that does not match its `pages/<page>.md` (or MASTER if no override) is a Phase 3 BLOCKER.
