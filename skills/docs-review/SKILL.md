---
name: adk-docs-review
description: "adk - [full] [docs] Review documentation — local files, Confluence, or Google Docs. Standard, interactive, and follow-up modes with multi-dimensional analysis."
user-invocable: true
argument-hint: "<path-or-url> [--mode standard|interactive|followup|auto] [--focus accuracy|completeness|clarity|style|all] [--publish] [--auto] [--verbosity short|standard|detailed]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
  mcp-servers: [detect-from-input]
workflow-tier: full
---

# Documentation Review

Review documentation files for accuracy, completeness, clarity, and style. Produces structured feedback with inline comments and actionable improvement suggestions. Supports local markdown files, entire `docs/` directories, Confluence pages, and Google Docs.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping for trivial/small tasks. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. Verbosity follows context. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. Detect source type and route to correct MCP. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Priority labels: Blocker, Critical, Should Have, May Have, Nitpick, Question. Cross-platform markdown safe for GitHub + Bitbucket. |
| `/adk:review-standards` | always (review skills) | Pipeline: intake → ingestion → parallel review → consolidation → output → postback. Canonical comment template with severity, confidence, concern, depth, dimension, guideline. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents with distinct roles. Standard team shapes: review, research, docs, diagram, security, migration, planning. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval, review findings, progress dashboard. |
| `/adk:confluence` | when target is Confluence | Confluence REST API via `curl` — page CRUD, comments, attachments. Uses `CONFLUENCE_*` from `~/.zshenv`. Supplements MCP connector for unsupported operations. |

This skill is review-only — it does not modify the source documents. Use `/adk:docs-crud` to apply fixes, or `/adk:docs-repo` to regenerate missing documentation.

## Reference Loading

Load reference files conditionally to minimize token usage:

| Reference | Load When |
|-----------|-----------|
| `workflow-6phase.md` | always (read only the section for the current phase) |
| `communication-style.md` | always |
| `preflight.md` | before preflight check |
| `output-formats.md` | when producing final output |
| `output-format-modes.md` | when producing final output |
| `principal-engineer.md` | Phase 0, complexity >= medium |
| `agentic-teams.md` | Phase 4, when launching child agents |
| `inline-interaction.md` | interactive phases, NOT --auto |
| `help-format.md` | when --help is passed |
| `project-guidelines.md` | Phase 1, when scanning project |
| `review-pipeline.md` | review skills only |
| `review-comment-template.md` | when posting review comments |
| `source-routing.md` | when target is external (PR, Confluence, Google Docs) |

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<path-or-url>` | file path, directory, Confluence URL, Google Docs URL | required | What to review. A single file, a directory of docs, or a platform URL |
| `--mode` | `standard`, `interactive`, `followup`, `auto` | `auto` | Review mode: `standard` (default for local files), `interactive` (accept/edit/reject each finding), `followup` (reconcile prior comments, check resolutions, reply to threads), `auto` (detect from existing comments) |
| `--focus` | `accuracy`, `completeness`, `clarity`, `style`, `all` | `all` | Focus the review on specific dimensions |
| `--publish` | flag | off | Post comments back to the source platform (Confluence or Google Docs) |
| `--auto` | flag | off | Skip interactive confirmation steps and proceed with recommended actions |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--confidence` | `0`-`100` | `80` | Minimum confidence threshold — only findings at or above this score are shown |
| `--help` | flag | off | Show this help section and exit |

### Review Dimensions

| Dimension | What It Checks |
|-----------|----------------|
| **Accuracy** | Facts match code. API signatures, config keys, CLI flags, endpoint paths, return types — all verified against the actual source. |
| **Completeness** | Missing topics. Undocumented public APIs, missing error handling docs, absent configuration options, no migration guides for breaking changes. |
| **Clarity** | Readability. Ambiguous phrasing, unclear antecedents, missing context, jargon without definition, overly complex sentences. |
| **Style** | Consistency. Heading hierarchy, code block formatting, alert usage, frontmatter correctness, terminology consistency across pages. |
| **Examples** | Quality and correctness of code examples. Runnable, up-to-date, properly highlighted, error handling shown. |

### Behavior Variations

- **Standard mode** (default for local files): Non-mutating review that produces a markdown artifact. Use `--publish` to also post comments to the platform.
- **Interactive mode** (`--mode interactive`): Presents each finding for user approval before posting. Only works with Confluence or Google Docs URLs. Interaction is inline in the agent conversation.
- **Follow-up mode** (`--mode followup`): Re-reviews a document that was previously reviewed. Reconciles prior comments, checks if issues were addressed, evaluates author replies, and posts only new or unresolved findings.
- **Auto mode** (default for platform URLs): Detects prior review comments by the current user. If found, uses follow-up mode; otherwise, uses interactive mode.
- **Single file**: Reviews one document in depth across all dimensions.
- **Directory**: Reviews all markdown files in the directory. Produces per-file findings plus a cross-cutting summary (consistency across files, missing cross-references, navigation gaps).
- **Focused review** (`--focus accuracy`): Deep-dives on a single dimension. More thorough than the `all` pass for that dimension.

### Examples

```
/adk:docs-review docs/
/adk:docs-review docs/guide/getting-started/README.md --focus accuracy
/adk:docs-review docs/reference/ --focus completeness --verbosity detailed
/adk:docs-review https://company.atlassian.net/wiki/spaces/ENG/pages/12345 --publish
/adk:docs-review https://docs.google.com/document/d/abc123 --mode interactive
/adk:docs-review https://docs.google.com/document/d/abc123 --mode interactive
/adk:docs-review https://docs.google.com/document/d/abc123 --mode followup
/adk:docs-review ./docs/architecture.md --verbosity detailed
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

After dependency checks:

1. Resolve the review target — local path, directory, or platform URL.
2. For local files: verify the path exists and identify all markdown files to review.
3. For platform URLs: verify MCP connectivity (Confluence via `mcp__atlassian-confluence__confluence_get_page`, Google Docs via `mcp__google-drive__getDocumentInfo`).
4. Check for `pagesmith.config.json5` — if present, add pagesmith-specific style checks (frontmatter validation, meta.json5 consistency, folder/README.md convention).
5. Scan for the corresponding source code to enable accuracy checks (look for `src/`, `lib/`, `packages/`, standard entry points).

## Stage Selection

| Condition | Stage File | Behavior |
|-----------|-----------|----------|
| `--mode standard` or local file default | `stages/standard.md` | Non-mutating review, produces markdown artifact |
| `--mode interactive` | `stages/interactive.md` | Interactive loop: accept/edit/reject/skip findings, then post to platform |
| `--mode followup` | `stages/followup.md` | Reconcile prior comments, check resolutions, evaluate replies, post remaining |
| `--mode auto` (platform URL default) | Auto-detect | Check for prior review comments by current user. If found -> `stages/followup.md`; otherwise -> `stages/interactive.md` |

Load and follow the selected stage file after preflight completes.

## Guideline Loading

Invoke the `/adk:coding` helper skill to detect the repo stack and load coding guidelines when the documentation contains code examples that need accuracy verification.

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm review target, focus dimensions, audience expectations |
| 1. Research & Options | yes | Read all docs, scan corresponding code, identify review scope |
| 2. Approach Selection | skip | Direct review execution after scope confirmation |
| 3. Planning | skip | Review agents launch directly |
| 4. Execute | yes | Parallel review agents produce findings |
| 5. Validate & Learn | yes | Deduplicate findings, rank by severity, produce final report |

## Common Workflow

### Phase 0: Intent Expansion

- Confirm the review target and scope
- Identify which dimensions to focus on (default: all)
- Detect pagesmith format — if present, include pagesmith-specific checks
- Confirm the audience: is this review for the doc author, a PR reviewer, or a team?

### Phase 1: Research & Options

Read the documentation and corresponding source code:

- **Doc reader**: reads all markdown files in scope, builds a content inventory (pages, headings, code examples, links, frontmatter)
- **Code scanner**: identifies public APIs, CLI commands, config schemas, types — the "source of truth" the docs should match
- **Cross-reference builder**: maps doc claims to code locations for the accuracy reviewer

### Phase 4: Execute

Launch review agents in parallel based on the selected focus:

**Accuracy reviewer** (when focus includes `accuracy` or `all`):
- Cross-references every API signature, config key, CLI flag, and endpoint path against actual code
- Verifies code examples compile/run conceptually (correct imports, valid syntax, realistic usage)
- Checks version numbers, dependency names, and external links
- Confidence-scored: each finding includes how certain the reviewer is

**Completeness reviewer** (when focus includes `completeness` or `all`):
- Compares the public API inventory against documented APIs — flags undocumented exports
- Checks for missing sections: error handling, edge cases, migration notes, troubleshooting
- Verifies every config option has a description and default value documented
- Checks cross-references: do guide pages link to relevant reference pages?

**Style reviewer** (when focus includes `style` or `all`):
- Checks heading hierarchy consistency (no skipped levels, consistent casing)
- Validates code block formatting (language tags, appropriate use of expressive code features)
- Verifies alert usage (correct alert type for the content: NOTE vs WARNING vs CAUTION)
- If pagesmith: validates frontmatter fields, meta.json5 consistency, folder/README.md structure
- Checks terminology consistency across pages (same concept = same term)

**Clarity reviewer** (when focus includes `clarity` or `all`):
- Flags ambiguous language, unclear antecedents, sentences requiring domain knowledge not established in the doc
- Identifies missing context: a concept used before it's defined, an acronym without expansion
- Checks for "wall of text" — long paragraphs without structure or visual breaks
- Evaluates whether a newcomer could follow the getting-started guide without prior knowledge

### Phase 5: Validate & Learn

Post-process all findings:

- Deduplicate findings across reviewers (same issue found by multiple agents)
- Rank by severity: `must-fix` > `should-fix` > `suggestion` > `nitpick`
- Group by file for readability
- Produce a summary with aggregate scores per dimension
- Present findings for human review — the user can accept or reject individual findings

## Output Format

### Per-File Findings

```markdown
### File: docs/guide/getting-started/README.md

**Line 12** [accuracy] [must-fix]: The install command is `npm install @foo/bar`, not `npm install foo-bar` as written.

**Line 34** [completeness] [should-fix]: Missing error handling example for the `connect()` function. The function throws `ConnectionError` on timeout — document this.

**Line 56** [clarity] [suggestion]: "Configure the service appropriately" is vague. Specify which config keys are required for a minimal setup.

**Line 78** [style] [nitpick]: Code block missing language tag. Add ` ```typescript ` for syntax highlighting.
```

### Summary

```markdown
## Documentation Review Summary

Target: docs/
Files reviewed: <count>
Total findings: <count>

| Dimension | Must-Fix | Should-Fix | Suggestion | Nitpick |
|-----------|----------|------------|------------|---------|
| Accuracy | <n> | <n> | <n> | <n> |
| Completeness | <n> | <n> | <n> | <n> |
| Clarity | <n> | <n> | <n> | <n> |
| Style | <n> | <n> | <n> | <n> |
| Examples | <n> | <n> | <n> | <n> |

### Top Issues
1. <highest severity finding>
2. <second highest>
3. <third highest>

### Next Steps
- Use `/adk:docs-crud improve <path>` to apply accepted suggestions
- Use `/adk:docs-repo` to generate documentation for undocumented APIs
```

## Pagesmith-Specific Checks

When `pagesmith.config.json5` is detected, add these style checks:

- Every page uses folder/README.md convention (not flat files)
- Frontmatter includes required fields: `title`, `description`
- `order` values are unique within each section
- Every section folder has a `meta.json5` with `label` and `order`
- Home page (`docs/README.md`) uses `layout: hero`
- No frontmatter on pages in non-pagesmith projects
- Markdown features use @pagesmith/core conventions (GitHub alerts, expressive code syntax)

## Adjacent Skills

- `/adk:docs-crud` — apply fixes and improvements from review findings
- `/adk:docs-repo` — generate documentation for undocumented areas
- `/adk:docs-write` — write formal engineering documents (ADRs, RFCs)
- `/adk:diagram` — create diagrams for documentation
