# `code-migrate` — worked examples

## Example 1 — React 18 → 19

**Prompt:** `/adk-code:code-migrate "React 18 to 19" --scope packages/web`

**Phase 0:** Slug `migrate-react-18-19`. Repo `~/code/acme/storefront`. Scope `packages/web`. From: `^18.2.0` (per `package.json`). To: `^19.0.0`.

**Phase 1:** Clean tree. Branch `migrate/react-18-19`. Commands: `pnpm typecheck && pnpm lint && pnpm test --filter web && pnpm build --filter web`. Baseline green.

**Phase 2:** WebFetch `https://react.dev/blog/2024/12/05/react-19` and the upgrade guide. Curate `migration-notes.md`:

```markdown
## Breaking changes (React 19)
1. `<Context.Provider>` is now just `<Context>`.
   Source: react.dev/upgrade-guide
   Quote (≤15 words): "context can render directly: <Context value={...}>"
   Applies: yes (we use 11 contexts).
2. `useRef` requires an initial value.
   Quote: "useRef must be called with one argument".
   Applies: yes (~30 sites without arg).
3. Removed legacy refs (string refs, findDOMNode).
   Quote: "string refs and findDOMNode no longer supported".
   Applies: yes (3 occurrences in old class components).
4. Some new ref types …
   …
```

**Phase 3 inventory:**

```markdown
## Inventory
| Rule | Pattern | Files | Sites |
| --- | --- | --- | --- |
| Context.Provider → Context | `<\w+\.Provider` | 11 | 38 |
| useRef requires init value | `useRef\(\s*\)` | 23 | 31 |
| Legacy refs removed | `findDOMNode\|string-ref` | 3 | 3 |
```

**Phase 4 plan groups:**

```markdown
## Groups
| # | Name | Files | Strategy |
| --- | --- | --- | --- |
| 1 | useRef init values | 23 | mechanical: pass `null` to all `useRef()` |
| 2 | Context.Provider → Context | 11 | mechanical: replace `.Provider` with the bare component |
| 3 | Legacy refs migration | 3 | manual: 3 components to convert to function + forwardRef |
| Z | Bump react/react-dom to 19 in package.json | 1 | last (after source migration) |
```

**Phase 5:** Apply group 1 (mechanical). Tests + typecheck green. Apply group 2. Green. Apply group 3 (3 manual conversions). Test green. Apply group Z (bump versions, run `pnpm install`). Tests green.

**Phase 6 final:** Full build green. Full test green. Smoke check: `pnpm dev --filter web` starts; HMR works on a sample edit.

**Phase 7 report:** `report.md` lists the 4 groups, the rule-by-rule application, the version diff (`react: 18.2.0 → 19.0.0`, `react-dom: 18.2.0 → 19.0.0`), and one item NOT applied: "the new `use()` hook for promises — recommended but optional; deferred to a `code-write` follow-up."

---

## Example 2 — Spring Boot 2 → 3

**Prompt:** `/adk-code:code-migrate "Spring Boot 2.7 to 3.2 in checkout-api"`

**Phase 0:** Slug `migrate-spring-boot-2-3`. Repo `~/code/acme/checkout-api`. From `2.7.18`. To `3.2.0`.

**Phase 1:** Clean. Branch `migrate/spring-boot-2-3`. Commands: `./gradlew compileKotlin check test bootJar`. Baseline green.

**Phase 2:** WebFetch the Spring Boot 3 release notes + the migration guide on GitHub Wiki. Notes the BIG breaking change: Java EE 8 → Jakarta EE 9 (`javax.*` → `jakarta.*`). Plus: minimum Java 17, Spring Framework 6, etc.

**Phase 3 inventory:**

```markdown
## Inventory
| Rule | Pattern | Files | Sites |
| --- | --- | --- | --- |
| javax.* → jakarta.* | `import javax\.(servlet|persistence|validation|transaction)` | 87 | 142 |
| @ConfigurationProperties without setter | `@ConfigurationProperties` (with val/final) | 4 | 4 |
| Removed properties: server.ssl.* | `server.ssl.protocol` etc. | 1 | 1 (application.yml) |
```

**Phase 4 plan groups:**

```markdown
## Groups
| # | Name | Files | Strategy |
| --- | --- | --- | --- |
| 1 | Java 17 minimum | 1 | bump `JavaVersion.VERSION_17` in build.gradle.kts |
| 2 | javax → jakarta (servlet) | 22 | mechanical: replace import |
| 3 | javax → jakarta (persistence) | 31 | mechanical: replace import |
| 4 | javax → jakarta (validation) | 28 | mechanical: replace import |
| 5 | javax → jakarta (transaction) | 6 | mechanical: replace import |
| 6 | @ConfigurationProperties setter | 4 | manual: add setters or use @ConstructorBinding |
| 7 | application.yml ssl prop rename | 1 | per release notes |
| Z | bump spring-boot version | 1 | last |
```

**Phase 5:** Per-group validation. Group 1 succeeds. Group 2 succeeds. Group 3 — 1 file fails because of a custom converter referencing the old package name; smallest follow-up edit; re-run; green. Continue. Group Z bumps versions; full test green.

**Phase 6 final:** Full Gradle `bootJar test check` green. Smoke check: `./gradlew bootRun` starts; `/actuator/health` returns 200.

**Phase 7 report:** Notes that Spring 6 also enabled new defaults that the team may want to opt out of (e.g. Lambda's path-style URL handling); listed as residual risk for a follow-up review.

---

## Example 3 — Node 18 → 20

**Prompt:** `/adk-code:code-migrate "Node 18 to 20 across the storefront repo"`

**Phase 0:** Slug `migrate-node-18-20`. Repo `~/code/acme/storefront`. From `18.20.0` (in `.nvmrc`). To `20.10.0`.

**Phase 1:** Clean. Branch `migrate/node-18-20`. Commands: `pnpm typecheck && pnpm lint && pnpm test && pnpm build`. Baseline green on Node 18.

**Phase 2:** WebFetch the Node 20 release notes + the deprecation list. Notes the changes that affect this codebase:
- `fetch` is no longer experimental (was opt-in in 18; default in 20).
- Some `crypto` algorithm names normalized.
- `--inspect` debugging changes.
- WebSocket built-in (new, not breaking).

**Phase 3 inventory:**

```markdown
## Inventory
| Rule | Pattern | Files | Sites |
| --- | --- | --- | --- |
| fetch from undici / node-fetch (replaceable) | `import.*from ['"]node-fetch['"]` | 4 | 4 |
| crypto.createCipher (deprecated) | `crypto\.createCipher\b` | 0 | 0 (no impact) |
```

**Phase 4 plan groups:**

```markdown
## Groups
| # | Name | Files | Strategy |
| --- | --- | --- | --- |
| 1 | Bump .nvmrc + Dockerfile + CI | 3 | environment-config change |
| 2 | Replace node-fetch with built-in fetch | 4 | mechanical |
| 3 | (opt-in) Adopt built-in WebSocket | 0 | flagged but NOT applied — out of scope |
```

**Phase 5:** Group 1: update `.nvmrc` to `20.10.0`, `Dockerfile` `FROM node:20-alpine`, `.github/workflows/*.yml` to `node-version: 20`. Test passes (CI runs on the new version locally via nvm switch).

Group 2: replace `node-fetch` imports + remove the package. Test green.

**Phase 6 final:** Full build green on Node 20. Full test green. Smoke check: start dev server (`pnpm dev`) — runs cleanly.

**Phase 7 report:** 7 files changed (3 config + 4 code). 1 dependency removed (`node-fetch`). Item NOT applied: built-in WebSocket adoption — listed as a follow-up `code-write` task.

---

## Example 4 — Jest → Vitest

**Prompt:** `/adk-code:code-migrate "Jest to Vitest in packages/web"`

**Phase 0:** Slug `migrate-jest-to-vitest`. Repo `~/code/acme/storefront`. Scope `packages/web`. From: `jest@29`. To: `vitest@latest`.

**Phase 1:** Clean. Branch `migrate/jest-to-vitest`. Commands: `pnpm test --filter web` (currently runs Jest), `pnpm typecheck`, `pnpm lint`. Baseline green.

**Phase 2:** WebFetch `https://vitest.dev/guide/migration.html`. Curate notes. Key items:
- `jest.fn()` → `vi.fn()`. Same API mostly.
- `jest.mock` → `vi.mock` (slightly different module-resolution semantics).
- Globals: Vitest defaults to no-globals; Jest assumes globals. Either enable globals in Vitest config or update tests.
- Snapshot files: format differs slightly; existing snapshots may need re-generation.
- Module imports: Vitest is ESM-first; Jest's CJS interop may differ.

**Phase 3 inventory:**

```markdown
## Inventory
| Rule | Pattern | Files | Sites |
| --- | --- | --- | --- |
| jest.fn → vi.fn | `\bjest\.fn\b` | 47 | 318 |
| jest.mock → vi.mock | `\bjest\.mock\b` | 23 | 41 |
| jest.spyOn → vi.spyOn | `\bjest\.spyOn\b` | 18 | 29 |
| globals (describe/it/expect imports) | (test files using bare globals) | 142 | n/a |
| jest.config.js | filename | 1 | 1 |
```

**Phase 4 plan groups:**

```markdown
## Groups
| # | Name | Files | Strategy |
| --- | --- | --- | --- |
| 1 | Add vitest as devDep + create vitest.config.ts (with globals: true to start) | 2 | dependency add + config |
| 2 | Replace jest.fn → vi.fn (mechanical) | 47 | mechanical |
| 3 | Replace jest.mock → vi.mock + audit semantics | 23 | mechanical + manual review of 5 hard cases |
| 4 | Replace jest.spyOn → vi.spyOn | 18 | mechanical |
| 5 | Update package.json test script: jest → vitest | 1 | config |
| 6 | Re-generate snapshots (if shape differs) | varies | automatic via `vitest --update-snapshots` after Group 5 |
| 7 | Remove jest from devDeps | 1 | last |
```

**Phase 5:** Per-group validation. Groups 1-4 green. Group 5: `pnpm test` now runs Vitest. Some snapshot tests fail because of Vitest's slightly different snapshot format. Group 6: re-generate snapshots; eyeball-diff (the Jest-format → Vitest-format difference is whitespace + serializer detail; not behavior change). Test green. Group 7: remove Jest; full test green.

**Phase 6 final:** Full test on Vitest green (test count matches Jest count: 1,247 passed). Typecheck + lint + build green.

**Phase 7 report:** Lists the 7 groups, ~80 files changed, 1 devDep added (`vitest`), 1 removed (`jest`), residual risk: "5 `jest.mock` cases had subtle hoisting differences; flagged for human review in PR comments. Snapshot format differs (whitespace/serialization) but no behavior changed."
