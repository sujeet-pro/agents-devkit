# General Code Review Guidelines

These guidelines apply to **all** repositories and languages. They represent baseline
expectations for code quality, correctness, and professionalism.

---

## 1. Correctness and Logic

- **Verify the happy path works as described in the PR description.** The code must
  do what the author says it does.
- **Check edge cases**: empty inputs, zero values, negative numbers, null/undefined,
  maximum-length strings, concurrent access, and off-by-one errors.
- **Trace data flow** end to end. Follow inputs from their source through
  transformations to their destination. Look for places where assumptions about data
  shape or type are implicit rather than enforced.
- **Boolean logic**: Carefully verify complex conditions. De Morgan's law mistakes
  (`!(a && b)` vs `!a && !b`) are common. Watch for inverted conditions and missing
  parentheses.
- **State management**: When state is modified, verify that all consumers of that
  state handle the change correctly. Look for stale reads, race conditions, and
  inconsistent intermediate states.
- **Return values**: Verify that all code paths return the expected type and value.
  Watch for functions that implicitly return `undefined` in some branches.

## 2. Error Handling

- **Never swallow errors silently.** Every `catch` block should either:
  - Log the error with enough context to debug it, OR
  - Re-throw a more specific error, OR
  - Handle the error with explicit recovery logic and a comment explaining why
    swallowing is intentional
- **Use specific error types** when the language supports them. Avoid catching and
  throwing generic `Error` / `Exception` unless at a top-level boundary.
- **Fail fast**: Validate inputs at function boundaries. Do not let invalid data
  propagate deep into the system before failing with a confusing error.
- **Error messages must be actionable.** Include what happened, what was expected,
  and (when appropriate) how to fix it. Include relevant identifiers (user ID,
  request ID, etc.) for debugging.
- **Async error handling**: Ensure promises have `.catch()` handlers or are wrapped
  in `try/catch` within `async` functions. Unhandled promise rejections crash
  processes.
- **Cleanup on error**: When a function acquires resources (file handles, database
  connections, locks), ensure they are released on all exit paths, including error
  paths. Use `finally`, `defer`, `using`, or similar constructs.

## 3. Naming Conventions

- **Names should reveal intent.** A reader should understand what a variable holds
  or what a function does from its name alone, without reading the implementation.
- **Boolean variables/functions** should read as yes/no questions: `isVisible`,
  `hasPermission`, `canEdit`, `shouldRetry`.
- **Functions** should be named with verbs: `fetchUser`, `calculateTotal`,
  `validateInput`, `renderHeader`.
- **Avoid abbreviations** unless they are universally understood in the domain
  (`URL`, `HTTP`, `ID`, `DB`). Do not use `usr`, `mgr`, `btn`, `val` unless
  mandated by an existing codebase convention.
- **Avoid generic names**: `data`, `info`, `result`, `temp`, `value`, `item`.
  These are acceptable only in very small scopes (1-3 lines) or when naming is
  genuinely arbitrary (e.g., a generic utility).
- **Consistency**: Follow whatever naming convention the codebase already uses. If
  the codebase uses `camelCase` for functions, do not introduce `snake_case`.

## 4. DRY Principle (Don't Repeat Yourself)

- **Flag duplication only when there are 3+ occurrences** of meaningfully similar
  code. Two occurrences may be coincidental; three indicates a pattern.
- **Do not over-abstract.** Premature abstraction is worse than duplication. If two
  pieces of code look similar but serve different purposes or are likely to diverge,
  let them remain separate.
- **The right abstraction captures a concept**, not just shared syntax. A good
  extraction is named after what it *means*, not what it *does*.
- **Configuration over duplication**: When the only difference between repeated
  blocks is a few values, consider extracting a data-driven approach (map of
  config objects, table-driven patterns).

## 5. Security Basics

- **Never commit secrets.** API keys, passwords, tokens, private keys, and
  certificates must never appear in source code, test fixtures, or configuration
  files. Use environment variables or a secrets manager.
- **Validate all external input** at the system boundary. This includes HTTP
  request bodies, query parameters, headers, file uploads, and data from external
  APIs. Do not trust anything that crosses a trust boundary.
- **Sanitize output** according to its destination. Data going into HTML must be
  HTML-escaped. Data going into SQL must be parameterized. Data going into shell
  commands must be properly quoted or use structured APIs.
- **Use allowlists over denylists** when validating input. It is safer to
  enumerate what is permitted than to enumerate what is forbidden.
- **Principle of least privilege**: Code should request only the permissions it
  needs. Database users should have minimal grants. API tokens should have minimal
  scopes.
- **Do not log sensitive data.** PII, credentials, session tokens, and financial
  data must not appear in log output, error messages, or stack traces.

## 6. Testing Expectations

- **New features should have tests.** If a PR adds new functionality, there should
  be test coverage for the happy path and at least the most important edge case.
- **Bug fixes should have regression tests.** A test that fails without the fix and
  passes with it proves the fix is correct and prevents regression.
- **Tests should be deterministic.** No flaky tests. Avoid dependencies on system
  time, random values, network state, or execution order. Mock or control all
  sources of non-determinism.
- **Tests should be readable.** A test is documentation. It should clearly show:
  what is being tested, what the inputs are, and what the expected output is. Use
  descriptive test names.
- **Test behavior, not implementation.** Tests should verify *what* the code does,
  not *how* it does it. Avoid testing private methods or internal state. This makes
  tests resilient to refactoring.
- **Do not test framework/library code.** Trust that `Array.prototype.map` works.
  Test your logic, not your tools.

## 7. Documentation for Public APIs

- **Every public function, class, or module should have a doc comment** explaining:
  - What it does (one sentence)
  - Parameters and return values
  - Exceptions/errors it can throw
  - Side effects, if any
  - Example usage, for non-obvious APIs
- **Keep docs close to the code.** Inline doc comments (JSDoc, Javadoc, docstrings)
  are preferred over external documentation for API references because they stay in
  sync with the code.
- **Update docs when behavior changes.** Stale documentation is worse than no
  documentation because it actively misleads readers.
- **Do not document the obvious.** A function named `getUserById(id)` does not need
  a doc comment saying "Gets a user by ID." Add docs when the name alone is
  insufficient.

## 8. Git Hygiene

- **No debug code in commits.** Remove `console.log`, `debugger`, `print()`,
  `TODO` / `FIXME` (unless tracked), and commented-out code before merging.
- **Meaningful commit messages.** Each commit message should explain *why* the
  change was made, not just *what* changed. The diff already shows the *what*.
- **Atomic commits.** Each commit should represent one logical change. Do not mix
  unrelated changes in a single commit.
- **No large generated files.** Lockfiles are acceptable if the project uses them.
  Compiled output, vendored dependencies, and large binaries should be `.gitignore`d.
- **No merge commits in feature branches** (prefer rebase to keep history linear),
  unless the team convention says otherwise.

## 9. Accessibility Basics

- **Semantic HTML**: Use `<button>` for buttons, `<a>` for links, `<nav>` for
  navigation, `<main>` for main content. Do not use `<div>` with click handlers
  when a native element exists.
- **Alt text**: All `<img>` elements must have an `alt` attribute. Decorative images
  should use `alt=""`. Informative images should have descriptive alt text.
- **Keyboard navigation**: All interactive elements must be reachable and operable
  via keyboard. Test with Tab, Shift+Tab, Enter, Space, and Escape.
- **Color contrast**: Text must have a contrast ratio of at least 4.5:1 against its
  background (WCAG AA). Large text (18px+ bold or 24px+ regular) may use 3:1.
- **ARIA**: Use ARIA attributes only when native HTML semantics are insufficient.
  Incorrect ARIA is worse than no ARIA.

## 10. Performance Basics

- **Avoid unnecessary work in hot paths.** Do not compute, allocate, or fetch data
  that is not needed for the current operation.
- **Pagination**: Any API or query that returns a list should support pagination.
  Never return an unbounded result set.
- **Caching**: Consider caching for data that is expensive to compute or fetch and
  does not change frequently. But always define a cache invalidation strategy.
- **Lazy loading**: Load heavy resources (images, components, data) only when they
  are needed.
- **Batch operations**: Prefer batch APIs over loops of individual operations when
  interacting with databases, external services, or the DOM.

## 11. Code Comments

- **Comment the *why*, not the *what*.** The code shows what it does. Comments should
  explain why it does it that way, especially when the choice is non-obvious.
- **Document workarounds.** If code works around a bug in a library or browser,
  include a link to the issue and describe when the workaround can be removed.
- **Explain complex algorithms.** If a function implements a specific algorithm or
  formula, reference the source (paper, documentation link) and explain the key
  steps.
- **No commented-out code.** Deleted code lives in version control. Do not leave
  commented-out blocks "just in case."
- **Keep comments up to date.** A comment that contradicts the code is a bug.

## 12. Code Style and Formatting

- **Follow the existing project style.** If the project has a linter/formatter
  configuration, respect it. Do not introduce a different style in your PR.
- **Consistent formatting**: If there is no formatter, at least be internally
  consistent within the file.
- **Import organization**: Group imports logically (standard library, third-party,
  internal) and keep them sorted. Most formatters handle this automatically.
- **File length**: If a file exceeds ~300-400 lines, consider whether it should be
  split. Long files are hard to navigate and often indicate mixed responsibilities.
- **Function length**: Functions longer than ~50 lines are usually doing too much.
  Consider extracting helper functions with descriptive names.
