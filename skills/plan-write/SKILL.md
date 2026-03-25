---
name: plan-write
description: Use when turning requirements into an execution plan that can be carried out by engineers or child-agent teams with minimal ambiguity
---

# Writing Plans

Plans should be executable by a human or by DevKit child-agent teams.

## Plan Storage

Save all plans to `.temp/plans/<plan-id>.md` in the current working directory. If `.temp/` does not exist, create it and ensure it is listed in `.gitignore`.

Use this plan file format:

```markdown
---
plan_id: <short-id>
created: <ISO-8601>
updated: <ISO-8601>
skill: <skill-that-created-this>
status: draft | approved | in-progress | completed
---

# <Plan Title>

## Context
<Why this plan exists, what triggered it>

## Tasks

- [ ] Task 1: <description>
  - Files: <exact paths>
  - Verification: <command or check>
- [ ] Task 2: <description>
  ...
```

## Plan Requirements

- exact files and responsibilities per task
- clear task boundaries so tasks can be parallelized
- verification commands for each task
- docs and migration follow-ups
- review checkpoints after groups of related tasks

## Review Loop

After drafting the plan, run a child-agent review pass on the plan itself before execution. The reviewer should check for gaps, missing dependencies, and unclear ownership.
