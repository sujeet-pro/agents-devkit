# `audit-repo` — anti-patterns

## Findings volume

- **600 findings of varying severity dumped together.** Organize: Top-10 + per-dimension. The reader scans the Top-10 in 30 seconds.
- **Padding to hit 10.** If the repo has 6 real findings, surface 6 (and surface "the repo is in good shape"). Don't fabricate.
- **Re-litigating every TODO comment.** TODOs are sometimes tech debt; usually not. Sniff for genuinely-stale TODOs (e.g. >2 years old, on a critical path, with no JIRA reference); ignore the rest.
- **Surfacing every linter warning.** Quality findings should be aggregated ("eslint reports 47 warnings, 0 errors; mostly `no-unused-vars` in test files; recommend tightening rule"). Don't list each warning.
- **Nitpick-heavy Top-10.** The Top-10 should be biased toward Blockers + Criticals + Should-Haves. Nitpicks belong in per-dimension detail, not Top-10.

## Coverage / methodology

- **Auditing without running the repo's own tooling first.** Always: `npm audit`, `pip-audit`, `pytest --cov`, `eslint`, etc., before heuristics.
- **Pretending heuristics are tools.** If a tool isn't installed, mark the dimension's coverage as partial; surface the install command.
- **Auditing without an inventory.** The dimension passes need to know language / framework / tools; skipping inventory leads to wrong tool selection.
- **Skipping methodology section.** Without it, the report isn't trustable. Always include: tools used, time taken, scope, what was NOT covered.
- **Reading ALL files in a 50K-LOC repo.** Heuristics: top-20 largest + top-20 most-changed + the directories called out by CODEOWNERS. Don't try to "read everything" — context-budget pressure makes the audit shallow.

## Severity

- **Severity inflation.** Calling "missing test for a non-critical helper" a Blocker. Use Should-Have or May-Have.
- **Severity deflation.** Calling "auth bypass on an admin endpoint" a Should-Have because "the endpoint is internal-only". Internal != trusted. Critical or Blocker.
- **Untiered findings.** Same rule as `review-pr`: tier or drop.
- **Cross-dimension severity contradiction.** If security says "critical" and quality says "nitpick" on the same line, surface both, mark as `discuss` — don't pick one.

## "What's healthy" section

- **Skipping it.** Engineers need to know what's working. The section keeps the audit balanced; without it, the report reads as 100% bad news (and gets dismissed).
- **Padding it.** Don't list "uses semicolons consistently" as healthy. Stick to substantive things: "0 secrets in repo", "CI is green and fast (<5min)", "coverage is >80% on critical paths", "deps are within 1 minor version of latest".
- **Listing healthy items per-dimension only.** The TOP-5 healthy across dimensions belongs in a dedicated section, not buried in per-dimension tables.

## Recommendations

- **Inline fixes.** Don't write the fix; reference the right `/adk-code:*` skill with scope filter.
- **Sorting by severity only, not effort.** Low-effort high-impact items first (e.g. "address `secret_in_diff` Blocker" → 1h to rotate + remove; "refactor god class" → 2 weeks). Effort matters for prioritization.
- **No effort estimate.** Each recommendation should include a rough effort estimate (e.g. "1 hour", "1 day", "1 week", "1 quarter").
- **Vague recommendations.** "Improve test coverage" is useless. "Add integration tests for `routes/admin.go` (currently 0 lines covered; suggest `/adk-code:code-test --scope src/routes/admin/`)" is actionable.

## Process

- **Running dimensions serial.** Parallelize. The dispatcher rule: max 4 at once.
- **Spawning more than 4 parallel subagents.** Coordination overhead grows past 4.
- **Re-running the same audit on the same SHA.** Wasteful — the result is identical. Use `--scope <subdir>` if focusing.
- **Auditing a dirty working tree.** The repo's state should be `clean` (or close to it). Surface dirty files in the methodology; recommend re-running on the next clean commit.
- **Auditing a stale checkout.** Surface in the methodology: "audited at SHA <sha>; remote main is at <other-sha>; rebase before relying on the report".

## Privacy / security

- **Quoting secrets verbatim.** NEVER. Name the type + file:line; never the bytes.
- **Quoting customer names from logs.** Anonymize.
- **Including PII in findings.** Anonymize.
- **Posting the report publicly without explicit user opt-in.** This skill doesn't post; if the user wants to share, they do it manually.

## Output

- **Verdict-buried-in-detail.** Lead with the verdict in the executive summary. Don't bury it after 600 lines of dimension detail.
- **No artifact paths in the report.** Every reference (e.g. "see per-finding/sec-001-npm-audit.txt for the full output") should be a clickable / copy-pastable path.
- **Re-running the audit but not archiving the prior report.** Always move prior `audit-<slug>.md` to `.archive/<iso-ts>/` first (slug includes the date, so different days have different slugs; same-day re-runs DO need archiving).
- **Mixing audit findings with `review-pr` findings or `audit-pr` findings in the same report.** Each skill writes its own; don't fold them together.
