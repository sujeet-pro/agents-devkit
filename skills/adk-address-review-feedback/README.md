# adk-address-review-feedback

Fix review feedback, update the code, and confirm the comments are addressed.

## Quick Start

```
npx adk-address-review-feedback https://github.com/acme/api/pull/87
```

## What This Skill Does

Takes existing review findings (from a PR, inline review, or local review notes) and addresses them. Groups related fixes, applies the smallest correct change for each, re-runs relevant validation, and reports what was fixed vs. what still needs follow-up.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<feedback-source>` | free text, file, or PR thread reference | required | What feedback must be addressed |
| `--scope` | path | none | Limit the edit surface |
| `--auto` | flag | off | Skip confirmations; apply all fixes |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Required | Purpose |
| --- | --- | --- |
| `git` | yes | Read diffs, apply changes, check status |
| `python3` | yes | Run pre-flight checks |

## Skill Layout

```
adk-address-review-feedback/
  SKILL.md              # Agent-facing skill definition
  README.md             # This file (human-facing docs)
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Skill-specific workflow steps
    persona.md           # Fixer persona and tone
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. **Pre-flight** -- run `scripts/preflight.py` to verify dependencies.
2. **Confirm source** -- confirm the feedback source and which findings are in scope (skipped with `--auto`).
3. **Group fixes** -- group related findings; avoid bundling unrelated cleanup.
4. **Apply fixes** -- apply the smallest change that resolves each issue.
5. **Validate** -- re-run the validation relevant to each fix.
6. **Report status** -- state what was addressed, what was deferred, and what needs follow-up.

## Interaction Protocol

### Confirmations

Before starting, the skill confirms:
- The feedback source (PR comments, inline review, local notes, or pasted text)
- Which findings are in scope for this pass
- Any scope limits on the edit surface

This step is skipped when `--auto` is passed.

### Findings Format

The fix plan uses stable IDs and a status for each item:

```
F-1  [Fix]        Null check added in parseConfig per reviewer comment
F-2  [Fix]        Auth middleware applied to new endpoint
F-3  [Deferred]   Refactor suggestion noted; out of scope for this pass
F-4  [Follow-up]  Reviewer asked for benchmark; needs manual run
```

Status levels: **Fix** (applied), **Deferred** (acknowledged, not applied), **Follow-up** (needs reviewer or manual action)

### User Response

After seeing the fix plan, respond with any combination of:

| Syntax | Meaning |
| --- | --- |
| `a-N` | Accept the proposed fix for N |
| `r-N` | Reject the fix for N (keep current code) |
| `e-N` | Expand finding N (show what changed) |
| `all` | Accept all proposed fixes |

Example: `a-1, a-2, r-3, e-4`

## Output Format

The output contains six parts:

1. **Summary** -- one-line overview of what was addressed.
2. **Scope** -- which feedback was in scope and what files changed.
3. **Findings** -- fix status per finding (fixed, deferred, follow-up).
4. **Validation** -- what was re-run and results.
5. **Risk** -- residual risk from deferred or follow-up items.
6. **Next steps** -- what the reviewer or author should do next.

## Examples

### Fix PR review feedback

```
npx adk-address-review-feedback https://github.com/acme/api/pull/87
```

Reads PR comments, builds a grouped fix plan, applies accepted fixes.

### Fix feedback from local review notes

```
npx adk-address-review-feedback review-notes.md --scope src/auth/
```

Reads a local review notes file, limits edits to `src/auth/`, reports status.

### Auto-fix all feedback

```
npx adk-address-review-feedback https://github.com/acme/api/pull/87 --auto
```

Skips confirmation, applies all fixes, reports what was fixed vs. deferred.

## What Success Looks Like

- [ ] All in-scope feedback items are addressed or explicitly deferred
- [ ] Each fix is the smallest correct change
- [ ] Related fixes are grouped; unrelated cleanup is not bundled
- [ ] Validation was re-run for changed code
- [ ] Deferred and follow-up items are clearly listed
- [ ] No regression introduced by the fixes
- [ ] User can accept, reject, or expand any fix
