---
name: adk-publish-bitbucket
description: Run Bitbucket Cloud PR/issue/comment/merge actions via REST API or the bitbucket MCP server - create or update a PR, post a comment, request review, label, transition status, merge with the right strategy. Use when the destination is bitbucket.org and the deliverable is a remote action with verification. Do not use for GitHub (use adk-publish-github), drafting the message itself (use adk-publish-commit), or reviewing the PR (use adk-review-pr).
---

# ADK Publish / Bitbucket

Standalone task skill under the `adk-publish` category router. Executes Bitbucket Cloud actions through the `bitbucket` MCP server (preferred) or direct REST API, then verifies the action landed.

## When to use

- Open a new PR for the current branch on Bitbucket Cloud.
- Update an existing PR title, description, reviewers.
- Post a comment (general or inline) on a PR.
- Approve, unapprove, decline, or merge a PR.
- Create or update an issue (in repos where Bitbucket Issues is enabled).

## When NOT to use

- Drafting the message text -> `adk-publish-commit`
- Reviewing the PR's content -> `adk-review-pr`
- GitHub destination -> `adk-publish-github`
- Confluence / Drive destination -> `adk-publish-confluence` / `adk-publish-gdrive`
- Bitbucket Server / Data Center (different API) - this skill targets Bitbucket Cloud only

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `pr-create` / `pr-update` / `pr-comment` / `pr-approve` / `pr-merge` / `pr-decline` / `issue-create` / `issue-comment` |
| `<target>` | yes when applicable | PR id or full URL |
| `<body>` | optional | Comment / description body (markdown) |
| `<merge-strategy>` | optional for `pr-merge` | `merge_commit` / `squash` (default) / `fast_forward` |
| `--auto` | optional | Skip confirmations on non-destructive actions |

## Workflow

1. **Confirm intent** - restate action, target, body summary, and any flags. Approval gate unless `--auto` (and never auto for `pr-merge` or `pr-decline`).
2. **Check tooling** - prefer the `bitbucket` MCP server; fall back to direct REST (`https://api.bitbucket.org/2.0/`) with `BITBUCKET_USERNAME` + `BITBUCKET_APP_PASSWORD` from env. Stop with a clear install/config message if neither is available.
3. **Resolve workspace/repo** - detect `<workspace>/<repo>` from `git remote get-url origin` (must be a bitbucket.org host) or from the URL in `<target>`.
4. **Execute** - call the MCP or REST endpoint. Capture the returned PR/issue id and URL.
5. **Verify** - re-fetch the artifact via the same provider to confirm the change landed (title, description, reviewers, state).
6. **Report** - lead with the URL; include action, key changes, and verification status.

## Action playbooks

### pr-create

REST:

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests
{
  "title": "<title>",
  "source": { "branch": { "name": "<head>" } },
  "destination": { "branch": { "name": "<base>" } },
  "description": "<markdown>",
  "reviewers": [ { "uuid": "{uuid}" } ],
  "close_source_branch": true
}
```

The description must be the full markdown produced by `adk-publish-commit` (action `pr-describe`).

### pr-update

```
PUT /2.0/repositories/{workspace}/{repo}/pullrequests/{id}
{ "title": "<title>", "description": "<markdown>" }
```

### pr-comment

General comment:

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments
{ "content": { "raw": "<markdown>" } }
```

Inline comment (anchored to a file/line):

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/comments
{
  "content": { "raw": "<markdown>" },
  "inline": { "to": <line>, "path": "<file>" }
}
```

### pr-approve

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/approve
```

(Use the `unapprove` verb to revoke.)

### pr-merge

Approval gate is mandatory; never `--auto` for merges.

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/merge
{ "merge_strategy": "squash", "close_source_branch": true }
```

Refuse to merge if: required builds failing, required approvals missing, branch behind destination by repo policy, or open declined / blocking comments exist.

### pr-decline

```
POST /2.0/repositories/{workspace}/{repo}/pullrequests/{id}/decline
{ "content": { "raw": "<reason as markdown>" } }
```

Approval gate mandatory.

### issue-create / issue-comment

(Only when the repo enables Bitbucket Issues.)

```
POST /2.0/repositories/{workspace}/{repo}/issues
{ "title": "<title>", "content": { "raw": "<markdown>" }, "kind": "bug" }

POST /2.0/repositories/{workspace}/{repo}/issues/{id}/comments
{ "content": { "raw": "<markdown>" } }
```

## Output format

```
## Bitbucket action: <action>
- Target: <PR/issue URL>
- Result: <URL of created / updated / merged artifact>
- Tool used: <bitbucket MCP | REST>

## Verification
- <field>: matches expected
- <field>: matches expected

## Follow-up
- <e.g. "source branch closed", "request review from @alice">
```

## Hard rules

- Never auto-merge. `pr-merge` always requires explicit user approval.
- Never auto-decline.
- Never force-push or rewrite history from this skill.
- Inline comments must include `path` and `to` (line); otherwise post as general comment.
- All multi-line bodies pass through the `content.raw` field with markdown.
- Verify after every write. If verification fails, surface it loudly.

## Anti-patterns

- Skipping verification because "the API returned 200".
- Approving your own PR without explicit user request.
- Merging while builds are red because "the failing build is flaky".
- Mixing MCP and REST in the same action mid-flow.
- Deleting branches via `close_source_branch` without coordinating with the author.

## Examples

```
adk-publish-bitbucket pr-create --body-file .temp/drafts/pr-body.md
```

```
adk-publish-bitbucket pr-comment 17 --body-file .temp/drafts/comment.md
```

```
adk-publish-bitbucket pr-merge 17 --merge-strategy squash
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Action: pr-create / pr-update / pr-comment / pr-task / pr-merge / issue-create / issue-comment?** — _How to pick:_ Comments are discussion; tasks are blocking checklist items the author must resolve. Pick deliberately.
2. **Target: PR/issue ID or URL?** — _How to pick:_ Required for actions on existing artifacts.
3. **Body source: file path or auto-generate?** — _How to pick:_ Prefer file (drafted upstream). Auto-generate only when no body exists.

**Default report:** Action result URL + verification block + tool used (REST / MCP).

**Detailed report (on request or `--verbose`):** Add: full HTTP request/response JSON archived, follow-up suggestions (assign reviewers, link to spec page).

**Artifact:** `bitbucket-action-result` — The remote PR/issue/comment/task is the artifact. Action log in .temp/notes/.

**Artifact path:** .temp/notes/publish-bitbucket-<action>-<target>.md

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/clarifying-questions.md`) and reports the choices.

1. **Action: pr-create / pr-update / pr-comment / pr-task / pr-merge / issue-create / issue-comment?** — _How to pick:_ Comments are discussion; tasks are blocking checklist items the author must resolve. Pick deliberately.
2. **Target: PR/issue ID or URL?** — _How to pick:_ Required for actions on existing artifacts.
3. **Body source: file path or auto-generate?** — _How to pick:_ Prefer file (drafted upstream). Auto-generate only when no body exists.

## Default vs detailed output

**Default report:** Action result URL + verification block + tool used (REST / MCP).

**Detailed report (on request or `--verbose`):** Add: full HTTP request/response JSON archived, follow-up suggestions (assign reviewers, link to spec page).

**Artifact:** `bitbucket-action-result` — The remote PR/issue/comment/task is the artifact. Action log in .temp/notes/.

**Artifact path:** .temp/notes/publish-bitbucket-<action>-<target>.md

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |

<!-- adk:references:end -->
