---
name: self-review
description: Iterative self-review that reviews code, applies fixes, and runs lint/test/build until everything passes
user_invocable: true
arguments:
  - name: scope
    description: "What to review: staged, branch, files (default: branch — reviews all changes vs base branch)"
    required: false
  - name: base
    description: "Base branch to compare against (default: main)"
    required: false
  - name: max-iterations
    description: "Maximum review-fix-verify iterations (default: 5)"
    required: false
  - name: fix
    description: "Auto-fix mode: prompt, auto, dry-run (default: prompt). 'auto' applies fixes without asking. 'dry-run' shows fixes without applying."
    required: false
  - name: skip-validation
    description: "Skip lint/test/build validation (default: false)"
    required: false
---

# Self-Review Skill

> **Dependencies**: This skill works best with the full devkit installed (`/plugin install devkit-full@claude-devkit` or `./install.sh`). It uses guidelines from `guidelines/coding/` and delegates to the `code-reviewer` agent. If guidelines or agents are missing, the skill still works but uses built-in review heuristics instead.

Iterative code review that reviews your changes, applies fixes, and runs lint/test/build in a loop until everything is clean. Designed to be run before pushing — catches issues early and fixes them automatically.

## Agent & Skill Delegation

**Always use the devkit's own agents and skills:**

| Task | Delegate To |
|------|-------------|
| Code review | Spawn **code-reviewer** agent (multi-perspective review) |
| Research (unfamiliar patterns) | `/research` skill → **research-agent** |
| Diagram updates (if architecture changed) | `/diagram` skill → **diagram-agent** |

---

## Phase 1: Setup

### 1a. Determine scope

Based on `$ARGUMENTS.scope` (default: `branch`):

| Scope | What to review |
|-------|---------------|
| `branch` | All changes on current branch vs `$ARGUMENTS.base` (default: `main`) |
| `staged` | Only staged changes (`git diff --cached`) |
| `files` | Specific files (passed as additional args or detected from recent edits) |

```bash
# For branch scope
git diff $(git merge-base HEAD origin/$BASE)..HEAD --name-only

# For staged scope
git diff --cached --name-only

# Get the full diff
git diff $(git merge-base HEAD origin/$BASE)..HEAD   # branch
git diff --cached                                      # staged
```

### 1b. Detect project validation commands

Look for validation commands in this order of precedence:

**1. Repo-level CLAUDE.md instructions** — Check the project's `CLAUDE.md` for a validation section:

```markdown
## Validation

- lint: `npm run lint`
- test: `npm run test`
- build: `npm run build`
- typecheck: `npx tsc --noEmit`
```

The CLAUDE.md may define these under headings like `## Validation`, `## CI`, `## Commands`, `## Development`, or `## Testing`. Look for keywords: lint, test, build, typecheck, check, verify, validate.

**2. Package manager / build system detection** — Auto-detect from project files:

| File | Lint | Test | Build | Typecheck |
|------|------|------|-------|-----------|
| `package.json` | `npm run lint` | `npm test` | `npm run build` | `npx tsc --noEmit` (if tsconfig exists) |
| `Makefile` / `Justfile` | `make lint` | `make test` | `make build` | — |
| `pyproject.toml` (ruff/flake8) | `ruff check .` | `pytest` | — | `mypy .` |
| `pom.xml` | `mvn checkstyle:check` | `mvn test` | `mvn package` | — |
| `build.gradle` | `./gradlew check` | `./gradlew test` | `./gradlew build` | — |
| `Cargo.toml` | `cargo clippy` | `cargo test` | `cargo build` | — |
| `go.mod` | `golangci-lint run` | `go test ./...` | `go build ./...` | — |

For `package.json`, also check for specific script names:
```bash
jq -r '.scripts | keys[]' package.json
```
Prefer existing scripts like `lint`, `lint:fix`, `test`, `test:unit`, `build`, `typecheck`, `type-check`, `check`.

**3. CI config detection** — If no local commands found, parse CI configs for validation steps:
- `.github/workflows/*.yml` — look for `run:` commands
- `bitbucket-pipelines.yml` — look for `script:` commands
- `.gitlab-ci.yml` — look for `script:` commands
- `Jenkinsfile` — look for `sh` commands

Store the detected commands:
```
LINT_CMD = detected lint command (or null)
TEST_CMD = detected test command (or null)
BUILD_CMD = detected build command (or null)
TYPECHECK_CMD = detected typecheck command (or null)
```

### 1c. Present plan

Show the user what will happen:

```
## Self-Review Plan

**Scope**: branch (vs main)
**Changed files**: 12 files
**Max iterations**: 5
**Fix mode**: prompt

**Validation commands detected**:
- Lint: `npm run lint`
- Test: `npm test`
- Build: `npm run build`
- Typecheck: `npx tsc --noEmit`

Proceed? (yes / adjust commands / skip validation)
```

If the user wants to adjust commands, accept their overrides.

---

## Phase 2: Initial Validation Run

Before reviewing code, run all validation commands to establish a baseline. This tells us what's already broken vs what the review introduces.

### 2a. Run validation commands

Run each detected command and capture output + exit code:

```bash
# Run lint
$LINT_CMD 2>&1; echo "EXIT:$?"

# Run typecheck
$TYPECHECK_CMD 2>&1; echo "EXIT:$?"

# Run tests (only tests related to changed files if possible)
$TEST_CMD 2>&1; echo "EXIT:$?"

# Run build
$BUILD_CMD 2>&1; echo "EXIT:$?"
```

### 2b. Record baseline

For each command, record:
- Pass/fail status
- Error output (if failed)
- Number of warnings/errors

This baseline is used later to distinguish pre-existing failures from regressions.

---

## Phase 3: Code Review (Iteration Loop)

This is the core iterative loop. Each iteration:
1. Reviews the code
2. Proposes fixes
3. Applies fixes (based on fix mode)
4. Re-runs validation
5. Checks if done or needs another iteration

```
iteration = 0
max_iterations = $ARGUMENTS.max-iterations ?? 5

while iteration < max_iterations:
    iteration += 1
    review_and_fix()
    if all_clean(): break
```

### 3a. Review the code

Read the current diff and spawn a review using the **code-reviewer** agent pattern. The review covers:

**Code quality review:**
- Logic errors and bugs
- Security vulnerabilities
- Performance issues
- Error handling gaps
- Type safety issues
- Code style and conventions (based on loaded guidelines)

**Guideline compliance:**
Load guidelines from `~/.claude/guidelines/coding/` based on detected repo type (same detection as `/pr-review` Phase 1d).

**Diff-aware review:**
- Only review changed lines and their immediate context
- Don't flag pre-existing issues in unchanged code
- Consider the intent from commit messages

### 3b. Categorize findings

Group findings into:

| Category | Action |
|----------|--------|
| **Auto-fixable** | Can be fixed with a code edit (style, imports, simple bugs) |
| **Needs human decision** | Multiple valid approaches, architectural choices |
| **Validation failures** | Lint/test/build errors from Phase 2 that relate to changed code |
| **Pre-existing** | Issues that exist in the base branch (skip unless directly related) |

### 3c. Present findings

Display findings grouped by file:

```
## Iteration 1 — Review Results

### Auto-fixable (7 findings)
1. [WARNING] src/api/handler.ts:42 — Unhandled promise rejection
2. [WARNING] src/utils/parse.ts:18 — Missing null check
3. [SUGGESTION] src/api/handler.ts:55 — Unused import
...

### Needs Decision (2 findings)
1. [QUESTION] src/models/user.ts:30 — Should this use soft delete or hard delete?
2. [SUGGESTION] src/api/routes.ts:12 — Consider splitting this route handler

### Validation Failures (3 issues)
1. [LINT] src/api/handler.ts:42 — no-floating-promises
2. [TEST] tests/api/handler.test.ts — "should handle errors" failing
3. [TYPECHECK] src/utils/parse.ts:18 — Type 'string | undefined' not assignable to 'string'
```

### 3d. Apply fixes

Based on `$ARGUMENTS.fix`:

**`prompt` (default):**
- Show each auto-fixable finding with the proposed fix
- Ask: `Apply this fix? (yes/no/edit/all)` — `all` applies remaining without prompting
- For "needs decision" findings, present options and ask

**`auto`:**
- Apply all auto-fixable findings immediately
- Skip "needs decision" findings (report them at the end)
- Log every change made

**`dry-run`:**
- Show all proposed fixes without applying
- No code modifications

### 3e. Re-run validation

After fixes are applied, re-run all validation commands:

```bash
$LINT_CMD 2>&1
$TYPECHECK_CMD 2>&1
$TEST_CMD 2>&1
$BUILD_CMD 2>&1
```

### 3f. Check convergence

The iteration loop stops when ANY of these conditions are met:

| Condition | Meaning |
|-----------|---------|
| All validation passes AND no new review findings | **Clean** — done |
| `iteration >= max_iterations` | **Max iterations reached** — report remaining issues |
| No fixes were applied this iteration | **Stuck** — remaining issues need human intervention |
| Only "needs decision" findings remain | **Human input needed** — report and stop |

If the loop continues, go back to 3a with the updated code.

---

## Phase 4: Final Validation

After the iteration loop completes (or exits early), run a final comprehensive validation:

```bash
# Full lint (not just changed files)
$LINT_CMD

# Full test suite
$TEST_CMD

# Full build
$BUILD_CMD

# Full typecheck
$TYPECHECK_CMD
```

Record final pass/fail status for each.

---

## Phase 5: Report

Present a final summary:

```
## Self-Review Complete

**Iterations**: 3 of 5
**Fix mode**: prompt

### Validation Status
| Check | Before | After |
|-------|--------|-------|
| Lint | FAIL (4 errors) | PASS |
| Tests | FAIL (1 failing) | PASS |
| Build | PASS | PASS |
| Typecheck | FAIL (2 errors) | PASS |

### Changes Made
- Fixed 7 code issues across 4 files
- All auto-fixable findings resolved

### Remaining Issues (need human decision)
1. [QUESTION] src/models/user.ts:30 — Soft delete vs hard delete
2. [SUGGESTION] src/api/routes.ts:12 — Route handler splitting

### Files Modified
- src/api/handler.ts (3 fixes)
- src/utils/parse.ts (2 fixes)
- src/models/user.ts (1 fix)
- tests/api/handler.test.ts (1 fix)
```

If all validation passes and no remaining issues:

```
All checks pass. Ready to push.
```

---

## Phase 6: Stage Changes (optional)

If fixes were applied, offer to stage the changes:

```
Stage all modified files? (yes/no/pick)
```

- `yes` — `git add` all modified files
- `no` — Leave unstaged
- `pick` — Show files and let user choose

---

## Validation Command Configuration

Projects should define their validation commands in `CLAUDE.md` for best results:

```markdown
## Validation

Commands to run for self-review validation:

- lint: `npm run lint`
- lint-fix: `npm run lint -- --fix`
- test: `npm test`
- test-related: `npx jest --findRelatedTests`
- build: `npm run build`
- typecheck: `npx tsc --noEmit`
```

The `lint-fix` command is used during auto-fix iterations. The `test-related` command (if available) runs only tests related to changed files for faster iteration.

---

## Flaky Test Detection

During iterations, if a test fails, apply these heuristics before treating it as a real failure:

| Signal | Likely Flaky | Action |
|--------|-------------|--------|
| Test passes on re-run with no code changes | Yes | Mark as flaky, skip in iteration loop |
| Test fails consistently across 2+ runs | No | Treat as real failure, investigate |
| Test involves timing, network, or randomness | Likely | Re-run up to 2x before treating as real |
| Test was already failing in baseline (Phase 2) | Pre-existing | Skip unless directly related to changes |

If a test is identified as flaky, report it at the end but do not block the iteration loop.

## Rules

1. **Never break working code.** If a fix introduces a new test failure or build error, revert it immediately and report the issue.
2. **Preserve intent.** Fixes should address the issue without changing the developer's intended behavior. When in doubt, ask.
3. **Minimal changes.** Each fix should be the smallest change that resolves the issue. Don't refactor surrounding code.
4. **Track every change.** Log every edit made so the developer can review what was auto-fixed.
5. **Respect fix mode.** In `prompt` mode, always ask. In `dry-run` mode, never modify. In `auto` mode, only fix clear-cut issues.
6. **Don't loop forever.** If the same issue reappears after being fixed, it needs human intervention. Stop and report.
7. **Distinguish regressions from pre-existing.** Only fix issues in changed code. Don't fix pre-existing lint errors in untouched files.
8. **Test isolation.** When running tests, prefer running only related tests during iterations (faster feedback). Run the full suite only in Phase 4.
9. **Validation order matters.** Run in this order: typecheck → lint → test → build. Fix type errors first since they often cascade into other failures.
10. **Flaky test awareness.** Re-run intermittent failures before treating as real. Report identified flaky tests separately.
