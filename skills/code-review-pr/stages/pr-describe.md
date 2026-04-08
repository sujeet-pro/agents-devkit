# PR Describe Stage

Generate or update a PR description from the actual diff, commits, and docs impact. The description serves two audiences: **human reviewers** who need to understand context, risk, and how to test; and **agent reviewers** who need structured metadata to scope their analysis.

---

## Workflow

### Step 1: Read PR

Fetch metadata, diff, and commit history through the source MCP or API fallback.

### Step 2: Check for Template

If `style` is not specified, check for `.github/pull_request_template.md` or equivalent. Load the template if found and merge its sections with the generated content.

### Step 3: Launch Child Agents

Run in parallel:

- **Diff analyzer** (`adk-code-reviewer`): reads the full diff and commit history. Identifies what changed, categorizes changes (feature, fix, refactor, test, docs), assesses risk areas, and flags breaking changes or rollback considerations.
- **Docs impact reviewer** (`adk-doc-reviewer`): checks whether the changes affect documentation, migration notes, API contracts, or configuration.

### Step 4: Draft Description

Compose the PR description based on `style`:

- **concise** (default): structured summary with metadata block and bullet points
- **detailed**: full sections with what, why, key decisions, risk, testing, deployment, docs, follow-ups
- **conventional**: conventional commit format with scope and type, plus a metadata block

### Step 5: Present for Review

Show the drafted description to the user for approval or editing before publishing.

### Step 6: Publish

Post through the MCP or API, or output as markdown based on `publish`.

---

## Description Content

Every PR description must answer these questions for both human and agent reviewers:

| Question | For Humans | For Agents |
|----------|-----------|-----------|
| What changed? | Narrative summary with key files | Structured `Areas` list with file paths |
| Why? | Motivation, linked issues, context | Change type classification |
| What decisions were made? | Key trade-offs explained | Approach rationale for alignment checking |
| What's risky? | Breaking changes, edge cases | Risk level, rollback steps |
| How do I verify it works? | Step-by-step test instructions | Verification commands |
| What needs to happen at deploy? | Feature flags, migrations, config | Deployment checklist |
| What's left? | Follow-up items, known gaps | Open items for tracking |

---

## Metadata Block

Every PR description starts with a structured metadata block. This block is parseable by both humans and agents.

```md
| Key | Value |
|-----|-------|
| **Type** | feature / fix / refactor / test / docs / chore |
| **Risk** | low / medium / high |
| **Breaking** | yes / no |
| **Areas** | `src/auth/`, `src/middleware/` |
| **Dependencies** | new: `zod@3.22` / removed: `joi` / upgraded: `express@5` |
| **Linked issues** | #123, #456 |
```

---

## Style Examples

### Concise

````md
## Summary

| Key | Value |
|-----|-------|
| **Type** | fix |
| **Risk** | low |
| **Breaking** | no |
| **Areas** | `src/handlers/user.ts`, `src/routes/orders.ts` |
| **Linked issues** | #123 |

### Changes

- Add user profile validation before accessing `profile.id`
- Fix N+1 query in order list endpoint with eager loading
- Update API docs for the new validation behavior
- Add tests for missing profile edge case

### How to test

1. Create a user without a profile via the lightweight signup flow
2. Hit `GET /api/users/:id` — should return 400 instead of 500
3. Hit `GET /api/orders` with 50+ orders — verify response time is stable
````

### Detailed

````md
## Summary

| Key | Value |
|-----|-------|
| **Type** | feature |
| **Risk** | medium |
| **Breaking** | yes — `GET /api/users/:id` now returns 400 for profileless users (previously 500) |
| **Areas** | `src/handlers/`, `src/routes/`, `src/middleware/` |
| **Dependencies** | none |
| **Linked issues** | #123, #456 |

### What changed

<Narrative description of changes with file references and line-level detail for significant modifications.>

### Why

<Motivation and context. Link to the issue, spec, ADR, or conversation that drove this change. Explain what was wrong or missing before.>

### Key decisions

<Architectural or design choices made during implementation. Explain the trade-offs considered and why this approach was chosen over alternatives. This helps reviewers evaluate the approach rather than suggesting a completely different one.>

- **Decision 1**: chose X over Y because <rationale>
- **Decision 2**: kept existing pattern Z to minimize disruption

### Risk and rollback

<Breaking changes with migration path. Edge cases that need attention. Rollback steps if the change needs to be reverted.>

- **Breaking**: `GET /api/users/:id` returns 400 for profileless users
- **Rollback**: revert this PR; no data migration involved
- **Edge case**: legacy users with partial profile data — handled by guard in `user.ts:47`

### How to test

<Step-by-step instructions a reviewer can follow to verify the changes work correctly. Include setup steps, specific inputs, and expected outputs.>

1. **Setup**: `npm run seed:test-users` to create test fixtures
2. **Happy path**: `GET /api/users/1` with a complete profile — returns 200 with profile data
3. **Missing profile**: `GET /api/users/99` (profileless user) — returns 400 with `"profile is required"`
4. **Performance**: `GET /api/orders?limit=100` — verify response under 200ms (was 2s+ before)
5. **Run tests**: `npm test -- --grep "user|order"`

### Deployment notes

<Feature flags, config changes, database migrations, or infrastructure requirements that must happen at deploy time.>

- No database migration required
- No feature flags needed
- No config changes

### Tests

<Test coverage summary. New tests added, existing tests modified, coverage delta.>

- Added: 3 unit tests for profile validation edge cases
- Modified: order list test to verify query count
- Coverage: `src/handlers/user.ts` 94% -> 98%

### Docs impact

<Documentation that needs updating as a result of this change.>

- API docs: updated `GET /api/users/:id` response codes
- No migration guide needed

### Follow-up

<Remaining work, known issues, or items deferred from this PR.>

- [ ] Add rate limiting to the user endpoint (#457)
- [ ] Consider batch profile backfill for legacy users (#458)

### Self-review checklist

- [x] Tests pass locally
- [x] No new warnings or linting errors
- [x] Breaking change documented in description
- [x] Edge cases covered in tests
- [ ] Performance verified under load (deferred to staging)
````

### Conventional

````md
fix(auth): add profile validation before accessing profile.id

| Key | Value |
|-----|-------|
| **Type** | fix |
| **Risk** | low |
| **Breaking** | no |
| **Areas** | `src/handlers/user.ts` |
| **Linked issues** | Closes #123 |

- Guard `user.profile` before dereferencing
- Add `BadRequestError` for missing profile
- Update related tests

**How to test:** create a profileless user, hit `GET /api/users/:id`, expect 400.
````

---

## Summary

```text
## PR Description Updated

Style: <concise|detailed|conventional>
Template: <used|none>
Metadata: <generated>
Published: [yes | markdown only]
```
