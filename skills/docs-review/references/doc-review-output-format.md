# Output Format for `adk-docs-review`

The skill always produces two layers of output: a **default** (concise, decision-oriented) report and an **on-request detailed** report.

## Status banner (always first)

Lead the report with one of:

```
DOC-REVIEW-DRAFT  |  DOC-FRESH (no Blockers)  |  DOC-DRIFTED <n> findings  |  DOC-POSTED <n inline> + <footer>  |  AWAITING-APPROVAL-TO-POST
```

`DOC-POSTED` and `AWAITING-APPROVAL-TO-POST` only appear under `--mode confluence`.

## Default report (always shown)

```
<status banner>

## Doc Review: <doc title or path>
- Target: <path or URL>
- Mode: <local | confluence>
- Source-of-truth: <path or URL>
- Focus: <focus>
- Reconciliation: <validate-then-keep | aggressive-cleanup | read-only>  (Confluence only)
- Post mode: <dry-run | posted | awaiting-approval>  (Confluence only)

## Verdict
<ready-to-publish | needs-fixes | needs-rewrite>

## Existing-comment reconciliation  (Confluence mode only)
- Threads inspected: <n>
- Kept open (still apply): <n>
- Resolved-confirmed: <n>
- Resolved-stale (restated): <n>
- Moved (restated at new section): <n>
- No-longer-applicable (dismissed): <n>
- Pushback (reviewer was wrong): <n>
- Out-of-scope (handed off): <n>

## Findings

### Blockers
<Finding cards per `doc-review-comment-format.md`>

### Critical
<Finding cards>

### Should Have
<Finding cards>

### May Have
<Finding cards>

### Nitpicks
<Finding cards>

### Questions
<Finding cards>

### Praise
<Finding cards if any>

## Out of Scope
- <items explicitly not reviewed and why>

## Recommended Next Step
- <e.g. "fix Blockers in place" or "hand off to `adk-docs-write` for restructure">

## Validation (per `doc-review-validator.md`)
- Phase 1 (pre-execution): OK
- Phase 2 (mid-flow gates): OK
- Phase 3 (pre-post): OK | N/A (local / dry-run)
- Phase 4 (post-execution): OK | N/A (local / dry-run)
- Validator log: `.temp/notes/doc-review-<slug>-validator.md`

## Postback summary  (Confluence mode, after posting)
- Inline comments posted: <n>
- Reconciliation replies posted: <n>
- Footer summary comment: <YES | N/A>
- Failed to post: <list or none>

## Decisions auto-picked (if --auto)
- <decision> — <one-line rationale>

## Residual risk
- <bulleted, prioritized>

Need more detail on any finding? Pass `--verbose` or ask explicitly.
```

## Detailed report (on request, or under `--verbose`)

Add to the default:

- Drift map: doc claim → actual source state, per finding.
- Readability metrics (Flesch, sentence length) for the doc as a whole.
- Missing-sections analysis by doc-type template (README / runbook / API ref / ADR / onboarding / migration / tech radar).
- Per-dimension narrative (accuracy / freshness / structure / completeness / readability).
- Suggested replacement Markdown blocks per finding (one fenced block each).
- Full Phase 1-4 validator log inline.

## Severity ladder

`Blocker > Critical > Should Have > May Have > Nitpick > Question`. Lead with the highest. Never mix levels in one bullet.

## Decisions auto-picked under `--auto`

When running under `--auto`, the report MUST list each decision the skill auto-picked, with a one-line rationale, so the user can audit retrospectively. The list always includes:

- mode (auto-detected from target shape)
- focus (default `all`)
- post-mode (Confluence; under `--auto`, default `post`)
- reconciliation aggressiveness (Confluence; default `validate-then-keep`)

## Per-doc-type focus tips

| Doc type | Watch for |
| --- | --- |
| README | Quick start commands actually work; install steps include version requirements; supported OS list current |
| Runbook | Mitigation steps tested in the last quarter; commands are copy-paste ready; on-call rotation links current |
| API reference | Signatures match the code; error codes complete; deprecated endpoints flagged |
| ADR | Status reflects reality (Accepted vs Superseded); consequences honest; supersedes-link present |
| Onboarding | Day-1 list still possible from a clean machine; "who to ask" is current; access requests still valid |
| Migration guide | Source/target versions still relevant; rollback path concrete; "how to verify" steps present |
| Tech radar | Dates and signals not stale; ring movement justified; superseded items moved out |

## Verbosity rules

- Lead with the status banner, then the verdict, then findings ordered by severity.
- Use bullets for process and counts; reserve prose for finding `Issue Explanation` sections.
- Do not dump long context unprompted; offer it instead.
- Quote primary evidence (doc anchor + source anchor) inline for findings; keep raw fetched HTML and analyzer output in `.temp/notes/`.
