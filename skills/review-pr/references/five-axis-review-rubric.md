# Five-axis review rubric

Optional reference loaded by `review-pr` (and recommended for `review-local`). Encodes the staff-engineer-grade review rubric: every change is evaluated on **five axes** with an explicit verdict per axis.

## The five axes

| Axis | What it asks |
| --- | --- |
| **1. Correctness** | Does this do what it says it does? Are edge cases handled? Are the tests real? |
| **2. Readability** | Will the next person (or the agent) understand this in 6 months? |
| **3. Architecture** | Is this in the right layer? Does it match the repo's conventions? Does it create or pay down debt? |
| **4. Security** | Does this introduce / preserve / weaken any security property? Three-tier check. |
| **5. Performance** | Does this introduce any new hot-path slowness, N+1, unbounded growth, or budget violation? |

Each axis gets a verdict: **OK**, **Important**, **Critical**, **FYI / Nit**.

## Severity labels (use exactly these)

- **Critical** — must be fixed before merge (correctness defect, security regression, data loss, contract break).
- **Important** — should be fixed before merge; can be deferred with explicit owner + ticket.
- **Optional** — improvement worth considering; reviewer's opinion.
- **Nit** — style / preference; non-blocking.
- **FYI** — informational; no action expected.
- **Praise** — what's done well; explicitly call it out (signal preservation matters).

## Change sizing — when to ask for a split

| Lines changed | Default reviewer reaction |
| --- | --- |
| ≤ 100 | "Easy to review thoroughly." Proceed. |
| 100–300 | "Reviewable but slower." Proceed; suggest splitting if logically separable. |
| 300–1000 | "Slow review." Strongly suggest splitting unless single concern. |
| > 1000 | "Block." Ask for a split unless the diff is mechanical (codemod, dependency lockfile, generated). |

The size is a heuristic; concern coherence matters more. A 1500-line single rename is fine; a 250-line PR mixing 4 concerns is not.

## Splitting strategies

| Pattern | Use when |
| --- | --- |
| **By stack layer** | The change spans data → service → API → UI; ship the data layer first behind a flag. |
| **By file group** | Change touches many similar files; group by feature area (e.g. all auth files, then all billing files). |
| **Horizontal slice** | The change is genuinely thin and end-to-end; split by user-visible behavior. |
| **Vertical slice** | The change adds a new feature that can be flag-gated; split by feature flag. |
| **Refactor first, feature second** | The change includes restructuring needed to add the feature; ship the refactor as a separate (no-behavior-change) PR first. |

## Tests-first, code-second on review

Read the tests before reading the code:

- Tests describe what the author *intended*.
- Code shows what they *built*.
- The gap between intent and implementation is where defects live.

If there are no tests for new behavior, that's an Important finding by itself.

## Per-axis quick checklist

### 1. Correctness

- [ ] Tests cover the happy path AND meaningful edge cases (null, empty, boundary, encoding, time zone).
- [ ] Tests would FAIL if the new code were deleted (no coverage farming).
- [ ] No silent skipped tests (`it.skip`, `xit`, `pytest.skip`).
- [ ] Errors are handled, not swallowed.
- [ ] Async code handles rejection / cancellation.
- [ ] No `// TODO: actually implement this` left in.

### 2. Readability

- [ ] Names describe intent.
- [ ] Functions have one job.
- [ ] No deeply nested control flow without good reason.
- [ ] Comments explain *why*, not *what*.
- [ ] No commented-out code blocks.
- [ ] Diff stays inside scope; no drive-by refactors.

### 3. Architecture

- [ ] Lives in the right layer (UI, service, repo, util).
- [ ] Uses the repo's existing patterns, not a new one for one file.
- [ ] No circular dependencies introduced.
- [ ] No leaky abstractions (DB types in the API layer; HTTP types in the service layer).
- [ ] No "extension points" without a current consumer.
- [ ] Pays down or preserves debt; does not silently increase coupling.

### 4. Security

- [ ] No secrets in the diff (`git diff main..HEAD | rg -i 'password|secret|api[_-]?key|token'`).
- [ ] Input validation at the boundary (Zod / Pydantic / etc.).
- [ ] Parameterized queries — no string concatenation into SQL / shell / NoSQL.
- [ ] Authz check on protected paths.
- [ ] No security header weakened.
- [ ] No `eval` / `Function(userInput)` / dynamic require with user data.
- [ ] If auth-related: see `@adk:build-security`'s three-tier classification.

### 5. Performance

- [ ] No new N+1 queries.
- [ ] No new unbounded loop / unbounded result set.
- [ ] No new long task on hot paths (> 50 ms).
- [ ] Bundle delta within budget (if applicable).
- [ ] Caches are invalidated correctly.
- [ ] No new synchronous I/O on request hot path.

## Multi-model review

For high-stakes PRs (auth, payments, infra, data migrations), have a **second model / second human** independently review. Different rubrics catch different defects.

## Output shape

```markdown
# PR review — <title> (#<number>)

## Verdict
APPROVE | APPROVE WITH NITS | REQUEST CHANGES | BLOCK

## Summary
<2-3 sentences on what the PR does and how it goes.>

## Per-axis findings

### 1. Correctness
- [Critical] <file:line> — <finding>
- [Important] <file:line> — <finding>

### 2. Readability
- [Nit] <file:line> — <finding>

### 3. Architecture
- [Important] <file:line> — <finding>

### 4. Security
- OK

### 5. Performance
- [FYI] <file:line> — <observation>

## What's done well
- <bullet>
- <bullet>

## Verification story
- Tests: <ran X, passes>
- Build: <passes>
- Manual: <verified Y manually>

## Sizing note (if applicable)
- <PR is N lines; suggest splitting because ...>
```

## Anti-patterns

- "It works, that's good enough" — works ≠ correct, readable, secure, performant.
- "I wrote it, so I know it's correct" — review your own code as if a stranger wrote it.
- "We'll clean it up later" — later doesn't come.
- "AI-generated code is probably fine" — apply the same rigor.
- "Tests pass, so it's good" — tests are necessary, not sufficient.
- Praise-only reviews — reviewers exist to find problems; if there are none, the PR is too small.
