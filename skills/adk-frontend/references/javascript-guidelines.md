# JavaScript Coding Guidelines

Comprehensive reference for modern JavaScript patterns, performance optimization, and loading strategies. Covers design patterns, runtime performance, bundle optimization, and resource loading.

---

## 1. Design Patterns

### 1.1 Singleton

Ensure one instance exists, shared application-wide. In JS, prefer module exports over class singletons.

```js
// DO: Module-scoped singleton (simplest)
let counter = 0;
export const increment = () => ++counter;
export const getCount = () => counter;

// DO: Frozen class singleton (when class is needed)
let instance;
class Config {
  constructor() {
    if (instance) throw new Error("Use Config.getInstance()");
    instance = this;
    this.settings = {};
  }
  static getInstance() { return instance || new Config(); }
}
export default Object.freeze(Config.getInstance());
```

**When to use:** Global config, shared caches, connection pools.
**Anti-pattern:** Using singletons for testable state -- prefer dependency injection.

### 1.2 Observer

Decouple event producers from consumers via subscribe/notify.

```js
class EventBus {
  #listeners = new Map();
  on(event, fn) {
    if (!this.#listeners.has(event)) this.#listeners.set(event, new Set());
    this.#listeners.get(event).add(fn);
    return () => this.#listeners.get(event)?.delete(fn); // unsubscribe
  }
  emit(event, data) {
    this.#listeners.get(event)?.forEach(fn => fn(data));
  }
}
```

**When to use:** Event-driven communication, real-time updates, decoupled modules.
**Anti-pattern:** Over-subscribing without cleanup (memory leaks). Always return unsubscribe functions.

### 1.3 Proxy

Intercept object operations for validation, logging, or access control.

```js
const validated = new Proxy(formData, {
  set(obj, prop, value) {
    if (prop === "email" && !value.includes("@")) {
      throw new TypeError("Invalid email");
    }
    return Reflect.set(obj, prop, value);
  },
});
```

**When to use:** Validation layers, debugging, reactive systems.
**Anti-pattern:** Proxies in hot paths -- they add overhead on every access. Use only for cold-path validation.

### 1.4 Module

ES modules are the standard. Use `import`/`export` everywhere.

```js
// Named exports (preferred for libraries)
export function add(x, y) { return x + y; }
export function multiply(x, y) { return x * y; }

// Default export (one per module, for primary export)
export default class UserService { /* ... */ }

// Dynamic import (code splitting)
const { Chart } = await import("./Chart.js");

// Re-export barrel (use sparingly -- see performance section)
export { Button } from "./Button.js";
export { Input } from "./Input.js";
```

**Rule:** Always use ES modules. CommonJS (`require`) cannot be tree-shaken.

### 1.5 Factory

Create objects without `new`, centralizing creation logic.

```js
const createUser = ({ name, email, role = "viewer" }) => ({
  name,
  email,
  role,
  createdAt: new Date(),
  hasPermission(action) {
    return ROLE_PERMISSIONS[this.role]?.includes(action) ?? false;
  },
});
```

**When to use:** Object creation with defaults, polymorphic construction, test fixtures.
**Note:** For many instances, classes share methods via prototype (more memory efficient).

### 1.6 Command

Encapsulate operations as objects for undo/redo, queuing, or logging.

```js
class CommandManager {
  #history = [];
  execute(command) {
    command.execute();
    this.#history.push(command);
  }
  undo() {
    const command = this.#history.pop();
    command?.undo();
  }
}

const moveCommand = (element, dx, dy) => ({
  execute() { element.x += dx; element.y += dy; },
  undo()    { element.x -= dx; element.y -= dy; },
});
```

### 1.7 Provider (React Context)

Share data across component trees without prop drilling.

```jsx
const ThemeContext = React.createContext();

function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be inside ThemeProvider");
  return ctx;
}

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState("light");
  const value = useMemo(() => ({ theme, setTheme }), [theme]);
  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
```

**Rule:** Split contexts by update frequency. Memoize context values to avoid unnecessary re-renders.

### 1.8 Mediator/Middleware

Route communication through a central point (Express middleware, event bus).

```js
// Express middleware chain
app.use((req, res, next) => {
  req.startTime = Date.now();
  next();
});
app.use((req, res, next) => {
  console.log(`${req.method} ${req.url}`);
  next();
});
```

### 1.9 Flyweight

Conserve memory by sharing intrinsic state via a cache.

```js
const iconCache = new Map();
function getIcon(name) {
  if (!iconCache.has(name)) {
    iconCache.set(name, createSVGElement(name)); // expensive
  }
  return iconCache.get(name).cloneNode(true);
}
```

**When to use:** Thousands of similar objects. Less relevant for small collections.

---

## 2. Runtime Performance

**Priority:** Fix algorithms first (O(n^2) to O(n), remove waterfalls, reduce DOM mutations). Then apply micro-patterns.

### 2.1 Use Set/Map for Lookups [HIGH]

```js
// DON'T: O(n) per check
const allowed = ["a", "b", "c", /* ...hundreds */];
items.filter(item => allowed.includes(item.id)); // O(n * m)

// DO: O(1) per check
const allowed = new Set(["a", "b", "c"]);
items.filter(item => allowed.has(item.id)); // O(n)

// For key-value lookups
const userMap = new Map(users.map(u => [u.id, u]));
const user = userMap.get(targetId); // O(1)
```

### 2.2 Batch DOM Reads/Writes [HIGH]

```js
// DON'T: Layout thrashing (read-write-read-write)
elements.forEach(el => {
  const h = el.offsetHeight;      // read -> forces layout
  el.style.height = `${h * 2}px`; // write
});

// DO: Batch reads, then batch writes
const heights = elements.map(el => el.offsetHeight);
elements.forEach((el, i) => {
  el.style.height = `${heights[i] * 2}px`;
});
```

### 2.3 Memoize Expensive Results [MEDIUM-HIGH]

```js
const cache = new Map();
function expensiveCompute(key) {
  if (cache.has(key)) return cache.get(key);
  const result = /* expensive work */;
  cache.set(key, result);
  return result;
}
```

### 2.4 Combine Iterations [MEDIUM]

```js
// DON'T: 3 iterations, 2 intermediate arrays
const result = users.filter(u => u.active).map(u => u.name).join(", ");

// DO: Single pass
let result = "";
for (const u of users) {
  if (u.active) result += (result ? ", " : "") + u.name;
}
```

### 2.5 Hoist Constants Outside Loops [LOW-MEDIUM]

```js
// DON'T: Regex compiled on every iteration
items.filter(item => /^[a-z0-9]+@[a-z0-9]+\.[a-z]+$/i.test(item));

// DO: Compile once
const EMAIL_RE = /^[a-z0-9]+@[a-z0-9]+\.[a-z]+$/i;
items.filter(item => EMAIL_RE.test(item));
```

### 2.6 requestAnimationFrame for Visual Updates [MEDIUM]

```js
let ticking = false;
window.addEventListener("scroll", () => {
  if (!ticking) {
    requestAnimationFrame(() => {
      updateProgressBar(getScrollPercent());
      ticking = false;
    });
    ticking = true;
  }
}, { passive: true });
```

### 2.7 structuredClone for Deep Copies [LOW]

```js
// DON'T: Loses Dates, Maps, Sets, undefined
const copy = JSON.parse(JSON.stringify(obj));

// DO: Handles all standard types
const copy = structuredClone(obj);
```

### 2.8 Non-Mutating Array Methods [LOW]

```js
const sorted = items.toSorted((a, b) => a.price - b.price);
const reversed = items.toReversed();
const without = items.toSpliced(index, 1);
const changed = items.with(index, newValue);
```

---

## 3. Bundle Optimization

### 3.1 Avoid Barrel File Imports [CRITICAL]

```js
// DON'T: Loads ALL components even if you only use Button
import { Button } from "@/components";
import { Check, X } from "lucide-react"; // loads 1500+ icons

// DO: Import directly from source
import { Button } from "@/components/Button";
import Check from "lucide-react/dist/esm/icons/check";

// Or use vite-plugin-barrel for auto-fix
plugins: [barrel({ packages: ["lucide-react", "@mui/material"] })];
```

### 3.2 Manual Chunk Splitting [HIGH]

```js
// vite.config.ts
build: {
  rollupOptions: {
    output: {
      manualChunks: {
        "vendor-react": ["react", "react-dom"],
        "vendor-router": ["react-router-dom"],
        "vendor-query": ["@tanstack/react-query"],
      },
    },
  },
}
```

### 3.3 Route-Level Code Splitting [HIGH]

```jsx
const Home = lazy(() => import("./pages/Home"));
const Dashboard = lazy(() => import("./pages/Dashboard"));
const Settings = lazy(() => import("./pages/Settings"));

<Suspense fallback={<PageSkeleton />}>
  <Routes>
    <Route path="/" element={<Home />} />
    <Route path="/dashboard" element={<Dashboard />} />
    <Route path="/settings" element={<Settings />} />
  </Routes>
</Suspense>
```

### 3.4 Tree Shaking

**Rules:**
- Use ES modules (`import`/`export`), not CommonJS (`require`)
- Use named imports, not `import *`
- Mark packages `"sideEffects": false` in package.json when safe
- Modules with side effects at import time cannot be tree-shaken

### 3.5 Compression

```js
// vite.config.ts -- enable Brotli + Gzip
import compression from "vite-plugin-compression";

plugins: [
  compression({ algorithm: "gzip" }),
  compression({ algorithm: "brotliCompress" }),
];
```

Brotli is 15-25% better than Gzip. Use static compression for built assets.

### 3.6 Bundle Analysis

```bash
npx vite-bundle-visualizer
```

**Red flags:** Chunks > 200KB gzipped, duplicate packages, full libraries when only a few functions are used.

### 3.7 Dead Code via Environment

```js
// Removed in production build
if (import.meta.env.DEV) {
  console.log("Debug:", data);
}
```

---

## 4. Loading and Import Patterns

### 4.1 Loading Sequence

**Optimal order for Core Web Vitals:**

| Priority | Resource |
|---|---|
| 1 | Inline critical CSS + font preconnect |
| 2 | LCP image (preload or fetchpriority="high") |
| 3 | First-party JS for interactivity (defer) |
| 4 | Above-the-fold images |
| 5 | Non-critical CSS (async) |
| 6 | Below-the-fold images (lazy) |
| 7 | Third-party scripts (defer/lazyOnload) |

### 4.2 Dynamic Import

```js
// Load on demand (code splitting)
const openModal = async () => {
  const { ConfirmDialog } = await import("./ConfirmDialog");
  renderDialog(ConfirmDialog);
};
```

### 4.3 Import on Visibility

```js
// Lazy-load when element scrolls into viewport
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      import("./HeavyWidget").then(mod => {
        renderWidget(entry.target, mod.default);
      });
      observer.unobserve(entry.target);
    }
  });
});
observer.observe(document.querySelector("#widget-slot"));
```

### 4.4 Import on Interaction

```jsx
// Load expensive code only when user interacts
<button
  onMouseEnter={() => import("./EmojiPicker")} // prefetch on hover
  onClick={async () => {
    const { EmojiPicker } = await import("./EmojiPicker");
    setPicker(<EmojiPicker />);
  }}
>
  Add Emoji
</button>
```

**Facade pattern:** Replace heavy embeds with lightweight placeholders:
- YouTube: `lite-youtube-embed` (image + play button, loads iframe on click)
- Chat widgets: fake chat button, loads real widget on click
- Maps: static image, loads interactive map on click

### 4.5 Preload vs Prefetch

```html
<!-- Preload: high priority, needed for current page -->
<link rel="preload" href="/fonts/inter.woff2" as="font" type="font/woff2" crossorigin />
<link rel="preload" href="/hero.webp" as="image" />

<!-- Prefetch: low priority, needed for next navigation -->
<link rel="prefetch" href="/dashboard.js" />
<link rel="prefetch" href="/next-page.html" />
```

**Rule:** Always set `crossorigin` on font preloads (fonts are CORS resources). Without it, the browser fetches the font twice.

### 4.6 PRPL Pattern

1. **Push** critical resources via preload hints
2. **Render** initial route ASAP
3. **Pre-cache** remaining routes via service workers
4. **Lazy-load** non-critical routes/assets on demand

### 4.7 Third-Party Script Optimization

| Script Type | Strategy |
|---|---|
| Analytics, tag managers | `defer` or `afterInteractive` |
| Chat widgets | Facade pattern, load on click |
| YouTube/maps embeds | Facade pattern (`lite-youtube-embed`) |
| Social share buttons | `lazyOnload` |
| Bot detection, consent | `beforeInteractive` |
| A/B testing | Server-side when possible |

```jsx
// Next.js Script component
import Script from "next/script";
<Script src="https://analytics.example.com/a.js" strategy="afterInteractive" />
<Script src="https://chat.example.com/widget.js" strategy="lazyOnload" />
```

### 4.8 Islands Architecture

Ship static HTML with zero JS for most of the page, hydrate only interactive "islands".

```astro
<!-- Astro: only SocialButtons ships JS -->
<article class="content">
  <h1>Post title (static HTML, no JS)</h1>
  <p>Content...</p>
  <SocialButtons client:visible />
</article>
```

**When to use:** Content-heavy sites (blogs, docs, marketing) with sprinkles of interactivity.
**Frameworks:** Astro, Marko, Eleventy + Preact.

### 4.9 View Transitions API

```js
// Smooth page transitions with CSS control
if (document.startViewTransition) {
  document.startViewTransition(() => {
    updateDOM(); // swap content
  });
}
```

```css
/* Customize transition per element */
.hero-image { view-transition-name: hero; }

::view-transition-old(hero) { animation: 300ms ease-out fade-out; }
::view-transition-new(hero) { animation: 300ms ease-in fade-in; }
```

### 4.10 Virtual Lists / Windowing

Render only visible rows for large lists (hundreds/thousands of items).

```jsx
import { FixedSizeList } from "react-window";

<FixedSizeList height={600} itemCount={items.length} itemSize={50} width="100%">
  {({ index, style }) => (
    <div style={style}>{items[index].name}</div>
  )}
</FixedSizeList>
```

**Rule:** Use `react-window` (lighter) or `@tanstack/virtual`. CSS `content-visibility: auto` is a simpler alternative for non-React contexts.

---

## 5. General JavaScript Rules

### Modern Syntax

```js
// Use const by default, let when rebinding needed, never var
const name = "Alice";
let counter = 0;

// Optional chaining and nullish coalescing
const city = user?.address?.city ?? "Unknown";

// Destructuring
const { id, name: userName, roles = [] } = user;
const [first, ...rest] = items;

// Template literals
const message = `Hello ${userName}, you have ${roles.length} roles`;

// Object shorthand
const point = { x, y, toString() { return `(${x}, ${y})`; } };

// Spread for immutable updates
const updated = { ...user, name: "Bob" };
const appended = [...items, newItem];
```

### Error Handling

```js
// Specific error types
class ValidationError extends Error {
  constructor(field, message) {
    super(message);
    this.name = "ValidationError";
    this.field = field;
  }
}

// Catch specific errors
try {
  await processOrder(order);
} catch (error) {
  if (error instanceof ValidationError) {
    showFieldError(error.field, error.message);
  } else {
    throw error; // re-throw unexpected errors
  }
}
```

### Async Patterns

```js
// Parallel independent operations
const [user, posts, comments] = await Promise.all([
  fetchUser(id),
  fetchPosts(id),
  fetchComments(id),
]);

// Sequential with error boundaries
for (const item of items) {
  try {
    await processItem(item);
  } catch (error) {
    console.error(`Failed to process ${item.id}:`, error);
  }
}

// AbortController for cancellation
const controller = new AbortController();
const response = await fetch(url, { signal: controller.signal });
// cancel with: controller.abort()
```

### Avoid Common Mistakes

```js
// DON'T: == (loose equality)
if (value == null) { }   // matches null AND undefined (this specific case is OK)
if (value == 0) { }      // BAD: "" == 0 is true

// DO: === (strict equality)
if (value === 0) { }

// DON'T: typeof checks that miss null
typeof null === "object"  // true! Use explicit null check

// DON'T: for...in on arrays (iterates prototype keys)
for (const i in arr) { }

// DO: for...of on arrays
for (const item of arr) { }

// DON'T: Floating point comparison
0.1 + 0.2 === 0.3  // false
// DO: Compare with epsilon
Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON
```
