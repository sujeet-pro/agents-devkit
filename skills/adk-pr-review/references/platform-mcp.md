# platform-mcp — per-platform MCP tool table for PR-review writes

> Loaded as needed by the agent at Phase 6 (post). Every write (post,
> resolve, reopen, approve) **prefers an MCP call** over the direct REST
> equivalent. Direct API stays only as the headless / no-MCP fallback path.

## Rule of thumb

- **Reads** (PR meta, comments, diff): direct API is fine, the orchestrator
  does this in Phase 2 (`fetch_pr.py`). Refreshing comments during review
  via MCP is preferred (lower latency, no extra creds).
- **Writes** (post inline + summary, resolve / reopen, approve): **MCP
  preferred**. The orchestrator writes `posting-plan.json` with the named
  tool + args per step; the agent dispatches.

The orchestrator NEVER includes a merge step in any plan. Merging is a
human action.

## GitHub

| Operation | MCP tool | Direct-API fallback |
|---|---|---|
| List PR review comments | `mcp__adk-mcp-github__pull_request_read` (subcommand `comments`) | `gh api repos/<o>/<r>/pulls/<n>/comments` |
| Add a top-level PR comment (= **general comment**, no anchor, no resolve state) | `mcp__adk-mcp-github__add_issue_comment` | `gh api repos/<o>/<r>/issues/<n>/comments` |
| Reply to an existing review comment | `mcp__adk-mcp-github__add_reply_to_pull_request_comment` | `POST /pulls/<n>/comments/<id>/replies` |
| Submit a review (with N inline comments + APPROVE / REQUEST_CHANGES / COMMENT) | `mcp__adk-mcp-github__pull_request_review_write` | `POST /pulls/<n>/reviews` with `event` field |
| Resolve / reopen a thread (canonical) | (GitHub exposes only via GraphQL; the MCP tool above does the equivalent via a status reply) | `mutation { resolveReviewThread / unresolveReviewThread }` |
| **Merge PR (not used)** | `mcp__adk-mcp-github__merge_pull_request` — DO NOT INVOKE | — |

GitHub-specific notes:

- **Approve = review event.** The approval is encoded in the review's
  `event: "APPROVE"` field, not a separate call. `posting-plan.json`
  always carries the APPROVE in the `review_summary` step's mcp_args
  when applicable; it then emits an `approve_pr` step with
  `via: "bundled_in_review_summary_event=APPROVE"` for clarity.
- **Resolve via reply.** REST + most token scopes cannot flip a thread's
  resolved state directly; GraphQL can. The plan emits a textual reply
  ("Resolving this thread — …") that the team can read; humans / the
  GraphQL fallback can flip the actual state afterward.

## Bitbucket Cloud

| Operation | MCP tool | Direct-API fallback |
|---|---|---|
| List PR comments | `mcp__adk-mcp-bitbucket__getPullRequestComments` | `GET /pullrequests/<n>/comments` |
| Get one comment | `mcp__adk-mcp-bitbucket__getPullRequestComment` | `GET /pullrequests/<n>/comments/<id>` |
| Add a top-level comment (= **general comment**, no anchor, no resolve state) | `mcp__adk-mcp-bitbucket__addPullRequestComment` (no `inline` arg) | `POST /pullrequests/<n>/comments` |
| Add an inline comment | `mcp__adk-mcp-bitbucket__addPullRequestComment` (with `inline: {path, to}`) | `POST /pullrequests/<n>/comments` (same body shape) |
| Add a pending comment (drafts before publish) | `mcp__adk-mcp-bitbucket__addPendingPullRequestComment` | — |
| Publish all pending comments at once | `mcp__adk-mcp-bitbucket__publishPendingComments` | — |
| Resolve a comment | `mcp__adk-mcp-bitbucket__resolveComment` | `PUT /pullrequests/<n>/comments/<id>/resolution` |
| Reopen a comment | `mcp__adk-mcp-bitbucket__reopenComment` | `DELETE /pullrequests/<n>/comments/<id>/resolution` |
| Approve PR | `mcp__adk-mcp-bitbucket__approvePullRequest` | `POST /pullrequests/<n>/approve` |
| Unapprove PR | `mcp__adk-mcp-bitbucket__unapprovePullRequest` | `DELETE /pullrequests/<n>/approve` |
| **Merge PR (not used)** | `mcp__adk-mcp-bitbucket__mergePullRequest` — DO NOT INVOKE | — |

Bitbucket-specific notes:

- **Pending comments are a real feature.** When the review has more than
  ~5 inline comments, prefer `addPendingPullRequestComment` per finding
  then a single `publishPendingComments` at the end — that gives the
  author one notification, not N.
- **Approve is its own endpoint.** No bundling like GitHub. The plan
  emits a discrete `approve_pr` step with the `approvePullRequest` MCP
  tool.

## Appreciation comments (general, no resolve state)

When a finding has `severity: "appreciation"`, the posting plan emits a
`general_comment` step (NOT an inline `review_summary.comments[]` entry):

- **GitHub**: `mcp__adk-mcp-github__add_issue_comment` with `body` — the
  appreciation lives on the PR's *conversation* tab, not the *files
  changed* tab. GitHub doesn't expose a resolve state on issue comments,
  so the positive note stays put. (Inline review-comments would carry a
  resolve state we'd need to manage.)
- **Bitbucket**: `mcp__adk-mcp-bitbucket__addPullRequestComment` with
  `content.raw` but **no `inline` field** — a "general" PR comment on BB.
  These also lack a resolve state.

The rendered body includes `*Location:* file:line` since it's no longer
anchored. Triage auto-accepts every appreciation at `--init` time — they
never enter the interactive walk; the user does NOT walk through them.

This is the only step kind that posts even when the review summary is
suppressed (`n_findings=0 && recommendation != approve`). Positive
feedback on otherwise-trivial PRs still ships.

## Plan shape (`posting-plan.json`)

```json
{
  "host": "bitbucket",
  "pr_url": "https://bitbucket.org/acme/ecomm-ssr/pull-requests/5521",
  "recommendation": "approve",
  "approve_ready": true,
  "post_review": false,
  "n_findings": 0,
  "n_actions": 3,
  "never_merge": true,
  "steps": [
    {
      "kind": "resolve",
      "mcp_tool": "mcp__adk-mcp-bitbucket__resolveComment",
      "mcp_args": { "workspace": "acme", "repoSlug": "ecomm-ssr",
                    "pullRequestId": 5521, "commentID": "799143917" },
      "fallback": "PUT /pullrequests/<n>/comments/<id>/resolution",
      "comment_id": "799143917",
      "reason": "diff touched anchored line src/checkout/payment.ts:42"
    },
    {
      "kind": "approve_pr",
      "mcp_tool": "mcp__adk-mcp-bitbucket__approvePullRequest",
      "mcp_args": { "workspace": "acme", "repoSlug": "ecomm-ssr",
                    "pullRequestId": 5521 }
    }
  ]
}
```

## How the agent dispatches the plan

```
1. Read posting-plan.json from the task dir.
2. Constitution §I.4 confirmation is already-handled by the orchestrator's
   --no-post / interactive-triage gate. The plan itself does not re-prompt.
3. For each step (in order):
   a. If `mcp_tool` is set:
        Invoke the named tool with `mcp_args`. On success → record the step
        result in `post-result.json`. On failure → fall through to the
        `fallback` string IF it's named, else surface the error.
   b. If `kind == "approve_pr"` and `via == "bundled_in_review_summary_event=APPROVE"`:
        The APPROVE already shipped with the preceding review_summary step.
        Nothing more to do here.
4. Write the merged result + step statuses to <task_dir>/post-result.json.
5. NEVER call merge_pull_request / mergePullRequest. If the user wants a
   merge, they pass `--merge` to the skill (not currently implemented; the
   plan refuses regardless).
```

## What's NOT in this table

- **Repo / branch creation** — out of scope for PR review.
- **Workflow / CI re-runs** — out of scope.
- **Cross-repo references** — out of scope.
- **Merge** — out of scope by design. Reviewers approve; humans merge.
