# Risk-first PR body format

The default `pr-body.md` structure when no repo template applies.
The ordering maximizes signal-per-skim for a reviewer with 10
minutes and 3 open tabs.

## Section order

1. **Summary** (2-4 bullets; first bullet names the risk)
2. **Changes by area** (table; 1-10 rows)
3. **Test plan** (Automated + Manual; at least one non-empty)
4. **Risks** (explicit list; even "none" is acceptable)
5. **Linked tickets** (only tickets actually in commits)
6. **Follow-ups** (optional; TODOs deferred to a next PR)

## Why "risk first"

- The reviewer's scarce resource is attention.
- Risk answers: "what could break in prod?" — more important than
  "what changed?" because the diff answers "what changed?".
- A reviewer who reads only the first bullet should know the blast
  radius.

## Summary bullets — anatomy

### Bullet 1 (risk, always)

- Imperative, named blast radius.
- "**Risk:** touches the add-to-cart happy path; regression if the
  clamp is wrong."
- "**Risk:** DB migration is forward-only; rollback script attached."
- "**Risks:** touches the shared `Money` helper; currency formatting
  may drift."

### Bullet 2 (user-visible behavior change)

- One sentence. What would a user notice? "Adds the export button to
  the order-history page under `FEATURE_EXPORTS`."
- If nothing user-visible, say so: "No user-visible behavior change
  (internal refactor)."

### Bullet 3 (rollback / follow-up)

- One sentence that completes the picture. "Rollback: flip
  `FEATURE_EXPORTS` to `false` and re-deploy; no data migration
  needed." / "Follow-up: the out-of-stock toast copy needs design
  review (CHK-1240)."

## Test plan — anatomy

The Test plan answers "did you run this?" with specifics.

```markdown
## Test plan

- **Automated:** `<list of tests added / modified>`. Run with
  `<exact command>`.
- **Manual:** `<exact reproduction steps the reviewer can run>`.
```

Patterns:

- Pure bug fix: Automated = new regression test; Manual = reproduce
  the bug on the base branch, confirm fix on the branch.
- New feature: Automated = unit + integration; Manual = happy path +
  error path + rollback.
- Refactor: Automated = existing tests green; Manual = spot-check of
  the hottest path.
- Dependency bump: Automated = full suite; Manual = smoke test in the
  app.
- Config / infra: Automated = none possible; Manual = staged rollout
  steps.

## Risks — anatomy

Explicit, bulleted. Each risk names:

- What could go wrong.
- The mitigation (feature flag, rollback, monitoring).
- The detection path (which DD monitor, which dashboard).

## Linked tickets — anatomy

- `Fixes <TICKET-NNN>.` — the ticket this PR closes.
- `Part of <TICKET-NNN>.` — the parent epic / story.
- `Refs <TICKET-NNN>.` — related but not directly resolved.

**Hard rule:** every TICKET-NNN must appear literally in a commit
body. Never invent from the branch name alone.

## Follow-ups — anatomy

Bulleted list of deferred work. Each item:

- Short description of the deferred task.
- Ticket number if one was filed; "(no ticket)" otherwise.
- Why deferred (scope; risk; timing).

## Length

- Target: 30-80 lines total. Reviewers skim past the first fold.
- Hard cap: 150 lines. Beyond that, split the PR.
