# Design System / Component Library Review Guidelines

These guidelines apply to **design system** and **component library** repositories.
They supplement the general guidelines with rules specific to building reusable,
accessible, and well-documented UI components that are consumed by many teams and
applications.

---

## 1. Design Token Usage

- **No hardcoded values.** Colors, spacing, font sizes, border radii, shadows,
  z-indexes, and breakpoints must reference design tokens -- never raw hex codes,
  pixel values, or magic numbers.
  - Wrong: `color: #1a73e8;`, `padding: 16px;`, `font-size: 14px;`
  - Right: `color: var(--color-primary);`, `padding: var(--space-4);`,
    `font-size: var(--font-size-sm);`
- **Token names should be semantic**, not descriptive of the value.
  - Wrong: `--color-blue-500`, `--space-16`
  - Right: `--color-primary`, `--space-md`
  - Exception: primitive/base tokens CAN be descriptive (e.g., `--blue-500` in the
    base scale), but component code should reference semantic aliases.
- **Token layers** must be respected:
  1. **Primitive tokens**: Raw values (colors, sizes) -- `--blue-500: #3b82f6`
  2. **Semantic tokens**: Purpose-based aliases -- `--color-primary: var(--blue-500)`
  3. **Component tokens**: Component-specific overrides --
     `--button-bg: var(--color-primary)`
- **New tokens must be justified.** Adding a new token increases surface area.
  Verify that an existing token does not already serve the need. If a new token is
  needed, it must be added to the token definition file, not created inline.
- **Token documentation**: New tokens must be documented with their purpose, allowed
  usage, and an example.

## 2. Component API Design

- **Props should be minimal and purposeful.** Every prop should have a clear use
  case. Avoid "just in case" props. You can always add props later; removing them
  is a breaking change.
- **Use composition over configuration.** Prefer slots/children patterns over
  boolean flags that toggle complex behavior.
  - Wrong: `<Card showHeader showFooter headerTitle="..." footerActions={[...]} />`
  - Right:
    ```jsx
    <Card>
      <Card.Header>Title</Card.Header>
      <Card.Body>Content</Card.Body>
      <Card.Footer><Button>Action</Button></Card.Footer>
    </Card>
    ```
- **Consistent prop naming** across all components:
  - `size`: `"sm" | "md" | "lg"` (not `"small" | "medium" | "large"`)
  - `variant`: visual style variant (not `type` or `kind`)
  - `disabled`: boolean, never `isDisabled`
  - `className`: for custom class overrides (not `class`, `style`, or `css`)
  - `children`: for slot content
  - `as` or `asChild`: for polymorphic rendering
  - `onX`: for event handlers (`onClick`, `onChange`, not `handleClick`)
- **Forward refs.** All components that render a DOM element should forward refs
  using `React.forwardRef` (or the new React 19 ref prop pattern).
- **Spread remaining props** onto the root element (`...rest`) so consumers can
  pass standard HTML attributes (`id`, `data-*`, `aria-*`).
- **Default values** should be sensible. The component should look correct with
  only required props.
- **Controlled and uncontrolled modes.** Form components (input, select, checkbox)
  should support both controlled (`value` + `onChange`) and uncontrolled
  (`defaultValue`) usage.

## 3. Accessibility (WCAG 2.1 AA)

- **All components must be WCAG 2.1 AA compliant.** This is non-negotiable for a
  design system.
- **Keyboard navigation**: Every interactive component must be fully operable with
  a keyboard. Follow WAI-ARIA Authoring Practices for standard patterns:
  - Buttons: Enter and Space to activate
  - Tabs: Arrow keys to navigate, Tab to move out
  - Menus: Arrow keys to navigate, Enter to select, Escape to close
  - Dialogs: Tab to cycle focus, Escape to close, focus trap inside
  - Combobox: Arrow keys to navigate, Enter to select, typing to filter
- **ARIA roles and attributes**: Use the correct ARIA role for each component type.
  Do not invent custom roles. Required ARIA attributes:
  - Dialog: `role="dialog"`, `aria-labelledby`, `aria-modal="true"`
  - Alert: `role="alert"` or `aria-live="assertive"`
  - Tabs: `role="tablist"`, `role="tab"`, `role="tabpanel"`, `aria-selected`
  - Tooltip: `role="tooltip"`, connected via `aria-describedby`
- **Color contrast**: All text must meet 4.5:1 contrast ratio (3:1 for large text).
  All non-text UI elements (icons, borders, focus indicators) must meet 3:1.
- **Focus indicators**: All focusable elements must have a visible focus indicator
  that meets 3:1 contrast ratio against adjacent colors. Never use `outline: none`
  without a replacement.
- **Screen reader testing**: Components must be tested with at least one screen
  reader (VoiceOver on macOS, NVDA on Windows). Include screen reader behavior in
  test descriptions.
- **Motion**: All animations must respect `prefers-reduced-motion`. Provide a way
  to disable motion globally.

## 4. Cross-Browser and Cross-Framework Compatibility

- **Browser support**: Test in Chrome, Firefox, Safari, and Edge (latest 2 versions).
  Document any known browser-specific issues.
- **CSS feature usage**: When using modern CSS features (container queries, `:has()`,
  `@layer`), verify browser support or provide fallbacks.
- **Framework agnosticism**: If the design system targets multiple frameworks
  (React, Vue, Angular), ensure shared logic (tokens, CSS) is framework-agnostic.
  Framework-specific wrappers should be thin.
- **SSR compatibility**: All components must work with server-side rendering. No
  direct `window`, `document`, or `navigator` access during initial render. Guard
  browser-only code with `typeof window !== 'undefined'` or `useEffect`.
- **CSS-in-JS SSR**: If using CSS-in-JS (Emotion, styled-components), ensure the
  SSR setup extracts critical CSS correctly. Verify no flash of unstyled content.

## 5. Theming Support

- **Token-based theming.** Theme switching should work by swapping CSS custom
  property values, not by loading separate stylesheets or toggling class names on
  every component.
- **Dark mode**: All components must support dark mode out of the box. Use semantic
  tokens that automatically switch between light and dark values.
- **Brand theming**: If the design system supports multiple brands, ensure
  components respond to brand token changes without code modifications.
- **Theme type safety**: Theme tokens should be typed. Accessing a non-existent
  token should be a TypeScript error, not a runtime `undefined`.
- **Contrast guarantee**: Theming must not break color contrast requirements. If a
  consumer provides a custom theme, document the contrast requirements for each
  token.

## 6. Documentation Requirements

- **Every component must have**:
  - A description of what it does and when to use it
  - A complete prop/API table with types, defaults, and descriptions
  - A basic usage example
  - Variants/sizes showcase
  - Accessibility documentation (keyboard interactions, ARIA attributes)
  - Do's and Don'ts (common misuse patterns)
- **Storybook stories**: Every component must have Storybook stories covering:
  - Default/basic usage
  - All variants and sizes
  - Interactive states (hover, focus, active, disabled)
  - Edge cases (long text, missing data, many items)
  - Composition with other components
- **Changelog**: Every PR must update the changelog if it changes component behavior,
  props, or visual appearance.
- **Migration guides**: Breaking changes must include a migration guide explaining
  what changed and how to update consuming code.

## 7. Visual Regression Testing

- **Every component must have visual regression tests** (e.g., Chromatic, Percy,
  Playwright visual comparisons).
- **Test all visual states**: default, hover, focus, active, disabled, loading,
  error, empty, overflow.
- **Test responsive behavior**: Capture screenshots at mobile, tablet, and desktop
  breakpoints.
- **Test theming**: Capture screenshots in light and dark themes.
- **New components**: Must add visual regression tests before merging.
- **Visual changes**: Any PR that changes the visual appearance of a component must
  show before/after screenshots in the PR description.

## 8. Bundle Size Awareness

- **Track bundle size** on every PR. Use bundlesize, size-limit, or similar tools
  to enforce budgets.
- **Component-level code splitting**: Each component should be independently
  importable. `import { Button } from '@design-system/react'` should NOT pull in
  the entire library.
- **No heavy dependencies**: Avoid adding runtime dependencies when CSS or native
  APIs can achieve the same result. If a dependency is needed, justify it.
- **Tree-shaking**: Ensure components are tree-shakeable. Use named exports, avoid
  side effects in module scope, and set `"sideEffects": false` in `package.json`.
- **CSS size**: Monitor CSS bundle size. Avoid generating redundant utility classes
  or unused token variables.
- **Icon handling**: Icons should be individually importable, not bundled as a
  single sprite or font.

## 9. Breaking Change Detection

- **Prop removal or rename** is a breaking change.
- **Changing default values** is a breaking change (it changes behavior for existing
  consumers without code changes).
- **Removing or renaming CSS classes/custom properties** is a breaking change (consumers
  may target them for overrides).
- **Changing the DOM structure** is a breaking change (consumers may target elements
  with CSS selectors or `querySelector`).
- **Changing TypeScript types** to be more restrictive is a breaking change (existing
  valid code may no longer compile).
- **Visual changes** that affect layout (spacing, sizing) are breaking changes for
  snapshot/visual tests in consuming repos.
- **All breaking changes must**:
  - Be explicitly called out in the PR description
  - Follow the project's deprecation policy (if one exists)
  - Include a codemod or migration script when feasible
  - Be batched into major version releases

## 10. Semantic Versioning

- **Patch** (`1.0.x`): Bug fixes, internal refactors with no visible change,
  documentation updates, dependency patches.
- **Minor** (`1.x.0`): New components, new props on existing components, new tokens,
  new variants, additive CSS changes.
- **Major** (`x.0.0`): Breaking changes (see section 9).
- **Pre-release** (`1.0.0-beta.1`): For testing breaking changes before a major
  release. Consumers can opt in.
- **Version bump must be included in the PR** (or handled by the release automation).
  Do not merge a breaking change without a major version bump planned.

## 11. Storybook and Documentation Site

- **Stories must be up to date.** If a component changes, its stories must be
  updated in the same PR.
- **No broken stories.** The Storybook build must pass on every PR. A broken story
  is a broken document.
- **Controls/args**: All props should be configurable via Storybook Controls so
  consumers can experiment interactively.
- **Autodocs**: Use Storybook autodocs to generate API documentation from prop types.
  Supplement with handwritten docs for usage guidance.
- **Composition stories**: Show how components work together (e.g., a Card with a
  Button, a Form with Input and Select).

## 12. Token Naming Conventions

- **Consistent hierarchy**: `--{category}-{property}-{variant}-{state}`
  - Example: `--color-text-primary`, `--color-bg-surface-hover`
- **Categories**: `color`, `space`, `size`, `font`, `radius`, `shadow`, `border`,
  `z`, `motion`, `opacity`
- **Semantic naming**: Tokens used by components should describe their purpose, not
  their visual appearance.
  - Wrong: `--button-blue`, `--input-gray-border`
  - Right: `--button-primary-bg`, `--input-border-default`
- **State variants**: Use consistent suffixes for states:
  - `default` (can be omitted when it is the only variant)
  - `hover`, `active`, `focus`, `disabled`
  - `subtle`, `strong` (for intensity variants)

## 13. Layer Architecture

The design system should follow a clear layer architecture. Each layer should only
reference tokens from its own layer or layers below it.

```
Tokens (primitive + semantic)
  |
  v
Primitives (atomic components: Button, Input, Badge, Icon)
  |
  v
Composites (composed from primitives: Select, DatePicker, DataTable)
  |
  v
Patterns (opinionated layouts: PageHeader, SideNav, FormSection)
```

- **Primitives** should never import from Composites or Patterns.
- **Composites** should only import from Primitives and Tokens.
- **Patterns** can import from any lower layer.
- **Enforce layer boundaries** with lint rules (e.g., eslint-plugin-import
  restrictions) or folder-based conventions.
- **New components must be placed in the correct layer.** A PR that adds a composite
  component to the primitives folder should be flagged.
