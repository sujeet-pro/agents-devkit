# `validate-browser` — how it works

## Backend selection chain (priority order)

```mermaid
flowchart TD
    Start["validate-browser invoked"] --> Try1{"chrome-devtools MCP available? (Claude's built-in)"}
    Try1 -- yes --> Use1["Use chrome.* tools (chrome.navigate, chrome.screenshot, chrome.snapshot, chrome.console_messages, chrome.network_requests)"]
    Try1 -- no --> Try2{"cursor-ide-browser MCP available? (Cursor host)"}
    Try2 -- yes --> Use2["Use browser_* tools (browser_navigate + browser_lock + browser_take_screenshot + ...)"]
    Try2 -- no --> Try3{"playwright MCP available?"}
    Try3 -- yes --> Use3["Use playwright.* tools"]
    Try3 -- no --> Try4{"npx playwright on disk?"}
    Try4 -- yes --> Use4["Generate one-off playwright script in .temp/scripts/, run via node"]
    Try4 -- no --> Fail["Phase 1 fail: install one of chrome-devtools / cursor-ide-browser / playwright MCP, or `npm i -D @playwright/test`"]
```

The chosen backend is announced in the skill's status banner. Workflows below are written against an internal abstraction; an adapter maps to the picked backend's API (`chrome.*` vs `browser_*` vs `playwright.*`).

## Per-mode flow

```mermaid
flowchart TD
    M{"Mode?"} -- "verify-fix" --> VF["Read repro.md -> walk steps -> assert"]
    M -- "visual-check" --> VC["Per viewport: set -> navigate -> screenshot -> diff vs baseline"]
    M -- "console-audit" --> CA["Attach console+network listeners -> navigate -> wait idle -> report errors/warnings/failures"]
    M -- "interaction-test" --> IT["Read script.yaml -> walk actions -> assert state"]
    M -- "a11y-audit" --> AA["Inject axe-core -> per-viewport scan -> group by WCAG SC"]
    VF --> Write
    VC --> Write
    CA --> Write
    IT --> Write
    AA --> Write
    Write["Write report.md + raw evidence to .temp/task-slug/browser-validation/<mode>/"]
```

## Visual diff threshold

```mermaid
flowchart LR
    Cap["Capture actual screenshot"] --> Has{"Baseline exists?"}
    Has -- no --> Mkbase["Save as new baseline. Mark 'first run'. Pass."]
    Has -- yes --> Diff["pixelmatch(actual, baseline)"]
    Diff --> Pct{"diff% > 0.5?"}
    Pct -- no --> Pass["Pass. Save diff/<viewport>.png annotated."]
    Pct -- yes --> Fail["Fail. Save diff. Surface in report."]
```

## a11y-audit severity mapping

```mermaid
flowchart LR
    AxeViolation["axe violation"] --> Impact{"impact?"}
    Impact -- "critical" --> Blocker["Severity: Blocker"]
    Impact -- "serious" --> Critical["Severity: Critical"]
    Impact -- "moderate" --> Should["Severity: Should Have"]
    Impact -- "minor" --> May["Severity: May Have"]
```
