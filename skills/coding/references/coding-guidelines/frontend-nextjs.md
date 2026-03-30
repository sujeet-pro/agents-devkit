# Next.js Frontend Review Guidelines

These guidelines apply to projects using **Next.js** (App Router preferred, Pages
Router also covered). They supplement the general guidelines with framework-specific
rules for server/client component architecture, data fetching, performance, and
frontend best practices.

---

## 1. Server Components vs Client Components

- **Default to Server Components.** In the App Router, every component is a Server
  Component unless explicitly marked with `"use client"`. Keep it that way. Only add
  `"use client"` when the component genuinely needs browser APIs, event handlers,
  hooks (`useState`, `useEffect`, `useRef`, etc.), or third-party client-only
  libraries.
- **Push `"use client"` to the leaves.** Do not mark a layout or page as a client
  component. Instead, extract the interactive parts into small client components and
  import them into the server component.
- **No `"use client"` on data-fetching components.** If a component fetches data
  (from a database, API, or file system), it should be a Server Component. Pass
  fetched data to client components as props.
- **Watch for accidental client boundaries.** Importing a client component into a
  server component is fine, but importing a server component into a client component
  forces the server component to become a client component. Be vigilant about the
  component tree.
- **Serialization boundary**: Props passed from server to client components must be
  serializable (no functions, Dates, Maps, Sets, or class instances). Verify this.

## 2. Data Fetching Patterns

- **Use RSC (React Server Components) for initial data.** Fetch data in server
  components using `async`/`await` directly. Do not use `useEffect` + `fetch` for
  data that is known at request time.
- **Server Actions for mutations.** Use Next.js Server Actions (`"use server"`) for
  form submissions and data mutations. They provide progressive enhancement (work
  without JavaScript) and automatic CSRF protection.
- **API Routes for external consumers.** Use Route Handlers (`app/api/`) only when
  the API is consumed by external clients, mobile apps, or webhooks. Internal data
  fetching should use Server Components or Server Actions.
- **Parallel data fetching**: Use `Promise.all()` or React's automatic parallel
  fetching (multiple `async` components at the same level) to avoid waterfalls.
  Never fetch sequentially when the requests are independent.
- **Caching strategy**: Explicitly set `revalidate` values or `cache: 'no-store'`
  on fetch calls. Do not rely on default caching behavior, as it changes between
  Next.js versions and can cause surprising stale data in production.
- **Error handling in data fetching**: Wrap server-side data fetching in try/catch.
  Do not let database or API errors crash the entire page. Use error boundaries
  (`error.tsx`) for graceful degradation.
- **Loading states**: Every page and layout that fetches data should have a
  `loading.tsx` sibling for Suspense-based streaming. Users should never see a blank
  screen while data loads.

## 3. Performance

### Images
- **Always use `next/image`** for images. It provides automatic optimization,
  responsive sizing, lazy loading, and WebP/AVIF conversion.
- **Set `width` and `height`** (or use `fill`) on all images to prevent layout
  shift (CLS).
- **Use `priority` prop** on above-the-fold images (hero images, logos in the
  header). This disables lazy loading and preloads the image.
- **Serve images from a CDN** when possible. Configure `remotePatterns` in
  `next.config.js` for external image domains.

### Fonts
- **Use `next/font`** for font loading. It eliminates layout shift from font
  swapping and self-hosts fonts for better performance.
- **Do not use `@import` or `<link>` for Google Fonts.** Always use `next/font/google`.
- **Subset fonts** to the characters you need (e.g., `subsets: ['latin']`).

### Bundle Size
- **Check imports for tree-shaking.** Import only what you need:
  `import { Button } from '@ui/components'` instead of
  `import * as UI from '@ui/components'`.
- **Dynamic imports for heavy components.** Use `next/dynamic` (or `React.lazy`)
  for components that are not needed on initial render (modals, charts, editors).
- **Analyze bundle size** when adding new dependencies. Flag any new dependency
  larger than 50KB gzipped.
- **No duplicate dependencies.** Check for multiple versions of the same library
  (e.g., two versions of `lodash`, `date-fns`, or `moment`).

### Core Web Vitals
- **Largest Contentful Paint (LCP)**: Ensure the main content is visible within
  2.5 seconds. Preload critical resources. Avoid client-side rendering for
  above-the-fold content.
- **First Input Delay (FID) / Interaction to Next Paint (INP)**: Avoid heavy
  JavaScript execution on the main thread. Break up long tasks. Use
  `startTransition` for non-urgent updates.
- **Cumulative Layout Shift (CLS)**: Set explicit dimensions on images, videos,
  and embeds. Avoid inserting content above existing content after load.

## 4. Routing and Layouts

- **Use the App Router layout system.** Shared UI (navigation, sidebars, footers)
  should live in `layout.tsx` files, not repeated in every page.
- **Layouts should not re-render on navigation.** Verify that layouts do not fetch
  data that changes per page. Page-specific data belongs in `page.tsx`.
- **Use `generateStaticParams`** for static generation of dynamic routes when the
  set of valid params is known at build time.
- **Parallel routes and intercepting routes**: Use these advanced patterns when
  appropriate (e.g., modals that have their own URL), but do not over-engineer
  simple navigation.
- **Not-found handling**: Ensure dynamic routes have proper `notFound()` calls
  when data is missing. Include a `not-found.tsx` in the app root.
- **Middleware**: Use `middleware.ts` for cross-cutting concerns (auth, redirects,
  feature flags). Keep middleware fast -- it runs on every request.

## 5. State Management

- **Server state vs client state**: Data from the server should be managed by
  Server Components (RSC) or a server-state library (React Query / SWR). Client
  state (UI state like toggles, form inputs, selections) should use React hooks.
- **Do not duplicate server state in client state.** If a Server Component fetches
  a list of items, do not `useState(items)` in a child client component unless
  the client needs to locally modify the list.
- **URL as state**: For filterable/sortable lists, use URL search params
  (`useSearchParams`) as the source of truth. This makes the state shareable,
  bookmarkable, and compatible with SSR.
- **Form state**: Use `useFormState` and `useFormStatus` (React 19) or
  `react-hook-form` for form state. Avoid manual `useState` for every field.
- **Global state**: Avoid global state management libraries (Redux, Zustand)
  unless the app has genuinely complex cross-component client state. Most state
  in a Next.js app should be server state or URL state.

## 6. Accessibility

- **All interactive elements must be keyboard-accessible.** This includes custom
  dropdowns, modals, tabs, and carousels. Use `@radix-ui`, `@headlessui`, or
  `react-aria` for complex interactive patterns.
- **Focus management**: When opening a modal or drawer, move focus into it. When
  closing, return focus to the trigger element. Use `FocusTrap` or equivalent.
- **ARIA roles and labels**: Custom components must have appropriate ARIA roles.
  Buttons must have accessible names (text content or `aria-label`). Form inputs
  must have associated labels.
- **Live regions**: Dynamic content updates (toasts, notifications, form errors)
  should use `aria-live` regions so screen readers announce them.
- **Skip links**: Include a "Skip to main content" link as the first focusable
  element on every page.
- **Reduced motion**: Respect `prefers-reduced-motion`. Disable or simplify
  animations for users who request it.

## 7. CSS and Styling

- **Tailwind CSS**: If the project uses Tailwind, prefer utility classes over custom
  CSS. Use `@apply` sparingly (only for highly reused patterns like `.btn`).
- **CSS Modules**: If the project uses CSS Modules, keep styles co-located with
  components. Use `.module.css` or `.module.scss`.
- **No inline styles** unless they are dynamic values that cannot be expressed as
  classes (e.g., `style={{ '--progress': percentage }}`).
- **Design tokens**: Use CSS custom properties or Tailwind theme values for colors,
  spacing, and typography. Do not hardcode hex values, pixel sizes, or font
  families.
- **Responsive design**: All new UI must work on mobile (320px+), tablet (768px+),
  and desktop (1024px+). Use Tailwind breakpoints or media queries.
- **Dark mode**: If the project supports dark mode, ensure all new components work
  in both light and dark themes. Use `dark:` variants in Tailwind or CSS custom
  properties that respect the theme.

## 8. Error Boundaries and Loading States

- **Every route segment should have an `error.tsx`** for uncaught errors. The error
  boundary should show a user-friendly message and a retry button.
- **Every data-fetching route should have a `loading.tsx`** for Suspense fallback.
  Loading states should match the layout of the final content to minimize CLS.
- **Granular error boundaries**: For pages with multiple independent data sources,
  wrap each section in its own `<Suspense>` + error boundary so one failure does
  not take down the entire page.
- **Global error handling**: Include a root `global-error.tsx` for catastrophic
  failures (e.g., layout component errors).

## 9. SEO

- **Metadata API**: Use the Next.js `metadata` export or `generateMetadata` function
  for page titles, descriptions, and Open Graph tags. Do not use `<Head>` directly.
- **Structured data**: Add JSON-LD structured data for content pages (articles,
  products, FAQs) using a `<script type="application/ld+json">` tag.
- **Canonical URLs**: Set canonical URLs to prevent duplicate content issues,
  especially for pages with query parameters.
- **Sitemap**: Generate a `sitemap.xml` using `next-sitemap` or the built-in
  `sitemap.ts` convention.
- **robots.txt**: Configure `robots.txt` to allow/disallow appropriate paths.
- **Dynamic rendering**: Ensure important content is server-rendered (not loaded
  via client-side `useEffect`) so search engines can index it.

## 10. Security

- **CSRF protection**: Server Actions provide automatic CSRF protection. If using
  API Routes for mutations, implement CSRF tokens manually.
- **XSS prevention**: Never use `dangerouslySetInnerHTML` without sanitizing the
  input with a library like `DOMPurify`. Prefer rendering structured data as React
  elements.
- **Environment variables**: Client-exposed env vars must use the `NEXT_PUBLIC_`
  prefix. Server-only secrets must NOT have this prefix. Verify that secret keys
  are not accidentally exposed to the browser.
- **Content Security Policy**: Configure CSP headers in `next.config.js` or
  middleware to prevent XSS and data injection attacks.
- **Auth middleware**: Authentication checks should happen in middleware or layout
  server components, not in individual page components where they can be forgotten.

## 11. Testing

- **Component testing**: Use React Testing Library (`@testing-library/react`) for
  component tests. Test behavior (what the user sees and does), not implementation.
- **Server Component testing**: Server Components can be tested by importing and
  calling them directly (they are async functions). Mock data sources.
- **E2E testing**: Use Playwright or Cypress for critical user flows (auth, checkout,
  form submissions). E2E tests should cover at least the happy path.
- **Visual regression testing**: For UI-heavy changes, consider visual regression
  tests with tools like Playwright screenshots or Chromatic.
- **Accessibility testing**: Include axe-core (`@axe-core/react` or
  `jest-axe`) in component tests to catch accessibility violations automatically.

## 12. TypeScript Strictness

- **Enable `strict: true`** in `tsconfig.json`. Do not disable individual strict
  checks.
- **No `any` type.** Use `unknown` when the type is genuinely unknown, then narrow
  with type guards. Use generic types when the type varies but is constrained.
- **No `@ts-ignore` or `@ts-expect-error`** without a comment explaining why it is
  necessary and a tracking issue for removing it.
- **Prefer `interface` for object shapes** that may be extended. Use `type` for
  unions, intersections, and computed types.
- **Exhaustive checks**: Use `never` type in switch/if-else chains to ensure all
  cases are handled. This catches missing cases at compile time when new enum values
  are added.
- **Strict null checks**: Do not use non-null assertions (`!`) except in tests.
  Narrow nullability with explicit checks.
