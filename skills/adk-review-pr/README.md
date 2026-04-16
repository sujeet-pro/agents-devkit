# adk-review-pr

Review a pull request for correctness, regression risk, and missing validation.

## Quick Start

```
npx adk-review-pr https://github.com/acme/api/pull/87
```

## What This Skill Does

Reviews a pull request or branch diff before merge. Inspects the changed code for correctness issues, regression risk, missing validation, and testing gaps. Produces a prioritized list of findings with stable IDs that can be accepted, rejected, or expanded.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<pr-or-branch>` | PR URL, branch name, or diff target | required | What should be reviewed |
| `--focus` | `correctness`, `risk`, `tests`, `security`, `performance` | `correctness` | Primary review lens |
| `--auto` | flag | off | Skip confirmations; run end-to-end |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Required | Purpose |
| --- | --- | --- |
| `git` | yes | Read diffs, branches, and history |
| `python3` | yes | Run pre-flight checks |

## Skill Layout

```
adk-review-pr/
  SKILL.md              # Agent-facing skill definition
  README.md             # This file (human-facing docs)
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Skill-specific workflow steps
    persona.md           # Reviewer persona and tone
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. **Pre-flight** -- run `scripts/preflight.py` to verify dependencies.
2. **Confirm scope** -- confirm the PR/branch target and review focus with the user (skipped with `--auto`).
3. **Inspect diff** -- read the diff and surrounding context.
4. **Identify issues** -- find correctness and regression risk first, then validation gaps.
5. **Classify findings** -- assign severity (Blocker/Critical/Should Have/May Have/Nitpick/Question) and stable F-IDs.
6. **Present findings** -- show the prioritized list; wait for user response.
7. **Finalize** -- report residual risk, testing gaps, and next steps.

## Interaction Protocol

### Confirmations

Before starting the review, the skill confirms:
- The PR URL, branch name, or diff target
- The review focus lens
- Any scope narrowing

This step is skipped when `--auto` is passed.

### Findings Format

Each finding has a stable ID, a severity level, and a one-line summary:

```
F-1  [Blocker]    Missing null check in parseConfig causes crash on empty input
F-2  [Critical]   SQL query built with string concat; use parameterized query
F-3  [Should Have] Unit test missing for the new retry path
F-4  [May Have]   Consider extracting the validation helper for reuse
F-5  [Nitpick]    Inconsistent brace style on line 42
F-6  [Question]   Is the 30s timeout intentional or a placeholder?
```

Severity levels: **Blocker** > **Critical** > **Should Have** > **May Have** > **Nitpick** > **Question**

### User Response

After seeing findings, respond with any combination of:

| Syntax | Meaning |
| --- | --- |
| `a-N` | Accept finding N |
| `r-N` | Reject finding N |
| `e-N` | Expand finding N (show detail) |
| `all` | Accept all findings |

Example: `a-1, a-2, r-4, e-6`

## Output Format

The review output contains six parts:

1. **Summary** -- one-line overview of the review result.
2. **Scope** -- what was reviewed (PR, branch, files, lines changed).
3. **Findings** -- prioritized list with stable F-IDs and severity.
4. **Validation** -- what was checked and what could not be verified.
5. **Risk** -- residual risk and blind spots.
6. **Next steps** -- recommended follow-up actions.

## Examples

### Review a PR by URL

```
npx adk-review-pr https://github.com/acme/api/pull/87
```

Fetches the PR diff, confirms scope with the user, and presents findings.

### Review a branch with security focus

```
npx adk-review-pr feature/auth-refactor --focus security
```

Compares the branch against the default base, focuses on security issues.

### Review in auto mode

```
npx adk-review-pr staging --focus performance --auto
```

Skips all confirmations, reviews the staging branch diff for performance issues.

## What Success Looks Like

- [ ] PR or branch diff was fully inspected
- [ ] Findings are prioritized with stable F-IDs
- [ ] Blocker and Critical items appear before suggestions
- [ ] Each finding cites evidence from the diff or code
- [ ] Testing gaps are called out explicitly
- [ ] Residual risk is stated clearly
- [ ] User can accept, reject, or expand any finding
