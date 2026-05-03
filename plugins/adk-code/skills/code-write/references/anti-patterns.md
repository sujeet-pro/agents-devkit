# `code-write` — anti-patterns

## Scope creep

- **"While I'm here, let me also clean up …"** — STOP. The diff balloons; review becomes harder; the new feature becomes harder to revert. If you spot legit cleanup, list it under "Residual risk / follow-ups" in `report.md` for a separate `code-refactor` task.
- **Renaming a function while implementing the new feature inside it.** Two changes; two diffs; two reviews.
- **Adding a new abstraction "in case we need it later".** Until 3 callers exist, the abstraction is speculation.
- **Touching files outside the planned set without re-confirming.** Even under `--auto`, surface the deviation and re-confirm.

## Defensive code for impossible cases

- **`if (!user) throw new Error("user required")`** at line 200 of an internal helper that is only called from line 50 of a parent that already validated `user`. Trust internal callers.
- **`try { internalCall() } catch { /* swallow */ }`** — hides real bugs as "intermittent issues".
- **Adding null checks on a parameter typed as `User` (non-optional) in TypeScript.** The type system already rules out null. The runtime check is dead code.
- **Wrapping every external SDK call in a `try / catch` that just rethrows.** Pure noise; the SDK throws the same error either way.
- The rule: validate at the **boundary** (HTTP request handler, CLI arg parser, event handler from an external bus). Internally, trust types + invariants.

## Reading shortcuts

- **Editing a file you have not just read.** State drift: the file may have changed since the plan was written.
- **Skipping AGENTS.md / CLAUDE.md / .cursorrules.** These exist because someone wrote them down so you wouldn't have to ask.
- **Inferring the test framework from "it's TypeScript so it's Jest".** Read `package.json devDependencies`. Could be Vitest, Mocha, Jest, AVA, node:test.
- **Guessing at the lint config from "it's a Node project".** Read the actual lint config.
- **Inferring style from one file.** Look at 2-3, plus a recent commit.

## Comments

- **`// Increment the counter`** above `counter++`. The code already says that.
- **`// Loop through users`** above `for (const u of users) { … }`. Same.
- **`// Returns the result`** above `return result;`. Same.
- **The good comment:** `// Workaround for upstream bug X (issue 1234) — remove when the upstream fix lands` above a one-line shim. That's a non-obvious WHY.

## Validation theater

- **Running `npm test` without arguments and reporting "tests pass" when only one new test ran.** Always include the count + the package scope.
- **Reporting "lint clean" without showing the command.** Show the exact command + exit code.
- **Treating a passing test as proof of correctness when the test was the one you just wrote.** It might be testing the wrong thing — pair it with the fail-first step.
- **Skipping the baseline check.** If HEAD was red and you didn't notice, your "test pass" claim is suspect.

## Backwards-compat shims

- **Adding a new function and keeping the old one as a wrapper "for backwards compatibility"** when there are 4 callers in the same repo. Just update the callers.
- **Adding a `if (legacyFlag) { … } else { … }` branch** to support a config style that nobody uses any more. Remove the dead branch.
- The exception: **public API surface** — if `code-api` says the old shape stays for a deprecation window, honor it. (But that's `code-api`, not `code-write`.)

## Dependencies

- **Importing `lodash` for one `pick` call** when the standard library + 4 lines of code does it.
- **Adding a new dependency without surfacing it in `plan.md`.** Dependencies are decisions; the plan must list them.
- **Mixing `npm install` (or `yarn add`, etc.) into the same diff as the feature** without separating the lockfile change in the report.

## Reporting

- **Saying "done" when 1 of 3 changed files has been re-tested.** Always re-validate the full affected scope.
- **Burying the diff summary in 5 paragraphs of context.** Lead with what changed; provide context on offer.
- **Hiding the auto-decisions made under `--auto`.** Every auto-pick goes in the Decisions table with a one-line rationale.

## Workflow

- **Skipping Phase 0 prompt expand because "the prompt is clear".** The expand step also sets the slug + creates `.temp/task-<slug>/`. Always run it.
- **Skipping Phase 3 plan because "this is a 1-line change".** Even a 1-line change benefits from a documented WHY in `plan.md` for the report.
- **Editing in Phase 2 (read first).** Read first, plan, then edit.
- **Looping on the same broken validation step.** After 3 failures of the same kind, stop and surface.
