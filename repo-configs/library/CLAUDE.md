# JavaScript / TypeScript Library Repository

This is a **JS/TS library** intended for consumption by other packages. All code, reviews, and generation must prioritize API stability, bundle efficiency, and developer experience.

## Devkit Integration

Load library guidelines from the claude-devkit installation:

```
~/.claude/guidelines/general.md          — baseline code quality rules
~/.claude/guidelines/js-ts-library.md    — library-specific rules (if available)
```

Always apply both the general and library guidelines when reviewing or generating code in this repo.

## Public API Surface Management

The public API is the contract with consumers. Every change to the public API must be deliberate and documented.

### Export Rules

1. **Explicit exports only.** Use a barrel file (`index.ts`) to define exactly what is public. Never use `export *` from internal modules.
2. **Internal modules stay internal.** Code that is not exported from the barrel file is implementation detail. Use directory structure or naming conventions (e.g., `internal/`, `_private`) to make this clear.
3. **One entry point per package.** The `exports` field in `package.json` must define all entry points explicitly:
   ```json
   {
     "exports": {
       ".": {
         "import": "./dist/index.mjs",
         "require": "./dist/index.cjs",
         "types": "./dist/index.d.ts"
       },
       "./utils": {
         "import": "./dist/utils.mjs",
         "require": "./dist/utils.cjs",
         "types": "./dist/utils.d.ts"
       }
     }
   }
   ```
4. **No default exports for libraries.** Use named exports exclusively. Default exports cause issues with CommonJS interop and make tree-shaking less predictable.
5. **Re-export types.** All public TypeScript types, interfaces, and enums must be exported from the barrel file.

### API Documentation

Every public export must have:
- JSDoc comment with `@description`, `@param`, `@returns`, `@throws`, `@example`
- TypeScript type annotations (no `any` in public APIs)
- At least one usage example in the JSDoc

## Bundle Size Awareness

Library consumers pay the cost of every byte. Bundle size is a feature.

### Size Rules

1. **Track bundle size in CI.** Use `size-limit`, `bundlewatch`, or equivalent to enforce size budgets.
2. **No unnecessary dependencies.** Every production dependency must be justified. Prefer implementing small utilities over adding a dependency.
3. **Peer dependencies for frameworks.** React, Vue, Angular, and similar frameworks must be peer dependencies, not direct dependencies.
4. **Side-effect free.** Mark `"sideEffects": false` in `package.json` when applicable. If specific files have side effects, list them explicitly.
5. **Measure before and after.** When adding new functionality, report the bundle size impact in the PR description.

### Size Budgets (adjust per project)

- Core package: < 10KB gzipped
- With all optional features: < 30KB gzipped
- Individual entry point: < 5KB gzipped

## Tree-Shaking

Consumers must be able to import only what they need without pulling in the entire library.

### Tree-Shaking Rules

1. **ESM output is required.** The library must ship ES module output (`.mjs` or `"type": "module"`).
2. **No side effects at module scope.** Top-level code must not execute side effects on import. This includes:
   - DOM manipulation
   - Global variable mutation
   - Console output
   - Network requests
   - Polyfill installation (provide a separate entry point for polyfills)
3. **Isolate features.** Large features should be in separate entry points or dynamically importable.
4. **Avoid barrel file re-exports of heavy modules.** If the barrel file imports everything, tree-shaking becomes ineffective. Use direct imports for heavy sub-packages.
5. **Test tree-shaking.** Verify that importing a single function does not bundle the entire library. Use `rollup` or `webpack` analysis to confirm.

## TypeScript Types

Type quality is a first-class concern for library consumers.

### Type Rules

1. **Ship `.d.ts` files.** Always include TypeScript declarations in the published package.
2. **No `any` in public types.** Use `unknown` when the type is genuinely uncertain. Use generics when the type depends on consumer input.
3. **Use strict TypeScript configuration.** Enable `strict: true`, `noUncheckedIndexedAccess: true`, and `exactOptionalPropertyTypes: true` in `tsconfig.json`.
4. **Export all public types.** Every type that appears in a public function signature must also be exported.
5. **Use discriminated unions over optional properties** for complex API shapes.
6. **Generic types should have meaningful constraints.** Use `T extends SomeBase` instead of bare `T` when appropriate.
7. **Template literal types for string APIs.** When a string parameter has a known pattern, use template literal types for autocomplete and validation.
8. **Test types.** Use `tsd`, `expect-type`, or `@ts-expect-error` to test that types work as expected.

## Semantic Versioning

This library follows [Semantic Versioning 2.0.0](https://semver.org/) strictly.

### Version Rules

- **MAJOR** (X.0.0): Breaking changes to the public API
  - Removing an export
  - Changing a function signature incompatibly
  - Removing or renaming a prop/option
  - Changing default behavior
  - Dropping support for a Node.js or browser version
  - Narrowing accepted types
- **MINOR** (0.X.0): New functionality, backward-compatible
  - Adding a new export
  - Adding a new optional parameter
  - Adding a new feature behind a flag
  - Deprecating (not removing) an API
- **PATCH** (0.0.X): Bug fixes, backward-compatible
  - Fixing incorrect behavior
  - Performance improvements with no API change
  - Documentation fixes
  - Internal refactoring with no API change

### Pre-release

Use pre-release versions for testing: `1.0.0-beta.1`, `1.0.0-rc.1`.

## PR Review Configuration

When reviewing PRs in this repository, automatically apply the `[lib]` tag.

### Patterns to Watch For

1. **Breaking changes without major version bump**: Removal, renaming, or type changes to existing exports. Flag as CRITICAL.
2. **Missing exports**: New public functionality that is not exported from the barrel file. Flag as WARNING.
3. **Bundle bloat**: New dependencies or large code additions without size impact analysis. Flag as WARNING.
4. **Undocumented APIs**: New exports without JSDoc documentation and examples. Flag as WARNING.
5. **`any` in public types**: Use of `any` in exported function signatures or type definitions. Flag as WARNING.
6. **Side effects at module scope**: Top-level code that executes on import. Flag as WARNING.
7. **Default exports**: Use of `export default` instead of named exports. Flag as SUGGESTION.
8. **Missing test coverage**: New public functions without corresponding tests. Flag as WARNING.
9. **Peer dependency issues**: Framework dependencies listed as direct dependencies instead of peer dependencies. Flag as WARNING.
10. **Missing changelog entry**: Changes to public API without a corresponding changelog entry. Flag as SUGGESTION.

## Testing Expectations

- **Unit tests**: Every public function with edge cases
- **Type tests**: Verify TypeScript types behave correctly with `tsd` or `expect-type`
- **Integration tests**: Test the library as a consumer would use it (import from the package, not relative paths)
- **Bundle tests**: Verify tree-shaking works, verify bundle size stays within budget
- **Cross-environment tests**: Test in Node.js (CJS and ESM) and browser environments as applicable

## Build Configuration

### Required Outputs

- **ESM** (`.mjs` or `.js` with `"type": "module"`): Primary format for modern bundlers
- **CJS** (`.cjs` or `.js` with `"type": "commonjs"`): For Node.js require() compatibility
- **TypeScript declarations** (`.d.ts`): For TypeScript consumers
- **Source maps** (`.map`): For debugging

### Recommended Tools

- `tsup` for simple libraries (zero-config, fast)
- `rollup` for complex builds (plugins, code splitting)
- `unbuild` for monorepo packages
