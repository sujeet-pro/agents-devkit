# `code-bugfix` — anti-patterns

## The "I see the issue, let me just patch it" trap

Without a failing test FIRST, you cannot prove the fix is real. You also cannot prove the bug existed. The test is the contract between "this was broken" and "this stays fixed forever".

- **No reproducer? No fix.** Even when the bug is "obvious", the test is the artifact that future-you will thank current-you for.
- **Manual reproduction in a terminal doesn't count.** A test in the suite that runs in CI is what locks the fix in.
- **A reproducer that passes unexpectedly** means either the bug is gone (env-specific?) or the reproducer is wrong. Either way, STOP and investigate.

## Symptom patching

- **`if (value === undefined) value = 0`** — without asking why it's undefined. The cause is upstream; the symptom is masked; the underlying bug is still there.
- **`try { call() } catch { /* swallow */ }`** — turns "throws under condition X" into "silently misbehaves under condition X". Worse, not better.
- **Defensive `null` checks added throughout the file** when the bug was on one specific line. The diff balloons; the cause is still mis-diagnosed.
- The test for symptom-patching: read the `## Root cause` paragraph in `plan.md`. If it says "the value can sometimes be wrong, so we now handle that", that's symptom-patching. The right cause is "the value is wrong because of <specific upstream condition>".

## Drive-by changes

- **Renaming a function while fixing its behavior.** Two changes, one diff. The reviewer can't tell which lines are the fix and which are the rename.
- **Re-formatting the file** because your editor auto-formatted on save. Use the repo's formatter (run it explicitly) so the diff stays clean.
- **Adding a missing type annotation** while you're there. Useful, but separate concerns — list it under residual risk and let `code-refactor` handle it.
- **Sweeping similar code paths.** If you find the same bug pattern elsewhere, list it in residual risk; don't mass-fix in this diff.

## Validation theater

- **Closing the bug because "the test passes" without confirming the test was failing before.** Run the test FIRST without the patch; observe red. Then apply patch; observe green. Document the transition.
- **Running only the new test.** Always run the full affected-package suite — your patch could regress another test.
- **Reporting "passing" when only one of three changed files was re-tested.** Always include count + scope.
- **Not running the reproducer one more time after the patch.** Run it explicitly, separate from the suite, to be unambiguous.

## Diagnosis shortcuts

- **Guessing the cause from the stack trace alone.** The trace tells you where the crash happened, not always why.
- **Stopping at the first plausible cause.** "It crashes because the value is null" — but why is it null? Trace one more level.
- **Skipping `git log -L` / `git blame`.** Knowing when the bug was introduced often points at the cause.
- **Treating an intermittent test as a flake without investigation.** Intermittent failures are real bugs (race conditions, ordering assumptions, time/zone bugs).

## Test-engineering anti-patterns (specific to bugfix)

- **A regression test that passes both before and after the patch.** It's not testing the bug. Verify the red→green transition explicitly.
- **A regression test that mocks the system under test** so heavily that the test passes regardless of the actual fix.
- **A regression test named after the function** (e.g. `it("calculateTotal()")`) instead of the behavior (`it("returns 0 for empty cart")`).
- **A regression test in the wrong file.** It should live with the existing tests for the same module.
- **A regression test that doesn't fail in CI's environment.** Test it with the same Node / Python / Java version CI uses.

## Scope creep masquerading as completeness

- **"Let me also add input validation while I'm here."** That's a `code-write` (or `code-security`) task — separate diff.
- **"Let me also clean up these adjacent helpers."** That's `code-refactor` — separate diff.
- **"Let me also add tests for the other branches of this function."** That's `code-test` — separate diff. (For the bug fix, you only need the regression test.)

## Loop traps

- **Patch → fail → patch → fail → patch → fail.** After the second wrong patch, STOP. The diagnosis is wrong. Re-read the failing output; re-trace the code path; consider whether you have the right reproducer.
- **Validation suite goes red on a different test.** That's a regression you introduced. Don't paper over it; investigate.
- **Tooling failure (typecheck refuses to start, lint segfaults).** Fix the tooling separately; don't keep "fixing" the bug while the tooling is broken.

## Reporting

- **Burying the root cause** in five paragraphs of context. Lead with one sentence; expand on offer.
- **Hiding decisions made under `--auto`.** List every auto-pick in the Decisions table.
- **Saying "fixed" without showing the test transition.** Always include the red output + the green output.
- **Closing the issue without listing residual risk.** Even a clean fix often surfaces "we should also do X" — list it.
