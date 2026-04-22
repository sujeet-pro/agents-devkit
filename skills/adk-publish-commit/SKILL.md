---
name: adk-publish-commit
description: Draft a commit message, PR description, or changelog entry from real git diff and history - matching the repo's existing convention, surfacing breaking changes, and flagging mixed concerns. Use when the deliverable is release-communication text grounded in actual changes. Do not use to push the change to a remote (use adk-publish-github / adk-publish-bitbucket) or to review the code itself (use adk-review-local).
---

# ADK Publish / Commit

Standalone task skill under the `adk-publish` category router. Produces accurate commit messages, PR descriptions, and changelog entries derived from real git state.

## When to use

- Drafting or creating a commit message from staged or unstaged changes.
- Writing a PR description from branch history.
- Generating a changelog entry from a range of commits.
- Surfacing breaking changes and validation status in release text.

## When NOT to use

- Reviewing the code itself -> `adk-review-local`
- Pushing the commit / opening the PR on a remote -> `adk-publish-github` / `adk-publish-bitbucket`
- Authoring project documentation -> `adk-docs-write`
- Planning implementation work -> `adk-plan-roadmap`

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<action>` | yes | `commit` (default) / `pr-describe` / `changelog` |
| `<convention>` | optional | `conventional` (default) / `plain` / `auto` (match the repo) |
| `<scope>` | optional | Path filter |
| `<range>` | optional | For `changelog`: `<base>..<head>` git range |
| `--auto` | optional | Skip confirmations; execute when applicable |

## Workflow

This is a quick-action skill. The workflow is intentionally lightweight.

1. **Inspect** - read real git state for the action:
   - `commit`: `git diff --cached` (staged) and `git diff` (unstaged).
   - `pr-describe`: `git log <base>..HEAD` and `git diff <base>...HEAD` for the branch.
   - `changelog`: `git log <range>` and per-commit subjects/bodies.
2. **Match repo convention** - read recent `git log` to detect convention (conventional commits, plain subjects, scoped prefixes). Use that, not personal preference.
3. **Classify** - identify change type (`feat`, `fix`, `refactor`, `docs`, `chore`, `perf`, `test`, `build`, `ci`, `revert`), scope, breaking changes, validation status.
4. **Draft** - write the smallest accurate text that explains *why* the change exists. Approval gate unless `--auto`.
5. **Validate (per `publish-commit-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/publish-commit-<slug>-validator.md` before the final report.
6. **Execute** -
   - `commit`: run `git commit -F <tmpfile>` with the approved message.
   - `pr-describe`: output the PR description as markdown (does not create the PR; that is `adk-publish-github` / `adk-publish-bitbucket`).
   - `changelog`: output the changelog entry as markdown (does not edit `CHANGELOG.md` unless the user asks).
6. **Verify** - confirm git state matches expectations after execution. Report any discrepancy.

## Conventional commit shape

```
<type>(<scope>): <subject>

<body>

BREAKING CHANGE: <description if applicable>

Refs: <issue-or-pr>
```

Subject rules:

- ~50-72 chars, imperative mood, no trailing period.
- Lowercase after the colon.
- Subject explains *what + why* in plain language.

Body rules (when present):

- Hard wrap at ~72 chars.
- Explain the *reasoning* and *non-obvious context*; do not restate the diff.
- Bullet structure when listing multiple non-trivial changes.

## PR description shape

```markdown
## Summary
- <bullet>
- <bullet>

## Why
<2-3 sentences>

## Changes
- <bullet>

## Validation
- <command> - PASS / FAIL / not-run with reason

## Breaking Changes
- <none, or list with migration note>

## Screenshots / Recordings
<if UI changes>

## Refs
- <issue / spec / ADR>
```

## Changelog shape (Keep a Changelog by default)

```markdown
## [<version>] - <YYYY-MM-DD>

### Added
- <bullet>

### Changed
- <bullet>

### Deprecated
- <bullet>

### Removed
- <bullet>

### Fixed
- <bullet>

### Security
- <bullet>
```

Match an existing `CHANGELOG.md` style if present (some repos use a different ordering or sectioning).

## Output format (commit)

```
## Proposed Commit Message
<rendered message>

## Rationale
- <type and scope justification>
- <key changes summarized>

## Validation
- [x] diff inspected
- [x] convention matched
- [<x|>] tests <run / not run with reason>

## Follow-up
- <push / tag / publish steps still needed>
```

## Output format (pr-describe)

```
## PR Description
<rendered markdown>

## Branch Stats
- Commits: <N>
- Files: <N> (+<add> / -<del>)
- Convention: <detected>
```

## Output format (changelog)

```
## Changelog Entry
<rendered markdown>

## Range
- <base>..<head>: <N> commits
```

## Hard rules

- Derive the text from actual diffs and history, not memory.
- Match the repo's existing convention; do not impose a new one.
- Never hide breaking changes; always surface them in subject footer or dedicated section.
- Flag mixed concerns and suggest splitting if the diff conflates unrelated changes.
- If validation status is unknown, say "not run" - do not claim "tests pass".

## Anti-patterns

- Generic messages ("update files", "fix stuff").
- Restating the diff in the body. Explain *why*, not *what*.
- Hiding a breaking change because the diff is small.
- Mixing concerns in one commit without surfacing it for a split.
- Claiming "all tests pass" without running them.
- Force-pushing as part of this skill. This skill drafts text only.

## Examples

```
adk-publish-commit --action commit
```

```
adk-publish-commit --action pr-describe --convention conventional
```

```
adk-publish-commit --action changelog --range v1.4.0..HEAD
```

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/publish-commit-clarifying-questions.md`) and reports the choices.

1. **What artifact: commit message, PR description, or changelog entry?** — _How to pick:_ Commit = single change. PR = aggregate of branch commits. Changelog = release-scoped summary.
2. **Convention: detect from git log, conventional commits, or project template?** — _How to pick:_ Default = detect from last 20 commits. Override only if the user states otherwise.
3. **Include co-authors / sign-off?** — _How to pick:_ Sign-off when DCO / project policy requires. Co-authors when pair-programmed (use Co-authored-by trailer).

**Default report:** Message draft (subject + body) + detected convention + breaking-change note.

**Detailed report (on request or `--verbose`):** Add: diff summary, recent-commit examples used to infer style, alternative subject lines, suggested labels.

**Artifact:** `commit-or-pr-message` — Markdown body file (`.temp/drafts/commit-<slug>.md` / `pr-<slug>.md`). Use `--body-file` when handing to publish-github/bitbucket.

**Artifact path:** .temp/drafts/commit-<slug>.md or .temp/drafts/pr-<slug>.md (passed to adk-publish-github/bitbucket --body-file)

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/publish-commit-clarifying-questions.md`) and reports the choices.

1. **What artifact: commit message, PR description, or changelog entry?** — _How to pick:_ Commit = single change. PR = aggregate of branch commits. Changelog = release-scoped summary.
2. **Convention: detect from git log, conventional commits, or project template?** — _How to pick:_ Default = detect from last 20 commits. Override only if the user states otherwise.
3. **Include co-authors / sign-off?** — _How to pick:_ Sign-off when DCO / project policy requires. Co-authors when pair-programmed (use Co-authored-by trailer).

## Default vs detailed output

**Default report:** Message draft (subject + body) + detected convention + breaking-change note.

**Detailed report (on request or `--verbose`):** Add: diff summary, recent-commit examples used to infer style, alternative subject lines, suggested labels.

**Artifact:** `commit-or-pr-message` — Markdown body file (`.temp/drafts/commit-<slug>.md` / `pr-<slug>.md`). Use `--body-file` when handing to publish-github/bitbucket.

**Artifact path:** .temp/drafts/commit-<slug>.md or .temp/drafts/pr-<slug>.md (passed to adk-publish-github/bitbucket --body-file)

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/publish-commit-anti-patterns.md` | Things to avoid when running this skill. |
| `references/publish-commit-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/publish-commit-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/publish-commit-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/publish-commit-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/publish-commit-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/publish-commit-persona.md` | The agent persona that drives this skill. |
| `references/publish-commit-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/publish-commit-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-publish, post-publish) this skill MUST run. |

<!-- adk:references:end -->
