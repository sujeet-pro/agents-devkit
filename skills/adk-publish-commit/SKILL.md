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
5. **Execute** -
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

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |

<!-- adk:references:end -->
