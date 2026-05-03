# `code-refactor` — workflow detail

## Phase 0 — prompt expand

1. **Restate** the move. One sentence: "Extract X from Y into Z" / "Rename A to B everywhere" / "Deduplicate three near-identical helpers in folder F" / "Split file F by concern" / "Inline single-use wrapper W".
2. **Resolve the repo** via `cwd → .git → ~/.config/adk/repos.md`.
3. **Identify the scope**. Walk through the move:
    - Rename: list call-sites via Grep.
    - Extract: identify the source function + the destination file.
    - Dedupe: identify the N copies + the destination canonical version.
    - Split: identify the file + the proposed split-by-concern boundaries.
    - Move: source path + destination path.
    - Inline: which wrapper + how many call-sites.
4. **Pick task slug**. Often shaped `refactor-<move>-<area>` (e.g. `extract-validate-cart`).
5. **Create** `.temp/task-<slug>/`. Write `prompt.txt`.
6. **Approval gate** unless `--auto`: show restated move + scope + estimated micro-step count.

## Phase 1 — preflight

1. `git status` — clean. Dirty tree → ask. A refactor on a dirty tree is hard to verify.
2. Branch — if on protected, prompt `refactor/<slug>`.
3. Resolve commands (typecheck + lint + test). See `code-write/references/validation-recipes.md`.
4. **Baseline check**. ALL three commands MUST be green on HEAD. A refactor on a red baseline is unverifiable; STOP.

## Phase 2 — read first

1. Read the target code end-to-end.
2. Run `Grep` for every symbol about to move / rename. Record call-site count + file list.
3. Read the existing tests for the area — these are your safety net. If the existing tests don't cover the move, list "test coverage gap" in the plan; the user may want to do `code-test` first to establish a safety net before refactoring.
4. Read `AGENTS.md` / `CLAUDE.md` for any "don't refactor X" rules (some repos lock specific files for cross-team coordination).
5. Read recent commits to see the file's recent rate of change. A high-churn file is risky to refactor (more merge conflicts likely).

## Phase 3 — plan (TDD-shape micro-steps)

Write `.temp/task-<slug>/plan.md`:

- **Move (one sentence)** — the goal.
- **Scope** — repo, files, call-site count.
- **Existing test coverage** — which tests cover the affected behavior. If thin, list the gap and propose `code-test` as a prerequisite.
- **Micro-steps** — numbered, each leaving the suite green. Examples:
    1. Add new module `services/cart/validate.ts` exporting `validateCart` (cut-paste from `checkout.ts`; old function still in `checkout.ts` for now). Suite green.
    2. Update `checkout.ts` to import `validateCart` from the new module. Delete the old function. Suite green.
    3. Update 3 other call-sites to import from the new path. Suite green.
- **Validation plan** — exact commands.
- **Out of scope (deliberate)** — bullet list.

Approval gate unless `--auto`.

## Phase 4 — execute the micro-steps

For each micro-step in order:

1. Apply the change (Edit / Write).
2. Run the affected-package tests scoped to the changed area.
3. If GREEN: continue to next step. Append to `validation/per-skill/code-refactor.md`: step number + commands + exit code.
4. If RED:
    a. Read the failure.
    b. Make the smallest possible micro-step-fix to recover. Re-run.
    c. If still red: REVERT the micro-step's edits. Re-run; confirm green. Then re-think the step.
    d. After 2 failed-and-reverted attempts on the same step, STOP and surface.

## Phase 5 — validate

1. **Full affected-package suite** runs. Green.
2. **Typecheck** runs. Green.
3. **Lint** runs (with the repo's `--max-warnings` policy). Green.
4. **Snapshot tests should NOT need `--update`**. If they do: STOP. A snapshot change indicates a behavior change. The refactor either:
    - Accidentally changed behavior — bug; revert the offending step; redo.
    - Intentionally changed behavior — wrong skill; this should be `code-write` or `code-api`.
5. Capture all outputs to `.temp/task-<slug>/validation/per-skill/code-refactor.md`.

## Phase 6 — report

Write `.temp/task-<slug>/report.md`:

- **Move** — one sentence.
- **Files changed** — table: path, +N/-M, role (renamed / extracted / inlined / etc.).
- **Micro-step list** — table: step number, description, post-step suite size.
- **Validation evidence** — final commands + exit codes.
- **Decisions** — every auto-pick.
- **Residual risk** — anything noticed but not changed.
- **NOT done (deliberate)** — explicit list with reason.
- **Next steps** — typical: `/adk-review:review-code-changes` before push.

End with the offer-depth question.

## Loop control

- After 2 failed-and-reverted attempts on the same micro-step, STOP and surface.
- If a snapshot test changes during a "refactor", STOP — the refactor changed behavior. Re-categorize the change (likely `code-write`).
- If the suite was green on HEAD but goes red after step 1 in a way that doesn't revert cleanly, STOP and surface — there's a non-obvious dependency.

## When the move is too large for one task

If the planned micro-step list has more than ~10-12 steps, the move is probably too large. Suggest splitting:

- "Refactor 1/2: extract `validateCart`."
- "Refactor 2/2: extract `validatePayment`."

Each as a separate `code-refactor` task with its own slug.
