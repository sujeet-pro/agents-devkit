# adk-review-local-changes

Review local uncommitted or branch changes before commit or PR.

## Quick Start

```
npx adk-review-local-changes
```

## What This Skill Does

Reviews work that exists locally and has not yet been committed or pushed. Inspects uncommitted changes or a local branch diff for correctness issues, missing tests, and regression risk. Produces a prioritized list of findings with stable IDs that can be accepted, rejected, or expanded.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `--scope` | path | none | Limit the diff to one area |
| `--focus` | `correctness`, `risk`, `tests`, `security`, `performance` | `correctness` | Primary review lens |
| `--auto` | flag | off | Skip confirmations; run end-to-end |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Required | Purpose |
| --- | --- | --- |
| `git` | yes | Read local diffs, status, and history |
| `python3` | yes | Run pre-flight checks |

## Skill Layout

```
adk-review-local-changes/
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
2. **Confirm scope** -- confirm the review scope (uncommitted changes, branch diff, or scoped path) and focus lens (skipped with `--auto`).
3. **Read local diff** -- run `git status` and read the local diff.
4. **Inspect context** -- check impacted files and nearby tests.
5. **Classify findings** -- assign severity (Blocker/Critical/Should Have/May Have/Nitpick/Question) and stable F-IDs.
6. **Present findings** -- show the prioritized list; wait for user response.
7. **Finalize** -- report confidence, blind spots, and residual risk.

## Interaction Protocol

### Confirmations

Before starting the review, the skill confirms:
- The review scope (uncommitted changes vs. branch diff vs. scoped path)
- The review focus lens
- Whether the diff is against HEAD, a branch, or a specific commit

This step is skipped when `--auto` is passed.

### Findings Format

Each finding has a stable ID, a severity level, and a one-line summary:

```
F-1  [Blocker]    Uncommitted migration drops the users table
F-2  [Critical]   New endpoint has no auth middleware
F-3  [Should Have] Added function lacks corresponding unit test
F-4  [May Have]   Variable name could be more descriptive
F-5  [Nitpick]    Trailing whitespace on line 88
F-6  [Question]   Should this default to retry=3 or be configurable?
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

Example: `a-1, a-3, r-4, e-6`

## Output Format

The review output contains six parts:

1. **Summary** -- one-line overview of the review result.
2. **Scope** -- what was reviewed (uncommitted changes, branch diff, scoped path).
3. **Findings** -- prioritized list with stable F-IDs and severity.
4. **Validation** -- what was checked and what could not be verified.
5. **Risk** -- residual risk, confidence level, and blind spots.
6. **Next steps** -- recommended follow-up actions.

## Examples

### Review uncommitted changes

```
npx adk-review-local-changes
```

Reviews all uncommitted changes in the working tree, presents findings with F-IDs.

### Review with test focus and scope

```
npx adk-review-local-changes --focus tests --scope src/api/
```

Scoped review of local changes in `src/api/`, focused on test coverage gaps.

### Review in auto mode

```
npx adk-review-local-changes --focus risk --auto
```

Skips confirmation, reviews the current branch diff against the base, focused on regression risk.

## What Success Looks Like

- [ ] Local diff was fully inspected
- [ ] Findings are prioritized with stable F-IDs
- [ ] Blocker and Critical items appear before suggestions
- [ ] Each finding is grounded in the actual local diff
- [ ] Testing gaps are called out explicitly
- [ ] Confidence level and blind spots are stated
- [ ] User can accept, reject, or expand any finding
