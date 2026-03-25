# Design System Repository

This is a **design system** repository. All code, reviews, and generation must follow design system principles and standards.

## Devkit Integration

Load design-system guidelines from the agents-devkit installation:

```
~/.claude/guidelines/general.md        — baseline code quality rules
~/.claude/guidelines/design-system.md  — design system-specific rules (if available)
```

Always apply both the general and design-system guidelines when reviewing or generating code in this repo.

## Architecture: Layered Token System

This design system follows a strict layered architecture. Each layer builds on the one below it. Never skip layers.

```
Tokens (foundation)
  └─ Primitives (base UI elements: colors, typography, spacing)
       └─ Components (composed UI elements: Button, Input, Card)
            └─ Patterns (composed layouts: Form, Dialog, Navigation)
```

### Layer Rules

1. **Tokens** define raw values (colors, font sizes, spacing units, breakpoints). They are the single source of truth for all visual properties.
2. **Primitives** consume tokens to define base-level UI atoms (e.g., a `Box`, `Text`, or `Icon` primitive). Primitives must not contain business logic.
3. **Components** compose primitives and tokens into reusable UI elements (e.g., `Button`, `TextField`, `Card`). Components must expose a stable, documented public API.
4. **Patterns** compose components into higher-order layouts (e.g., `FormField`, `NavigationBar`, `DialogLayout`). Patterns encode UX behavior and layout decisions.

## Design Token Enforcement

All visual values MUST come from design tokens. Hardcoded values are not permitted.

### Required

- Colors via token references (e.g., `var(--color-primary-500)`, `theme.colors.primary.500`)
- Spacing via token scale (e.g., `var(--space-4)`, `theme.space[4]`)
- Typography via token definitions (e.g., `var(--font-size-body)`, `theme.fontSizes.body`)
- Border radius via tokens (e.g., `var(--radius-md)`)
- Shadows via tokens (e.g., `var(--shadow-sm)`)
- Breakpoints via tokens (e.g., `var(--breakpoint-md)`)

### Prohibited

- Hardcoded color values (`#ff0000`, `rgb(255, 0, 0)`, `red`)
- Hardcoded pixel values for spacing (`margin: 16px` instead of `margin: var(--space-4)`)
- Hardcoded font sizes (`font-size: 14px` instead of `font-size: var(--font-size-sm)`)
- Magic numbers without token references

## Accessibility Standards (WCAG 2.1 AA)

All components MUST meet WCAG 2.1 Level AA compliance. This is non-negotiable.

### Requirements

- **Color contrast**: Minimum 4.5:1 for normal text, 3:1 for large text (18px+ bold or 24px+)
- **Keyboard navigation**: All interactive components must be fully operable via keyboard (Tab, Shift+Tab, Enter, Space, Escape, Arrow keys where appropriate)
- **Focus indicators**: Visible focus styles on all interactive elements. Never use `outline: none` without providing an alternative focus indicator.
- **ARIA attributes**: Use ARIA roles, states, and properties when native HTML semantics are insufficient. Never use incorrect or redundant ARIA.
- **Screen reader support**: All components must announce their purpose, state, and changes to assistive technology.
- **Motion**: Respect `prefers-reduced-motion`. All animations must have a reduced-motion fallback.
- **Touch targets**: Minimum 44x44px touch target size for interactive elements on touch devices.

### Component Accessibility Checklist

Every component must include:
- [ ] Semantic HTML elements used where possible
- [ ] ARIA labels for non-text interactive elements
- [ ] Keyboard event handlers alongside pointer event handlers
- [ ] Focus management for compound components (e.g., combobox, menu, tabs)
- [ ] Role and state announcements for dynamic content
- [ ] Color-independent state indication (not relying on color alone)

## Component API Stability

The public API of every component is a contract. Breaking changes require explicit justification and a migration path.

### API Rules

1. **Props are the public API.** Every prop must be documented with its type, default value, and description.
2. **No prop removal without deprecation.** Deprecated props must log a console warning in development and be documented in the changelog.
3. **No type narrowing.** A prop that accepts `string | number` must not be changed to accept only `string`.
4. **No behavioral changes to existing props.** If a prop called `variant` accepts `"primary"` and it renders blue, changing it to render green is a breaking change.
5. **New required props are breaking.** Adding a required prop to an existing component is a breaking change.
6. **Ref forwarding.** All components that render DOM elements must forward refs.
7. **Spread props.** Components should spread remaining props onto the root DOM element to support `className`, `style`, `data-*`, and `aria-*` attributes.

## Documentation Requirements

Every exported component, token, and utility must have documentation.

### Component Documentation

Each component must include:
- **Description**: What the component does and when to use it
- **Props table**: All props with types, defaults, and descriptions
- **Usage examples**: At least one basic example and one advanced example
- **Accessibility notes**: Keyboard interactions, ARIA usage, screen reader behavior
- **Design guidelines**: When to use vs. when not to use, related components
- **Visual examples**: Storybook stories covering all variants, states, and edge cases

### Token Documentation

Each token set must include:
- **Token table**: Name, value, and usage context
- **Visual preview**: Swatches for colors, scale visualization for spacing/typography
- **Usage guidelines**: When to use each token, semantic meaning

## PR Review Configuration

When reviewing PRs in this repository, automatically apply the `[ds]` tag.

### Patterns to Watch For

1. **Hardcoded colors**: Any color value that is not a token reference. Flag as CRITICAL.
2. **Missing ARIA attributes**: Interactive elements without proper ARIA roles, labels, or states. Flag as CRITICAL.
3. **Breaking API changes**: Removal, renaming, or type changes to existing component props. Flag as CRITICAL.
4. **Missing visual regression tests**: New or modified components without corresponding visual regression test updates. Flag as WARNING.
5. **Skipped layers**: Components directly consuming raw values instead of tokens, or patterns bypassing the component layer. Flag as WARNING.
6. **Missing documentation**: New exports without corresponding documentation updates. Flag as WARNING.
7. **Missing Storybook stories**: New component variants or states without story coverage. Flag as SUGGESTION.
8. **Inconsistent naming**: Props or tokens that do not follow established naming conventions. Flag as SUGGESTION.
9. **Missing keyboard support**: Interactive elements that only respond to pointer events. Flag as CRITICAL.
10. **Insufficient contrast**: Color combinations that do not meet WCAG AA contrast ratios. Flag as CRITICAL.

## Testing Expectations

- **Unit tests**: All components must have unit tests covering props, states, and user interactions
- **Accessibility tests**: Automated a11y testing via axe-core or similar in every component test
- **Visual regression tests**: Screenshot tests for all component variants and states
- **Cross-browser testing**: Components must render correctly in Chrome, Firefox, Safari, and Edge
- **SSR compatibility**: Components must not break when server-side rendered
