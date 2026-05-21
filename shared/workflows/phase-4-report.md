# workflow: Phase 4 — report

> The final artifact. What the user sees. Also the input for `/adk-improve`'s session-summary store.

## Steps

1. **Write the final report** to `<task_dir>/report.md` (the task folder resolved in Phase 0, per `shared/paths.md`).
2. **Append a one-paragraph session summary** to `~/.agents-devkit/improve/learning/sessions/<date>-<skill>-<slug>.md`.
3. **Display the report** in the agent's chat.
4. **Suggest next-best skill** if applicable (e.g., after `/adk-investigate`, suggest `/adk-document --type rca` if symptom was post-incident).

## Report shape (lead with risk, bury bookkeeping)

```markdown
# <skill> — <task-slug>

## TL;DR
<two sentences max>

## Risk / Blockers / Follow-ups
- <only if any; else "none">

## What got done
- <bullet>
- <bullet>

## What got skipped (and why)
- <gap>: <reason>
- <e.g., Slack MCP unreachable, scrape skipped>

## Evidence
- <link to relevant artifact in `<task_dir>/`>
- <link to changed files>
- <link to validation output>

## Decisions made this run
- <fork_id>: <chose X> [user-answered / auto-defaulted / inferred]

## Next-best action
- <suggested skill or action>

---
artifacts: <task_dir>     # e.g. /Users/sujeet/code/storefront-bff/.temp/adk/implement/SF-1234/
                          #  or  /Users/sujeet/.agents-devkit/skill-pr-review/storefront-bff_pr-456/
decision log: ~/.agents-devkit/improve/learning/decisions.jsonl (12 new entries this run)
```

## Session summary shape

`~/.agents-devkit/improve/learning/sessions/2026-05-18-implement-SF-1234.md`:

```markdown
# 2026-05-18 — /adk-implement SF-1234

scope: implement coupon engine MVP per Jira SF-1234.
outcome: 5 files changed, 8 tests added, lint+typecheck+tests green, PR not yet opened.
overrides: chose `full` over recommended `vertical-slice` ("demo Monday"); chose `jest` (already-set default).
surprises: existing util `discounts.applyMultiple` covered 40% of the requirement — used it instead of writing new code.
gaps: Slack scrape skipped (token missing); didn't query Mixpanel for prior coupon usage data (not in scope).
next: user to open PR + run /adk-document --type pr-body.
```

## Honest report rules

- The "What got skipped" section is required. If nothing was skipped, say "none" explicitly.
- The "Risk" section is required. If no risks, say "no known risks". Don't omit.
- Quote exact diff stats ("5 files changed, +120/-30"). Don't summarize as "small".
- Link out to source artifacts; don't embed long fetched content.
