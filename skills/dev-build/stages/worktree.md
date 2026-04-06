# Worktree Mode

Create isolated git worktrees for feature work that needs isolation from the current workspace. Systematic directory selection and safety verification ensure reliable isolation.

**Core principle:** Systematic directory selection + safety verification = reliable isolation.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Detect directory preference, verify git state; No proposal needed |
| 2. Approach Selection | skip | Worktree creation follows a fixed process; No iteration needed |
| 3. Planning | skip | Single setup operation |
| 4. Execute | yes | Create worktree, install deps, verify baseline |
| 5. Validate & Learn | yes | Verify clean baseline, report location |

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
