---
name: adk-docs-crud
description: "adk - [full] [docs] Manage documentation lifecycle — create, update, improve, respond to comments"
user-invocable: true
argument-hint: "<action: create|update|improve|comment-reply> <path> [--auto]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git]
workflow-tier: full
---

# Documentation CRUD

Manage individual documentation pages through their lifecycle. The user owns these docs — this skill helps create new pages, update existing ones based on code changes, improve quality, and respond to review comments.

For bulk documentation generation, use `/adk:docs-repo`. For review-only feedback, use `/adk:docs-review`. For formal documents like ADRs or RFCs, use `/adk:docs-write`.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always | 6-phase workflow: intent → research → approach → plan → execute → validate. Complexity-adaptive skipping. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics over abstractions. |
| `/adk:preflight-check` | before work | Run preflight.py for MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. Markdown default, Confluence/Google Docs when requested. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents. Standard doc team: source analyst, outline editor, fact checker, code/diagram specialist, publisher. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |
| `/adk:confluence` | when target is Confluence | Confluence REST API via `curl` — page CRUD, comments, attachments. Uses `CONFLUENCE_*` from `~/.zshenv`. Supplements MCP connector for unsupported operations. |
| `/adk:jira` | when context references Jira | Jira REST API via `curl` — issues, comments, search, projects, sprints. Uses `JIRA_*` from `~/.zshenv`. Supplements MCP connector for unsupported operations. |

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
| `<action>` | `create`, `update`, `improve`, `comment-reply` | required | The lifecycle action to perform |
| `<path>` | file path, directory, or URL | required | Target document or location for new document |
| `--auto` | flag | off | Apply changes without interactive approval (use with caution) |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section and exit |

### Actions

| Action | Purpose | Input | Output |
|--------|---------|-------|--------|
| `create` | Create a new documentation page | Target directory + topic | New markdown file with proper structure |
| `update` | Update a doc based on code changes | Existing doc path | Updated doc with outdated sections refreshed |
| `improve` | Review a doc and apply improvements | Existing doc path | Improved doc with clarity/completeness fixes |
| `comment-reply` | Respond to comments on a doc | Doc path or PR URL | Updated doc + comment replies |

### Behavior Variations

- **`create`**: Interactive page creation. Asks for title, section placement, and content outline. If pagesmith format is detected, creates folder/README.md structure with proper frontmatter and updates the parent meta.json5.
- **`update`**: Diff-driven update. Compares the doc against current code to find outdated information — stale API signatures, removed config options, changed behavior. Suggests specific updates.
- **`improve`**: Quality-focused pass. Runs a focused quality check (clarity, examples, structure) and suggests concrete improvements. Applies accepted changes in-place.
- **`comment-reply`**: Comment triage. Reads comments from PR reviews, Confluence inline comments, or Google Docs suggestions. Categorizes each as fix-needed, discussion, or resolved. Applies fixes, writes reply text.
- **`--auto`**: Skips interactive approval. All proposed changes are applied directly. Useful for CI-driven doc updates.

### Examples

```
/adk:docs-crud create docs/guide/authentication
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

## Phase Applicability

| Phase | Applies | Notes |
|-------|---------|-------|
| 0. Intent Expansion | yes | Confirm the action, target, and scope |
| 1. Research & Options | yes | Read current doc state, scan related code, identify changes needed |
| 2. Approach Selection | conditional | Only for `create` when section placement is ambiguous |
| 3. Planning | conditional | Only for `create` when the page has multiple sections to outline |
| 4. Execute | yes | Perform the action — create, update, improve, or reply |
| 5. Validate & Learn | yes | Verify the result — links work, code examples match, frontmatter valid |

## Action Workflows

### Create

**Phase 0**: Confirm:
- Page topic and title
- Target location in the doc tree
- Audience and depth (overview vs deep-dive)

**Phase 1**: Research:
- Scan the codebase for relevant source material (types, functions, tests, comments)
- Read adjacent docs to match voice, depth, and cross-reference conventions
- If pagesmith: read the section's meta.json5 to determine the next `order` value

**Phase 2** (conditional): If the section placement is ambiguous (e.g., guide vs reference), present options and confirm.

**Phase 3** (conditional): For substantial pages, present a section outline for approval before writing.

**Phase 4**: Generate the page:
- Create the file with proper structure (folder/README.md or flat file)
- Add frontmatter if pagesmith detected
- Write content using the researched source material
- Update the parent meta.json5 if creating a new section
- Add cross-references to related pages

**Phase 5**: Validate:
- Verify all code examples match actual source
- Check internal links resolve
- Confirm frontmatter fields are correct
- Print the created file path and a content summary

### Update

**Phase 0**: Confirm the target document and what triggered the update (code change, version bump, new feature).

**Phase 1**: Research:
- Read the current document
- Diff against the corresponding source code to identify stale content
- Detect: renamed APIs, changed signatures, removed options, new parameters, updated defaults
- Produce a change list: what's outdated and what should replace it

**Phase 4**: Apply updates:
- Present each proposed change with before/after comparison
- Wait for user approval per change (unless `--auto`)
- Apply approved changes in-place using targeted edits
- Preserve the document's existing voice and structure

**Phase 5**: Validate:
- Re-read the updated document
- Verify all updated references match current code
- Check no broken links were introduced
- Print a summary of changes applied

### Improve

**Phase 0**: Confirm the target document and improvement goals (general quality, or specific focus like "better examples").

**Phase 1**: Research:
- Read the document thoroughly
- Run a focused quality assessment across: clarity, structure, examples, completeness, formatting
- Cross-reference code examples with source for accuracy
- Identify concrete improvement opportunities

**Phase 4**: Apply improvements:
- Present each suggested improvement with rationale
- Categories: clarity (rewrite unclear passages), examples (add/fix code examples), structure (reorder sections, add headings), completeness (add missing information), formatting (fix code blocks, add alerts)
- Wait for user approval per improvement (unless `--auto`)
- Apply accepted improvements in-place

**Phase 5**: Validate:
- Re-read the improved document
- Verify improvements didn't introduce new issues
- Print a before/after quality summary

### Comment-Reply

**Phase 0**: Confirm the comment source and target document.

**Phase 1**: Research:
- Read all comments on the document (from PR review, Confluence inline comments, Google Docs suggestions)
- Read the current document content
- Categorize each comment:
  - **fix-needed**: a factual error, broken example, or missing information — requires a doc change
  - **discussion**: an opinion, question, or design choice — requires a reply but may not need a doc change
  - **resolved**: already addressed or no longer applicable — mark as resolved

**Phase 4**: Process comments:
- For fix-needed: propose a doc edit that addresses the comment, show before/after, apply on approval
- For discussion: draft a reply that addresses the point (agree, disagree with rationale, or ask for clarification)
- For resolved: draft a brief resolution note
- Present all proposed actions for user approval (unless `--auto`)

**Phase 5**: Validate:
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

## Output Format

Output varies by action. All actions end with a concise summary. Adapt verbosity based on `--verbosity`:

- **short**: One-line status (e.g., "Created docs/guide/auth/README.md with 4 sections")
- **standard**: Action summary with change list
- **detailed**: Full change list with before/after comparisons and rationale

## Adjacent Skills

- `/adk:docs-repo` — bulk documentation generation for the entire repository
- `/adk:docs-review` — review-only feedback without modifications
- `/adk:docs-write` — formal engineering documents (ADRs, RFCs, specs)
- `/adk:diagram` — generate diagrams to embed in documentation
