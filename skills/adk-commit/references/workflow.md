# ADK Commit Workflow

This is a **quick-action** workflow. It is designed to be fast and lightweight while maintaining accuracy.

## Phase 1: Inspect

**Goal**: establish the facts from the actual repository state.

**Steps by action**:

### `commit`
1. Run `git diff --cached` to read staged changes.
2. Run `git diff` to read unstaged changes for context.
3. Run `git status` to understand the overall working tree state.
4. If `--scope` is set, filter the diff to the specified path.

### `pr-describe`
1. Detect the base branch (look for `main`, `master`, `develop`, or the upstream tracking branch).
2. Run `git log base..HEAD` to read branch commit history.
3. Run `git diff base..HEAD` to read the aggregate diff.
4. If `--scope` is set, filter to the specified path.

### `changelog`
1. Determine the commit range (tags, branch points, or explicit range).
2. Run `git log <range>` with `--oneline` and full format.
3. If `--scope` is set, filter to the specified path.

**Edge cases**:
- No staged changes for `commit`: warn and ask whether to stage all or abort.
- Detached HEAD: note the state explicitly in the output.
- Merge commits in the range: include or exclude based on convention (default: exclude).

## Phase 2: Classify

**Goal**: categorize the change for accurate messaging.

**Steps**:
1. Identify the primary change type: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`, `build`, `style`.
2. Determine the scope (module, package, or area most affected).
3. Detect breaking changes: API signature changes, removed exports, schema migrations, changed defaults.
4. Check for mixed concerns: does the diff touch unrelated areas?
5. Surface validation gaps: are there test changes? Are tests passing?

**Convention detection**:
- Check for `.commitlintrc`, `.czrc`, `.conventional-changelog` config.
- Scan recent `git log --oneline -20` for patterns.
- If no convention is detected and `--convention` is not set, default to conventional commits.

**Edge cases**:
- Multiple change types in one diff: use the most significant type for the subject; list others in the body.
- Breaking change in a `fix` or `refactor`: the breaking change footer is mandatory regardless of type.

## Phase 3: Draft

**Goal**: write the smallest accurate message or description.

### Commit message structure
```
<type>(<scope>): <subject>

<body - only if needed>

BREAKING CHANGE: <description if applicable>
```

### PR description structure
```markdown
## Summary
<1-3 sentences>

## Key Changes
- <change 1>
- <change 2>

## Breaking Changes
<if any, with migration steps>

## Test Status
<what was tested, what was not>

## Follow-up
<remaining work, if any>
```

### Changelog structure
```markdown
### <version or range>

#### Features
- <feat 1>

#### Fixes
- <fix 1>

#### Breaking Changes
- <breaking change with migration>
```

**Gate**: present the draft for user approval. Skip if `--auto`.

**Edge cases**:
- User rejects the draft: ask for specific feedback, revise, re-present.
- User provides their own message: validate it against the diff (flag mismatches) but respect the user's choice.

## Phase 4: Execute

**Goal**: perform the git operation or output the artifact.

### `commit`
1. Run `git commit -m "<approved message>"`.
2. Capture the output (commit hash, branch, files changed).

### `pr-describe`
1. Output the PR description in markdown.
2. Do not create the PR (that is the user's or CI's job).

### `changelog`
1. Output the changelog entry in markdown.
2. Optionally write to `CHANGELOG.md` if the user confirms.

**Edge cases**:
- Commit hook failure (pre-commit, commit-msg): report the hook output, suggest fixes, do not retry automatically.
- Amend requests: only amend if the user explicitly asks and the commit has not been pushed.

## Phase 5: Verify

**Goal**: confirm the result matches expectations.

### `commit`
1. Run `git log -1 --format='%s'` to verify the committed message.
2. Run `git status` to confirm clean state.
3. Report the commit hash and any remaining untracked or modified files.

### `pr-describe` / `changelog`
1. Confirm the output was delivered (displayed to user or written to file).
2. Report any follow-up steps (push, tag, publish).

**Edge cases**:
- Post-commit hooks modified files (auto-formatting, linting): note the modifications and whether they need a follow-up commit.

## Validation Rules (Summary)

- The message reflects actual git state, never guesswork.
- Breaking changes are always explicit.
- Missing validation or test coverage is flagged, not hidden.
- Wording is concise and matches repo conventions.
- Mixed concerns are flagged with a split suggestion.
- Post-execution state is verified.
