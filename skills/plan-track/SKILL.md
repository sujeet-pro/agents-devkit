---
name: plan-track
description: Use when you need to monitor, report on, or update the status of one or more execution plans
user_invocable: true
arguments:
  - name: plan
    description: "Path to a specific plan file (default: scan all plans in .temp/plans/)"
    required: false
  - name: format
    description: "Output format: markdown, json (default: markdown)"
    required: false
---

# Plan Tracking

## Plan Location

Look for plans in `.temp/plans/` in the current working directory. If `plan` is provided, use that specific file instead.

## Flow

### 1. Discover Plans

- If `plan` is provided, load that single file
- Otherwise, scan `.temp/plans/*.md` for all plan files
- If no plans are found, report that and suggest `/devkit:plan-write` to create one

### 2. Parse Each Plan

For each plan file, extract:

- **Plan ID** and **title** from frontmatter and heading
- **Status** from frontmatter (`draft`, `approved`, `in-progress`, `completed`)
- **Created** and **updated** timestamps
- **Total steps**: count all task lines (`- [ ]` and `- [x]`)
- **Completed steps**: count checked lines (`- [x]`)
- **In-progress steps**: steps with explicit in-progress markers or the first unchecked step after a completed one
- **Blocked steps**: steps with `BLOCKED` or `blocked` annotations

### 3. Identify Blockers and Risks

For each plan, flag:

- Steps annotated as blocked, with the blocking reason
- Plans where no progress has been made since the last `updated` timestamp
- Plans with a stale `in-progress` status but no recent updates
- Steps that depend on external actions (MCP calls, PR merges, approvals)

### 4. Calculate Progress

For each plan:

- Progress percentage: `(completed / total) * 100`
- Estimated remaining work based on step count
- Timeline analysis if timestamps are available on individual steps

### 5. Present Dashboard

Output a progress dashboard:

```
## Plan Progress Dashboard

### <Plan Title> (`<plan-id>`)
Status: <status> | Progress: <N>/<total> (<percentage>%)
Updated: <timestamp>

[====================----------] 67%

#### Completed
- [x] Task 1: <description>
- [x] Task 2: <description>

#### Remaining
- [ ] Task 3: <description>
- [ ] Task 4: <description>

#### Blockers
- Task 5: BLOCKED -- <reason>

---
(repeat for each plan)

### Summary
| Plan | Status | Progress | Blockers | Last Updated |
|------|--------|----------|----------|--------------|
| <name> | <status> | <pct>% | <count> | <date> |
...
```

### 6. Suggest Resolutions

For each blocker found, suggest concrete resolution actions:

- If blocked on an external dependency, suggest checking its status
- If blocked on a review, suggest dispatching a review child agent
- If stale, suggest resuming with `/devkit:plan-execute`

### 7. Update Stale Status

If a plan's status field does not match its actual progress, update it:

- All steps done but status is not `completed` -> set `status: completed`
- Some steps done but status is `draft` -> set `status: in-progress`
- Update the `updated` timestamp when making status corrections

## Adjacent Skills

- `/devkit:plan-write` to create new plans
- `/devkit:plan-execute` to resume or execute plans
