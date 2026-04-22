# Research Protocol for `adk-review-pr`

The skill consults sources in the order below. Higher-ranked sources win conflicts. Stop researching when the stop condition is met — diminishing returns past that point.

## Sources, in order

1. **PR diff + description + linked issue** — fetched via `gh` / github MCP / bitbucket MCP per `pr-mcp-fallback.md`. The diff is the ground truth for what the review is about.
2. **Files in their post-PR state** — read each changed file at the PR head, plus immediate dependencies and tests. Repo evidence over guessing.
3. **Existing comments + replies + tasks on the PR** — fetched once at the start; used by `pr-comment-reconciliation.md`. Do NOT re-file what is already raised.
4. **Repo conventions** — lint config, formatter config, `.editorconfig`, `CONTRIBUTING.md`, code-style docs, `AGENTS.md`/`CLAUDE.md` if present. The PR must conform to repo conventions, not generic best practice.
5. **Recent git log on the changed surface** — `git log --oneline -- <changed-paths>` to detect "this is the third revert in two weeks" patterns.
6. **Linked design docs / ADRs / RFCs** — only if referenced by the PR description or code.
7. **External docs** — official upstream docs (framework, library, language). Use sparingly; only when the finding turns on a published API contract.

## Stop condition

Every finding has Type, Severity, Confidence, file:line, quoted evidence, and a justified suggested fix. The verdict is justified by the highest-severity finding. Stop researching past that point.

## Evidence buckets

For every finding, label it (in `.temp/notes/`, not in the posted comment):

- `Verified` — backed by primary source (PR diff, repo file, official upstream doc with retrieval date).
- `Inferred` — extrapolated from related evidence; the posted comment must say so explicitly (e.g., "I cannot reproduce locally; based on the diff, this branch can hit ...").
- `Open` — could not verify; goes in the `Question` section of the report, not the inline comments.

`Inferred` findings cap their `Confidence` at 70/100. `Open` findings cap at 50/100 and are filed as `Question` Type only.

## Citation discipline

- File paths as `path/to/file.ext:LINE-LINE`. Always lines from the post-PR state.
- URLs with retrieval date (e.g., "fetched 2026-04-21").
- Git commits as short SHAs from the host repo.
- Cloned reference repos as `.temp/reference-repos/<owner>__<repo>/path:LINE`.
- Do NOT cite line numbers from the pre-PR state — the author and other reviewers will look in the wrong place.

## Freshness

Treat any external web source older than 6 months for fast-moving libraries (React, Vite, Next.js, browser APIs) as suspect — verify against the latest official changelog before using.

For Bitbucket / GitHub API behavior: the providers' documented behavior is the ground truth; do not rely on community docs.

## Diff-vs-files trade-off

The PR diff alone is rarely enough for a serious review. Read:

- the full file as it stands at PR head (not just the diff), for every changed file
- the immediate caller(s) of any changed exported function
- the test file(s) for the changed module
- any config that the changed code reads at runtime

If the PR is too large to read in this depth, propose batching to the user (per `pr-clarifying-questions.md` Question 5 / Phase 1 validator's `Diff size sanity` check).
