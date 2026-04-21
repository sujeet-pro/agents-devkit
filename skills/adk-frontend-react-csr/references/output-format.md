# Output Format

The skill always produces two layers of output: a **default** (concise, decision-oriented) report and an **on-request detailed** report.

## Default report (always shown)

Result + version table + changed files (config / styles / components / routes / ci) + validation matrix + deploy URL + remaining risk + next steps.

End the default report with: `Need more detail on any section? Pass --verbose or ask explicitly.`

## Detailed report (on request, or under `--verbose`)

Add: per-route Lighthouse breakdown, axe full report, theme-grid screenshots (12 cells), bundle visualization, suggested follow-ups numbered.

## Status banner

Lead the report with one of:
`BOOTSTRAPPED  |  FEATURE-LANDED  |  AUDIT-DONE  |  STACK-DRIFT (flagged)`

## Severity ladder (where applicable)

If the skill produces findings: `Blocker > Critical > Should Have > May Have > Nitpick > Question`. Lead with the highest. Never mix levels in one bullet.

## Decisions auto-picked under `--auto`

When running under `--auto`, the report MUST list each decision the skill auto-picked, with a one-line rationale, so the user can audit retrospectively.

## Verbosity rules

- Lead with the answer / status / artifact path.
- Use bullets for process and lists; reserve prose for rationale.
- Do not dump long context unprompted; offer it instead.
- Quote primary evidence (file:line, command output) inline for findings; keep raw analyzer output in `.temp/notes/`.
