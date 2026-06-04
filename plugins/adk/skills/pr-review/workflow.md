# pr-review — workflow

Seven phases. GitHub-only, read-only worktree, all GitHub access via the `gh` CLI, all git via `git`, clones SSH-only. The **Workflow tool** drives Phase 3 (the multi-dimension fan-out + adversarial verification).

## Phase 0 — parse + auth

1. Parse the URL → `(owner, repo, number)`. Reject anything that isn't `https://github.com/<owner>/<repo>/pull/<n>` (Bitbucket/GitLab out of scope — `rules.md`).
2. Verify `gh auth status` succeeds. If not, stop and tell the user to `gh auth login`.

## Phase 1 — checkout (read-only worktree)

Pick a scratch dir outside the user's cwd (e.g. `${TMPDIR:-/tmp}/adk-pr-review/<owner>-<repo>-<n>`).

1. **Clone (SSH only) if absent**: `git clone git@github.com:<owner>/<repo>.git <scratch>/repo`. **Never** an `https://` clone URL.
2. `git -C <scratch>/repo fetch origin` and fetch the PR head: `gh pr checkout` is avoided (it mutates branches); instead get the head SHA from Phase 2 and `git -C <scratch>/repo fetch origin pull/<n>/head`.
3. Add a **detached** read-only worktree at the head SHA: `git -C <scratch>/repo worktree add --detach <scratch>/wt <head-sha>`. You review `<scratch>/wt`; you never edit it.

## Phase 2 — gather

All GitHub data via the `gh` CLI:

- Metadata: `gh pr view <url> --json title,body,author,baseRefName,headRefName,headRefOid,additions,deletions,files,labels`.
- Diff: `gh pr diff <url>` (or `git -C <scratch>/repo diff <base>...<head>` once fetched).
- Existing review threads + reviews: `gh api graphql` for review threads (id, isResolved, path, line, comments), or `gh pr view <url> --json comments,reviews` for a simpler view.
- Linked supporting docs: scan the PR body + comments for Jira/Confluence URLs (one hop) and fetch via the `adk-atlassian` MCP. Read them — the diff must satisfy what they specify; flag drift as a `docs` finding.

## Phase 3 — review (the Workflow)

Drive a **Workflow** over the diff + worktree:

1. **Fan out one agent per applicable dimension** (`dimensions.md`): `code-reviewer` for correctness/performance/api/concurrency/readability/consistency; `security-auditor` for security; `test-engineer` (consulted) for tests; a feature-flow pass when a flag/experiment is in the diff. Each agent gets the diff, the worktree path for cross-file context (Read/Grep/Glob), and its single dimension. The minimum bar for any code-touching PR: correctness, security, tests.
2. **Feature-flow tracing**: for any new path behind a flag/experiment/config, resolve current state via the `adk-statsig` MCP + a repo-config grep, and check kill-switch / fallback / metric-to-watch (`dimensions.md`).
3. **Adversarially verify** every surfaced finding: an independent skeptic tries to refute it (is the quote real? is the trigger plausible? is it already handled elsewhere in the diff?). Survives only if not refuted.
4. **Dedup + synthesize** into one severity-ordered set. Cite every finding by `file:line`. `--scope` narrows the dimension family.

## Phase 4 — classify existing threads

For each pre-existing review thread, decide resolve / reopen / leave-as-is by **re-checking the worktree at the comment's anchor** (`comment-resolution.md`). This is the real re-validation: look at the current code where the concern was raised.

## Phase 5 — triage

- **default** (auto): accept every surviving finding; appreciations always post.
- **`-i`**: walk each finding with the user (accept / reject / edit) via AskUserQuestion, showing the rendered comment + the code at its anchor before asking. Only accepted findings post.

## Phase 6 — post + report

Render and post via the `gh` CLI, after a one-line confirmation ("about to post N inline comments + a summary on PR #X — proceed?"):

- Inline review comments + a single review event: `gh api` to create a review with inline comments, or `gh pr review`. Event = **APPROVE** when no surviving blocker/critical and no thread needs reopen; **REQUEST_CHANGES** when there's a blocker/critical; else **COMMENT**.
- Appreciations (1–3 when warranted) as PR-level general comments: `gh pr comment`.
- Thread resolve/reopen: `gh api graphql` (`resolveReviewThread` / `unresolveReviewThread`); if the token can't mutate thread state, post a status reply instead.
- **NEVER a merge step.** Even if asked, print the merge link and exit (`rules.md`).
- `--no-post`: produce `report.md` and post nothing.

Then write a one-page report: verdict, finding counts by severity, thread actions, and the PR link.

## Narrate

State each phase, the worktree path, the Workflow fan-out ("reviewing 9 dimensions in parallel"), the skeptic's pruning, any skipped dimension + why, and the posting confirmation. Never go silent for more than a phase.
