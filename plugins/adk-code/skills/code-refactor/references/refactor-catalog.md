# `code-refactor` — refactoring catalog (safe-step recipes)

A reference of common refactoring moves, each with the safe micro-step shape. Inspired by Martin Fowler's catalog (refactoring.com); adapted for "tests-green-between-steps" discipline.

## Extract function

Goal: pull a code block out of an enclosing function into its own function.

**Safe steps:**

1. Create the new function. Empty body. The new function is unused. Tests still green.
2. Cut-paste the block from the enclosing function into the new function. The enclosing function now calls the new function. Tests still green.
3. (Optional) Move the new function to its own module file. Tests still green.

**Anti-pattern:** rewriting the enclosing function and the new function in one step. Hard to verify behavior preservation.

## Inline function

Goal: replace a single-use wrapper with its body.

**Safe steps:**

1. Identify all call-sites of the wrapper. There must be 1 (or `code-refactor` will resist — fewer than 3 callers is the threshold for "remove the abstraction").
2. Inline the body at the call-site. Tests still green.
3. Delete the now-unused wrapper definition. Tests still green.

**Anti-pattern:** inlining and modifying the body in the same step.

## Rename (symbol, file, package)

Goal: change the name of a thing without changing what it does.

**Safe steps for symbol rename:**

1. Add a new export alias for the new name pointing at the old function:
   ```ts
   export const newName = oldName;
   ```
   The old name continues to work; the new name is also available. Tests still green.
2. Update each call-site (one batch at a time, or all at once if mechanical) to use `newName`. Tests still green after each batch.
3. Delete the old name's definition; rename the new alias to be the canonical definition. Tests still green.

**Safe steps for file rename:**

1. `git mv old.ts new.ts`. Update imports. Tests still green.

**Anti-pattern:** renaming a symbol that is part of a public API. That's `code-api`.

## Extract module / split file

Goal: take a function/class out of a large file into its own file.

**Safe steps:**

1. Create the new file. Cut-paste the symbol. Old file imports from the new file. Tests still green.
2. Update other call-sites of the symbol (if any) to import from the new file. Tests still green.
3. (Optional) Remove the re-export from the old file if not part of the public API. Tests still green.

**Anti-pattern:** moving 5 symbols at once. Each symbol = its own micro-step.

## Inline module

Goal: pull a single-use module's content back into the calling file.

Mirror image of "extract module"; similar safe steps.

## Dedupe (3-into-1)

Goal: collapse N near-identical functions into one canonical function.

**Pre-condition:** the N functions are TRULY equivalent (same inputs accepted, same outputs produced, same side effects). If not, you are doing "extract common core" instead (see below).

**Safe steps:**

1. Create the canonical function (or pick one of the N as canonical). Tests still green.
2. For each of the N-1 others: rewrite as a thin wrapper around the canonical (or alias). Tests still green after each.
3. Update each call-site to call the canonical directly. Tests still green after each batch.
4. Delete the now-unused wrappers. Tests still green.

**Anti-pattern:** "they look similar enough; let me just collapse them" — without proving equivalence, you are changing behavior.

## Extract common core (when functions are similar but not equivalent)

**Safe steps:**

1. Identify the common core. Extract it into a new function `coreOp`. Tests still green.
2. Update each of the original functions to delegate the common part to `coreOp`. The originals are now thin wrappers around `coreOp` + their unique pre/post-processing. Tests still green after each.

**Anti-pattern:** assuming the wrappers can later be unified — they were intentionally different. Document why each remains distinct in their docstrings.

## Move method to a different class / module

**Safe steps:**

1. Add the method on the destination. Tests still green (new method is unused).
2. Update one call-site to use the destination. Tests still green.
3. Repeat for each call-site. Tests still green after each.
4. Delete the original method. Tests still green.

## Replace conditional with polymorphism (or vice versa)

This is a riskier move because it usually involves restructuring the type model.

**Pre-condition:** strong test coverage (high coverage on the conditional branches).

**Safe steps:**

1. Introduce the new shape (the polymorphic types or the unified conditional) IN PARALLEL with the old. Tests still green.
2. One call-site at a time, switch to the new shape. Tests still green after each.
3. Delete the old shape. Tests still green.

**Anti-pattern:** replacing the shape in one step. Big-bang refactors are hard to verify.

## Decompose conditional

Goal: extract complex `if/else` branches into named functions for readability.

**Safe steps:**

1. Extract the predicate into a named boolean function (or a `const x = …`). Tests still green.
2. Extract the body of each branch into a named function. Tests still green after each.

## Move from class to function (or vice versa)

Risk: this can change behavior subtly (class instances may be carrying state; functions don't).

**Safe steps:**

1. Add the function form alongside the class. Tests still green (function is unused).
2. Migrate one call-site. Tests still green.
3. Repeat. Tests still green after each.
4. Delete the class once all call-sites moved. Tests still green.

## Re-shape a module's internal structure (folder reorganization)

**Safe steps:**

1. Create the new folder structure. Move files one at a time with `git mv`. Update imports per file. Tests still green after each move.
2. (Optional) Update the re-export barrel file (`index.ts`) so external consumers don't see the move. Tests still green.

**Anti-pattern:** moving 20 files at once. Each `git mv` = its own micro-step.

## Convert callback to promise / promise to async-await

Risk: HIGH. These can introduce subtle behavior changes in error propagation, ordering, or timing.

**Safe steps:**

1. Add the new style as a wrapper (promisified version) alongside the old. Tests still green.
2. Migrate ONE call-site at a time; verify with extra care (especially around `try/catch` boundaries). Tests still green after each.
3. Once all call-sites migrated, remove the old function. Tests still green.

**Anti-pattern:** doing this conversion across the codebase in one PR. Too many moving parts.

## What's NOT in the catalog (intentionally)

- **"Rewrite this module from scratch."** Not a refactor.
- **"Modernize this code."** Vague; not a refactor.
- **"Make this more idiomatic."** Subjective; not a refactor unless you can name the specific moves.
- **"Apply Clean Code principles."** Same.

If the prompt is one of these, ask for the specific moves first.
