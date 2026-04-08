# Worktree Mode

Create isolated git worktrees for feature work that needs isolation from the current workspace. Systematic directory selection and safety verification ensure reliable isolation.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

## Workflow

This stage uses the **Quick Action** workflow: confirm → execute → verify.

## Exploration Guidance

Detect the right directory for worktrees:

1. **Check existing directories**: `.worktrees/` (preferred), `worktrees/`
2. **Check CLAUDE.md** for worktree directory preference
3. **Ask user** if no directory exists and no preference found

## Execution Instructions

### Directory Selection

| Situation | Action |
|-----------|--------|
| `.worktrees/` exists | Use it (verify ignored) |
| `worktrees/` exists | Use it (verify ignored) |
| Both exist | Use `.worktrees/` |
| Neither exists | Check CLAUDE.md then ask user |
| Directory not ignored | Add to .gitignore + commit |

### Safety Verification

For project-local directories, verify the directory is git-ignored:
```bash
git check-ignore -q .worktrees 2>/dev/null
```

If NOT ignored: add to `.gitignore` and commit before proceeding.

### Creation Steps

1. **Detect project name**: `project=$(basename "$(git rev-parse --show-toplevel)")`
2. **Create worktree**: `git worktree add "$path" -b "$BRANCH_NAME"`
3. **Run project setup**: auto-detect from project files (package.json, Cargo.toml, etc.)
4. **Verify clean baseline**: run tests to ensure worktree starts clean

If tests fail, report failures and ask whether to proceed or investigate.

### Report

```
Worktree ready at <full-path>
Tests passing (<N> tests, 0 failures)
Ready to implement <feature-name>
```

## Validation Criteria

1. Worktree exists at expected path
2. Directory is git-ignored (project-local)
3. Dependencies installed
4. Tests passing (or failures reported and acknowledged)
5. Clean git status in worktree

## Output Format

```markdown
## Worktree Created

Branch: <branch-name>
Location: <full-path>
Tests: <pass count> passing, <fail count> failing
Status: ready | needs attention

### Setup
- Dependencies: installed
- Baseline tests: passing
```
