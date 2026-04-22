# `validate-browser` — backend selection chain

The skill probes for backends in this priority order and picks the first available. The probe is non-destructive (lists MCP tools; does NOT navigate).

## 1. chrome-devtools MCP (1st priority — preferred everywhere)

Anthropic's Claude Code Chrome controller — `@anthropic/chrome-devtools-mcp` (or whatever the official package name is at your installed version; check `claude mcp ls`).

Tools used (typical names; verify via `claude mcp ls --tools chrome-devtools`):
- `chrome.navigate(url)` — navigate
- `chrome.screenshot({ fullPage, viewport: { width, height } })` — capture
- `chrome.snapshot()` — accessibility tree
- `chrome.console_messages()` — console log
- `chrome.network_requests()` — network log (optionally HAR-format)
- `chrome.evaluate(script)` — for axe-core injection
- `chrome.resize({ width, height })` — viewport switching for visual-check
- `chrome.click(selector)`, `chrome.type(selector, text)`, `chrome.hover(selector)` — interaction-test
- `chrome.dialog(...)` — handle confirm/prompt

Why first: officially supported in Claude Code, no Cursor dependency, ships with the same Chrome version Anthropic tests against.

## 2. cursor-ide-browser MCP (2nd priority — when host is Cursor)

Cursor's bundled browser MCP. Use when Claude Code is running inside Cursor (the host detection is implicit — Cursor injects the MCP automatically).

Tools used:
- `browser_navigate(url)`
- `browser_lock({ action: "lock" | "unlock" })` — REQUIRED wrap around interactions in Cursor
- `browser_snapshot()` — accessibility-tree (returns refs for click/type)
- `browser_take_screenshot({ fullPage, viewport: { width, height } })`
- `browser_console_messages()`
- `browser_network_requests()`
- `browser_evaluate(script)`
- `browser_resize({ width, height })`
- `browser_click({ ref })`, `browser_type({ ref, text })`, `browser_hover({ ref })`
- `browser_handle_dialog(...)`

Workflow inside Cursor:
1. `browser_navigate(target)`
2. `browser_lock({ action: "lock" })`
3. (interactions)
4. `browser_lock({ action: "unlock" })`

## 3. playwright MCP (3rd priority — universal fallback)

Install: `npx -y @playwright/mcp` (or via `bin/adk-mcp-install`).

Tools (canonical Playwright MCP names):
- `playwright.navigate(url)`
- `playwright.screenshot({...})`
- `playwright.snapshot()` (or `accessibility_tree()`)
- `playwright.console_messages()`
- `playwright.network_requests()`
- `playwright.evaluate(...)`
- `playwright.resize(...)`
- `playwright.click(...)`, `playwright.type(...)`, `playwright.hover(...)`

## 4. Bare `npx playwright` (4th priority — last resort)

Generate a one-off playwright script at `.temp/scripts/browser-validate-<slug>-<mode>.mjs` and run via `node` / `npx playwright test`. Headless by default. Use only when no MCP backend is available.

Template lives at `references/playwright-template.md` (created on first use).

## Selection logic

```javascript
async function pickBackend() {
  // 1st: Claude's chrome-devtools MCP
  if (await mcpAvailable("chrome-devtools")) return { backend: "chrome-devtools-mcp", api: "chrome.*" };
  // 2nd: Cursor's bundled browser MCP
  if (await mcpAvailable("cursor-ide-browser")) return { backend: "cursor-ide-browser-mcp", api: "browser_*" };
  // 3rd: playwright MCP (universal)
  if (await mcpAvailable("playwright")) return { backend: "playwright-mcp", api: "playwright.*" };
  // 4th: bare playwright on disk
  if (await commandExists("npx") && await packageInstalled("@playwright/test")) return { backend: "npx-playwright", api: "script" };
  throw Error("No browser backend available. Install one: chrome-devtools MCP, cursor-ide-browser MCP, playwright MCP, or `npm i -D @playwright/test`");
}
```

## Per-mode method abstraction

Each mode (`verify-fix`, `visual-check`, `console-audit`, `interaction-test`, `a11y-audit`) writes its workflow against an internal abstraction (`navigate`, `screenshot`, `console`, `evaluate`, `click`, etc.). The picked backend's API is mapped to those primitives by a small adapter — same workflow, different tool names underneath. The status banner prints the chosen backend so the user can see which one ran.
