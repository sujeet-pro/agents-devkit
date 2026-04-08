---
name: deps-tracker
description: "adk - [full] [project] Track upstream dependencies and inspirations for ADK skills. Detect changes in referenced tools/libraries and update skills accordingly."
user-invocable: true
argument-hint: "<action: status|sync|add|remove|check> [--source <name>] [--auto]"
allowed-tools: [Glob, Grep, Read, Edit, Write, Bash, WebSearch, WebFetch, Agent]
dependencies:
  commands: [git, python3]
workflow-tier: full
maturity: stable
workflow-family: investigative-loop
workflow-family-overrides:
  status: quick-action
  check: quick-action
  docs-check: quick-action
  add: quick-action
  remove: quick-action
  sync: standard-task
---

# Dependency Tracker

Manages `manifest.json` at the repo root — the single source of truth for upstream sources that ADK skills copy or reference. Keeps skills in sync with their inspirations by detecting upstream changes, diffing mapped paths, and applying updates with user confirmation.

## Shared Skills

This skill uses shared helper skills. Load each skill's reference file ONLY when the condition in "Load When" is met. If a shared skill is not installed, use the inline summary as a fallback.

| Skill | Load When | Inline Fallback |
|-------|-----------|-----------------|
| `/adk:workflow` | always, family varies by action | Investigative Loop (default), Standard Task (`sync`), Quick Action (`status,check,docs-check,add,remove`). `--auto` skips confirmations. |
| `/adk:communication` | always | Lead with conclusion. Bullet points. No preamble. Concrete specifics. |
| `/adk:preflight-check` | before work | Run preflight.py for tool dependencies and MCP validation. |
| `/adk:output-format` | when producing output | short/standard/detailed verbosity. |
| `/adk:principal-engineer` | complexity >= medium | Five questions: need? simplest? alternatives? maintenance costs? clarity in 6 months? |
| `/adk:agentic-teams` | complexity >= medium AND parallel work needed | Launch 2+ child agents for parallel sync and diff analysis. |
| `/adk:interaction` | NOT --auto | Inline protocols for intent confirmation, approach selection, plan approval. |

## Helper Skill Resolution

Resolve shared behavior through **helper skills**, not by loading reference markdown files. Invoke the needed skill using either form: `/adk:<skill>` (Claude plugin) or `/<skill>` (skills.sh). The usual helpers are **workflow** (phase structure), **communication** (tone and structure), **preflight-check** (tool and MCP validation), **output-format** (verbosity and deliverable shape), **principal-engineer** (engineering bar), **agentic-teams** (child agents), and **interaction** (prompting and confirmations).

If a required helper skill is unavailable, print a warning and continue using the inline fallback summary in the Shared Skills table.

## Help

### Parameters

| Parameter | Values | Default | Description |
|-----------|--------|---------|-------------|
| `action` | `status`, `sync`, `add`, `remove`, `check`, `docs-check` | `status` | Primary action to perform |
| `--source` | `<name>` | all | Limit action to a single source entry in manifest.json |
| `--auto` | flag | off | Skip confirmations, apply all available updates |
| `--verbosity` | `short`, `standard`, `detailed` | `standard` | Output detail level |
| `--help` | flag | off | Show this help section |

### Behavior Variations

- **`status`**: Read-only. Show current tracking status for all sources — last sync timestamp, last commit, staleness estimate, and which skills depend on each source.
- **`sync`**: Standard Task workflow (confirm → research → execute → validate). Check upstream repos for changes, present diffs, and apply updates with user confirmation (or `--auto`).
- **`add`**: Guided workflow to add a new upstream source to manifest.json. Prompts for repo URL, type (copy/ref), source path, mapping, and which skills reference it.
- **`remove`**: Remove a tracked source from manifest.json. Confirms before deletion.
- **`check`**: Read-only. Check if any tracked sources have been updated since last sync. Reports what changed but does NOT apply changes. Use `sync` to apply.
- **`docs-check`**: Read-only. For each source with a `docs` field in manifest.json, fetch the `llms.txt` or `llms-full.txt` URL if available. Compare against the corresponding skill's current reference content. Report which tool docs have changed and which skills may need updating. Does NOT apply changes.

### Examples

```
/adk:deps-tracker status
/adk:deps-tracker docs-check
/adk:deps-tracker docs-check --source diagramkit
/adk:deps-tracker check --source diagramkit
/adk:deps-tracker sync --source pagesmith
/adk:deps-tracker sync --auto
/adk:deps-tracker add
/adk:deps-tracker remove --source superpowers
```

## Preflight

`python3 ${CLAUDE_SKILL_DIR}/scripts/preflight.py ${CLAUDE_SKILL_DIR}`

## Source Types

### type=copy

Files are copied verbatim from the upstream repo into local skill directories via a path mapping. `sync` clones/fetches the repo, diffs mapped paths against local copies, shows what changed, and applies updates (with user confirmation or `--auto`).

### type=ref

The upstream repo is an inspiration, not a direct copy source. `sync` fetches the latest commit, checks if referenced patterns have meaningfully changed, and flags skills that may need manual updating.

## Skill-to-Source Mapping

Which skills depend on which upstream sources:

| Source | Type | Skills |
|--------|------|--------|
| `diagramkit` | copy | `diagram-mermaid`, `diagram-excalidraw`, `diagram-drawio`, `diagram-graphviz`, `diagram` |
| `pagesmith` | ref | `docs-write`, `docs-repo`, `docs-review`, `docs-crud`, `docs-md` |
| `superpowers` | ref | `dev-build`, `plan`, `code-review-pr` |

This mapping is also encoded in `manifest.json` under each source's `mapping` (for copy) or `ref_skills` (for ref) fields.

## Action: status

> Quick Action workflow: confirm → execute → verify.

Read `manifest.json` and for each source, display:

```
Source: diagramkit (copy)
  Repo:        https://github.com/sujeet-pro/diagramkit
  Last Sync:   2026-03-27T05:02:50Z (10 days ago)
  Last Commit: 046363...
  Skills:      diagram-mermaid, diagram-excalidraw, diagram-drawio, diagram-graphviz, diagram
  Status:      ⚠ Potentially stale (>7 days since sync)
```

## Action: check

> Quick Action workflow: confirm → execute → verify.

For each source (or `--source` to filter):

1. `git ls-remote` the upstream repo to get the latest HEAD commit
2. Compare against `last_commit` in manifest.json
3. If different, report that updates are available — show commit count and date range
4. Do NOT clone, diff, or apply anything

Output a summary table:

```
| Source      | Type | Last Sync  | Upstream HEAD | Status      |
|-------------|------|------------|---------------|-------------|
| diagramkit  | copy | 2026-03-27 | a1b2c3d       | ⚠ 3 new commits |
| superpowers | ref  | 2026-03-27 | eafe962       | ✓ Up to date |
| pagesmith   | ref  | 2026-03-27 | 8c59bd5       | ✓ Up to date |
```

## Action: docs-check

> Quick Action workflow: confirm → execute → verify.

For each source with a `docs` field (or `--source` to filter):

1. Read the `docs` entries from manifest.json
2. For each tool with a `llms_txt` or `llms_full_txt` URL:
   - Fetch the URL content
   - Compare key sections against the corresponding skill's SKILL.md and reference files
   - Look for: new features, deprecated features, changed syntax, new diagram types, updated APIs
3. For each tool with only a `docs_url`:
   - Report the docs URL for manual review
   - Check if the URL responds (basic connectivity test)
4. Update `last_checked` timestamp in manifest.json for each checked source

Output a summary table:

| Tool | Source | llms.txt | Status | Skills to Review |
|------|--------|----------|--------|-----------------|
| mermaid | diagramkit | available | New features detected | diagram-mermaid |
| excalidraw | diagramkit | not available | Manual review needed | diagram-excalidraw |

## Action: sync

Standard Task workflow (confirm → research → execute → validate):

### 1. Confirm

Confirm which sources to sync and whether `--auto` is active. Show the check summary first so the user knows what will happen.

### 2. Research

For each source with available updates:

- Clone or fetch the upstream repo into a temp directory
- For `type=copy`: diff each mapped path (`source_path` → local path) to produce a concrete changeset
- For `type=ref`: compare the latest source against the referenced patterns, summarize meaningful changes

### 3. Execute

Present what changed and which skills are affected:

```
diagramkit (copy) — 3 new commits since last sync:
  Changed files:
    refs/mermaid/syntax.md → skills/diagram/references/mermaid/syntax.md (modified)
    refs/excalidraw/export.md → skills/diagram/references/excalidraw/export.md (new)
  Affected skills: diagram, diagram-mermaid, diagram-excalidraw
```

List the concrete file operations to perform. For `type=copy`, this is a list of files to copy/overwrite. For `type=ref`, this is a list of skills to flag for manual review.

- `type=copy`: Copy files from the cloned repo to local paths per the mapping. Update `last_sync` and `last_commit` in manifest.json.
- `type=ref`: Update `last_sync` and `last_commit` in manifest.json. Output a list of skills that should be manually reviewed against the new upstream.
- If `--auto` is NOT set, confirm before applying each source's changes.

### 4. Validate

- Verify copied files exist and match the upstream versions
- Confirm manifest.json was updated correctly
- Summarize what changed

## Action: add

> Quick Action workflow: confirm → execute → verify.

Interactive guided flow:

1. Prompt for repo URL
2. Prompt for type (`copy` or `ref`)
3. Prompt for `branch` (default: `main`)
4. Prompt for `source_path` within the upstream repo
5. If `type=copy`: prompt for path mapping (upstream path → local path)
6. Prompt for which skills reference this source
7. Prompt for notes
8. Write the new entry to manifest.json
9. Optionally run `check` on the new source immediately

## Action: remove

> Quick Action workflow: confirm → execute → verify.

1. Confirm the source exists in manifest.json
2. Show what will be removed (source entry and its metadata)
3. Confirm with the user (unless `--auto`)
4. Remove the entry from manifest.json

## Output Format

Use the output format appropriate to each action. Adapt verbosity based on `--verbosity`:

- **short**: One-line status per source
- **standard**: Full structured output as shown in the action sections above
- **detailed**: Standard output plus full diffs, commit messages, and file-level changelogs

## Adjacent Skills

- `/adk:setup` — install required CLI tools (git)
- `/adk:project` — broader project management, milestones, and roadmaps
- `/adk:research` — deep investigation of upstream changes or new sources to track
