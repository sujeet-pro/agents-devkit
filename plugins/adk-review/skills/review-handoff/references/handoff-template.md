# `review-handoff` — handoff.md template

The canonical 10-section template, with per-section guidance.

## Template (verbatim — fill in the brackets)

```markdown
# Handoff — <task-slug>

_Authored <ISO-ts>Z by adk-review:review-handoff for <operator-name from info.md>._

## 1. Task summary

<one paragraph, 2-5 sentences. Restate the task in the operator's own voice (past tense for completed work, present continuous for in-flight work). Name the goal, name what's done, name what's not. Don't quote the prompt verbatim; restate.>

## 2. Decisions

| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| <0|1|2|...> | <one-line question> | <one-line answer> | <one-line rationale> |
| ... |

## 3. Work completed

- <action verb in past tense> — <commit-sha> / <artifact-path> — <one-line evidence>
- ...

## 4. Remaining work

1. <action verb in imperative> at <file:line> — <one-line context>
2. ...

## 5. Blockers

| Blocker | Owner | ETA | Workaround |
| --- | --- | --- | --- |
| (none) | — | — | — |

OR (if blockers exist):

| Blocker | Owner | ETA | Workaround |
| --- | --- | --- | --- |
| <one-line description> | <@login or "self" or "unknown"> | <date or "unknown"> | <one-line workaround or "(none)"> |

## 6. Key files touched

| File | Why | Last touched |
| --- | --- | --- |
| <path> | <one-line> | <commit-sha or "uncommitted"> |
| ... |

## 7. Files NOT touched (deliberately)

| File | Why not |
| --- | --- |
| <path> | <one-line — reason this was considered + skipped> |
| ... |

## 8. Git state

- Branch: <branch>
- Dirty: <yes (<n> files) | no>
- Last <n> commits:
  - <sha> <subject>
  - ...
- Uncommitted diff: +<add>/-<del> across <n> files
  - <truncated to 200 lines max; or "(see git diff for full)" if >500 lines>
- Stash: <empty | <n> entries>

## 9. Environment

- Editor: <from $EDITOR>
- Shell: <from $SHELL>
- pwd: <from `pwd`>
- Tools: <e.g. node v22.7, go 1.23, python 3.13, docker 27.3>
- Env vars relied on (names only): <e.g. GITHUB_PAT, DD_API_KEY> (values NEVER quoted)

## 10. Next step

<one sentence — concrete action to take>

```
<exact command(s)>
```

<optional: alternate paths if the next step depends on a decision>
```

## Section-by-section guidance

### Section 1 — Task summary

**Goal:** the reader knows what this task is and where it stands in 10 seconds.

**Voice:** the operator's voice. Past tense for completed work; present continuous for in-flight; future for planned.

**Don'ts:**

- Don't quote the prompt verbatim; restate.
- Don't say "the agent did X"; say "implemented X" (the agent is invisible to the next person).
- Don't editorialize ("this was a hard bug"); state facts.

**Worked example:**

> Implementing tiered pricing for B2B in `acme/storefront`. Schema migration + model + API endpoint complete; 8 of 9 unit-test cases passing; integration test still pending. Self-review run; 1 Should-Have remaining (missing test for tier transition). No blockers.

### Section 2 — Decisions

**Goal:** the reader sees the meaningful forks and why we picked each.

**Sources:** per-skill validation logs (`validation/per-skill/*.md`), `skill-plan.md`, the user's interactive picks (captured in `.temp/task-<slug>/decisions.md` if any skill writes it).

**Don'ts:**

- Don't list trivial decisions (e.g. "picked kebab-case slug").
- Don't list decisions you'd make again with no nuance ("picked option A; obvious") — these are noise.
- Do list decisions you might reconsider ("picked option B; if Z happens, consider C").

### Section 3 — Work completed

**Goal:** the reader can verify each claim.

**Format:** every bullet has a commit SHA OR an artifact path. If neither, the work isn't done.

**Don'ts:**

- Don't claim "tested" without naming the test command + result.
- Don't claim "implemented" without a commit SHA (if uncommitted, say "implemented; uncommitted at <files>").

### Section 4 — Remaining work

**Goal:** the reader picks the next task and can start without re-discovery.

**Format:** numbered (so the reader can refer "I did #1, blocked on #2"). Each item: action + file:line + one-line context.

**Don'ts:**

- Don't mix blockers in here (those go in section 5).
- Don't list speculative future work; only items the current task implies.

### Section 5 — Blockers

**Goal:** the reader knows what's actually preventing progress.

**Common case:** empty (`| (none) | — | — | — |`).

**When non-empty:** every blocker has owner + ETA + workaround. Owner is `@login`, "self", or "unknown". ETA is a date or "unknown". Workaround is one line or "(none)".

**Don'ts:**

- Don't mark "missing test" as a blocker if the test is something you can write yourself in <1h.
- Don't list blockers without an owner; "blocked on someone" is a void.

### Section 6 — Key files touched

**Goal:** the reader knows where the active code is.

**Format:** table sorted by importance (most-changed first).

**Don'ts:**

- Don't list every file in `git diff --name-only`; pick the 5-10 most important.
- Don't include lockfile churn (`package-lock.json` etc.).

### Section 7 — Files NOT touched (deliberately)

**Goal:** the reader doesn't redo work that was considered + rejected.

**The most-skipped section.** Always include unless `--no-files-not-touched`.

**Format:** table — file path + one-line "why not".

**Sources:** the skill heuristically identifies candidates by cross-referencing files mentioned in `findings.md` / `skill-plan.md` / `prompt.txt` against the touched-file list. Under `-i`, the user verifies; under `--auto`, the heuristic stands (and the user reviews after).

**Worked examples (the kinds of items that belong here):**

- `src/billing/legacy-pricing.ts` | will be deprecated in v2; left untouched intentionally
- `migrations/2026_05_02_seed_tiers.sql` | considered seeding default tiers; deferred — needs ops sign-off
- `src/admin/billing-dashboard.tsx` | UI work scoped to a separate PR per ADR

### Section 8 — Git state

**Goal:** the reader can `git checkout` and continue without surprises.

**Format:** branch + dirty + last 10 commits + diff stat + truncated diff (200 lines max) + stash.

**Defaults:** 10 commits; 200-line diff truncation. Override with `--commits <n>` and `--no-diff-truncate`.

### Section 9 — Environment

**Goal:** the reader has the same shape of dev environment.

**Format:** anonymized. Tool versions, editor, shell, pwd, env-var NAMES.

**Don'ts:**

- NEVER quote env-var values. Names only.
- Don't list every installed tool; just the ones relied on for this task.
- Don't include OS-internal paths if they're sensitive.

### Section 10 — Next step

**Goal:** the reader's first action is unambiguous.

**Format:** one sentence + the exact command (in a fenced bash block).

**Worked example:**

> Run `npm test src/billing/tier.test.ts` to confirm the 8 passing cases; then add the 9th case at `src/billing/tier.test.ts:120-160` (tier transition test). After that:
>
> ```
> git add -A && git commit -m "test: tier transition" && \
>   git push && \
>   /adk-docs:docs-pr-description --auto && \
>   gh pr create --body-file .temp/task-<slug>/pr-body.md
> ```

**Don'ts:**

- Don't say "open the PR" without the command.
- Don't list 5 alternative next steps; pick the most likely one and surface alternates as "Otherwise..."

## Per-context tone

| Context | Tone | Length |
| --- | --- | --- |
| End-of-day handoff to self (next morning) | terse, telegraphic | 60-100 lines |
| Handoff to colleague (PTO) | formal, complete | 100-200 lines |
| Incident handoff (oncall shift) | URGENT, lead with mitigation status | 50-120 lines |
| Multi-day task daily handoff | medium; emphasize delta from prior day | 80-150 lines |

The skill picks tone heuristically from the prompt (e.g. "incident" or "oncall handoff" → urgent tone; "PTO" → formal). Override with `--tone <terse|formal|urgent>` if needed.
