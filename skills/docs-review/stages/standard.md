# Standard Document Review

This stage is the default (non-interactive) mode. It produces a markdown review artifact without mutating the source document.

## Source Handling

- Local files: read the file plus any linked diagrams or attachments.
- Confluence: read the page body, labels, attachments, existing comments, and resolution state through the Confluence MCP.
- Google Docs: read the document body, comments, and linked assets through Google Drive MCP.
- Read existing comments first and reconcile them before emitting new findings.

## Guideline Loading

Invoke the `/adk:coding` helper skill to detect the repo stack and load the appropriate coding guidelines.

## Execution

Produce the review using parallel child agents. Each agent covers a distinct review dimension (structure, accuracy, completeness, style, actionability).

## Output

Produce a markdown review artifact containing:

- Summary of the document's purpose and audience
- Findings grouped by severity (critical, major, minor, suggestion)
- Each finding includes: location, issue, recommendation, confidence
- An overall assessment with strengths and areas for improvement

If `--publish` is set:
- **Confluence**: post comments back using the Confluence MCP.
- **Google Docs**: do **not** attempt to post comments via MCP (unreliable). Instead, produce a markdown file at `.temp/docs-review/<doc-title>-comments.md` listing each comment with its target section/paragraph and content. Present the file path and ask the user to add comments manually.
- **Local files**: the markdown review artifact is the final handoff.
