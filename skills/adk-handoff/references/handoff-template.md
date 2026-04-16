# Handoff Template

Use this template when creating handoff documents. Fill every section. If a section has no content, write "None" rather than omitting it.

---

## Task
<!-- One-sentence description of what is being worked on and the end goal. -->

**Goal:** [what success looks like]

## Current State

### Done
<!-- Completed items. Use checkboxes. -->
- [x] item

### In Progress
<!-- Items started but not finished. -->
- [ ] item -- [notes on current state]

### Not Started
<!-- Items planned but not yet begun. -->
- [ ] item

## Decisions Made
<!-- Each decision that was made during the session. Include rationale so the reader does not revisit settled questions. -->

| Decision | Rationale |
| --- | --- |
| [what was decided] | [why] |

## Remaining Work
<!-- Ordered by priority. Each item must be a concrete, actionable step. -->

1. [highest priority item]
2. [next item]
3. [next item]

## Blockers and Open Questions
<!-- Anything preventing progress. Be specific enough that someone can act on it. -->

- **Blocker:** [description] -- [what is needed to unblock]
- **Question:** [description] -- [who or what can answer it]

## Key Files
<!-- Files created, modified, or deleted during the session. -->

| File | Status | Notes |
| --- | --- | --- |
| `path/to/file` | created/modified/deleted | [brief note] |

## Git State
<!-- Captured automatically by handoff.py. Do not edit manually unless the script was not run. -->

- **Branch:** [branch name]
- **Uncommitted changes:** [yes/no, summary]
- **Staged files:** [list or "none"]
- **Recent commits:**
  - `abc1234` [commit message]
  - `def5678` [commit message]

## Environment Notes
<!-- Runtime versions, config, setup steps, or anything needed to reproduce the current state. -->

- [e.g., Python 3.11, Node 20, specific env vars]

## Next Immediate Step
<!-- The single most important thing the next session should do first. -->

[action]

## Resumption Checklist
<!-- Quick checks before resuming work. -->
- [ ] on the correct branch
- [ ] no unexpected uncommitted changes
- [ ] dependencies installed
- [ ] tests pass (or known failures documented above)
- [ ] read the "Decisions Made" section to avoid re-litigating
