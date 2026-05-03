# `docs-pr-description` — workflow detail

## Phase 0 — prompt expansion

1. Resolve the repo via `repos.md` (walk up from CWD to `.git`).
2. Determine current branch (`git rev-parse --abbrev-ref HEAD`).
3. Detect existing PR for this branch via `gh pr view --json number,url,body,baseRefName`.
4. Pick slug: `pr-<branch>` or `pr-<number>` if a PR exists.
5. Create `.temp/task-<slug>/`; write `prompt.txt`.

## Phase 1 — preflight

1. `bin/adk-info --check` (needs `info`, `repos`, `github`, `docs` parseable).
2. Resolve base branch:
   - Explicit CLI arg wins.
   - Else tracking branch from `git rev-parse --abbrev-ref '@{u}'`.
   - Else `origin/<repos.md.base_branch>`.
   - Else `main`.
3. Confirm base branch exists: `git rev-parse <base>`.
4. Under `--fix`: run `gh auth status`. If failed, report and stop;
   do not proceed to write.
5. Load `.github/pull_request_template.md` if present
   (see `references/pr-template-loader.md`).
6. If `adk-review` is installed, optionally switch from `gh` CLI to
   its `github` MCP. Either works — `github` MCP is slightly faster
   on multi-request turns; `gh` CLI is the default.

## Phase 2 — gather evidence

1. `git log <base>..HEAD --pretty=format:%H%x1f%an%x1f%ae%x1f%s%x1f%b%x1e > .temp/task-<slug>/commits.txt`.
2. `git diff <base>...HEAD --stat > .temp/task-<slug>/diffstat.txt`.
3. `git diff <base>...HEAD -- '**/*test*' '**/*spec*' '**/__tests__/**' > .temp/task-<slug>/tests.diff`.
4. Extract linked tickets from commit bodies (regex: `[A-Z]+-\d+` for
   Jira; `#\d+` for GitHub issues; `LIN-\d+` for Linear, etc.).
5. If a ticket link is present and unresolved, queue
   `/adk-core:context-gather`.

## Phase 3 — classify changes by area

1. Group the `diffstat.txt` files by top-level directory / feature
   area (e.g. `services/checkout/`, `db/migrations/`, `ui/components/`).
2. For each area, summarize what changed in 1-2 sentences, grounded
   in the diff. "Added `CartMutex.ts` to serialize add-to-cart calls
   per session" (not "improved checkout").
3. Identify breaking changes:
   - Removed public functions / classes / endpoints.
   - Renamed env vars used externally.
   - DB migrations that aren't backwards-compatible.
   - Changed default values in the config surface.

## Phase 4 — draft

Per `references/risk-first-format.md`:

1. **Title:** imperative, ≤70 chars, matches the repo's commit-
   subject convention if one exists. Default Conventional Commits if
   the repo uses it (`feat: add per-session add-to-cart mutex`).
2. **Summary:** 1-3 bullets. First bullet names the risk. Last bullet
   names the rollback or follow-up.
3. **Changes by area:** table (folder → one-sentence summary).
4. **Test plan:** what tests were added/changed (from `tests.diff`);
   manual steps if applicable.
5. **Risks / breaking changes:** explicit list.
6. **Linked tickets:** only those found in commit bodies. Format
   matches `github.md` convention if any.
7. **Follow-ups:** TODOs deferred to a next PR.

Write to `.temp/task-<slug>/pr-body.md`.

## Phase 5 — validate + optional `--fix`

1. Validator (see `references/validator.md`):
   - Title ≤70 chars.
   - Test plan section present and non-empty.
   - No ticket reference not in `commits.txt`.
   - All code fences have a language tag (so GitHub renders them).
2. If `--fix`:
   - Re-show the final body.
   - Ask once: "Update PR body via `gh pr edit`?" — even under `--auto`.
   - On confirm: `gh pr edit <number> --body-file .temp/task-<slug>/pr-body.md`.
   - Re-fetch the PR body; verify the update landed.
3. Write `.temp/task-<slug>/report.md`.
