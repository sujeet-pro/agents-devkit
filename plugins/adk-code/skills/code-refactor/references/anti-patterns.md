# `code-refactor` — anti-patterns

## Mixing concerns

- **"Refactor + bug fix in one PR"** — split them. The bug fix is verified by a regression test; the refactor is verified by tests staying green. Mixed, neither claim is provable.
- **"Refactor + new feature in one PR"** — split them. The reviewer can't tell the structural change from the new behavior.
- **"Refactor + perf optimization in one PR"** — same. Perf needs measurement; refactor needs tests-green. Different proofs.
- **"Refactor + minor cleanup in adjacent files"** — even if both are refactors, if they're in different concerns or could be merged independently, split.

## Hidden behavior changes

- **Snapshot tests updated as part of the refactor.** A snapshot change = behavior change. STOP and reconsider.
- **Tests passing because the assertion was loosened**, not because the refactor preserved behavior.
- **A micro-step that changes the order of side effects** (e.g. logging order, event-emit order). External callers may depend on the order. STOP.
- **Removing a deprecation warning while refactoring.** That's a behavior change for any consumer of the warning.
- **Inlining a function that was used as a stable reference** (e.g. for `useMemo` / `useEffect` deps). The identity changes; downstream behavior changes.

## Scope creep

- **"Massive rename across 50 files in one commit"** — fine if it's mechanical (one symbol, one definition, lots of call-sites). Problematic if any rename is semantically loaded ("rename `getCwd` to `currentDirectory`" — the new name implies a slightly different scope; that's a meaning change, not a rename).
- **"While I'm here, let me also …"** — STOP. The diff balloons.
- **Re-formatting unchanged adjacent code.** Use the repo's formatter; format only the lines you actually edited (or run formatter once at the end as a separate micro-step, in a separate diff if the formatting drift is significant).

## Rewrite-as-refactor

- **"Let me rewrite this file from scratch — it'll be cleaner."** A rewrite is not a refactor. The behavior preservation cannot be proved by green tests alone (the new file's behavior is whatever the new file does). If the existing file genuinely needs replacing, that's a `code-write` task with explicit scoping.
- **"I'll redesign this module."** Redesigning a module surface is `code-api`, not `code-refactor`. Or, if the surface stays the same but the implementation is rewritten, it's still risky — the new implementation might have different non-functional behavior (perf, memory, ordering).

## Skipping the green-between-steps invariant

- **"Tests are red on step 4, but they'll be green again by step 7."** That's not a safe sequence. If something goes wrong between steps 4-7, you can't bisect. Re-sequence so each step leaves the suite green.
- **"I'll run tests once at the end, not after each step."** The whole point of micro-steps is the per-step verification. Without it, you've just done a big-bang refactor.
- **Treating "tests don't fail" as "tests pass."** You ran them, right? Show the output.

## API surface changes

- **Renaming a public exported function** is `code-api`, not `code-refactor`. Even if you keep an alias for backwards compat, the canonical name is part of the contract.
- **Changing a public function's parameter shape** — `code-api`, even if "the implementation stays the same".
- **Changing a public type's structure** — `code-api`.
- **Renaming a CLI flag, an env var, a config key, a database column** — all are public API in disguise. `code-api` (or `code-migrate`).
- **Signing-up an internal-only refactor that "doesn't touch any exported names"** — confirm: are any of these symbols imported by other repos? If yes, it's not internal-only.

## Tooling theatre

- **Reporting "lint clean" without running lint.** Always run; show exit code.
- **Treating "TypeScript narrows the type after this rename" as a green signal.** Confirm with `tsc --noEmit`, not just IDE squiggles.
- **Skipping the baseline check.** A refactor on a red baseline is provable nothing.

## Reporting

- **Saying "refactored 5 files" without listing the moves.** List each move. Future-you cares.
- **Hiding a behavior change** because "the tests passed". Snapshot changes, log-order changes, side-effect-timing changes — all are behavior changes that the test suite may not catch. Surface them in residual risk.
- **Burying the micro-step list.** It's the most useful artifact for the reviewer.

## Pre-condition violations

- **Refactoring on a thin / no test coverage area** without surfacing the gap. The safety net is the suite; if there's no suite, the refactor is unverified. Recommend `code-test` first to establish the safety net.
- **Refactoring high-churn files** without coordinating with other in-flight branches. Surface "this file has 14 commits in the last week — your refactor will likely conflict heavily" — and let the operator decide.
