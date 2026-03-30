---
name: review-doc
description: "[full] [review-doc] Use when reviewing documents — local files, Confluence, or Google Docs. Supports standard and interactive modes"
user-invocable: true
argument-hint: "<document> [--mode standard|interactive|followup] [--publish] [--verbosity short|standard|detailed] [--help]"
allowed-tools: [Glob, Grep, Read, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
  mcp-servers: [detect-from-input]
workflow-tier: full
---

# Document Review

Use the shared DevKit child-agent contract in `references/agentic-teams.md`, the review flow in `references/review-pipeline.md`, the source routing rules in `references/source-routing.md`, and the output rules in `references/output-formats.md`.

This skill is review-only. Do not revise the source document in place. Produce a markdown review artifact, post comments to the platform, or both — depending on the selected stage.

## Help

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `<document>` | required | Path to local file, Confluence URL, or Google Docs URL |
| `--mode` | `auto` | Review mode: `standard` (default for local files), `interactive` (accept/edit/reject each finding), `followup` (reconcile prior comments, check resolutions, reply to threads), `auto` (detect from existing comments) |
| `--publish` | off | Post comments back to the source platform (Confluence or Google Docs) |
| `--verbosity` | `standard` | Output detail level: `short` (summary only), `standard` (findings + summary), `detailed` (full artifact with all findings) |
| `--help` | — | Show this help section and exit |

### Behavior Variations

- **Standard mode** (default for local files): Non-mutating review that produces a markdown artifact. Use `--publish` to also post comments to the platform.
- **Interactive mode** (`--mode interactive`): Presents each finding for user approval before posting. Only works with Confluence or Google Docs URLs.
- **Follow-up mode** (`--mode followup`): Re-reviews a document that was previously reviewed. Reconciles prior comments, checks if issues were addressed, evaluates author replies, and posts only new or unresolved findings.
- **Auto mode** (default for platform URLs): Detects prior review comments by the current user. If found, uses follow-up mode; otherwise, uses interactive mode.

### Examples

```
/review-doc ./docs/architecture.md
/review-doc https://company.atlassian.net/wiki/spaces/ENG/pages/12345 --publish
/review-doc https://docs.google.com/document/d/abc123 --mode interactive
/review-doc https://docs.google.com/document/d/abc123 --mode followup
/review-doc ./spec.md --verbosity detailed
```

## Preflight

Before loading the document body or comments, run:

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

For Confluence and Google Docs, follow that with one lightweight MCP read of the page or document metadata so connectivity is confirmed before the review team starts:

- Confluence -> `mcp__atlassian-confluence__confluence_get_page`
- Google Docs -> `mcp__google-drive__getDocumentInfo`

Load references: `references/workflow-6phase.md`, `references/agentic-teams.md`, `references/principal-engineer.md`, `references/communication-style.md`, `references/preflight.md`, `references/output-formats.md`.

## Stage Selection

| Condition | Stage File | Behavior |
|-----------|-----------|----------|
| `--mode standard` or local file default | `stages/standard.md` | Non-mutating review, produces markdown artifact |
| `--mode interactive` | `stages/interactive.md` | Interactive loop: accept/edit/reject/skip findings, then post to platform |
| `--mode followup` | `stages/followup.md` | Reconcile prior comments, check resolutions, evaluate replies, post remaining |
| `--mode auto` (platform URL default) | Auto-detect | Check for prior review comments by current user. If found -> `stages/followup.md`; otherwise -> `stages/interactive.md` |

Load and follow the selected stage file after preflight completes.

## Phase Applicability

| Phase | Applies | Skill-Specific Notes |
|-------|---------|----------------------|
| 0. Intent Expansion | yes | Confirm the goal, assumptions, required tools, and success criteria before acting |
| 1. Research & Options | yes | Analyze scope, detect source type, load guidelines |
| 2. Approach Selection | skip | Direct execution after early confirmation |
| 3. Planning | skip | Direct execution |
| 4. Execute | yes | Produce the review using parallel child agents |
| 5. Validate & Learn | yes | Verify review completeness, accuracy, and actionability |

## Output Format

All output is markdown by default. Structure varies by stage — see the loaded stage file for the exact format.

## Adjacent Skills

- See the parent router skill for related skills
