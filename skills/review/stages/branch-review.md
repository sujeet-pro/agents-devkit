# Branch Review Stage

This stage handles reviewing changes on a source branch compared to a target (base) branch, without PR context. It produces a review document without mutating the source.

**Core principle:** Review early, review often.

---

## Source Detection

Determine the branches to compare:

1. **Source branch**: the branch name provided by the user, or the current branch if none specified.
2. **Target branch**: detect the base branch automatically or accept user override.

### Target Branch Detection

```bash
for base in main master develop; do
  if git rev-parse --verify "$base" &>/dev/null; then
    MERGE_BASE=$(git merge-base HEAD "$base" 2>/dev/null)
    if [ -n "$MERGE_BASE" ]; then
      echo "$base"
      break
    fi
  fi
done
```

If auto-detection fails, ask: "Which branch should I compare against? (default: main)"

---

## Diff Analysis

### Step 1: Get Changed Files

```bash
git diff --name-only <target-branch>...<source-branch>
git diff --stat <target-branch>...<source-branch>
```

### Step 2: Dual Review

Apply both diff-based and full-file review approaches:

**Approach 1: Diff Review**

```bash
git diff <target-branch>...<source-branch>
```

Review the raw diff for:
- Exact line changes and their context
- Files added, removed, renamed
- Incomplete migrations or leftover debug code

**Approach 2: Full File Review**

For each changed file, read the full file on the source branch:

```bash
git show <source-branch>:<file-path>
```

Check for:
- Issues in surrounding code that interact with the change
- Missing imports or type mismatches outside the diff
- Broken invariants across the file
- Whether a suggested pattern already exists elsewhere in the file

### Step 3: Commit History Review

```bash
git log --oneline <target-branch>...<source-branch>
```

Review the commit history for:
- Logical commit grouping
- Incomplete work or fixup commits
- Commit message quality

---

## Guideline Loading

Invoke the `coding` skill to detect repo frameworks and load matching coding guidelines. Pass the list of changed files for scoped detection.

---

## Large Diff Handling

When the diff exceeds 500 changed lines:

1. Present a structure overview:
```text
## Large Diff Detected - <N> files, <M> lines changed

Areas of change:
1. <area 1>: N files, M lines -- <brief description>
2. <area 2>: N files, M lines -- <brief description>
3. <area 3>: N files, M lines -- <brief description>

Focus options:
[A]ll areas | [1-3] Specific areas | [C]ritical paths only | [S]ecurity focus
```

2. Use the user's selection to prioritize review depth.

---

## Required Child Agents

Run at least these child agents in parallel:

- `code-reviewer` for correctness, security, performance, tests, and code patterns
- `repo-auditor` for architecture, dependency direction, and change isolation
- `doc-reviewer` for docs, migration notes, naming, and reviewer ergonomics
- one domain specialist pass for frontend, backend, or design-system concerns

---

## Review Requirements

Every review must cover:

- correctness and regressions
- security and performance
- architecture and boundary fit
- tests, docs, and migration impact
- code patterns and maintainability

When `focus` is specified, weight child agent priorities accordingly.

---

## Auto-Validation

Run the same auto-validation as described in `stages/pr-review.md` -- verify each finding against the actual code on the source branch before presenting to the user. Discard findings where the referenced file or issue does not exist.

---

## Output

Produce a markdown review document at `.temp/branch-review/<branch>-review.md`:

```text
## Branch Review: <source-branch> vs <target-branch>

### Summary
- Files changed: N
- Lines added: N, removed: N
- Commits: N

### Findings (severity order)

[findings using canonical comment template format]

### Commit History Assessment
[notes on commit quality and grouping]

### Open Questions
[items needing clarification]
```

Display a final summary:

```text
## Branch Review Complete

Branch: <source-branch> vs <target-branch>
Files reviewed: N
Findings: N (critical: N, high: N, medium: N, low: N)
Auto-validation: N kept / M discarded
Output: Markdown at <path>
```
