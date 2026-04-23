# Simplification principles — Chesterton's Fence, Rule of 500, clarity over cleverness

Optional reference loaded by `build-refactor` when the goal is comprehension-improvement (vs structural reshape). Encodes the "preserve behavior while making the code easier to reason about" discipline.

## Chesterton's Fence

> *"If you don't see the use of [a fence], I certainly won't let you clear it away. Go away and think. Then, when you can come back and tell me that you do see the use of it, I may allow you to destroy it."* — G.K. Chesterton

Before deleting a piece of code that "looks unused" or "looks weird":

1. **Read the git blame.** When was it added? By whom? What was the commit message?
2. **Find the test (if any).** What behavior does it lock down?
3. **Find the original ticket / issue (if linked).** What was it solving?
4. **Search call sites.** Anything depend on it that grep didn't show (reflection, dynamic import, string-keyed dispatch)?
5. **Only THEN decide.**

If you cannot answer "why is this here" → leave it. Comment with your investigation findings if the next reader will benefit. The cost of a useless line is small; the cost of removing a load-bearing one is high.

## Rule of 500

> If you've changed > 500 lines mechanically and the change is repetitive, **automate it** — write a codemod, regex, or AST transform — instead of doing it by hand.

The cutoff is heuristic, not magic. The signal is:

- The change is uniform (rename, signature update, import path migration).
- You're at risk of fatigue-induced inconsistency.
- A future similar change would benefit from the same tool.

Tools:

- `jscodeshift` (TS/JS AST transforms).
- `ast-grep` (multi-language pattern matching + rewrite).
- `ruff` / `black` / `pylint --fix` (Python).
- `gofmt` / `goimports` (Go).
- `cargo fix` (Rust).
- Plain `sed` / `rg --replace` (only when the change is trivially regex-safe; quote everything).

## Five simplification principles

1. **Preserve behavior.** Tests stay green throughout; no "improving" defaults or error messages mid-refactor.
2. **Follow conventions.** Match the repo's existing patterns; don't introduce a new style for one file.
3. **Clarity over cleverness.** Two lines of obvious code beats a one-line ternary that requires a comment.
4. **Balance, not extremes.** A function with 4 args is fine; a function with 14 needs an object. There is no fixed magic number — readability is the test.
5. **Stay in scope.** Refactor what the user asked for. Note other opportunities; don't act on them in the same pass.

## Common simplification patterns

| Symptom | Pattern | Notes |
| --- | --- | --- |
| Deeply nested ifs | Early returns / guard clauses | Removes the "happy path indented 4 levels in" |
| Long function (> 50 lines) | Extract method | Each named method becomes documentation |
| Boolean parameter | Two functions | `setActive(true)` → `activate()` |
| Repeated conditional | Polymorphism / lookup table | Keep the dispatch in one place |
| Long parameter list | Parameter object | Cohesive groups of args become a typed shape |
| Magic number | Named constant | The constant's name explains the *why* |
| Implicit nullability | Explicit option/result type | `T | null` vs `Option<T>` vs `Maybe<T>` |
| Mutable shared state | Local state + return | Easier to reason; fewer race conditions |
| Comment that explains code | Rename / extract | If a comment is needed, the code can usually be clearer |

## Refactor-vs-feature separation

A refactor pass changes structure without changing behavior. A feature pass changes behavior. **Mixing them in one PR makes review impossible.**

- Refactor first, in a separate PR (or at least separate commits with `refactor:` prefix), with green tests proving no behavior change.
- Then the feature, on top, with the new tests for new behavior.
- If you're tempted to "fix this small thing while I'm here" — note it, finish the current pass, then come back.

## Common excuses to ignore

| Excuse | Counter |
| --- | --- |
| "It's working, no need to touch it" | The next change is the one that pays the cost. Simplify when you have context. |
| "Fewer lines is always simpler" | Fewer lines can be denser and harder. Optimize for comprehension, not LOC. |
| "I'll just quickly simplify this unrelated code too" | That's not a refactor pass anymore. Note it; do it separately. |
| "The types make it self-documenting" | Types are necessary, not sufficient. Names matter too. |
| "This abstraction might be useful later" | YAGNI. Add abstraction when it has 2+ concrete users. |
| "The original author must have had a reason" | Investigate (Chesterton's Fence). If you can't find one, document the investigation. |
| "I'll refactor while adding this feature" | Mixing scopes hides regressions. Split. |

## Verification

- All tests pass before and after, identical output.
- Lint passes.
- Build passes.
- The diff is reviewable in chunks (no mega-commit).
- A teammate would understand the change from the diff alone.
- No dead code introduced (no commented-out blocks, no "for future use" interfaces).
- Repo conventions (formatting, naming, module layout) preserved.
