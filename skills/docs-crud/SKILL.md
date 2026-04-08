---
name: docs-crud
description: "adk - [full] [docs] Manage documentation lifecycle — create, update, improve, respond to comments"
user-invocable: true
argument-hint: "<action: create|update|improve|comment-reply> <path> [--type tdd|hld|lld|prd|erd|adr|rfc|runbook|incident-report|status-report|api-reference|onboarding|release-notes|project] [--template <path-or-url>] [--auto]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3, curl, jq]
  npm-packages: [@pagesmith/docs]
workflow-tier: full
maturity: stable
workflow-family: standard-task
---

# Documentation CRUD

Manage individual documentation pages through their lifecycle. The user owns these docs — this skill helps create new pages, update existing ones based on code changes, improve quality, and respond to review comments.

For bulk documentation generation, use `/adk:docs-repo`. For review-only feedback, use `/adk:docs-review`. For formal documents like ADRs or RFCs, use `/adk:docs-write`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow --family standard-task` | always | Standard Task workflow: confirm → research → execute → validate. For tasks with known approach that benefit from context scan. `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before work | Run preflight.py for MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Markdown default, Confluence/Google Docs when requested. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents. Standard doc team: source analyst, outline editor, fact checker, code/diagram specialist, publisher. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |
| `/adk:confluence` | when target is Confluence | Confluence REST API via `curl` — page CRUD, comments, attachments. Uses `CONFLUENCE_*` from `~/.zshenv`. Supplements MCP connector for unsupported operations. |
| `/adk:jira` | when context references Jira | Jira REST API via `curl` — issues, comments, search, projects, sprints. Uses `JIRA_*` from `~/.zshenv`. Supplements MCP connector for unsupported operations. |
| `/adk:docs-guidelines` | when `--type` is set | Load type-specific document writing guidelines for quality rules. |
| `/adk:diagram` | when doc needs diagrams | Generate diagrams (Mermaid, Excalidraw, draw.io, Graphviz) and render to SVG/PNG for embedding. |
| `/adk:chart` | when doc needs data charts | Generate charts from data (bar, line, pie, scatter, etc.) and render to SVG/PNG for embedding. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `<action>` | `create`, `update`, `improve`, `comment-reply` | required | The lifecycle action to perform |
| `<path>` | file path, directory, or URL | required | Target document or location for new document |
| `--type` | `tdd`, `hld`, `lld`, `prd`, `erd`, `adr`, `rfc`, `runbook`, `incident-report`, `status-report`, `api-reference`, `onboarding`, `release-notes`, `project` | auto-detect | Document type — loads matching template skeleton |
| `--template` | file path or URL | none | Custom template — overrides `--type` template. Supports local markdown, Confluence URL, Google Docs URL |
| `--auto` | flag | off | Apply changes without interactive approval (use with caution) |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--format` | `markdown`, `confluence`, `google-doc`, `pdf`, `docx` | `markdown` | Output format for the final document |
| `--help` | flag | off | Show this help section and exit |

### Actions

| Action | Purpose | Input | Output |
|--------|---------|-------|--------|
| `create` | Create a new documentation page | Target directory + topic | New document with proper structure |
| `update` | Update a doc based on code changes | Existing doc path | Updated doc with outdated sections refreshed |
| `improve` | Review a doc and apply improvements | Existing doc path | Improved doc with clarity/completeness fixes |
| `comment-reply` | Respond to comments on a doc | Doc path or PR URL | Updated doc + comment replies |

### Behavior Variations

- **`create`**: Interactive page creation. If `--type` is set, loads the matching template from `references/doc-templates/`. If `--template` is provided, reads the custom template. Without either, creates a plain page and asks for title, section placement, and content outline. If pagesmith format is detected, creates folder/README.md structure with proper frontmatter and updates the parent meta.json5.
- **`create --type tdd`**: Loads the TDD template skeleton, confirms scope and audience, runs research on the topic, collates findings into the template sections, generates diagrams for architecture/data-flow sections, generates charts for any metrics/performance sections, and produces the complete document.
- **`create --template <url>`**: Fetches the template from the URL, extracts its heading structure and placeholder patterns, and uses it as the skeleton. Merges with type-specific quality rules if `--type` is also set.
- **`update`**: Diff-driven update. Compares the doc against current code to find outdated information — stale API signatures, removed config options, changed behavior. Suggests specific updates.
- **`improve`**: Quality-focused pass. Runs a focused quality check (clarity, examples, structure) and suggests concrete improvements. Applies accepted changes in-place.
- **`comment-reply`**: Comment triage. Reads comments from PR reviews, Confluence inline comments, or Google Docs suggestions. Categorizes each as fix-needed, discussion, or resolved. Applies fixes, writes reply text.
- **`--auto`**: Skips interactive approval. All proposed changes are applied directly. Useful for CI-driven doc updates.

### Document Type Aliases

| Alias | Maps To |
|-------|---------|
| `tech-spec`, `tech-design`, `design-doc` | `tdd` |
| `high-level-design`, `architecture` | `hld` |
| `low-level-design`, `detailed-design` | `lld` |
| `product-requirements`, `product-spec` | `prd` |
| `engineering-requirements`, `requirements` | `erd` |
| `decision-record`, `architecture-decision` | `adr` |
| `request-for-comments`, `proposal` | `rfc` |
| `ops-runbook`, `playbook` | `runbook` |
| `postmortem`, `incident-postmortem` | `incident-report` |
| `sprint-report`, `weekly-report`, `progress-report` | `status-report` |
| `api-docs`, `api-doc`, `endpoint-reference` | `api-reference` |
| `getting-started`, `new-hire`, `setup-guide` | `onboarding` |
| `changelog`, `release`, `what's-new` | `release-notes` |
| `readme`, `project-docs` | `project` |

### Examples

```
/adk:docs-crud create docs/design/ --type tdd
/adk:docs-crud create docs/requirements/ --type erd
/adk:docs-crud create docs/prd/ --type prd
/adk:docs-crud create docs/design/auth-service.md --type hld
/adk:docs-crud create docs/reports/ --type incident-report
/adk:docs-crud create docs/ --type status-report
/adk:docs-crud create docs/ --template https://company.atlassian.net/wiki/spaces/ENG/pages/99999
/adk:docs-crud create docs/ --template docs/templates/custom-template.md
/adk:docs-crud update docs/reference/api/README.md
/adk:docs-crud improve docs/guide/getting-started/README.md
/adk:docs-crud comment-reply docs/guide/configuration/README.md
/adk:docs-crud update docs/reference/ --auto
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

After dependency checks:

1. Detect documentation format by checking for `pagesmith.config.json5` in the project root.
2. If present, read the config to understand the content directory, section structure, and navigation.
3. For `create`: verify the target directory exists and identify the parent section's meta.json5.
4. For `update`/`improve`: verify the target file exists and read its current contents.
5. For `comment-reply`: identify the comment source (PR review, Confluence, Google Docs) and verify access.

## Format Detection

| Condition | Format | Behavior |
|-----------|--------|----------|
| `pagesmith.config.json5` exists | pagesmith | Use folder/README.md convention, add frontmatter, manage meta.json5 |
| No config file | markdown | Plain markdown files, no frontmatter, no meta.json5 |

### Pagesmith Conventions

When pagesmith format is detected:

- New pages use the folder/README.md convention: `docs/guide/auth/README.md`, not `docs/guide/auth.md`
- Every page gets YAML frontmatter with `title`, `description`, and `order`
- Section folders get `meta.json5` with `label` and `order`
- Use the full @pagesmith/core markdown feature set:
  - GFM: tables, strikethrough, task lists, autolinks, footnotes
  - GitHub alerts: `> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`
  - Math: `$inline$` and `$$display$$` where relevant
  - Expressive Code: syntax highlighting with language tags, titles, `mark`/`ins`/`del`, `collapse`
  - Smart typography: standard quotes and dashes (renderer handles curly quotes, em dashes, ellipses)

When no pagesmith config exists: use the same markdown features but omit frontmatter and meta.json5 entirely.

## Template System

### Built-in Templates

When `--type` is provided, load the matching template from `references/doc-templates/<type>.md`. The template provides:

- **Document skeleton**: All required sections with heading hierarchy
- **Placeholder text**: `[bracketed instructions]` indicating what to fill in
- **Metadata block**: Standard header with document ID, status, owner, dates
- **Diagram placeholders**: `<!-- DIAGRAM: description -->` markers where diagrams should be generated
- **Chart placeholders**: `<!-- CHART: type | data-description -->` markers where data charts should be generated
- **Review tracker**: Table for tracking reviewers and approval status
- **Example tables**: Pre-structured tables for requirements, risks, metrics, etc.

### Custom Templates

When `--template <path-or-url>` is provided:

1. **Read the template** — local file via `Read`, Confluence page via MCP or API, Google Doc via MCP
2. **Extract structure** — headings, section order, placeholder text (`[TODO: ...]`, `<describe ...>`), tables, and boilerplate
3. **Merge with type guidance** — if `--type` is also set, use `/adk:docs-guidelines` for content quality rules but the custom template for structure. If `--type` is not set, infer the type from the template's structure.
4. **Generate section-by-section** — during Phase 4, produce each section following the template's layout
5. **Preserve boilerplate** — keep any template content that is not a placeholder (legal disclaimers, standard headers, org-specific formatting)

Template sources:
- **Local path**: read the file directly
- **Confluence URL**: read via `mcp__atlassian-confluence__confluence_get_page` or API fallback
- **Google Docs URL**: read via `mcp__google-drive__getDocument` or API fallback

### Type Detection from Keywords

If `--type` is not set, detect the type from the user's prompt using keyword matching:

| Keywords | Detected Type |
|----------|--------------|
| tech spec, technical design, design doc, TDD | `tdd` |
| high level design, HLD, system architecture | `hld` |
| low level design, LLD, detailed design, component design | `lld` |
| product requirements, PRD, product spec | `prd` |
| engineering requirements, ERD, requirements document | `erd` |
| architecture decision, ADR | `adr` |
| RFC, request for comments, proposal | `rfc` |
| runbook, playbook, ops guide, incident response guide | `runbook` |
| incident report, postmortem, outage report | `incident-report` |
| status report, sprint report, weekly report, progress | `status-report` |
| API reference, API documentation, endpoint docs | `api-reference` |
| onboarding, getting started, new hire, setup guide | `onboarding` |
| release notes, changelog, what's new | `release-notes` |
| README, project documentation | `project` |

## Action Workflows

### Create

**1. Confirm**: Confirm:
- Page topic and title
- Target location in the doc tree
- Document type (explicit `--type`, detected from keywords, or general)
- Audience and depth (overview vs deep-dive)
- Whether a custom template is provided

**2. Research**: Research:
- If `--type` is set: load the template from `references/doc-templates/<type>.md`
- If `--template` is set: read and extract the custom template structure
- Load type-specific quality guidelines via `/adk:docs-guidelines` if available
- Scan the codebase for relevant source material (types, functions, tests, comments)
- Read adjacent docs to match voice, depth, and cross-reference conventions
- If pagesmith: read the section's meta.json5 to determine the next `order` value
- Identify sections that need diagrams or charts based on template placeholders

**3. Execute**: Generate the document:
- Create the file with proper structure (folder/README.md or flat file)
- Add frontmatter if pagesmith detected
- Write content section-by-section following the template
- **Generate diagrams** for `<!-- DIAGRAM: description -->` placeholders:
  - Invoke `/adk:diagram` with the description to generate diagram source files
  - Render to SVG (and PNG if the output format requires raster images)
  - For PDF/DOCX output: convert SVG to PNG using `diagramkit render --format png`
  - Embed the rendered image in the document with alt text
- **Generate charts** for `<!-- CHART: type | data-description -->` placeholders:
  - Invoke `/adk:chart` with the chart type and data
  - Render to SVG (and PNG if needed)
  - Embed the rendered chart in the document
- Update the parent meta.json5 if creating a new section
- Add cross-references to related pages

**4. Validate**: Validate:
- Verify all code examples match actual source
- Check internal links resolve
- Confirm frontmatter fields are correct
- Verify all diagrams and charts rendered successfully
- Print the created file path and a content summary

### Update

**1. Confirm**: Confirm the target document and what triggered the update (code change, version bump, new feature).

**2. Research**: Research:
- Read the current document
- Diff against the corresponding source code to identify stale content
- Detect: renamed APIs, changed signatures, removed options, new parameters, updated defaults
- Produce a change list: what's outdated and what should replace it
- Check if existing diagrams need updating

**3. Execute**: Apply updates:
- Present each proposed change with before/after comparison
- Wait for user approval per change (unless `--auto`)
- Apply approved changes in-place using targeted edits
- Re-render diagrams if the architecture has changed
- Preserve the document's existing voice and structure

**4. Validate**: Validate:
- Re-read the updated document
- Verify all updated references match current code
- Check no broken links were introduced
- Verify diagrams are current
- Print a summary of changes applied

### Improve

**1. Confirm**: Confirm the target document and improvement goals (general quality, or specific focus like "better examples").

**2. Research**: Research:
- Read the document thoroughly
- Run a focused quality assessment across: clarity, structure, examples, completeness, formatting
- Cross-reference code examples with source for accuracy
- Identify concrete improvement opportunities
- Suggest diagrams or charts that could enhance understanding

**3. Execute**: Apply improvements:
- Present each suggested improvement with rationale
- Categories: clarity (rewrite unclear passages), examples (add/fix code examples), structure (reorder sections, add headings), completeness (add missing information), formatting (fix code blocks, add alerts), visuals (add diagrams or charts)
- Wait for user approval per improvement (unless `--auto`)
- Apply accepted improvements in-place

**4. Validate**: Validate:
- Re-read the improved document
- Verify improvements didn't introduce new issues
- Print a before/after quality summary

### Comment-Reply

**1. Confirm**: Confirm the comment source and target document.

**2. Research**: Research:
- Read all comments on the document (from PR review, Confluence inline comments, Google Docs suggestions)
- Read the current document content
- Categorize each comment:
  - **fix-needed**: a factual error, broken example, or missing information — requires a doc change
  - **discussion**: an opinion, question, or design choice — requires a reply but may not need a doc change
  - **resolved**: already addressed or no longer applicable — mark as resolved

**3. Execute**: Process comments:
- For fix-needed: propose a doc edit that addresses the comment, show before/after, apply on approval
- For discussion: draft a reply that addresses the point (agree, disagree with rationale, or ask for clarification)
- For resolved: draft a brief resolution note
- Present all proposed actions for user approval (unless `--auto`)

**4. Validate**: Validate:
- Verify all fix-needed comments have corresponding doc changes
- Verify all discussion comments have draft replies
- Print a summary:
  ```
  ## Comment Response Summary
  
  Comments processed: <n>
  - Fixed: <n>
  - Replied: <n>
  - Resolved: <n>
  
  Pending user review: <n>
  ```

## Diagram Integration

Documents frequently need visual aids. When creating or updating docs:

### Diagram Generation Pipeline

1. **Identify diagram needs** — scan template placeholders (`<!-- DIAGRAM: ... -->`) and section content for architecture, data flow, sequence, ER, or state diagrams
2. **Select engine** — invoke `/adk:diagram` which auto-detects the best engine:
   - **Mermaid**: sequence diagrams, ER diagrams, flowcharts, Gantt charts
   - **Excalidraw**: architecture overviews, hand-drawn style diagrams
   - **Graphviz**: dependency graphs, strict layout graphs
   - **draw.io**: network topology, BPMN, infrastructure diagrams
3. **Generate source** — create the diagram source file (`.mermaid`, `.excalidraw`, `.dot`, `.drawio`)
4. **Render** — use `diagramkit render <source-file>` to produce SVG output
5. **Convert to raster if needed** — for PDF, DOCX, or Confluence, render to PNG: `diagramkit render <source-file> --format png`
6. **Embed** — insert the rendered image in the document with descriptive alt text
7. **Keep both files** — store the editable source file alongside the rendered output for future updates

### Image Embedding Format

For markdown docs:
```markdown
![Architecture overview](./diagrams/architecture.svg)
```

For Confluence: upload as attachment and reference via `<ac:image>` tag.

## Chart Integration

Data-driven documents need charts for comparisons, metrics, and trends. When creating or updating docs:

### Chart Generation Pipeline

1. **Identify chart needs** — scan template placeholders (`<!-- CHART: type | data-description -->`) and section content for metrics, comparisons, trends, or performance data
2. **Prepare data** — create a CSV or JSON data file from the section content or research
3. **Select chart type** — match the data to the appropriate chart type (bar, line, pie, scatter, area, etc.)
4. **Generate** — invoke `/adk:chart` to render the chart to SVG/PNG
5. **Embed** — insert the rendered chart in the document

### When to Use Charts vs Tables

| Data Pattern | Use Chart | Use Table |
|-------------|-----------|-----------|
| Trends over time | Line/Area chart | No |
| Category comparisons | Bar chart | If ≤ 3 items |
| Part-of-whole | Pie/Donut chart | If ≤ 3 items |
| Correlations | Scatter plot | No |
| Performance metrics | Bar chart with targets | Also include table |
| Sprint velocity | Bar chart | Also include table |
| Budget/capacity projections | Line chart | Also include table |

## Output Format

Output varies by action and `--format`. All actions end with a concise summary. Adapt verbosity based on `--verbosity`:

- **short**: One-line status (e.g., "Created docs/guide/auth/README.md with 4 sections")
- **standard**: Action summary with change list
- **detailed**: Full change list with before/after comparisons and rationale

### Format-Specific Behavior

| Format | Diagrams | Charts | Embedding |
|--------|----------|--------|-----------|
| `markdown` | SVG (default) | SVG | `![alt](path)` |
| `confluence` | PNG (uploaded as attachment) | PNG (uploaded) | `<ac:image>` tag |
| `google-doc` | PNG (uploaded) | PNG (uploaded) | Inline image |
| `pdf` | PNG (embedded) | PNG (embedded) | Inline |
| `docx` | PNG (embedded) | PNG (embedded) | Inline |

## Adjacent Skills

- `/adk:docs-repo` — bulk documentation generation for the entire repository
- `/adk:docs-review` — review-only feedback without modifications
- `/adk:docs-write` — formal engineering documents (ADRs, RFCs, specs) with stages
- `/adk:diagram` — generate diagrams to embed in documentation
- `/adk:chart` — generate data charts to embed in documentation
- `/adk:docs-guidelines` — document writing quality guidelines per type
