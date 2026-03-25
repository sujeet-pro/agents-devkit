# Next.js Frontend Repository

This is a **Next.js frontend** application. All code, reviews, and generation must follow Next.js best practices and the App Router paradigm.

## Devkit Integration

Load frontend guidelines from the agents-devkit installation:

```
~/.claude/guidelines/general.md           — baseline code quality rules
~/.claude/guidelines/frontend-nextjs.md   — Next.js-specific rules (if available)
```

Always apply both the general and frontend-nextjs guidelines when reviewing or generating code in this repo.

## Server Components vs Client Components

Next.js App Router defaults to Server Components. This is intentional and must be respected.

### Server Components (default)

Use Server Components for:
- Pages and layouts that fetch data
- Components that access backend resources directly (database, file system, internal APIs)
- Components that render static or mostly-static content
- Components that use heavy dependencies that should not ship to the client

Server Components can:
- Use `async/await` for data fetching
- Access server-only resources (environment variables with server-only secrets, databases)
- Import server-only modules

Server Components cannot:
- Use React hooks (`useState`, `useEffect`, `useContext`, etc.)
- Use browser APIs (`window`, `document`, `localStorage`)
- Attach event handlers (`onClick`, `onChange`, etc.)
- Use `React.createContext` / `useContext`

### Client Components (`'use client'`)

Add the `'use client'` directive ONLY when the component needs:
- React hooks (state, effects, refs, context)
- Browser APIs
- Event handlers
- Third-party libraries that use hooks or browser APIs

### Rules

1. **Default to Server Components.** Only add `'use client'` when there is a specific technical reason.
2. **Push `'use client'` to the leaves.** Keep the boundary as low in the component tree as possible. A page should be a Server Component that renders Client Components for interactive parts.
3. **Never mark a layout as a Client Component** unless absolutely unavoidable.
4. **Do not pass Server Component as children to Client Components unless using the composition pattern** (passing as `children` prop is fine, importing directly is not).

## App Router Patterns

### File Conventions

```
app/
├── layout.tsx          — Root layout (Server Component)
├── page.tsx            — Home page
├── loading.tsx         — Loading UI (Suspense boundary)
├── error.tsx           — Error boundary (must be Client Component)
├── not-found.tsx       — 404 page
├── [slug]/
│   ├── page.tsx        — Dynamic route
│   └── loading.tsx
├── (marketing)/        — Route group (no URL segment)
│   ├── layout.tsx
│   └── about/page.tsx
└── api/
    └── route.ts        — API route handler
```

### Data Fetching

1. **Fetch in Server Components.** Use `async` Server Components with `fetch()` or direct database access.
2. **Use `fetch` with caching.** Leverage Next.js `fetch` caching and revalidation:
   - `fetch(url)` — cached by default
   - `fetch(url, { next: { revalidate: 3600 } })` — ISR with 1-hour revalidation
   - `fetch(url, { cache: 'no-store' })` — dynamic, no caching
3. **Parallel data fetching.** Use `Promise.all()` for independent data requests.
4. **Server Actions for mutations.** Use `'use server'` functions for form submissions and data mutations.
5. **No `getServerSideProps` or `getStaticProps`.** These are Pages Router patterns. Use the App Router equivalents.

### Metadata and SEO

1. **Export `metadata` or `generateMetadata` from every page.**
2. **Include at minimum**: title, description, Open Graph tags.
3. **Use `generateMetadata` for dynamic pages** that need data-dependent metadata.
4. **Add structured data (JSON-LD)** for content pages where appropriate.

## Performance Expectations

### Core Web Vitals Targets

- **LCP (Largest Contentful Paint)**: < 2.5 seconds
- **INP (Interaction to Next Paint)**: < 200 milliseconds
- **CLS (Cumulative Layout Shift)**: < 0.1

### Performance Rules

1. **Use `next/image` for all images.** Never use bare `<img>` tags. Configure `width`, `height`, and `alt` on every image.
2. **Use `next/font` for fonts.** Avoid layout shift from font loading.
3. **Use `next/link` for internal navigation.** Enables prefetching.
4. **Lazy load below-the-fold content.** Use `dynamic()` with `{ ssr: false }` for heavy client-only components.
5. **Minimize client-side JavaScript.** Every `'use client'` component adds to the client bundle.
6. **Use `Suspense` boundaries** for async Server Components to enable streaming.
7. **Optimize third-party scripts.** Use `next/script` with appropriate loading strategy (`afterInteractive`, `lazyOnload`).
8. **No blocking CSS.** Avoid large global stylesheets. Use CSS Modules, Tailwind, or CSS-in-JS with server extraction.

### Bundle Size

- Monitor bundle size with `next build` output
- Use `@next/bundle-analyzer` for detailed analysis
- Flag any single page bundle exceeding 200KB (gzipped)
- Flag any new dependency larger than 50KB (gzipped)

## Loading and Error States

Every route segment MUST handle loading and error states.

### Required Files

- **`loading.tsx`**: Provide meaningful loading UI (skeleton screens, not spinners) for every route segment that fetches data.
- **`error.tsx`**: Provide user-friendly error boundaries for every route segment. Must be a Client Component. Must include a retry mechanism.
- **`not-found.tsx`**: Custom 404 page at the app root, and optionally per-route for dynamic segments.

### Rules

1. **No empty loading states.** Loading UI must give the user a sense of what is coming (skeleton screens that match the layout).
2. **Error boundaries must be recoverable.** Include a "Try again" button that calls `reset()`.
3. **Errors must not leak implementation details.** Show user-friendly messages in production. Log detailed errors server-side.

## PR Review Configuration

When reviewing PRs in this repository, automatically apply the `[fe]` tag.

### Patterns to Watch For

1. **Unnecessary `'use client'` directives**: Components marked as Client Components that do not use hooks, browser APIs, or event handlers. Flag as WARNING.
2. **Missing `loading.tsx`**: Route segments that fetch data without a corresponding loading file. Flag as WARNING.
3. **Missing `error.tsx`**: Route segments without error boundaries. Flag as WARNING.
4. **Missing metadata**: Pages without `metadata` or `generateMetadata` exports. Flag as WARNING.
5. **Bare `<img>` tags**: Images not using `next/image`. Flag as WARNING.
6. **SEO issues**: Missing meta descriptions, missing Open Graph tags, missing structured data on content pages. Flag as SUGGESTION.
7. **Client-side data fetching in Server Components**: Using `useEffect` + `fetch` when the component could be a Server Component. Flag as WARNING.
8. **Large client bundles**: New dependencies or large client-side code additions without justification. Flag as SUGGESTION.
9. **Missing `Suspense` boundaries**: Async Server Components without Suspense wrappers. Flag as SUGGESTION.
10. **Hardcoded strings**: User-facing text that should be in a translation file or constants. Flag as NICE-TO-HAVE.

## Testing Expectations

- **Unit tests**: Component logic and utility functions
- **Integration tests**: Page-level tests verifying data flow and rendering
- **E2E tests**: Critical user journeys with Playwright or Cypress
- **Accessibility tests**: Automated a11y checks on all pages
- **Lighthouse CI**: Performance audits in CI to catch regressions

## Accessibility

- Semantic HTML in all components
- Keyboard navigation for all interactive elements
- ARIA attributes where native semantics are insufficient
- Color contrast meeting WCAG 2.1 AA
- Skip-to-content link in the root layout
- Focus management on route transitions
