# Output Format

## Goal

Keep public ADK skill output consistent across runtimes, installers, and copied skill bundles.

## Core Rules

- default to concise markdown
- lead with the answer, status, or findings
- prefer bullets over long prose when reporting process or results
- distinguish verified evidence from open questions
- do not imply validation ran when it did not
- end by offering deeper detail instead of front-loading it

## Verbosity Modes


| Mode       | Use When                                           | Characteristics                                |
| ---------- | -------------------------------------------------- | ---------------------------------------------- |
| `short`    | quick updates, low-risk results, narrow follow-ups | 1-3 bullets or a short paragraph               |
| `standard` | default for most engineering tasks                 | summary, scope, validation, remaining risk     |
| `detailed` | audits, docs, migrations, deep reviews             | expanded rationale, alternatives, and evidence |


## Standard Result Shape

Most public skills should end with:

- summary
- changed scope or target
- validation run
- remaining risk or open questions
- ask whether more detail is needed

## Brainstorming Result Shape

When a skill is in brainstorming or design-closure mode, prefer:

- current state
- target state
- change tolerance
- desired confidence and current confidence
- options with trade-offs
- open questions
- recommended route or artifact
- warning if the brainstorming MCP server is missing and fallback mode is in use

Lead with the recommendation, but keep the unresolved questions visible.

## Findings-First Review Shape

Review and audit skills should:

- lead with findings, not summary
- order findings by severity
- separate verified issues from lower-confidence questions
- call out missing validation explicitly

## Document Output Rules

- markdown is the source-of-truth output unless the destination requires another format
- when a skill supports publishing, keep the markdown source behavior explicit
- named templates and custom templates should preserve headings, boilerplate, and placeholders unless the user asks to rewrite them

## Visual Artifact Rules

- keep editable source files for diagrams and charts
- prefer SVG for markdown destinations
- use PNG only when the destination does not handle SVG reliably

## Cross-Platform Markdown Rules

- safe everywhere: headings, bullets, numbered lists, fenced code blocks, tables, links, blockquotes
- avoid HTML-only structures when the output may be pasted into PR comments or external review tools
- avoid nested formatting that depends on one specific renderer

## Severity Labels

Use one primary label when reporting review or audit findings:

- `Blocker`
- `Critical`
- `Should Have`
- `May Have`
- `Nitpick`
- `Question`