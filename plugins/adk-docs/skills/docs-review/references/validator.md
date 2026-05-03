# `docs-review` — per-phase validator

Logged to `.temp/task-<slug>/validation/docs-review.md`.

## Phase 0 — pre-execution

- [ ] Target kind resolved (`md` / `confluence` / `gdoc` / `url`).
- [ ] `.temp/task-<slug>/` exists, gitignored.
- [ ] Prompt saved verbatim to `prompt.txt`.

## Phase 1 — preflight

- [ ] `bin/adk-info --check` == 0.
- [ ] If target is Confluence: workspace Atlassian connector reachable.
- [ ] If target is GDoc: workspace Google Drive connector reachable.
- [ ] Repo (if any) resolved via `repos.md` with verified/inferred tag.
- [ ] For shared targets: last-modified + last-editor captured.

## Phase 2 — accuracy check

- [ ] `claims.md` lists every factual claim parsed from the doc.
- [ ] Every claim has a status (`OK` / `wrong` / `stale-but-correct`
      / `unverifiable`).
- [ ] Every `wrong` claim cites `<file>:<lines>` (the contradicting
      code).
- [ ] Every `unverifiable` claim has a one-line reason.

## Phase 3 — structure / freshness / readability

- [ ] Heading hierarchy checked (no skipped levels, depth ≤ 4).
- [ ] Internal link integrity checked (every anchor resolves).
- [ ] Cited-files freshness: `git log -1 --format=%ci` compared to
      target last-modified (informational, not gating).
- [ ] Audience calibration checked (runbook tone / README depth / ADR
      structure).

## Phase 4 — triage

- [ ] `review.md` exists.
- [ ] Every finding has a severity tier.
- [ ] Every finding cites `doc:<location>` + `code:<file>:<lines>`.
- [ ] No finding has "Undecided" or "Maybe" severity.

## Phase 5 — `--fix` (if enabled)

- [ ] Backup created under `.temp/task-<slug>/backup/<basename>`.
- [ ] Every applied fix is listed in `fixes-applied.md` with a diff.
- [ ] Every controversial finding is in `fixes-deferred.md`.
- [ ] For shared targets (Confluence / GDoc): post-update re-fetch
      confirms the fix landed.
- [ ] No more than 20 corrections applied without explicit user opt-in.
- [ ] No voice rewrite, section restructure, or new-section addition.

## On any check failure

- Log the failure with remediation in `validation/docs-review.md`.
- Do not proceed to the next phase.
- After 3 same-kind failures, surface to the user — do not loop.
