# React Coding Guidelines

Comprehensive reference for modern React patterns, rendering strategies, performance optimization, and data fetching. Covers component design, hooks, Server Components, and the 2026 ecosystem.

---

## 1. Component Patterns

### 1.1 Hooks (Default pattern for logic reuse)

```tsx
// Custom hook: reusable stateful logic
function useLocalStorage<T>(key: string, initial: T) {
  const [value, setValue] = useState<T>(() => {
    try {
      const stored = localStorage.getItem(key);
      return stored ? JSON.parse(stored) : initial;
    } catch { return initial; }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue] as const;
}

// Usage
const [theme, setTheme] = useLocalStorage("theme", "light");
```

**Rules:**
- Call hooks at the top level only (no conditionals, loops)
- Prefix custom hooks with `use`
- Avoid `useEffect` for derived state -- compute inline or with `useMemo`
- Let React Compiler handle memoization when possible

### 1.2 Compound Components

Components that work together sharing state through Context. Ideal for dropdowns, tabs, accordions.

```tsx
const SelectContext = createContext<{
  value: string;
  onChange: (v: string) => void;
} | null>(null);

function Select({ value, onChange, children }: SelectProps) {
  return (
    <SelectContext.Provider value={{ value, onChange }}>
      <div role="listbox">{children}</div>
    </SelectContext.Provider>
  );
}

function Option({ value, children }: OptionProps) {
  const ctx = useContext(SelectContext);
  if (!ctx) throw new Error("Option must be inside Select");
  const selected = ctx.value === value;

  return (
    <div
      role="option"
      aria-selected={selected}
      onClick={() => ctx.onChange(value)}
    >
      {children}
    </div>
  );
}

Select.Option = Option;

// Usage
<Select value={color} onChange={setColor}>
  <Select.Option value="red">Red</Select.Option>
  <Select.Option value="blue">Blue</Select.Option>
</Select>
```

### 1.3 Composition over Configuration

**DON'T: Boolean prop explosion**
```tsx
<Card showHeader showFooter collapsible bordered withShadow size="large" />
```

**DO: Compose smaller components**
```tsx
<Card variant="bordered" shadow="md">
  <Card.Header>
    <h3>Title</h3>
    <Card.CloseButton />
  </Card.Header>
  <Card.Body collapsible>
    <p>Content</p>
  </Card.Body>
  <Card.Footer>
    <Button>Save</Button>
  </Card.Footer>
</Card>
```

**DON'T: Mode/type prop with conditionals**
```tsx
function MediaDisplay({ type, src, ...props }) {
  if (type === "video") return <video src={src} {...props} />;
  if (type === "audio") return <audio src={src} {...props} />;
  return <img src={src} {...props} />;
}
```

**DO: Separate components**
```tsx
function VideoPlayer({ src, controls }: VideoProps) { return <video src={src} controls={controls} />; }
function AudioPlayer({ src }: AudioProps) { return <audio src={src} />; }
function Image({ src, alt }: ImageProps) { return <img src={src} alt={alt} />; }
```

### 1.4 Polymorphic `as` Prop

```tsx
type BoxProps<C extends React.ElementType = "div"> = {
  as?: C;
  children: React.ReactNode;
} & Omit<React.ComponentPropsWithoutRef<C>, "as" | "children">;

function Box<C extends React.ElementType = "div">({
  as,
  children,
  ...props
}: BoxProps<C>) {
  const Component = as || "div";
  return <Component {...props}>{children}</Component>;
}

// Usage
<Box as="section">A section</Box>
<Box as={Link} to="/about">Router link</Box>
```

### 1.5 Headless Components (Logic without rendering)

```tsx
function useToggle(initial = false) {
  const [on, setOn] = useState(initial);
  const toggle = useCallback(() => setOn(o => !o), []);
  const buttonProps = {
    "aria-pressed": on,
    onClick: toggle,
    role: "switch" as const,
  };
  return { on, toggle, buttonProps };
}

// Usage: any UI, same logic
function DarkModeToggle() {
  const { on, buttonProps } = useToggle();
  return <button {...buttonProps}>{on ? "Dark" : "Light"}</button>;
}
```

### 1.6 React 19 Updates

```tsx
// ref as regular prop (no forwardRef needed)
function Input({ ref, ...props }: InputProps & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />;
}

// use() for reading promises and context
function UserName({ userPromise }: { userPromise: Promise<User> }) {
  const user = use(userPromise);
  return <span>{user.name}</span>;
}

// useActionState for form handling
function Form() {
  const [state, formAction, isPending] = useActionState(submitForm, initialState);
  return (
    <form action={formAction}>
      <input name="email" />
      <button disabled={isPending}>Submit</button>
      {state.error && <p>{state.error}</p>}
    </form>
  );
}

// useOptimistic for instant feedback
function LikeButton({ liked, likeCount }: LikeProps) {
  const [optimistic, setOptimistic] = useOptimistic({ liked, likeCount });
  async function toggleLike() {
    setOptimistic(prev => ({
      liked: !prev.liked,
      likeCount: prev.liked ? prev.likeCount - 1 : prev.likeCount + 1,
    }));
    await fetch("/api/like", { method: "POST" });
  }
  return <button onClick={toggleLike}>{optimistic.likeCount}</button>;
}
```

---

## 2. Rendering Strategies

### Decision Matrix

| Strategy | TTFB | FCP | TTI | SEO | Dynamic Data | Best For |
|---|---|---|---|---|---|---|
| CSR | Fast | Slow | Slow | Poor | Excellent | SPAs, dashboards, internal tools |
| SSR | Slow | Fast | Medium | Great | Good | Content sites, SEO pages |
| SSG | Fastest | Fast | Fast | Great | None | Static content, blogs, docs |
| ISR | Fast | Fast | Fast | Great | Periodic | Large sites, slow-changing data |
| Streaming SSR | Fast | Faster | Medium | Great | Good | Large pages, complex layouts |
| RSC | Fast | Fast | Fast | Great | Good | Any -- reduces client JS |

### 2.1 Client-Side Rendering (CSR)

**When to use:** Internal tools, dashboards, SPAs where SEO doesn't matter.

```tsx
// Vite + React SPA
createRoot(document.getElementById("root")!).render(<App />);
```

**Rules:**
- Keep initial JS < 100-170KB minified/gzipped
- Use code splitting and lazy loading
- Use service workers for repeat visits

### 2.2 Server-Side Rendering (SSR)

**When to use:** SEO-critical pages, content-heavy pages needing fast FCP.

```tsx
// React 18+ streaming SSR
import { renderToPipeableStream } from "react-dom/server";

const { pipe } = renderToPipeableStream(<App />, {
  bootstrapScripts: ["/build/client.js"],
  onShellReady() {
    response.statusCode = 200;
    response.setHeader("Content-Type", "text/html");
    pipe(response);
  },
});

// Client hydration
import { hydrateRoot } from "react-dom/client";
hydrateRoot(document.getElementById("root")!, <App />);
```

### 2.3 React Server Components (RSC)

**When to use:** Data-fetching, non-interactive UI, reducing client JS. Default in Next.js App Router.

```tsx
// Server Component (default, no directive needed)
import { marked } from "marked";       // zero client bundle cost
import sanitize from "sanitize-html";   // zero client bundle cost

async function BlogPost({ slug }: { slug: string }) {
  const post = await db.posts.findUnique({ where: { slug } });
  const html = sanitize(marked(post.content));
  return <article dangerouslySetInnerHTML={{ __html: html }} />;
}

// Client Component (explicit opt-in)
"use client";
function LikeButton({ postId }: { postId: string }) {
  const [liked, setLiked] = useState(false);
  return <button onClick={() => setLiked(!liked)}>Like</button>;
}
```

**Rules:**
- Server Components are the DEFAULT (no directive)
- `'use client'` only for components needing state, effects, or event handlers
- `'use server'` is for Server Functions/Actions, NOT for marking server components
- Server Components can import heavy libraries at zero client cost
- RSC complements SSR, does not replace it

### 2.4 Streaming SSR with Suspense

```tsx
function Page() {
  return (
    <div>
      <Header /> {/* Renders immediately */}
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel /> {/* Streams when data is ready */}
      </Suspense>
      <Suspense fallback={<FeedSkeleton />}>
        <ActivityFeed /> {/* Streams independently */}
      </Suspense>
    </div>
  );
}
```

### 2.5 Incremental Static Regeneration (ISR)

```tsx
// Next.js Pages Router
export async function getStaticProps() {
  return {
    props: { products: await getProducts() },
    revalidate: 60, // regenerate every 60 seconds
  };
}

// Next.js App Router
export const revalidate = 60;

// On-demand revalidation
import { revalidatePath, revalidateTag } from "next/cache";
revalidatePath("/products");
revalidateTag("products");
```

---

## 3. Performance Optimization

### 3.1 Compute Derived Values During Render [HIGH]

```tsx
// DON'T: Store derived state with useEffect
const [search, setSearch] = useState("");
const [filtered, setFiltered] = useState(products);
useEffect(() => {
  setFiltered(products.filter(p => p.name.toLowerCase().includes(search.toLowerCase())));
}, [products, search]);

// DO: Compute inline (cheap) or memoize (expensive)
const filtered = useMemo(
  () => products.filter(p => p.name.toLowerCase().includes(search.toLowerCase())),
  [products, search]
);
```

**Rule:** Plain `const` for cheap derivations. `useMemo` for O(n) or heavier.

### 3.2 Never Define Components Inside Components [HIGH]

```tsx
// DON'T: Creates new component type every render (remounts, loses state)
function Table({ data }) {
  function Row({ item }) {
    const [selected, setSelected] = useState(false);
    return <tr><td>{item.name}</td></tr>;
  }
  return <table>{data.map(item => <Row key={item.id} item={item} />)}</table>;
}

// DO: Define components at module scope
function Row({ item }: { item: Item }) {
  const [selected, setSelected] = useState(false);
  return <tr><td>{item.name}</td></tr>;
}
function Table({ data }: { data: Item[] }) {
  return <table>{data.map(item => <Row key={item.id} item={item} />)}</table>;
}
```

### 3.3 CSS content-visibility for Long Lists [HIGH]

```css
.list-item {
  content-visibility: auto;
  contain-intrinsic-size: 0 80px;
}
```

5-10x faster initial render for long lists. Works without any JS library.

### 3.4 Subscribe to Coarse State [HIGH]

```tsx
// DON'T: Re-renders on every pixel
const width = useWindowWidth();
const isMobile = width < 768;

// DO: Re-renders only when boolean flips
const isMobile = useMediaQuery("(max-width: 767px)");
```

### 3.5 Extract Expensive Subtrees into Memoized Components [HIGH]

```tsx
const UserAvatar = memo(function UserAvatar({ user }: { user: User }) {
  const avatar = useMemo(() => processAvatar(user), [user]);
  return <img src={avatar} />;
});
```

### 3.6 useDeferredValue for Expensive Renders [HIGH]

```tsx
function SearchPage({ query }: { query: string }) {
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;
  const results = useMemo(() => filterItems(deferredQuery), [deferredQuery]);

  return (
    <div style={{ opacity: isStale ? 0.7 : 1 }}>
      <ResultsList items={results} />
    </div>
  );
}
```

Use `useTransition` when you control the state setter. Use `useDeferredValue` when value comes from props.

### 3.7 React DOM Resource Hints (React 19) [HIGH]

```tsx
import { preload, preinit } from "react-dom";

function App() {
  preload("/fonts/inter.woff2", {
    as: "font",
    type: "font/woff2",
    crossOrigin: "anonymous",
  });
  preinit("/critical.css", { as: "style" });
  return <RouterProvider router={router} />;
}
```

### 3.8 Lazy State Initialization [MEDIUM]

```tsx
// DON'T: Runs every render
useState(buildSearchIndex(items));

// DO: Runs only on mount
useState(() => buildSearchIndex(items));
```

### 3.9 Event Handlers, Not Effects [MEDIUM]

```tsx
// DON'T: Effect for interaction response
useEffect(() => {
  if (submitted) { post("/api/register"); showToast("Done"); }
}, [submitted]);

// DO: Event handler
function handleSubmit() {
  post("/api/register");
  showToast("Done");
}
```

### 3.10 useRef for High-Frequency Updates [MEDIUM]

```tsx
function Cursor() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current) ref.current.style.transform = `translateX(${e.clientX}px)`;
    };
    window.addEventListener("mousemove", handler);
    return () => window.removeEventListener("mousemove", handler);
  }, []);
  return <div ref={ref} className="cursor" />;
}
```

### 3.11 startTransition for Non-Urgent Updates [MEDIUM]

```tsx
const [isPending, startTransition] = useTransition();

function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
  setQuery(e.target.value);           // urgent: update input
  startTransition(() => {
    setFiltered(items.filter(...));    // non-urgent: can be interrupted
  });
}
```

### 3.12 Stable Default References [MEDIUM]

```tsx
// DON'T: New array on every render
function Dashboard({ tabs = [] }: DashboardProps) { /* ... */ }

// DO: Module-level constant
const EMPTY_TABS: Tab[] = [];
function Dashboard({ tabs = EMPTY_TABS }: DashboardProps) { /* ... */ }
```

### 3.13 Prevent Hydration Flicker [MEDIUM]

```tsx
// Inline script to set theme before React renders
<script dangerouslySetInnerHTML={{ __html: `(function(){
  try{document.documentElement.dataset.theme=localStorage.getItem('theme')||'light'}catch(e){}
})();` }} />
```

### 3.14 Conditional Rendering: Avoid `0` Render [MEDIUM]

```tsx
// DON'T: Renders "0" when count is 0
{count && <Badge>{count}</Badge>}

// DO: Explicit boolean check
{count > 0 && <Badge>{count}</Badge>}
```

### 3.15 React Compiler (Auto-Memoization) [HIGH]

```ts
// vite.config.ts
export default defineConfig({
  plugins: [
    react({
      babel: { plugins: ["babel-plugin-react-compiler"] },
    }),
  ],
});
```

Eliminates manual `useMemo`, `useCallback`, `React.memo` in most cases. Requires React 19.

---

## 4. Data Fetching

### 4.1 Parallelize Independent Fetches [CRITICAL]

```tsx
// DON'T: Sequential (waterfall)
const user = await fetchUser();
const posts = await fetchPosts();

// DO: Parallel
const [user, posts] = await Promise.all([fetchUser(), fetchPosts()]);
```

### 4.2 Use TanStack Query for Client Data [CRITICAL]

```tsx
const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000, retry: 2 } },
});

function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetch(`/api/users/${userId}`).then(r => r.json()),
  });
  if (isLoading) return <Skeleton />;
  return <h1>{user.name}</h1>;
}
```

### 4.3 Avoid Fetch Waterfalls [CRITICAL]

```tsx
// DON'T: Child waits for parent
function Page({ userId }) {
  const { data: user } = useQuery({ queryKey: ["user", userId], queryFn: fetchUser });
  if (!user) return <Skeleton />;
  return <UserPosts userId={user.id} />; // starts only after user loads
}

// DO: Parallel at same level
function Page({ userId }) {
  const { data: user } = useQuery({ queryKey: ["user", userId], queryFn: () => fetchUser(userId) });
  const { data: posts } = useQuery({ queryKey: ["posts", userId], queryFn: () => fetchPosts(userId) });
  return <div><UserHeader user={user} /><PostList posts={posts ?? []} /></div>;
}
```

### 4.4 Suspense for Loading States [HIGH]

```tsx
function Dashboard() {
  return (
    <div>
      <Suspense fallback={<HeaderSkeleton />}>
        <UserHeader />
      </Suspense>
      <Suspense fallback={<StatsSkeleton />}>
        <StatsPanel />
      </Suspense>
    </div>
  );
}

function StatsPanel() {
  const { data } = useSuspenseQuery(statsQuery);
  return <div>{data.totalUsers} users</div>;
}
```

### 4.5 Prefetch on Hover/Focus [HIGH]

```tsx
function ProjectLink({ projectId }: { projectId: string }) {
  const queryClient = useQueryClient();
  const prefetch = () => {
    queryClient.prefetchQuery({
      queryKey: ["project", projectId],
      queryFn: () => fetchProject(projectId),
      staleTime: 30_000,
    });
  };

  return (
    <Link to={`/projects/${projectId}`} onMouseEnter={prefetch} onFocus={prefetch}>
      View Project
    </Link>
  );
}
```

### 4.6 Optimistic Updates [HIGH]

```tsx
const { mutate: toggleLike } = useMutation({
  mutationFn: () => fetch(`/api/posts/${postId}/like`, { method: "POST" }),
  onMutate: async () => {
    await queryClient.cancelQueries({ queryKey: ["post", postId] });
    const previous = queryClient.getQueryData(["post", postId]);
    queryClient.setQueryData(["post", postId], (old: Post) => ({
      ...old,
      liked: !old.liked,
      likeCount: old.liked ? old.likeCount - 1 : old.likeCount + 1,
    }));
    return { previous };
  },
  onError: (_err, _vars, context) => {
    queryClient.setQueryData(["post", postId], context?.previous);
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: ["post", postId] });
  },
});
```

### 4.7 Server-Side Deduplication with React.cache [MEDIUM]

```tsx
import { cache } from "react";

export const getSession = cache(async () => {
  const session = await auth();
  return session?.user?.id ? session : null;
});

// Called in multiple Server Components -- only executes once per request
```

**Rule:** Use primitive args for cache keys. Inline objects cause cache misses.

### 4.8 useSyncExternalStore for Browser APIs [MEDIUM]

```tsx
function subscribe(callback: () => void) {
  window.addEventListener("online", callback);
  window.addEventListener("offline", callback);
  return () => {
    window.removeEventListener("online", callback);
    window.removeEventListener("offline", callback);
  };
}

export function useOnlineStatus() {
  return useSyncExternalStore(subscribe, () => navigator.onLine, () => true);
}
```

---

## 5. Modern React Stack (2026)

### Framework Selection

| Need | Recommendation |
|---|---|
| Public-facing, SEO, SSR | Next.js |
| Progressive enhancement, web fundamentals | Remix |
| SPA, dashboard, internal tool | Vite + React Router or TanStack Router |

### Recommended Libraries

| Concern | Library |
|---|---|
| Server state | TanStack Query |
| Client state (complex) | Zustand or Redux Toolkit |
| Forms | React Hook Form + Zod |
| Routing (custom stack) | TanStack Router (type-safe) or React Router |
| Testing | Vitest + React Testing Library |
| E2E Testing | Playwright or Cypress |
| Build | Vite (or framework-provided) |

### Vite-Specific Rules

- Import from source files, not barrel `index.ts`
- Manual chunk splitting by stability (react, router, query)
- Route-level code splitting with `React.lazy()` + `<Suspense>`
- Add slow deps to `optimizeDeps.include`
- Run `npx vite-bundle-visualizer` after major dep changes
- Prefer CSS Modules or Tailwind over CSS-in-JS (zero runtime)

---

## 6. Anti-Patterns

| Anti-Pattern | Fix |
|---|---|
| Class components for new code | Functional components + hooks |
| `useEffect` for derived state | Compute inline or `useMemo` |
| Components defined inside components | Define at module scope |
| Prop drilling through 3+ levels | Context or composition |
| `useEffect` for event responses | Event handlers |
| `index` as key for dynamic lists | Use stable unique ID |
| `any` type in TypeScript | Define proper types/interfaces |
| State for values derivable from props | Compute during render |
| `useCallback`/`useMemo` everywhere | Only for expensive ops or memo'd children |
| Fetching in `useEffect` without cleanup | TanStack Query or AbortController |
| `dangerouslySetInnerHTML` without sanitization | Always sanitize HTML input |
| Catching errors without ErrorBoundary | Add error boundaries at route/feature level |
