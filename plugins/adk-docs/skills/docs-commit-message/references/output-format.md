# `docs-commit-message` — output format

## Per-turn status

```
[adk-docs:docs-commit-message] task=<slug> phase=<0|1|2|3|4> style=<conv|semantic|free> subject-len=<N> files=<N> mode=<auto|interactive|fix>
```

## `commit-msg.txt` — exact shape

```
<subject ≤72 chars>

<body paragraph 1, hard-wrapped at 72>

<body paragraph 2, hard-wrapped at 72>

<optional trailers>
```

Lines:

- Line 1: subject. No trailing period. No trailing newline inside the line.
- Line 2: exactly one blank line separating subject from body.
- Body: paragraphs separated by blank lines. Hard-wrap at 72, except
  for URLs and code fences (a line inside a fenced block isn't
  wrapped).
- Trailers: separated from the body by exactly one blank line.
  Format: `Token-Case: value`.

## Trailer format

```
Refs CHK-1238
Co-authored-by: Alice Example <alice@example.com>
Signed-off-by: Sujeet Jaiswal <sujeet@onequince.com>
```

Supported tokens:

- `Refs` — ticket reference (or multiple, comma-separated).
- `Fixes` — closes the ticket (only when PR is single-purpose).
- `Co-authored-by` — full name + email in angle brackets.
- `Signed-off-by` — DCO sign-off.
- repo-specific trailers detected from `recent-subjects.txt` (e.g.
  some repos use `Change-Id: <hash>` for Gerrit).

## Final report

`.temp/task-<slug>/report.md`:

```markdown
# docs-commit-message report — <slug>

## Result
Drafted commit message for `acme/checkout-api` staged diff.
Under --fix, ran `git commit`; new HEAD = <sha>.

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 1 | style | conventional | detected from git log -10 (8/10 matches) |
| 2 | scope | checkout | dominant area of the diff |
| 2 | type | fix | diff changes existing happy path; no new feature |

## Validation evidence
- subject: 52 chars
- body paragraphs: max width 71
- conventional regex: match
- no --no-verify, no --amend

## Residual risk / follow-ups
- The diff also touches `tests/checkout/CartService.add.test.ts` —
  staged along with the fix; single commit is correct.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  diffstat.txt
  staged.diff
  recent-subjects.txt
  detected-style.txt
  commit-msg.txt
  report.md
```

## Pre-commit hook rejection (under `--fix`)

If the commit-msg hook rejects, the skill:

1. Captures the hook's output into
   `.temp/task-<slug>/hook-rejection.txt`.
2. Shows the rejection to the user.
3. Offers: re-draft (loop to Phase 2), stop, or amend the message
   manually.
4. **Never** retries with `--no-verify`.
