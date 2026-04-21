# Output Format

The skill always produces two layers of output: a **default** (concise, decision-oriented) report and an **on-request detailed** report.

## Default report (always shown)

Routed task + why.

End the default report with: `Need more detail on any section? Pass --verbose or ask explicitly.`

## Detailed report (on request, or under `--verbose`)

(n/a — small router)

## Status banner

Lead the report with one of:
`ROUTED <frontend-task>`

## Severity ladder (where applicable)

If the skill produces findings: `Blocker > Critical > Should Have > May Have > Nitpick > Question`. Lead with the highest. Never mix levels in one bullet.

## Decisions auto-picked under `--auto`

When running under `--auto`, the report MUST list each decision the skill auto-picked, with a one-line rationale, so the user can audit retrospectively.

## Verbosity rules

- Lead with the answer / status / artifact path.
- Use bullets for process and lists; reserve prose for rationale.
- Do not dump long context unprompted; offer it instead.
- Quote primary evidence (file:line, command output) inline for findings; keep raw analyzer output in `.temp/notes/`.
