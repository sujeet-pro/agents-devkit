# ADK Frontend Workflow

## Phases

### Phase 1: Detect
Run `scripts/preflight.py` to identify the project stack.

**Inputs:** `--scope` path, `--stack` override
**Actions:**
- Locate `package.json` in the scope directory
- Parse dependencies and devDependencies
- Detect framework, bundler, CSS framework, TypeScript
- Output detected stack and reference file list

**Outputs:** JSON with `stack`, `framework`, `bundler`, `cssFramework`, `typescript`, `references`

### Phase 2: Load
Read the technology-specific reference files matching the detected stack.

**Actions:**
- Always read `html-guidelines.md` and `css-guidelines.md`
- Read `javascript-guidelines.md` if JS/TS detected
- Read `react-guidelines.md` if React detected
- Read `nextjs-guidelines.md` if Next.js detected
- If `--verbose`, report which references were loaded

**Outputs:** Loaded guideline context

### Phase 3: Apply
Use loaded guidelines as context for all subsequent coding tasks.

**Actions:**
- Silently enforce guidelines during code generation
- Match patterns to the detected framework and its version
- Respect project conventions over generic guidelines
- Do not output guidelines unless asked

**Outputs:** Standards-compliant code

### Phase 4: Surface
When writing or reviewing code, flag violations.

**Actions:**
- Identify guideline violations in existing or proposed code
- Provide the specific guideline, a code example, and the fix
- Keep violation reports to 1-2 lines
- Group related violations

**Outputs:** Violation reports (only when relevant)

## Auto-Load Trigger

The skill auto-loads when any of these conditions are met:
1. `package.json` exists in the working directory or parent (up to 3 levels)
2. `package.json` contains frontend dependencies (react, next, vue, angular, svelte, astro, vite, webpack)
3. `index.html` exists in the working directory
4. The user explicitly invokes `/adk-frontend`

## Stack-Specific Loading Matrix

| Detected Dependencies | References Loaded |
| --- | --- |
| `next` | html, css, js, react, nextjs |
| `react` (no next) | html, css, js, react |
| `vue` | html, css, js |
| `svelte`, `@sveltejs/kit` | html, css, js |
| `@angular/core` | html, css, js |
| `astro` | html, css, js |
| `vite`, `webpack`, `parcel` (no framework) | html, css, js |
| `index.html` only | html, css, js |

## Verbose Mode

When `--verbose` is set, output after detection:
```
Stack Detection:
  package.json: ./package.json
  Framework: nextjs (next@14.2.0)
  Bundler: next-builtin
  CSS: tailwind (tailwindcss@3.4.0)
  TypeScript: true (typescript@5.4.0)
  
Loaded References:
  [x] html-guidelines.md (always)
  [x] css-guidelines.md (always)
  [x] javascript-guidelines.md (JS/TS detected)
  [x] react-guidelines.md (react detected)
  [x] nextjs-guidelines.md (next detected)
```

## Integration with Other Skills

This skill provides **context** for other skills. It does not replace them:

| Invoking Skill | How Frontend Guidelines Help |
| --- | --- |
| `adk-build` | Guidelines inform implementation patterns |
| `adk-review-local-changes` | Guidelines provide the review checklist |
| `adk-design` | HTML/CSS guidelines complement design patterns |
| `adk-refactor` | Guidelines identify modernization targets |
| `adk-audit-site` | Performance guidelines complement site audit |
