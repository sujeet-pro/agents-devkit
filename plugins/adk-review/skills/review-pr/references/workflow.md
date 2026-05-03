# `review-pr` — workflow detail

Detailed phase-by-phase stage list. Every checkpoint logs to `.temp/task-<slug>/validation/per-skill/review-pr.md`.

## Phase 0 — prompt expand

1. **Parse the PR reference.** Accept any of: full URL (`https://github.com/acme/checkout-api/pull/2841`), `<owner>/<repo>#<num>`, or bare `#<num>` (resolves against current repo's remote).
2. **Resolve the local checkout.** Look up the repo in `~/.config/adk/repos.md`. If found, use `repos[<name>].path`. If not found, ask once; under `--auto`, fall back to `gh repo clone` into `.temp/task-<slug>/review-checkout/`.
3. **Create the isolated review checkout.**

   ```bash
   git worktree add .temp/task-<slug>/review-checkout <head-sha>
   ```

   This avoids colliding with the user's main checkout while reviewing. Multiple parallel PR reviews each get their own worktree.
4. **Detect ownership.**

   ```bash
   gh api graphql -f query='query { viewer { login } }' --jq '.data.viewer.login'
   git config user.email
   ```

   Compare to PR `author.login`. If equal → `own`. Else → `peer`. Restate in the status banner.
5. **Slug.** Derive `<slug>` from the PR title (e.g. `checkout-api-pr-2841`). Kebab-case, max 6 words. Date-prefix only on collision.
6. **Create `.temp/task-<slug>/`** + write `prompt.txt` (the verbatim user prompt + ISO timestamp + the resolved PR URL + ownership).
7. **Determine mode.** `--auto` (default), `-i`, `--fix`, or composed (`--auto --fix`, `-i --fix`). `--auto -i` is invalid → refuse at parse.

## Phase 1 — preflight

1. **MCP / CLI selection.** Run `bin/adk-mcp-health --json | jq '.shipped.github'` AND `gh auth status`. Pick `gh` if both work (faster cold start; no Docker). Record choice in `validation/per-skill/review-pr.md`.
2. **Auth scope check.** `gh api /user` → confirm authed. For `--fix`: `gh api /repos/<repo>` → confirm `permissions.push: true`.
3. **Local repo state.** In the worktree: `git status --porcelain` → must be clean for `--fix`. (Read-only review tolerates dirty.)
4. **Branch protection.** `gh api /repos/<repo>/branches/<base>/protection` → record `required_status_checks` and `restrictions`. Refuse `--fix` if head branch is protected.
5. **Meta-info.** `bin/adk-info github --check` AND `bin/adk-info review --check` → must return 0. Stop with the validation errors otherwise.
6. **`forbid_force_push_branches`** loaded from `github.md` and held for any later push.

## Phase 2 — fetch context

Parallel where possible. Each call writes to `.temp/task-<slug>/pr-context/`:

| Call | Output | Tool |
| --- | --- | --- |
| PR metadata | `pr.json` | `gh pr view <num> --json title,body,baseRefName,headRefOid,author,additions,deletions,files,labels,reviewRequests,assignees,statusCheckRollup` |
| Diff | `diff.patch` | `gh pr diff <num> --patch` |
| Existing review comments | `comments.json` | `gh api /repos/<repo>/pulls/<num>/comments --paginate` |
| Issue comments (top-level) | `issue-comments.json` | `gh api /repos/<repo>/issues/<num>/comments --paginate` |
| Reviews + replies | `reviews.json` | `gh api /repos/<repo>/pulls/<num>/reviews --paginate` |
| Resolved threads | `threads.json` | `gh api graphql` (REST doesn't expose resolved state cleanly) |
| PR template | `template.md` | read `.github/pull_request_template.md` from worktree |
| CODEOWNERS | `codeowners.txt` | read `.github/CODEOWNERS` from worktree |
| Author's last 5 PRs | `author-history.md` | `gh pr list --author <login> --limit 5 --json number,title,state` |
| Repo's `AGENTS.md` / `CLAUDE.md` / `.cursorrules` | `repo-conventions.md` | read each if present |
| Linked Jira ticket | `jira-context.md` | only if Atlassian workspace connector available + URL detected in PR body |

## Phase 3 — full-scope review (always; never delta)

1. **Read every changed file in its post-diff state.** Not just the diff hunks — the full function body / class / module the change lives in.
2. **Spawn dimension passes** in parallel (max 4 at once — see `agents/dispatcher.md` rule). Each pass loads the appropriate agent:

   | Dimension | Agent | Skip when |
   | --- | --- | --- |
   | correctness | `code-reviewer` | rename / move / config-only diff |
   | security | `security-reviewer` | diff doesn't touch a boundary or auth path |
   | performance | `code-reviewer` | non-hot-path / one-shot scripts (use repo's perf budget signals) |
   | tests | `code-reviewer` | diff is test-only or pure refactor with green tests |
   | docs | `code-reviewer` | internal refactor; no public surface change |
   | style | `code-reviewer` | repo's lint config is silent on the rule |

3. **Each agent emits findings** in the canonical card shape (see `references/comment-template.md`). Findings collected at `.temp/task-<slug>/review/raw-findings.md`.
4. **Apply `~/.config/adk/review.md` overrides:**
   - `severity_bar` — re-tier findings whose category was overridden.
   - `ignore_in_repos[<repo>]` — drop findings whose category is in the ignore list.
5. **De-noise.** If 3+ findings on the same file/line have the same root cause, collapse to 1 with the others as `references` in the card.

## Phase 4 — reconcile existing comments

For every existing comment / reply / resolved task, classify per `references/pr-comment-reconciliation.md`:

| State | Treatment |
| --- | --- |
| `still-open` | Surface in `reconciliation.md`. Don't draft a duplicate finding. |
| `resolved-confirmed` | Confirm against current code; note in `reconciliation.md`. No new finding. |
| `resolved-stale` | Surface as `Should-Have`: "comment marked resolved but issue still in code at `<file>:<line>`". |
| `pushback` | If we drafted a similar finding, merge into `pushback-context.md` with the author's reasoning; only re-raise with a stronger argument or new evidence. |
| `clarify` | Surface in `reconciliation.md`; if we have an answer (read the code), draft a reply. |

Write `.temp/task-<slug>/review/reconciliation.md` with the per-comment classification table.

**Dedupe.** Walk the new findings list (Phase 3 output) against `still-open` and `pushback`. Drop new findings that duplicate a comment already on the PR.

## Phase 5 — propose

1. **Sort** new findings by severity: Blocker → Critical → Should-Have → May-Have → Nitpick → Question.
2. **Write `findings.md`** at `.temp/task-<slug>/review/findings.md` with the sorted list.
3. **Mode branch:**
   - `-i`: walk each finding. For each, ask `accept | edit | discard | discuss-in-person`. Capture decisions.
   - `--auto`: keep all validated, non-duplicate findings.
4. **Approval gate** unless `--auto`: show the count by severity + the Blocker (if any), ask "post these?".

## Phase 6 — post / reply / fix (mode-dependent)

### Phase 6a — post (peer's PR, review-mode)

1. **Re-validate line anchors.** For each finding, re-fetch the diff. If the target line shifted, drop the finding (or re-anchor if trivial).
2. **Flip `GITHUB_READ_ONLY=0`** for this stage only (or use `gh`).
3. **Post.** Prefer one PR review with multiple inline comments (`gh pr review --comment -F <body-file>` with inline annotations) over many individual comments — preserves the "single review" UX.
4. **Capture provider-returned IDs** into a post-receipt set. Write `.temp/task-<slug>/review/post-receipts.json`.
5. **Post-confirmation** per `references/post-confirmation.md`:
   - Wait 5s.
   - Re-fetch comments via `gh api /repos/<repo>/pulls/<num>/comments`.
   - Confirm every receipt ID appears.
   - On miss: wait 10s, re-fetch. On miss: wait 20s, re-fetch.
   - On final miss: log to `postback.md` as `unconfirmed`. **NEVER re-post.** Surface to the user.
6. **Restore `GITHUB_READ_ONLY=1`** before returning.
7. **Write `postback.md`** with the receipt table (finding ID → comment URL → confirmed at).

### Phase 6b — validate + reply (your PR)

1. Same review pass — but findings serve to validate your own work, not post adversarially.
2. For each existing reviewer comment classified in Phase 4:
   - `still-open` → draft a reply (template: `pr-reply-templates.md` → fix-applied / pushback / clarification).
   - `clarify` → draft a clarification reply.
   - `pushback` → consider; if your draft now aligns with the reviewer, draft `fix-applied`.
3. Write `.temp/task-<slug>/review/replies-draft.md`.
4. Under `-i`: walk each draft. Under `--auto`: post replies (same post-confirmation as 6a).

### Phase 6c — fix (`--fix` mode only)

1. **Build the fix queue.** Accepted findings (own + peers') prioritized by severity.
2. **Apply each fix.** For trivial edits, do it inline. For non-trivial fixes, delegate to `/adk-code:code-bugfix` (passes the finding card as the brief; receives a fix patch).
3. **Validate.** Run repo-native tests / typecheck / lint. Use `repos[<name>].notes` for the build command if `repos.md` lists it.
4. **Commit per finding** (preferred for traceability) OR one squashable commit if the user prefers (under `-i`, ask once at the top of the session).
5. **PUSH-GATE.** Ask the user before the first push of the session. Even under `--auto --fix`. Show the exact `git push` command.
6. **Push.** `git push origin <head-branch>`. NEVER `--force`. NEVER to a branch in `forbid_force_push_branches`.
7. **Reply per addressed comment.** `pr-reply-templates.md` → `fix-applied` template, quoting the commit SHA.
8. **Mark inline comments resolved** (only after reply post-confirmation).
9. **NEVER `gh pr merge`.** Refuse with a clear message: "merge is the author's call — `gh pr merge` is not in this skill's allow-list".
10. **Write `fix-log.md`** with per-finding commit SHA + validation evidence.

## Phase 7 — report

1. **Final report** at `.temp/task-<slug>/report.md` per `references/output-format.md`.
2. Surface to user: severity counts, links to PR comments posted, links to commits pushed, residual risk.
3. Offer depth: "Need more detail on any finding?" — never dump long context unprompted.

## Loop control

- **Post-confirmation final miss.** Log + surface; do NOT re-post. The right move is to ask the user to refresh the PR page and confirm.
- **Same finding rejected by author 2x.** Don't re-raise without new evidence.
- **Same dimension pass failing 3x in a row.** Stop and surface to the user (might be MCP / network / repo state issue).
- **More than 4 parallel subagents.** Refuse — coordination overhead grows past 4 (per `agents/dispatcher.md` rule).
