---
title: 'adk-publish-github'
description: 'Run GitHub PR/issue/comment/merge actions via `gh` CLI or the github MCP server - create or update a PR, post a comment, request review, label, transition status, merge with the right strategy. Use when the destination is github.com (or GitHub Enterprise) and the deliverable is a remote action with verification. Do not use for Bitbucket (use adk-publish-bitbucket), drafting the message itself (use adk-publish-commit), or reviewing the PR (use adk-review-pr).'
skill_name: adk-publish-github
category: task
---

# adk-publish-github

Run GitHub PR/issue/comment/merge actions via `gh` CLI or the github MCP server - create or update a PR, post a comment, request review, label, transition status, merge with the right strategy. Use when the destination is github.com (or GitHub Enterprise) and the deliverable is a remote action with verification. Do not use for Bitbucket (use adk-publish-bitbucket), drafting the message itself (use adk-publish-commit), or reviewing the PR (use adk-review-pr).

## Skill body

# ADK Publish / GitHub

Standalone task skill under the `adk-publish` category router. Executes GitHub actions through `gh` CLI (preferred) or the `github` MCP server, then verifies the action landed.

## When to use

- Open a new PR for the current branch.
- Update an existing PR title, body, labels, reviewers, draft state.
- Post a comment (issue or PR) or reply in a thread.
- Request review from specific users / teams.
- Close, reopen, or merge a PR with a chosen strategy.
- Create or update an issue.
- Transition project board status (when GitHub Projects is in use).

## When NOT to use

- Drafting the message text -> `adk-publish-commit`
- Reviewing the PR's content -> `adk-review-pr`
- Bitbucket destination -> `adk-publish-bitbucket`
- Confluence / Drive destination -> `adk-publish-confluence` / `adk-publish-gdrive`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `pr-create` / `pr-update` / `pr-comment` / `pr-merge` / `pr-request-review` / `issue-create` / `issue-comment` / `label` / `status` |
| `<target>` | yes when applicable | PR number, issue number, or URL |
| `<body>` | optional | Comment / description body (markdown) |
| `<merge-strategy>` | optional for `pr-merge` | `merge` / `squash` (default) / `rebase` |
| `--auto` | optional | Skip confirmations on non-destructive actions |

## Workflow

1. **Confirm intent** - restate action, target, body summary, and any flags. Approval gate unless `--auto` (and never auto for `pr-merge`).
2. **Check tooling** - prefer `gh` CLI:
   - `gh auth status` must be OK.
   - If `gh` is missing, fall back to the `github` MCP server.
   - If both are missing, stop and tell the user how to install `gh` or configure the MCP.
3. **Resolve repo** - detect `org/repo` from `git remote get-url origin` (must be a github.com host) or from the URL in `<target>`.
4. **Execute** - run the action via `gh` or MCP. Capture the resulting URL / SHA / id.
5. **Verify** - read back the artifact (`gh pr view`, `gh issue view`, MCP equivalent) to confirm the change landed (title matches, body matches, labels present, etc.).
6. **Report** - lead with the URL; include action, key changes, and verification status.

## Action playbooks

### pr-create

```bash
gh pr create \
  --title "<title>" \
  --body-file <markdown-file> \
  --base <base> \
  --head <head> \
  [--draft] \
  [--label <list>] \
  [--reviewer <list>]
```

Use a body file (not inline) so multi-line markdown is preserved. The body is provided by `adk-publish-commit` (action `pr-describe`) when chained.

### pr-update

```bash
gh pr edit <number> --title "<title>" --body-file <markdown-file>
gh pr edit <number> --add-label <label> --remove-label <label>
gh pr ready <number>     # un-draft
gh pr ready <number> --undo  # back to draft
```

### pr-comment

```bash
gh pr comment <number> --body-file <markdown-file>
```

### pr-merge

Approval gate is mandatory; never `--auto` for merges.

```bash
gh pr merge <number> --squash --delete-branch
gh pr merge <number> --merge   # only when squash is not desired
gh pr merge <number> --rebase  # rare; ensure repo policy allows
```

Refuse to merge if: required checks failing, required reviews missing, branch behind base by configured rule, or branch has unresolved review threads (best-effort detection).

### pr-request-review

```bash
gh pr edit <number> --add-reviewer <user-or-team>
```

### issue-create / issue-comment

```bash
gh issue create --title "<title>" --body-file <markdown-file> [--label <list>] [--assignee <user>]
gh issue comment <number> --body-file <markdown-file>
```

### label

```bash
gh issue edit <number> --add-label <label> --remove-label <label>
gh pr edit <number> --add-label <label> --remove-label <label>
```

### status

If the repo uses GitHub Projects, transition the linked item via `gh project item-edit` or the MCP equivalent.

## Output format

```
## GitHub action: <action>
- Target: <PR/issue URL>
- Result: <URL of created / updated / merged artifact>
- Tool used: <gh CLI | github MCP>

## Verification
- <field>: matches expected
- <field>: matches expected

## Follow-up
- <e.g. "branch deleted", "request review from @alice", "release draft updated">
```

## Hard rules

- Never auto-merge. `pr-merge` always requires explicit user approval.
- Never force-push from this skill. If a force-push is required, the user runs it directly.
- Never delete a branch as part of `pr-create` or `pr-update` (only as a side-effect of `pr-merge --delete-branch`).
- All multi-line bodies are passed via `--body-file`; no inline heredoc shortcuts.
- Verify after every write. If verification fails, surface it loudly.

## Anti-patterns

- Skipping verification because "the command exited 0".
- Editing the PR title to "WIP" without coordinating with the author.
- Force-pushing or rewriting history as part of a publish action.
- Merging while CI is red because "the failing job is flaky".
- Using `gh` and MCP in the same action, mid-flow. Pick one.

## Examples

```
adk-publish-github pr-create --base main --head my-branch --body-file .temp/drafts/pr-body.md
```

```
adk-publish-github pr-comment 842 --body-file .temp/drafts/comment.md
```

```
adk-publish-github pr-merge 842 --merge-strategy squash
```

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |

<!-- adk:references:end -->

## References shipped with this skill

- `references/anti-patterns.md`
- `references/constitution.md`
- `references/examples.md`
- `references/mcp-fallback.md`
- `references/output-format.md`
- `references/persona.md`
