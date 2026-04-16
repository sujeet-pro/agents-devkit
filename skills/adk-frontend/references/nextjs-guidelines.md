# Next.js Coding Guidelines

Comprehensive reference for Next.js App Router patterns, Server Components, data fetching, caching, middleware, and deployment. Targets Next.js 14+ with the App Router.

---

## 1. App Router Architecture

### File Conventions

```
app/
├── layout.tsx          # Root layout (wraps all pages, persistent across navigation)
├── page.tsx            # Home page (/)
├── loading.tsx         # Instant loading UI (wraps page in Suspense)
├── error.tsx           # Error boundary (must be 'use client')
├── not-found.tsx       # 404 page
├── global-error.tsx    # Root error boundary (must be 'use client')
├── template.tsx        # Re-renders on navigation (unlike layout)
├── dashboard/
│   ├── layout.tsx      # Nested layout
│   ├── page.tsx        # /dashboard
│   └── settings/
│       └── page.tsx    # /dashboard/settings
├── blog/
│   └── [slug]/
│       └── page.tsx    # /blog/:slug (dynamic route)
├── shop/
│   └── [...slug]/
│       └── page.tsx    # /shop/* (catch-all route)
├── (marketing)/        # Route group (no URL segment)
│   ├── about/
│   │   └── page.tsx    # /about
│   └── contact/
│       └── page.tsx    # /contact
├── @sidebar/           # Parallel route (named slot)
│   └── page.tsx
└── api/
    └── route.ts        # API route handler
```

### Rules

- `page.tsx` is required to make a route publicly accessible
- `layout.tsx` components do NOT re-render on navigation (state preserved)
- `template.tsx` re-renders on every navigation (use for animations, per-page effects)
- `loading.tsx` auto-wraps `page.tsx` in `<Suspense>`
- `error.tsx` must be a Client Component (`'use client'`)
- Route groups `(name)` organize without affecting URL structure
- Parallel routes `@name` render multiple pages in the same layout

---

## 2. Server Components vs Client Components

### Default: Server Components

```tsx
// Server Component (default, no directive)
// Can: access DB, read files, use heavy libraries (zero client JS cost)
// Cannot: use state, effects, event handlers, browser APIs

async function ProductPage({ params }: { params: { id: string } }) {
  const product = await db.products.findUnique({ where: { id: params.id } });
  return (
    <div>
      <h1>{product.name}</h1>
      <p>{product.description}</p>
      <AddToCartButton productId={product.id} /> {/* Client Component */}
    </div>
  );
}
```

### Client Components

```tsx
"use client";
// Opt-in for: state, effects, event handlers, browser APIs

import { useState } from "react";

function AddToCartButton({ productId }: { productId: string }) {
  const [adding, setAdding] = useState(false);

  async function handleAdd() {
    setAdding(true);
    await fetch("/api/cart", {
      method: "POST",
      body: JSON.stringify({ productId }),
    });
    setAdding(false);
  }

  return (
    <button onClick={handleAdd} disabled={adding}>
      {adding ? "Adding..." : "Add to Cart"}
    </button>
  );
}
```

### Boundary Rules

```
Server Component → can render Client Component children ✓
Client Component → CANNOT import Server Component ✗
Client Component → can ACCEPT Server Component as children prop ✓
```

**DO: Pass Server Components as children to Client Components**
```tsx
// layout.tsx (Server Component)
<ClientSidebar>
  <ServerNavigation /> {/* This works -- passed as children */}
</ClientSidebar>
```

**DON'T: Import Server Component in Client Component**
```tsx
"use client";
import ServerComponent from "./ServerComponent"; // This fails
```

### When to Use Each

| Feature Needed | Server | Client |
|---|---|---|
| Fetch data | Yes | Via useQuery/SWR |
| Access backend resources | Yes | No |
| Use state/effects | No | Yes |
| Event handlers (onClick, onChange) | No | Yes |
| Browser APIs (localStorage, geolocation) | No | Yes |
| Heavy library (zero bundle cost) | Yes | Adds to bundle |
| Static rendering / caching | Yes | No |

---

## 3. Data Fetching

### Server Component Fetching (Preferred)

```tsx
// Direct data access in Server Components
async function Dashboard() {
  const [stats, recentOrders] = await Promise.all([
    db.stats.get(),
    db.orders.findMany({ take: 10, orderBy: { createdAt: "desc" } }),
  ]);

  return (
    <div>
      <StatsCards stats={stats} />
      <OrderTable orders={recentOrders} />
    </div>
  );
}
```

### fetch() with Caching

```tsx
// Cached by default (static)
const data = await fetch("https://api.example.com/data");

// Revalidate every 60 seconds (ISR)
const data = await fetch("https://api.example.com/data", {
  next: { revalidate: 60 },
});

// No caching (dynamic)
const data = await fetch("https://api.example.com/data", {
  cache: "no-store",
});

// Tag-based invalidation
const data = await fetch("https://api.example.com/products", {
  next: { tags: ["products"] },
});

// Invalidate by tag
import { revalidateTag } from "next/cache";
revalidateTag("products");
```

### Deduplication

Next.js auto-deduplicates `fetch()` requests with the same URL and options within a single render pass. Call `fetch()` wherever you need data -- it won't make duplicate network requests.

```tsx
// Both components fetch the same URL -- Next.js deduplicates
async function Header() {
  const user = await fetch("/api/user").then(r => r.json());
  return <h1>Welcome, {user.name}</h1>;
}

async function Sidebar() {
  const user = await fetch("/api/user").then(r => r.json());
  return <nav>Role: {user.role}</nav>;
}
```

### Parallel Data Fetching

```tsx
// DO: Parallel at the same level
async function Page() {
  const statsPromise = getStats();
  const ordersPromise = getOrders();
  const [stats, orders] = await Promise.all([statsPromise, ordersPromise]);
  return <Dashboard stats={stats} orders={orders} />;
}

// OR: Use Suspense for streaming
function Page() {
  return (
    <div>
      <Suspense fallback={<StatsSkeleton />}><StatsPanel /></Suspense>
      <Suspense fallback={<OrdersSkeleton />}><OrdersList /></Suspense>
    </div>
  );
}
```

---

## 4. Server Actions

```tsx
// Server Action (runs on server, callable from client)
"use server";

import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

export async function createPost(formData: FormData) {
  const title = formData.get("title") as string;
  const content = formData.get("content") as string;

  // Validate
  if (!title || title.length < 3) {
    return { error: "Title must be at least 3 characters" };
  }

  // Create
  await db.posts.create({ data: { title, content } });

  // Revalidate and redirect
  revalidatePath("/posts");
  redirect("/posts");
}
```

### Using Server Actions in Forms

```tsx
// Server Component form (progressive enhancement -- works without JS)
function NewPostForm() {
  return (
    <form action={createPost}>
      <input name="title" required minLength={3} />
      <textarea name="content" required />
      <button type="submit">Create Post</button>
    </form>
  );
}
```

### Using Server Actions in Client Components

```tsx
"use client";
import { createPost } from "./actions";
import { useActionState } from "react";

function NewPostForm() {
  const [state, formAction, isPending] = useActionState(createPost, null);

  return (
    <form action={formAction}>
      <input name="title" required />
      <textarea name="content" required />
      <button type="submit" disabled={isPending}>
        {isPending ? "Creating..." : "Create Post"}
      </button>
      {state?.error && <p className="error">{state.error}</p>}
    </form>
  );
}
```

### Rules for Server Actions

- Always validate input (never trust client data)
- Always check authentication/authorization
- Use `revalidatePath` or `revalidateTag` after mutations
- Return error objects instead of throwing (for form state)
- Server Actions can be called from Client Components via `action` prop or direct invocation

---

## 5. Middleware

```tsx
// middleware.ts (at project root)
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  // Authentication check
  const token = request.cookies.get("auth-token");
  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/login", request.url));
  }

  // Add headers
  const response = NextResponse.next();
  response.headers.set("x-request-id", crypto.randomUUID());
  return response;
}

// Match specific paths
export const config = {
  matcher: ["/dashboard/:path*", "/api/:path*"],
};
```

### Rules

- Middleware runs on EVERY matched request (keep it fast)
- Cannot access database directly (use Edge Runtime)
- Cannot use Node.js APIs that aren't Edge-compatible
- Use `matcher` config to limit which paths trigger middleware
- Prefer checking headers/cookies over making network calls

---

## 6. Caching

### Four Caching Layers

| Layer | What | Where | Duration | Opt Out |
|---|---|---|---|---|
| Request Memoization | `fetch()` return values | Server | Per-request | `AbortController` |
| Data Cache | `fetch()` return values | Server | Persistent | `cache: 'no-store'` or `revalidate: 0` |
| Full Route Cache | HTML + RSC Payload | Server | Persistent | Dynamic functions or `revalidate` |
| Router Cache | RSC Payload | Client | Session | `router.refresh()` |

### Static vs Dynamic Rendering

**Static (default):** Rendered at build time, cached, served from CDN.

**Dynamic:** Rendered on every request when using:
- `cookies()`, `headers()`, `searchParams`
- `cache: 'no-store'` on fetch
- `export const dynamic = 'force-dynamic'`

```tsx
// Force dynamic rendering
export const dynamic = "force-dynamic";

// Or force static
export const dynamic = "force-static";

// Revalidation
export const revalidate = 60; // ISR: regenerate every 60 seconds
export const revalidate = 0;  // Dynamic: no caching
```

### On-Demand Revalidation

```tsx
// In a Server Action or API Route
import { revalidatePath, revalidateTag } from "next/cache";

export async function updateProduct(id: string, data: ProductData) {
  await db.products.update({ where: { id }, data });

  revalidatePath("/products");           // Revalidate page
  revalidatePath("/products/[id]", "page"); // Revalidate dynamic page
  revalidateTag("products");             // Revalidate by cache tag
}
```

---

## 7. Metadata and SEO

### Static Metadata

```tsx
// app/page.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Home - My App",
  description: "Welcome to my application",
  openGraph: {
    title: "Home - My App",
    description: "Welcome to my application",
    images: ["/og-image.jpg"],
  },
};
```

### Dynamic Metadata

```tsx
// app/blog/[slug]/page.tsx
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await getPost(params.slug);
  return {
    title: post.title,
    description: post.excerpt,
    openGraph: {
      title: post.title,
      images: [post.coverImage],
    },
  };
}
```

### Template Titles

```tsx
// app/layout.tsx
export const metadata: Metadata = {
  title: {
    template: "%s | My App",   // %s replaced by child page title
    default: "My App",          // fallback when child has no title
  },
};

// app/about/page.tsx
export const metadata: Metadata = {
  title: "About",  // Renders as "About | My App"
};
```

---

## 8. Image Optimization

```tsx
import Image from "next/image";

// Local image (auto width/height from import)
import heroImage from "@/public/hero.jpg";
<Image src={heroImage} alt="Hero" priority /> {/* LCP image: add priority */}

// Remote image (must specify width/height or fill)
<Image
  src="https://example.com/photo.jpg"
  alt="Description"
  width={800}
  height={600}
  sizes="(max-width: 768px) 100vw, 50vw"
/>

// Fill mode (responsive within container)
<div style={{ position: "relative", width: "100%", aspectRatio: "16/9" }}>
  <Image src="/photo.jpg" alt="Description" fill style={{ objectFit: "cover" }} />
</div>
```

### Rules

- Always use `next/image` instead of `<img>` (auto WebP/AVIF, lazy loading, srcset)
- Add `priority` to LCP images (disables lazy loading)
- Use `sizes` prop for responsive images
- Configure `remotePatterns` in `next.config.js` for external images

---

## 9. Route Handlers (API Routes)

```tsx
// app/api/users/route.ts
import { NextResponse } from "next/server";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const role = searchParams.get("role");

  const users = await db.users.findMany({
    where: role ? { role } : undefined,
  });

  return NextResponse.json(users);
}

export async function POST(request: Request) {
  const body = await request.json();

  // Validate
  const parsed = userSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.issues }, { status: 400 });
  }

  const user = await db.users.create({ data: parsed.data });
  return NextResponse.json(user, { status: 201 });
}
```

### Dynamic Route Handlers

```tsx
// app/api/users/[id]/route.ts
export async function GET(
  request: Request,
  { params }: { params: { id: string } }
) {
  const user = await db.users.findUnique({ where: { id: params.id } });
  if (!user) return NextResponse.json({ error: "Not found" }, { status: 404 });
  return NextResponse.json(user);
}
```

---

## 10. Loading and Error UI

### Loading States

```tsx
// app/dashboard/loading.tsx
// Automatically wraps page.tsx in Suspense
export default function Loading() {
  return <DashboardSkeleton />;
}
```

### Error Boundaries

```tsx
// app/dashboard/error.tsx (must be 'use client')
"use client";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try Again</button>
    </div>
  );
}
```

### Not Found

```tsx
// app/not-found.tsx
export default function NotFound() {
  return (
    <div>
      <h1>404 - Page Not Found</h1>
      <p>The page you're looking for doesn't exist.</p>
      <Link href="/">Go home</Link>
    </div>
  );
}

// Trigger programmatically
import { notFound } from "next/navigation";

async function ProductPage({ params }: Props) {
  const product = await getProduct(params.id);
  if (!product) notFound();
  return <ProductDetail product={product} />;
}
```

---

## 11. Patterns and Best Practices

### Streaming with Suspense

```tsx
async function Page() {
  return (
    <div>
      <h1>Dashboard</h1>
      {/* Shows immediately */}
      <Suspense fallback={<CardsSkeleton />}>
        <StatsCards /> {/* Streams when ready */}
      </Suspense>
      <Suspense fallback={<TableSkeleton />}>
        <RecentOrders /> {/* Streams independently */}
      </Suspense>
    </div>
  );
}

async function StatsCards() {
  const stats = await getStats(); // Can take time -- won't block other Suspense
  return <div>{stats.map(s => <Card key={s.id} {...s} />)}</div>;
}
```

### Parallel Routes

```tsx
// app/layout.tsx
export default function Layout({
  children,
  analytics,
  team,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  team: React.ReactNode;
}) {
  return (
    <div>
      {children}
      <div className="grid grid-cols-2">
        {analytics}
        {team}
      </div>
    </div>
  );
}
```

### Intercepting Routes

```
app/
├── feed/
│   ├── page.tsx           # Feed page
│   └── (..)photo/[id]/
│       └── page.tsx       # Intercepted modal view
└── photo/[id]/
    └── page.tsx           # Full page view (direct navigation)
```

---

## 12. Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| `'use client'` on every component | Only add where state/effects/handlers are needed |
| `'use server'` to "mark" server components | Server Components are the default -- no directive needed |
| Fetching in `useEffect` in Client Components | Prefer Server Components or TanStack Query |
| `getServerSideProps` in App Router | Use async Server Components directly |
| API routes for data used only by Server Components | Fetch data directly in the Server Component |
| Not using `Suspense` for streaming | Wrap slow components in Suspense boundaries |
| `router.push` for every navigation | Use `<Link>` for prefetching and client-side nav |
| Missing `revalidate` after mutations | Always `revalidatePath`/`revalidateTag` in Server Actions |
| Large Client Components wrapping small interactive parts | Extract interactive part into a small Client Component |
| Ignoring `loading.tsx` convention | Add loading states for better perceived performance |
| Using `next/image` without `sizes` | Always specify sizes for responsive images |
| Environment variables without `NEXT_PUBLIC_` prefix in client code | Client-side env vars must be prefixed with `NEXT_PUBLIC_` |
