# Doc Review Validator

The validator gate this skill MUST run before posting anything (Confluence mode) or before declaring the run complete (local mode). Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes.

## Phase 1: Pre-execution gate

Run before reading any doc content.

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Doc target reachable | Local: file path exists. Confluence: URL parses, page fetches | BLOCKER — ask the user |
| Mode validity | `--mode local` OR `--mode confluence` (default: detected from target) | BLOCKER — clarify |
| (Confluence) Atlassian MCP auth | `plugin-atlassian-atlassian` tool list responds OR Atlassian REST creds present | BLOCKER — install pointer in `doc-review-mcp-fallback.md` |
| Source-of-truth resolvable | Either explicit (path / URL given) OR inferable from doc (link present, code-block, repo reference) | WARN if inferred — surface the inference; BLOCKER if no source can be identified at all |
| (Confluence) Comment-write permission | The auth identity can post comments to the space | BLOCKER if `--post-mode post` requested; OK to proceed in dry-run |

## Phase 2: Mid-flow gates (between workflow phases)

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `doc-fetched` | After Fetch context, before Read source | Doc content retrieved AND matches the target (path / URL) | BLOCKER — re-fetch or stop |
| `source-read` | After Read source, before Run dimension passes | Every source-of-truth file/URL referenced by the doc has been read in current state | BLOCKER — finish reading |
| `reconciled` (Confluence only) | After Reconcile, before Tier findings | Every existing inline + footer comment classified per `doc-comment-reconciliation.md` | BLOCKER — finish reconciliation |
| `findings-tiered` | After Tier findings, before Validate | Every finding has Severity, Type, Confidence, doc anchor, source anchor, quoted evidence | BLOCKER — drop or fix unbacked findings |

## Phase 3: Pre-post validation (Confluence mode only)

Run immediately before the Postback phase. EVERY check must be `OK` before any comment is posted.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Findings reproducible from current page + source | Re-run dimension checks against current page snapshot; every finding still triggers | Per-finding match snippet |
| Comment shape compliance | Every drafted inline + footer comment matches `doc-review-comment-format.md` template | Template-validation result per finding |
| Anchor stability | For every inline finding, the anchor text exists verbatim in the current page; if it appears multiple times, anchor is unambiguous | Anchor map (text → unique-position confirmed) |
| Duplicate detection | No drafted comment duplicates an existing thread (per `doc-comment-reconciliation.md`) | Duplicate report (should be empty) |
| Verdict honesty | Verdict matches the highest-severity finding | Verdict justification |
| Posting permissions | Auth identity has comment-write permission on the space | Permission probe |

## Phase 4: Post-execution validation

Run after Postback (Confluence mode) or after the report is written (local mode).

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| All approved findings posted (Confluence) | Postback summary count matches accepted-findings count | Confluence-returned comment IDs |
| All reconciliation replies posted (Confluence) | Reply count matches reconciliation pipeline count | Confluence-returned reply IDs |
| Footer summary posted (Confluence) | Summary present at page level OR explicit dry-run mode | Confluence-returned summary ID |
| `.temp/reports/doc-review-<slug>.md` written | File exists, contains the full report | File path + size |
| No silent skips | Every finding flagged in Phase 3 has a posting outcome (posted / failed / dropped with reason) | Outcome table |
| (Local mode) Markdown report renders | The local report parses as valid Markdown; all finding cards present | Render check |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading source) and re-enter the gate.
- **Phase 3 BLOCKER** (Confluence): STOP. Do not post. Surface the failing check, fix it, re-run Phase 3 from the top.
- **Phase 4 partial failure** (Confluence): Record what posted; offer `retry-remaining` per `doc-postback-protocol.md`. Never re-post a successful comment.

## Status banner

The validator sets the run's status banner (per `doc-reviewer-persona.md`):

- `DOC-REVIEW-DRAFT` — Phases 1-2 passed; Phase 3-4 N/A because dry-run / local.
- `DOC-FRESH (no Blockers)` — Phases 1-2 passed; no Blockers found.
- `DOC-DRIFTED <n> findings` — Phases 1-2 passed; <n> total findings ≥ 1 Blocker.
- `AWAITING-APPROVAL-TO-POST` — Confluence mode; Phases 1-3 passed; awaiting user approval before Postback.
- `DOC-POSTED <n inline> + <footer>` — Confluence mode; Phase 4 OK.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/doc-review-<slug>-validator.md` for audit. Format:

```
## Phase 1
- Doc target reachable: OK (path or URL)
- Mode: local | confluence
- Atlassian MCP auth: OK | N/A (local mode)
- Source-of-truth resolvable: OK | WARN (inferred from doc)
- ...

## Phase 2
- doc-fetched: OK (size, fetched 2026-04-21)
- source-read: OK (4/4 source files)
- reconciled: OK (3 threads classified)  | N/A (local mode)
- findings-tiered: OK (12 findings)

## Phase 3 (Confluence only)
- Findings reproducible: OK (12/12)
- ...

## Phase 4
- Inline posted: 8 (IDs: ...)  | N/A (local mode / dry-run)
- ...
- Markdown report: .temp/reports/doc-review-<slug>.md
```
