---
title: 'publish-github'
description: 'Run GitHub PR/issue/comment/merge actions via the `gh` CLI EXCLUSIVELY (no MCP fallback).'
artifact_kind: skill
skill_name: publish-github
category: publish
---
# publish-github

Run GitHub PR/issue/comment/merge actions via the `gh` CLI EXCLUSIVELY (no MCP fallback). Create or update a PR, post a comment, request review, label, transition status, merge with the right strategy. Use when the destination is github.com (or GitHub Enterprise) and the deliverable is a remote action with verification. Do not use for Bitbucket (use `@adk:publish-bitbucket` (a.k.a. `adk-publish-bitbucket`)), drafting the message itself (use `@adk:publish-commit` (a.k.a. `adk-publish-commit`)), or reviewing the PR (use `@adk:review-pr` (a.k.a. `adk-review-pr`)). Requires `gh` installed and `gh auth status` ok — bootstrap via `@adk:setup` (a.k.a. `adk-setup`) if missing.

## Usage

> Examples assume this repo is installed as the `adk` Claude Code plugin
> (see [Quick Start](../guide/development/README.md)). Generic agents use the
> `adk-publish-github` form via `agents-skills/`.

```text
/adk:publish-github            # interactive run (Claude Code)
/adk:publish-github --auto     # unattended; pick safe defaults
```

In Cursor / Codex / Gemini: invoke as `adk-publish-github` (resolved through the
`agents-skills/adk-publish-github/` symlink).

## Source

Direct from `skills/publish-github/SKILL.md` — this page is auto-generated.

Standalone task skill under the `@adk:publish` (a.k.a. `adk-publish`) category router. Executes EVERY GitHub action through the `gh` CLI; verifies the action landed.

**`gh` is mandatory.** No MCP fallback. If `gh` is not installed or not authed, the skill fails Phase 1 with a clear "run `@adk:setup`" message. Per the user note for this restructure: GitHub MCP is removed in favor of the simpler, faster, more capable `gh` CLI for all PR/issue/comment/merge/run/release operations.

## When to use

- Open a new PR for the current branch.
- Update an existing PR title, body, labels, reviewers, draft state.
- Post a comment (issue or PR) or reply in a thread.
- Request review from specific users / teams.
- Close, reopen, or merge a PR with a chosen strategy.
- Create or update an issue.
- Transition project board status (when GitHub Projects is in use).

## When NOT to use

- Drafting the message text -> `@adk:publish-commit` (a.k.a. `adk-publish-commit`)
- Reviewing the PR's content -> `@adk:review-pr` (a.k.a. `adk-review-pr`)
- Bitbucket destination -> `@adk:publish-bitbucket` (a.k.a. `adk-publish-bitbucket`)
- Confluence / Drive destination -> `@adk:publish-confluence` (a.k.a. `adk-publish-confluence`) / `@adk:publish-gdrive` (a.k.a. `adk-publish-gdrive`)

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
5. **Verify (per `publish-github-validator.md`)** - read back the artifact (`gh pr view`, `gh issue view`, MCP equivalent) to confirm the change landed (title matches, body matches, labels present, etc.).
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

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/publish-github-clarifying-questions.md`) and reports the choices.

1. **Action: pr-create / pr-update / pr-comment / pr-merge / pr-request-review / issue-create / issue-comment / label / status?** — _How to pick:_ Pick by destination + intent. pr-merge is special — always requires explicit gate even with --auto.
2. **Target: PR/issue number or URL?** — _How to pick:_ Required for actions that operate on an existing artifact.
3. **Body source: file path, inline draft, or auto-generate via adk-publish-commit?** — _How to pick:_ Prefer file path (drafted upstream). Auto-generate only when no body exists.

**Default report:** Action result URL + verification block (title/body/labels match expected) + tool used (gh / MCP).

**Detailed report (on request or `--verbose`):** Add: full command line, full read-back JSON, follow-up suggestions (request reviewers, link to release draft).

**Artifact:** `github-action-result` — The remote PR/issue/comment is the artifact. Locally: action log in .temp/notes/.

**Artifact path:** .temp/notes/publish-github-<action>-<target>.md

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/publish-github-clarifying-questions.md`) and reports the choices.

1. **Action: pr-create / pr-update / pr-comment / pr-merge / pr-request-review / issue-create / issue-comment / label / status?** — _How to pick:_ Pick by destination + intent. pr-merge is special — always requires explicit gate even with --auto.
2. **Target: PR/issue number or URL?** — _How to pick:_ Required for actions that operate on an existing artifact.
3. **Body source: file path, inline draft, or auto-generate via adk-publish-commit?** — _How to pick:_ Prefer file path (drafted upstream). Auto-generate only when no body exists.

## Default vs detailed output

**Default report:** Action result URL + verification block (title/body/labels match expected) + tool used (gh / MCP).

**Detailed report (on request or `--verbose`):** Add: full command line, full read-back JSON, follow-up suggestions (request reviewers, link to release draft).

**Artifact:** `github-action-result` — The remote PR/issue/comment is the artifact. Locally: action log in .temp/notes/.

**Artifact path:** .temp/notes/publish-github-<action>-<target>.md

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/publish-github-anti-patterns.md` | Things to avoid when running this skill. |
| `references/publish-github-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/publish-github-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/publish-github-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/publish-github-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/publish-github-mcp-fallback.md` | Preferred MCP server and the manual fallback when it is missing. |
| `references/publish-github-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/publish-github-persona.md` | The agent persona that drives this skill. |
| `references/publish-github-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/publish-github-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-publish, post-publish) this skill MUST run. |

<!-- adk:references:end -->


## Related skills

- [`publish`](./skill-publish.md) — `@adk:publish` (a.k.a. `adk-publish`)
- [`publish-bitbucket`](./skill-publish-bitbucket.md) — `@adk:publish-bitbucket` (a.k.a. `adk-publish-bitbucket`)
- [`publish-commit`](./skill-publish-commit.md) — `@adk:publish-commit` (a.k.a. `adk-publish-commit`)
- [`publish-confluence`](./skill-publish-confluence.md) — `@adk:publish-confluence` (a.k.a. `adk-publish-confluence`)
- [`publish-gdrive`](./skill-publish-gdrive.md) — `@adk:publish-gdrive` (a.k.a. `adk-publish-gdrive`)
- [`review-pr`](./skill-review-pr.md) — `@adk:review-pr` (a.k.a. `adk-review-pr`)
- [`setup`](./skill-setup.md) — `@adk:setup` (a.k.a. `adk-setup`)
