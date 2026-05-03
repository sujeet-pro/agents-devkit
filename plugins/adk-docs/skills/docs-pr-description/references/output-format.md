# `docs-pr-description` — output format

## Per-turn status

```
[adk-docs:docs-pr-description] task=<slug> phase=<0|1|2|3|4|5> base=<branch> files=<N> commits=<M> pr=<#123|draft> mode=<auto|interactive|fix>
```

## `pr-body.md` — exact shape

```markdown
## Summary

- **Risk:** <1-sentence risk statement>
- <second bullet: what changed in user-visible terms>
- <third bullet: any follow-up / rollback note>

## Changes by area

| Area | Change |
| --- | --- |
| `<folder-or-subsystem>` | <one-sentence summary of the diff in this area> |
| `<folder-or-subsystem>` | <one-sentence summary> |

## Test plan

- **Automated:** <new / changed tests>
- **Manual:** <exact steps the reviewer can run>

## Risks

- <explicit list>

## Linked tickets

- Fixes <TICKET-NNN>.   # ONLY if in a commit body
- Part of <TICKET-NNN>. # ONLY if in a commit body

## Follow-ups

- <TODOs deferred to another PR>
```

## Rules

- **Title (first line of `pr-body.md` when the PR is created with
  `gh pr create`):** ≤70 chars, imperative, matches the repo's
  commit-subject convention. Stored separately in
  `.temp/task-<slug>/pr-title.txt`.
- **Summary bullets:** exactly 2-4. First always names the risk.
- **Changes by area:** rows ≥ 1, rows ≤ 10. Collapse areas if you
  have more than 10.
- **Test plan:** at least one of "Automated" or "Manual". Never
  empty.
- **Linked tickets:** only tickets that appear in commit bodies /
  branch name. Never invent.
- **Follow-ups:** optional section; include when a visible TODO was
  left for a future PR.

## Sample title file

`.temp/task-<slug>/pr-title.txt`:

```
feat(checkout): clamp add-to-cart quantity to current inventory
```

## Final report

`.temp/task-<slug>/report.md`:

```markdown
# docs-pr-description report — <slug>

## Result
Drafted PR body for `acme/checkout-api` branch `chk-1238-clamp`.
Under --fix, ran `gh pr edit 2841 --body-file pr-body.md`; re-fetch
confirmed body landed.

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 1 | base branch | origin/main | tracking branch |
| 4 | title convention | conventional-commits | matches `git log -10 --format=%s` |

## Validation evidence
- title: 52 chars (≤70)
- test plan present; 1 automated + 1 manual
- 3 ticket refs; all 3 present in commit bodies

## Residual risk / follow-ups
- CHK-1240 (out of stock toast copy) — tracked in Follow-ups.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  commits.txt
  diffstat.txt
  tests.diff
  pr-title.txt
  pr-body.md
  report.md
```
