---
name: dev-worktree
description: Use when you need an isolated workspace before implementation, review, or plan execution
---

# Using Git Worktrees

Create an isolated workspace before risky or long-running work.

## Checks

- choose a worktree directory that will not be committed accidentally
- ensure the directory is ignored when it lives inside the repo
- pair this with plan execution or child-agent workflows when parallel work is expected
