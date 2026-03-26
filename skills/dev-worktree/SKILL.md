---
name: dev-worktree
description: Use when you need an isolated workspace before implementation, review, or plan execution
user_invocable: true
arguments:
  - name: branch
    description: "Branch name for the worktree"
    required: true
  - name: base
    description: "Base branch to create from (default: current branch)"
    required: false
---

# Using Git Worktrees

Use `skills/_references/preflight-validations.md`.

Create an isolated workspace for risky, long-running, or parallel work without affecting the main working directory.

## Preflight

Before creating a worktree, run:

`zsh scripts/check-skill-deps.zsh dev-worktree`

Verify that:

- the current directory is a git repository
- the requested branch name does not already exist (unless reattaching to an existing worktree)
- the worktree target directory does not already exist

## Workflow

1. **Choose location.** Select a worktree directory outside the main repository tree to avoid accidental commits. Default: `../<repo-name>-worktrees/<branch>`.
2. **Create worktree.** Run `git worktree add <path> -b <branch> <base>` to create the isolated workspace.
3. **Verify isolation.** Confirm the worktree has its own working directory and `.git` file pointing to the main repository.
4. **Execute work.** Perform implementation, review, or plan execution in the worktree directory. Pair with `/devkit:plan-execute` or `/devkit:dev-implement` for structured work.
5. **Commit results.** Commit all changes in the worktree as normal.
6. **Clean up.** When done, return to the main working directory. Remove the worktree with `git worktree remove <path>` after merging or pushing the branch.

## Rules

- Choose a worktree directory that will not be committed accidentally.
- Ensure the directory is in `.gitignore` if it lives inside the repo.
- Do not delete worktree directories manually — use `git worktree remove` to keep git's worktree registry clean.
- Run `git worktree list` to see all active worktrees.
- Run `git worktree prune` to clean up stale worktree references.

## Output

```
## Worktree Created

Path: <worktree path>
Branch: <branch name>
Base: <base branch>

To work in this worktree:
  cd <worktree path>

To clean up when done:
  git worktree remove <worktree path>
```

## Adjacent Skills

- `/devkit:dev-implement` for feature implementation in the worktree
- `/devkit:plan-execute` for plan execution in an isolated workspace
- `/devkit:pr-finalize` to finalize the branch after worktree work
