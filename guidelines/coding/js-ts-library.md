# JavaScript / TypeScript Library Review Guidelines

These guidelines apply to **reusable JS/TS libraries** and **npm packages**. They
supplement the general guidelines with rules specific to building maintainable,
well-typed, and consumer-friendly library code that others depend on.

---

## 1. Public API Surface

- **Be intentional about exports.** Every export is a contract with consumers. Only
  export what consumers need. Keep internal helpers, utilities, and implementation
  details unexported.
- **Barrel files** (`index.ts`): The main entry point should re-export the public API
  in a clear, organized manner. Do not export everything from every file.
- **Named exports over default exports.** Named exports are easier to refactor,
  tree-shake, and auto-import. Default exports make it harder to enforce consistent
  naming across consuming codebases.
- **Export stability**:
  - Removing an export is a **breaking change** (major version bump).
  - Adding an export is a minor change.
  - Renaming an export is a breaking change (it removes the old name).
- **Avoid re-exporting third-party types.** If the library wraps a third-party
  library, do not expose its types in the public API. Define your own types that
  abstract away the dependency. This prevents breaking consumers when the dependency
  updates.
- **Package `exports` field**: Use the `exports` field in `package.json` to define
  explicit entry points. This replaces the older `main`/`module`/`browser` approach
  and gives you fine-grained control over what is importable.
  ```json
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    },
    "./utils": {
      "types": "./dist/utils.d.ts",
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.cjs"
    }
  }
  ```

## 2. TypeScript Types and Interfaces

- **All public APIs must be fully typed.** No `any` in public-facing types. Use
  `unknown` with type guards when the type is genuinely unknown.
- **Export all types that consumers need.** If a function returns a `Result<T>`,
  the `Result` type must be exported so consumers can reference it.
- **Use generics for flexibility.** Libraries should provide generic functions and
  types when the specific type varies by consumer.
  ```ts
  // Good: generic, reusable
  function createStore<T>(initial: T): Store<T>
  // Bad: forces consumers into a specific type
  function createStore(initial: Record<string, unknown>): Store
  ```
- **Discriminated unions over flags.** Use discriminated unions for variant types
  instead of boolean flags or string enums.
  ```ts
  // Good
  type Result<T> = { ok: true; value: T } | { ok: false; error: Error }
  // Bad
  type Result<T> = { ok: boolean; value?: T; error?: Error }
  ```
- **Declaration files**: Ensure `.d.ts` files are generated and included in the
  published package. The `types` field in `package.json` must point to the correct
  declaration file.
- **Strict types**: The library should compile with `strict: true`. If it does not,
  flag it.
- **Avoid `namespace`**: Use module-level exports instead of TypeScript namespaces.
  Namespaces do not tree-shake and are a legacy pattern.

## 3. Bundle Size

- **Tree-shaking must work.** Verify that unused exports are eliminated by bundlers.
  Requirements:
  - Use ESM (`import`/`export`), not CommonJS (`require`/`module.exports`) in source
  - Set `"sideEffects": false` in `package.json` (or list specific side-effect files)
  - Avoid module-level side effects (code that runs on import)
- **Measure bundle size on every PR.** Use `size-limit`, `bundlesize`, or similar
  tools. Set budgets and fail the build if they are exceeded.
- **Dependency cost**: When adding a new dependency:
  - Justify why it is needed (cannot be implemented in a reasonable amount of code)
  - Check its size with `bundlephobia.com`
  - Prefer smaller, focused packages over large swiss-army-knife libraries
  - Consider making it a `peerDependency` if consumers likely already have it
- **Code splitting**: For large libraries, support per-feature imports:
  ```ts
  // Consumer imports only what they need
  import { format } from 'my-lib/format'
  import { parse } from 'my-lib/parse'
  ```
- **No accidental inclusions**: Ensure development-only files (tests, stories,
  fixtures, docs) are excluded from the published package via `files` field in
  `package.json` or `.npmignore`.

## 4. Backward Compatibility

- **Do not break existing consumers without a major version bump.** Any change to
  the public API surface, default behavior, or required runtime environment is a
  breaking change.
- **Deprecation before removal.** When replacing a feature:
  1. Add the new feature in a minor release
  2. Mark the old feature as deprecated (JSDoc `@deprecated` + runtime warning)
  3. Remove the old feature in the next major release
  4. Provide a codemod when feasible
- **Behavioral changes are breaking changes.** If a function that previously returned
  `null` now throws, that is a breaking change -- even if the type signature is
  unchanged.
- **Default value changes are breaking changes.** Changing a default parameter value
  changes behavior for all consumers who rely on the default.
- **Test with consumers**: If possible, run tests of known downstream consumers
  against the proposed changes (especially for major version bumps).

## 5. Semantic Versioning

- **Follow semver strictly.** The version number communicates to consumers whether
  they can safely upgrade.
  - **Patch** (`x.y.Z`): Bug fixes that do not change the API
  - **Minor** (`x.Y.0`): New features, new exports, new options -- all additive
  - **Major** (`X.0.0`): Breaking changes of any kind
- **Pre-release versions** (`1.0.0-beta.1`, `1.0.0-rc.1`): Use for testing breaking
  changes before a stable release. Publish under a dist tag (e.g., `npm publish
  --tag next`).
- **Changelog**: Maintain a `CHANGELOG.md` (or equivalent) that documents every
  user-facing change. Group entries by version and category (Added, Changed, Fixed,
  Removed, Deprecated, Security).
- **Version bump must be part of the release process.** Do not rely on manual
  bumping. Use `changesets`, `standard-version`, `semantic-release`, or similar.

## 6. Test Coverage

- **Public API must be thoroughly tested.** Every exported function, class, and
  component should have tests covering:
  - Happy path with typical inputs
  - Edge cases (empty input, zero, null, undefined, maximum values)
  - Error cases (invalid input, network failure, etc.)
  - Type narrowing (for discriminated unions and overloads)
- **No tests for internals.** Test through the public API. Internal helpers can
  change without breaking consumers, so testing them couples tests to implementation.
- **Snapshot tests are acceptable for serializable output** (e.g., AST transforms,
  serialized objects). But prefer explicit assertions for behavior.
- **Performance tests**: For performance-critical libraries, include benchmarks and
  run them in CI to detect regressions.
- **Cross-environment tests**: If the library runs in both Node.js and browsers,
  test in both environments.

## 7. Documentation

- **Every public export must have JSDoc.** Minimum:
  - One-line summary
  - `@param` for each parameter
  - `@returns` description
  - `@throws` for known error conditions
  - `@example` for non-obvious usage
  - `@since` version when the API was added
  - `@deprecated` with migration path (when applicable)
- **README must include**:
  - What the library does (one paragraph)
  - Installation instructions
  - Quick start / basic usage example
  - API reference (or link to full docs)
  - Requirements (Node.js version, TypeScript version, etc.)
- **Examples**: Provide a working example in the repo (e.g., `examples/` directory)
  for common use cases. Examples should be runnable.
- **TypeDoc/API reference**: For larger libraries, generate API documentation from
  JSDoc with TypeDoc or similar tools.

## 8. Error Handling

- **Throw specific, typed errors.** Define custom error classes that extend `Error`.
  Give them meaningful names and properties.
  ```ts
  class ValidationError extends Error {
    constructor(
      message: string,
      public readonly field: string,
      public readonly value: unknown
    ) {
      super(message)
      this.name = 'ValidationError'
    }
  }
  ```
- **Error messages must be actionable.** Include:
  - What went wrong
  - What was expected
  - What was received
  - How to fix it (when possible)
  ```ts
  // Good
  throw new ValidationError(
    `Expected "format" to be one of: ${FORMATS.join(', ')}. Received: "${input}".`,
    'format', input
  )
  // Bad
  throw new Error('Invalid format')
  ```
- **Document thrown errors in JSDoc.** Consumers need to know what to `catch`.
- **Never swallow errors in library code.** If an error occurs, either handle it
  with clear recovery logic or propagate it to the consumer. Silent failures are
  the worst kind of bugs in a library.
- **Result types as an alternative**: For functions where errors are expected and
  frequent (parsing, validation), consider returning a `Result<T, E>` type instead
  of throwing. This forces consumers to handle both cases.

## 9. Dependency Management

- **Zero dependencies is the ideal.** Every dependency is a liability: supply chain
  risk, version conflict risk, bundle size cost, and maintenance burden.
- **Justify every dependency** in the PR description. Explain what it provides and
  why it cannot be implemented in the library itself.
- **Prefer `peerDependencies`** for dependencies that consumers likely already have
  (React, TypeScript, Node.js built-ins). This avoids duplicate installations.
- **Pin exact versions** for `dependencies` (not `peerDependencies`). Use
  `package-lock.json` / `pnpm-lock.yaml` / `yarn.lock` and commit it.
- **Audit dependencies**: New dependencies should be checked for:
  - Active maintenance (recent commits, responsive to issues)
  - Known vulnerabilities (`npm audit`)
  - License compatibility (MIT, Apache 2.0, BSD are safe; GPL may be problematic)
  - Bundle size impact
  - TypeScript type support
- **No `devDependencies` in production bundle.** Ensure build tooling, test
  frameworks, and linters are in `devDependencies`, not `dependencies`.

## 10. ESM + CJS Support

- **Ship both ESM and CJS.** Many consumers still use CommonJS (especially in
  Node.js). Provide both formats.
  ```json
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "types": "./dist/index.d.ts",
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs"
    }
  }
  ```
- **Test both formats.** Import the built package in both ESM and CJS contexts to
  verify it loads correctly.
- **Avoid CJS-only patterns** in source code (e.g., `__dirname`, `require.resolve`).
  Use ESM equivalents (`import.meta.url`, `import()`).
- **Dual package hazard**: When shipping both formats, ensure that consumers do not
  accidentally load both copies (which causes issues with `instanceof` checks and
  module-level state). Use the `exports` field to prevent this.

## 11. Node.js Version Compatibility

- **Declare minimum Node.js version** in `package.json`:
  ```json
  "engines": { "node": ">=18" }
  ```
- **Test on the minimum declared version.** CI should run tests on the oldest
  supported Node.js version, not just the latest.
- **Do not use APIs newer than the minimum version** without checking availability
  or polyfilling. Examples:
  - `Array.prototype.at()` requires Node 16.6+
  - `structuredClone()` requires Node 17+
  - `fetch()` (native) requires Node 18+
  - `AbortSignal.any()` requires Node 20+
- **Document Node.js requirements** in the README.
- **LTS policy**: Prefer supporting only Active LTS and Current Node.js versions.
  Drop support for EOL versions in minor releases (with documentation).
