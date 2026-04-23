# Atomic commits and change sizing

Optional reference loaded by `publish-commit`. Encodes the trunk-based / atomic-commit / change-sizing discipline.

## Atomic commit definition

A commit is **atomic** when:

1. It changes ONE logical thing.
2. It builds and tests green on its own.
3. Its message explains the **why**, not just the what.
4. It can be reverted without breaking unrelated functionality.

If any one fails, split.

## Change sizing rule of thumb

| Diff size | Default reaction |
| --- | --- |
| ≤ ~100 lines | "Easy to review." Default zone. |
| 100–300 lines | "Reviewable, slower." Acceptable for a single concern. |
| 300–1000 lines | "Slow review." Split unless mechanical (codemod, lockfile, generated). |
| > 1000 lines | "Reviewer fatigue zone." Split required unless mechanical. |

Sizing is heuristic; **concern coherence matters more than line count**. A 1500-line single rename is fine; a 250-line PR mixing 4 concerns is not.

## Conventional commit prefix

Use one prefix per commit:

| Prefix | When |
| --- | --- |
| `feat:` | New behavior visible to a user / consumer. |
| `fix:` | Behavior change that corrects a defect. |
| `refactor:` | Structural change, no behavior change. |
| `perf:` | Behavior preserved, but measurably faster. |
| `docs:` | Documentation only. |
| `test:` | Test code only. |
| `build:` | Build / tooling / dependency changes. |
| `ci:` | CI configuration only. |
| `chore:` | Anything not user-visible (e.g. lockfile bump). |
| `revert:` | Reverts a previous commit. |
| `style:` | Formatting / whitespace only (rare; usually folded into `refactor:`). |

Optional scope: `feat(auth):`, `fix(checkout):`. Match the repo's existing pattern (read `git log --oneline -50`).

## Message body — the *why*

```
fix(auth): keep session valid across token rotation

Previously, rotating the session token invalidated all in-flight
requests, causing user-visible 401s mid-flow. We now track the old
token for a 30-second grace window so concurrent requests succeed.

Closes #842
```

Rules:

- First line: ≤ 72 chars; imperative mood ("add", not "added").
- Blank line after subject.
- Body wrapped at 72 chars; explains motivation, alternatives considered, gotchas.
- Footer: issue refs (`Closes #N`, `Refs #N`), `BREAKING CHANGE: ...` if applicable, co-authors.

## What NOT to mix in one commit

- Behavior change + formatting change.
- Behavior change + dependency bump (unless the bump is the cause).
- Two independent fixes.
- Refactor + new feature.
- Generated-file regeneration + handwritten changes.
- Multiple unrelated typo fixes (one per commit if they're in different domains, or batch as a single `docs: typo fixes` chore).

## When split is harder than worth it

Sometimes splitting is not free. Acceptable to keep together:

- A behavior change + the new test that proves it.
- A type fix + the call sites that needed updating because of the type fix.
- A schema migration + the code that uses the new column (if rollback works either way).

Document the choice in the commit body if asked.

## Commit hygiene checklist

- [ ] One logical change.
- [ ] Builds and tests green AT this commit.
- [ ] Message has the right prefix and explains why.
- [ ] No secrets in the diff (`git diff --cached | rg -iE 'password|secret|api[_-]?key|token'`).
- [ ] No format-only churn mixed in.
- [ ] No commented-out code blocks added.
- [ ] No `console.log` / `print` debug statements left in production paths.
- [ ] No `// TODO: cleanup before merge` lines.
- [ ] `.gitignore` covers any new local-only files.

## Trunk-based development reminders

- Branches live ≤ 3 days; merge often.
- Long-lived feature branches → use feature flags instead.
- Always rebase / merge from main before opening PR (so reviewer sees the right diff).
- Never force-push to main.
- Force-push to your own branch only after explicit warning to anyone who's pulled it.

## Anti-patterns

- "I'll commit when the feature is done" — large blast radius, hard to revert.
- "The message doesn't matter, the diff speaks for itself" — diffs answer "what", not "why".
- "I'll squash it all later" — sometimes; not as default.
- "Branches add overhead" — short branches are the cheapest insurance.
- "I'll split this change later" — later doesn't come.
- "I don't need a `.gitignore`" — eventually you commit a `.env`.
