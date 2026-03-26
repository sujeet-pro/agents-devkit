---
name: review-code-local
description: Use when you need a non-mutating review of staged, unstaged, or branch-local code changes, including commits made since the branch diverged from its base
user_invocable: true
arguments:
  - name: scope
    description: "What to review: staged, unstaged, worktree, branch, files, range (default: branch)"
    required: false
  - name: base
    description: "Base branch or commit used for branch comparison (default: merge-base with main)"
    required: false
  - name: files
    description: "Optional comma-separated file list when scope=files"
    required: false
  - name: confidence
    description: "Minimum confidence threshold (0-100, default: 80)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
  - name: fix
    description: "When true, enter the interactive fix loop after producing the review (default: false)"
    required: false
---

# Local Review

Use the same review team and guideline loading model as `/devkit:review-code-pr`, but keep the result local instead of posting to a remote code review system.

**All review findings must follow the canonical format in `skills/_references/review-comment-template.md`.** This applies to the markdown review document and to findings presented in the interactive fix loop.

This skill is review-only. Do not auto-fix findings. When inline comments are unavailable, generate a markdown review document that other agents can use to plan and implement changes.

## Scope Rules

- `staged`: review the staged diff only
- `unstaged`: review only unstaged working-tree changes
- `worktree`: review staged plus unstaged changes
- `branch`: review everything changed since the branch diverged from `base`, including already committed files
- `files`: review only the named files
- `range`: review a caller-specified git range

## Required Child Agents

Run at least these child agents in parallel:

- `code-reviewer`
- `repo-auditor`
- `doc-reviewer`
- one domain specialist based on the affected area

## Intermediate Review Dispatch

If you need a focused intermediate review before the full review pass (e.g., early feedback on a tricky change), launch a `code-reviewer` child agent with:

- the requirement or plan
- the changed files or diff
- relevant guidelines
- the specific review question you want answered

Ask for review early enough that fixes are still cheap.

## Output

Always produce a review document with:

- severity-ordered findings
- file and line references when available
- open questions and assumptions
- a follow-up checklist suitable for implementation planning

## Interactive Fix Loop

When `fix=true`, enter the interactive fix loop after producing the review document.

### Cycle

1. Present each finding to the user one at a time with its severity, file, line, and description.
2. For each finding the user can choose:
   - **Accept** — apply the suggested fix automatically.
   - **Reject** — skip the finding entirely.
   - **Edit** — ask the user what to change, then apply the modified fix.
3. After all findings have been triaged, apply accepted and edited fixes to the codebase.
4. Run build/lint validation:
   - Detect the project's build command from `package.json` scripts, `Makefile`, `Cargo.toml`, `pyproject.toml`, or similar.
   - Run the detected lint and build commands. Report any failures.
5. Re-run the review on changed files only to catch regressions or new issues introduced by the fixes.
6. Repeat the cycle up to 3 times or until no more findings are reported.

### Progress Reporting

After each cycle, display a progress summary:

```text
## Fix Loop — Cycle N/3

Findings fixed this cycle: N
Findings remaining: N
Total findings fixed so far: N
New issues introduced: N
```

If no findings remain or 3 cycles have completed, exit the loop and display the final summary.
