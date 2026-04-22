# `validate-browser` — verify-fix repro format

A markdown file describing the original bug + the assertion that proves the fix.

```markdown
# Bug: Dashboard shows 0 active users since 13:00

**URL:** http://localhost:5173/dashboard
**Bug since:** 2026-04-22 13:00 UTC
**Linked:** JIRA-1234, Slack thread C123/p1745...

## Repro steps
1. Navigate to /dashboard
2. Wait for the "Active users" tile to load
3. Observe value

## Original (buggy) behavior
- Tile shows "0"
- Console error: `Uncaught TypeError: Cannot read properties of undefined (reading 'is_active')` from `userCount.ts:42`

## Expected (post-fix) behavior
- Tile shows a non-zero integer
- No console error matching the pattern above
- DOM: `[data-testid="active-users-value"]` text matches `/^\d+$/` and is > 0

## Assertion regex (used by verify-fix)
- console-error MUST NOT match: `is_active.*undefined`
- DOM `[data-testid="active-users-value"]` text MUST match: `^\d+$` and value > 0
```

The skill reads this file, walks the repro steps, captures console + DOM state, and asserts the post-fix conditions.
