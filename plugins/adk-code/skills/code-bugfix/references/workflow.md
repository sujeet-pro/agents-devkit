# `code-bugfix` — workflow detail

## Phase 0 — prompt expand

1. **Restate** the bug. Symptom + the conditions under which it occurs + the expected behavior. One paragraph max.
2. **Resolve the repo** via `cwd → .git → ~/.config/adk/repos.md`.
3. **Identify the system under suspicion**. From the symptom, name the function / module / endpoint most likely involved. Use Grep + Glob.
4. **Pick task slug** via `bin/adk-task-slug "<prompt>"`. Often shaped like `fix-<symptom>-<area>`.
5. **Create** `.temp/task-<slug>/`. Write `prompt.txt` with the verbatim user prompt + ISO timestamp + any pasted stack trace.
6. **Approval gate** unless `--auto`: show restatement + resolved repo + suspected area. Ask "proceed?".

## Phase 1 — preflight

1. `git status` — clean (dirty → ask: stash, abort, or include?). Dirty trees obscure the diagnosis.
2. `git rev-parse --abbrev-ref HEAD` — capture branch. If on a protected branch, prompt to create `fix/<slug>` (auto-create under `--auto` if `~/.config/adk/github.md.forbid_force_push_branches` includes the current branch).
3. Resolve test / typecheck / lint commands (see `code-write/references/validation-recipes.md` — same recipes apply).
4. **Baseline check**: typecheck + lint + tests on HEAD. The baseline should be green EXCEPT for any tests the user already added that capture the bug. If the baseline has unexpected red, STOP and ask.

## Phase 2 — REPRODUCE

This is the phase that distinguishes `code-bugfix` from `code-write`.

1. **Find the right test file location.** Match the repo's test conventions (e.g. `*.test.ts` next to the source, or `tests/<module>/test_<symbol>.py`).
2. **Write a failing test** that captures the bug:
    - Name it after the behavior, not the function (e.g. `it("returns wrong value when total is exactly 0")`).
    - Use the repo's existing test framework + idioms.
    - Assert on observable behavior (return value, side effect, status code), not implementation.
3. **Run the test**. Confirm it FAILS. Capture the failing output verbatim.
4. **If it passes** unexpectedly: the reproducer is wrong (or the bug is gone). STOP and ask the user for more detail (env, version, exact steps).
5. **Write `.temp/task-<slug>/reproducer.md`**:
    - The repro condition in plain prose.
    - The failing test code.
    - The observed failing output.
    - Any environmental notes (Node version, OS, etc.).
6. **Approval gate** under `-i` before moving to diagnose. Under `--auto`, proceed.

## Phase 3 — DIAGNOSE (root cause)

1. **Read the failing code path.** Start at the assertion in the failing test; trace into the code under test; follow each branch.
2. **Use git history** to identify *when* the bug was introduced:
    - `git log -L <line-range>:<file>` — line-history of the suspected lines.
    - `git blame <file>` — author + commit per line.
    - `git bisect` (rare; use only when the regression is recent and the bug isolates cleanly into a single commit).
3. **Identify the root cause** in one sentence. Not "we should validate inputs more thoroughly" but "the function uses `==` instead of `===` so empty string equals 0".
4. **Write `plan.md`** with the canonical shape (see `references/output-format.md`):
    - `## Root cause` — one sentence, falsifiable.
    - `## Patch` — the smallest correct change. List files + lines.
    - `## Regression test` — the test from Phase 2 (or a derivative) that will lock the fix in.
    - `## Validation plan` — exact commands.
    - `## Out of scope` — adjacent things you noticed but won't fix in this diff.
5. **Approval gate** unless `--auto`.

## Phase 4 — PATCH

1. Spawn the `implementer` subagent with `plan.md` + `reproducer.md`.
2. The implementer follows its read-before-write protocol; the patch should be the minimum lines necessary.
3. **Re-run the reproducer test**. Confirm it now PASSES. Capture the green output.
4. **If it still fails**: the diagnosis was wrong. Loop back to Phase 3 (do NOT keep patching). After 2 wrong diagnoses, STOP and ask.
5. The implementer hand-off goes to `validation/per-skill/code-bugfix.md`.

## Phase 5 — VALIDATE

1. **Run the full affected-package test suite.** Must be green (and not just the new test).
2. **Run typecheck.** Green.
3. **Run lint** (with the repo's `--max-warnings` policy). Green.
4. **Re-run the reproducer test one more time** (separate from the suite, to be explicit). Green.
5. Capture all of the above to `.temp/task-<slug>/validation/per-skill/code-bugfix.md`.
6. If a test that was green before is now red: it's a regression — STOP, do NOT ship the fix. Either the diagnosis or the patch is wrong.

## Phase 6 — REPORT

Write `.temp/task-<slug>/report.md`:

- **Symptom** — one sentence on what the bug looked like.
- **Root cause** — one sentence (verbatim from `plan.md`).
- **Patch** — table of files + +N/-M.
- **Regression test** — file::name + the red→green transition evidence.
- **Validation evidence** — commands + exit codes.
- **Decisions made** — list of branches the skill auto-picked.
- **Residual risk / follow-ups** — anything noticed but not fixed.
- **Next steps** — typical: `/adk-review:review-code-changes` before push.

End with the offer-depth question.

## Loop control

- After 2 wrong diagnoses (patch applied, reproducer still fails), STOP. Don't keep patching.
- After 3 broken validation runs of the same kind, STOP. The patch may be wrong or the diagnosis incomplete.
- If the reproducer test passes unexpectedly on HEAD → STOP and ask. The bug may be already fixed, env-specific, or misunderstood.

## Decision: when "patch the symptom" is the right call

There are real cases where you patch a symptom because the cause is upstream and out of scope:

- Third-party library has a known bug; the patch is a documented workaround.
- The cause is in a different repo/service.

In those cases:

- **Document it.** `## Root cause` says "upstream bug X (issue link); workaround locally pending fix".
- **Add a code comment** above the workaround quoting the upstream issue ID. This is one of the rare cases where a code comment is the right call (it's a non-obvious WHY).
- **List the upstream issue** in residual risk — when does the workaround go away?
