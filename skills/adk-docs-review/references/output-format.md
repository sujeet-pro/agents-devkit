# Output Format

## Core rules
- Default to concise markdown.
- Lead with the answer, status, or findings.
- Bullets over prose for process and status.
- Distinguish verified evidence from open questions.
- End by offering deeper detail instead of front-loading it.

## Verbosity modes
| Mode | Use when | Shape |
| --- | --- | --- |
| `short` | quick updates, low-risk results | 1-3 bullets or short paragraph |
| `standard` | default for most engineering tasks | summary, scope, validation, remaining risk |
| `detailed` | audits, docs, migrations, deep reviews | expanded rationale, alternatives, evidence |

## Standard result shape
- Summary
- Changed scope or target
- Validation evidence (commands run, output)
- Remaining risk or open questions
- Offer to expand

## Severity labels
`Blocker > Critical > Should Have > May Have > Nitpick > Question`

## Cross-platform safety
- Safe everywhere: headings, bullets, numbered lists, fenced code blocks, tables, links, blockquotes.
- Avoid HTML-only structures when output may land in PR comments or external tools.
