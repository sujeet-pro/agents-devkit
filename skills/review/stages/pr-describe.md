# PR Describe Stage

Generate or update a PR description from the actual diff, commits, and docs impact.

---

## Workflow

### Step 1: Read PR

Fetch metadata, diff, and commit history through the source MCP or API fallback.

### Step 2: Check for Template

If `style` is not specified, check for `.github/pull_request_template.md` or equivalent. Load the template if found.

### Step 3: Launch Child Agents

Run in parallel:

- **Diff analyzer** (`code-reviewer`): reads the full diff and commit history. Identifies what changed, categorizes changes (feature, fix, refactor, test, docs), assesses risk areas, and flags breaking changes or rollback considerations.
- **Docs impact reviewer** (`doc-reviewer`): checks whether the changes affect documentation, migration notes, API contracts, or configuration.

### Step 4: Draft Description

Compose the PR description based on `style`:

- **concise** (default): 3-5 bullet points covering what and why
- **detailed**: full sections with what, why, risk, tests, docs, follow-ups
- **conventional**: follows conventional commit format with scope and type

### Step 5: Present for Review

Show the drafted description to the user for approval or editing before publishing.

### Step 6: Publish

Post through the MCP or API, or output as markdown based on `publish`.

---

## Description Content

A PR description containing:

- **What changed**: summary of code changes with key files
- **Why**: motivation and context
- **Risk and rollback**: breaking changes, deployment notes, rollback steps if applicable
- **Tests and docs impact**: test coverage, docs updates needed
- **Follow-up items**: remaining work or known issues

---

## Style Examples

### Concise

```md
## Summary

- Add user profile validation before accessing profile.id
- Fix N+1 query in order list endpoint with eager loading
- Update API docs for the new validation behavior
- Add tests for missing profile edge case
```

### Detailed

```md
## What changed

<detailed description of changes with file references>

## Why

<motivation, context, related issues>

## Risk and rollback

<breaking changes, deployment considerations, rollback steps>

## Tests

<test coverage, new tests added>

## Docs impact

<documentation updates needed>

## Follow-up

<remaining work, known issues>
```

### Conventional

```md
fix(auth): add profile validation before accessing profile.id

- Guard user.profile before dereferencing
- Add BadRequestError for missing profile
- Update related tests

Closes #123
```

---

## Summary

```text
## PR Description Updated

Style: <concise|detailed|conventional>
Template: <used|none>
Published: [yes | markdown only]
```
