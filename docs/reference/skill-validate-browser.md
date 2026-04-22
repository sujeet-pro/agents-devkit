---
title: 'validate-browser'
description: '|'
skill_name: validate-browser
category: router
---
# validate-browser — real-browser UI validation

Runs a real browser, navigates to a target, and asserts what should be true.

## When to use

- After ANY UI change (`@adk:frontend-feature`, `@adk:frontend-mockup`, `@adk:build-bugfix` when UI-affecting).
- After ANY preview HTML is generated (`.temp/task-<slug>/preview/sample-N.html`).
- As Phase D2 of `@adk:auto`.
- For a UI bug fix to confirm the bug is gone (mode `verify-fix`).
- For an audit of a deployed site (`@adk:audit-site` calls this).

## When NOT to use

- Pure backend / CLI work with no UI surface — skip.
- Unit-test level component logic — use `@adk:build-test` (a.k.a. `adk-build-test`).

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<task-slug>` | yes | |
| `<target>` | yes | URL (`https://...` or `http://localhost:NNNN/...`) or file path (`file://.../sample-N.html` or just `.temp/.../sample-N.html`) |
| `<mode>` | yes | `verify-fix` / `visual-check` / `console-audit` / `interaction-test` / `a11y-audit` |
| `<viewports>` | optional | Default `360,768,1280`; comma-separated CSS px |
| `<script>` | required for `interaction-test` | Path to a markdown / yaml file describing steps |
| `<repro>` | required for `verify-fix` | Path to a markdown describing the original bug repro + the assertion that proves the fix |
| `<baseline>` | optional for `visual-check` | Path to a baseline image folder; default `.temp/task-<slug>/browser-validation/visual-check/baseline/` |
| `--auto` | optional | Skip approval gate before navigating to remote URLs |

## Workflow

```
1. Phase 1 validator. MCP availability check (cursor-ide-browser → playwright → bare npx playwright).
2. Per mode:

   verify-fix:
     a. Read repro doc.
     b. Open browser, navigate to target.
     c. Walk repro steps.
     d. Assert: original error signature absent in console; expected DOM state present;
        screenshot at each step.
     e. Pass = all assertions hold.

   visual-check:
     a. Per viewport (default 360, 768, 1280):
        - Set viewport.
        - Navigate to target.
        - Wait for network idle + 200ms.
        - Capture full-page screenshot to actual/<viewport>.png.
     b. If baseline exists, diff each viewport's actual vs baseline (pixel diff).
        Write diff/<viewport>.png. Threshold: 0.5% pixel difference.
     c. If no baseline: copy actual/ to baseline/ and mark as "first run".

   console-audit:
     a. Open browser, attach console listener + network listener.
     b. Navigate to target.
     c. Wait for full load + 5s idle.
     d. (Optional) Walk a list of URLs.
     e. Report: errors / warnings / failed requests / 4xx-5xx / blocked third-party.

   interaction-test:
     a. Read script (markdown or yaml: list of steps with action + selector + assertion).
     b. Walk steps; capture screenshot per step; assert each.
     c. Final report: pass / fail per step with screenshot evidence.

   a11y-audit:
     a. Open browser, navigate to target.
     b. Inject axe-core (cdn or bundled).
     c. Run axe.run({ runOnly: ['wcag2a','wcag2aa','wcag21aa','wcag22aa'] }).
     d. Per viewport: re-run.
     e. Report violations grouped by severity with WCAG SC references.

3. Write all artifacts to .temp/task-<slug>/browser-validation/<mode>/.
4. Phase 4 validator. All assertions recorded; report.md exists per mode.
5. Final report (chat): pass/fail per mode, link to artifacts.
```

## Mode contract

- `--mode review` (default for standalone use): run the audit, write findings; do NOT modify source code.
- `--mode fix`: for `a11y-audit` and `console-audit`, attempt auto-fixes for known patterns (missing alt text, missing aria-label, broken `outline:none`, missing lang attr). Validates after.
- `--mode auto`: same as `review` followed by an offer to run `--mode fix` on auto-fixable findings.

## Backend selection (priority order)

```
1st: chrome-devtools  MCP — Anthropic's Claude Code Chrome controller (preferred when running in Claude)
2nd: cursor-ide-browser MCP — Cursor IDE's built-in browser (preferred when running in Cursor)
3rd: playwright MCP — universal fallback (`npx -y @playwright/mcp`)
4th: bare `npx playwright` script — generated in .temp/scripts/ on the fly (last resort)
```

Selection logic: probe each backend in order and pick the first available. The probe is fast (no navigation) — list MCP tools and look for the canonical method name (`chrome.navigate`, `browser_navigate`, `playwright.navigate`). Skill announces the chosen backend in its status banner.

If none are available → fail Phase 1 with a clear "install one of: chrome-devtools MCP, cursor-ide-browser MCP, playwright MCP, or `npm i -D @playwright/test`" message.

## Output (per mode)

```
.temp/task-<slug>/browser-validation/
├── verify-fix/
│   ├── report.md
│   ├── screenshots/step-N.png
│   ├── console.json
│   └── network.har
├── visual-check/
│   ├── baseline/<viewport>.png
│   ├── actual/<viewport>.png
│   ├── diff/<viewport>.png
│   └── report.md
├── console-audit/
│   ├── report.md
│   └── raw.json
├── interaction-test/
│   ├── trace.md
│   └── screenshots/step-N.png
└── a11y-audit/
    ├── report.md
    └── axe.json
```

## Reporting

Each mode's `report.md` follows the structured shape in `references/output-format.md`:
- Status banner.
- Pass/fail summary.
- Findings ordered by severity.
- Evidence links (screenshots, HAR, axe JSON).
- Suggested fixes (auto-applicable in `--mode fix`).

## Anti-patterns

- Trusting headless typecheck as proof a UI works.
- Skipping `console-audit` because "the page looked ok" — runtime errors hide.
- Diffing visuals without a baseline (always allow first-run baseline-creation).
- Auto-fixing accessibility violations without re-validating.
- Closing the browser between steps in `interaction-test` (state lost).
- Running on a remote URL without explicit `--auto` (should approval-gate).

## References

| File | Purpose |
| --- | --- |
| `references/how-it-works.md` | Mode-by-mode flow + MCP fallback chain diagram |
| `references/modes.md` | All five mode behaviors |
| `references/persona.md` | The browser-validator |
| `references/workflow.md` | Per-mode detailed step list |
| `references/clarifying-questions.md` | Target / viewports / mode / repro file |
| `references/output-format.md` | Per-mode report shape |
| `references/artifact-format.md` | `browser-validation/` folder layout |
| `references/validator.md` | Four-phase gate |
| `references/anti-patterns.md` | What NOT to do |
| `references/mcp-fallback.md` | cursor-ide-browser → playwright → npx playwright |
| `references/interaction-script-format.md` | yaml/md syntax for `interaction-test` mode |
| `references/repro-format.md` | md syntax for `verify-fix` mode |
| `references/severity-ladder.md` | How to grade findings (Blocker/Critical/Should/May/Nit) |
| `references/auto-fix-recipes.md` | Patterns we can auto-fix in `--mode fix` |
| `references/examples.md` | Worked examples per mode |
| `references/interaction-contract.md` | Synced from canonical |
