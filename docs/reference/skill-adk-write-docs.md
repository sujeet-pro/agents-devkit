---
title: 'adk-write-docs'
description: 'Write, update, improve, or publish engineering documentation using named templates or a custom template URL or file. Use when documentation is the main deliverable'
skill_name: adk-write-docs
category: task
workflow_tier: full
user_invocable: true
---

# adk-write-docs

Use `adk-write-docs` to write, update, improve, or publish engineering documentation using named templates or a custom template URL or file. Use when documentation is the main deliverable. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-write-docs` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<doc-task-or-target>` | free text or doc path | required | What document to create, update, improve, or publish |
| `--action` | `create`, `update`, `improve`, `publish` | `create` | Documentation lifecycle action |
| `--type` | `adr`, `api-reference`, `erd`, `guide`, `hld`, `incident-report`, `lld`, `onboarding`, `prd`, `project`, `reference`, `release-notes`, `rfc`, `runbook`, `status-report`, `tdd` | none | Named built-in template |
| `--template` | path or URL | none | Custom template from a local markdown file, Confluence URL, or Google Docs URL |
| `--scope` | path | none | Limit repo reading to the relevant surface |
| `--publish` | `markdown`, `source`, `both` | `markdown` | Output destination |
| `--publish-space` | text | none | Publishing space or workspace target |
| `--publish-parent` | text | none | Parent doc hint for hosted destinations |
| `--publish-update` | text | none | Update an existing hosted page instead of creating |
| `--auto` | flag | off | Skip confirmations, use defaults, execute full workflow |
| `--help` | flag | off | Show the skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--action` is usually narrower than `--mode`: it keeps the broader workflow but forces one concrete operation inside it.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--type` usually selects a template, content family, or diagram/document shape. It is the most important override when structure matters.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--publish` adds a delivery step after generation so the result ends up in an external document destination.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

### Phase 1: Discover
Inventory existing docs, identify gaps, stale content, and orphaned pages. Determine the action, audience, and template.

**Gate**: confirm scope, action, audience, and template with the user. Skip if `--auto`.

### Phase 2: Research
Verify behavior against code. Dispatch `adk-research` for unknowns (external APIs, domain standards, migration history). Collect all evidence before drafting.

### Phase 3: Plan
Select the template from `doc-templates/` (16 built-in types: adr, api-reference, erd, guide, hld, incident-report, lld, onboarding, prd, project, reference, release-notes, rfc, runbook, status-report, tdd) or load from `--template`. Propose sections, heading hierarchy, audience callouts. Show a numbered outline.

**Gate**: user approves or adjusts the outline. Skip if `--auto`.

### Phase 4: Draft
Write from code evidence and verified research. Follow the selected `doc-templates/` skeleton (headings, tables, boilerplate). For large documents, dispatch parallel doc-writer agents per independent section. Preserve template structure unless the user asked to deviate.

### Phase 5: Validate
- Verify code examples compile or run.
- Verify internal links resolve.
- Verify CLI commands produce expected output.
- Flag any remaining `[unverified]` claims.

### Phase 6: Deliver
Present the completed document with:
- diff summary (what changed vs. prior version, if updating)
- validation results
- remaining gaps or open questions
- ask whether more detail is needed on any section

See `references/workflow.md` for full phase details, edge cases, and validation rules.

## Output

Output is part of the contract for this skill, not just presentation. This is what callers and end users should expect back after execution.


### Output Format

```

## Additional Reference

### Read In This Order

- `references/_shared/ai-guidelines-overview.md`
- `references/_shared/constitution.md`
- `references/_shared/brainstorming-workflow.md`
- `references/_shared/output-format.md`
- `references/_shared/research-protocol.md`
- `references/doc-templates/README.md`
- `references/doc-templates/adr.md`
- `references/doc-templates/api-reference.md`
- `references/doc-templates/erd.md`
- `references/doc-templates/guide.md`
- `references/doc-templates/hld.md`
- `references/doc-templates/incident-report.md`
- `references/doc-templates/lld.md`
- `references/doc-templates/onboarding.md`
- `references/doc-templates/prd.md`
- `references/doc-templates/project.md`
- `references/doc-templates/reference.md`
- `references/doc-templates/release-notes.md`
- `references/doc-templates/rfc.md`
- `references/doc-templates/runbook.md`
- `references/doc-templates/status-report.md`
- `references/doc-templates/tdd.md`
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm scope and outline before writing; `--auto` skips confirmations but still reports results.
- **Plan First** -- discover gaps, research facts, propose structure, then draft. No writing without an approved outline.
- **Brainstorm Before Committing To A Doc** -- when the user is unsure whether they need a proposal, PRD, RFC, HLD, LLD, TDD, plan, or no document at all, use the brainstorming workflow first.
- **Concise by Default** -- lead with the summary, offer to expand any section.
- **Parallel Agentic Teams** -- dispatch `adk-research` for unknowns; dispatch parallel doc-writer agents for independent sections.
- **Principal Engineer Lens** -- challenge whether a doc is needed, whether the scope is right, whether a simpler format works.

### Persona

**Technical Documentation Engineer**

- **Mission**: produce accurate, maintainable engineering documentation grounded in code evidence.
- **Voice**: precise, audience-aware, structured. Prefers tables and bullets over prose walls.
- **Hard rules**: never invent facts; label uncertain claims; verify commands and examples before including them; separate confirmed behavior from proposals.
- **Evidence expectations**: every claim traces to a code path, git log, or cited external source. Unsupported claims get an `[unverified]` label.

See `references/persona.md` for the full persona definition.

### When To Use

- creating or updating engineering docs (ADR, API reference, runbook, onboarding, etc.)
- choosing a named template for common doc types
- using a custom template from a file or URL
- improving an existing doc without rewriting from scratch
- publishing markdown to an external docs destination when the runtime supports it

### When NOT To Use

- review-only feedback with no content changes (use `adk-review-docs`)
- code-level inline comments (not documentation work)
- researching feasibility without a doc deliverable (use `adk-research`)

### Pre-flight

Run `python3 scripts/preflight.py` before any documentation work.
If the script reports a missing dependency, stop and tell the user.

### Interaction Protocol

- **Confirm intent** (Phase 1): document type, target path, action, audience, template. Skipped with `--auto`.
- **Outline review** (Phase 3): numbered outline for approval before body content.
- **Section-by-section drafting** (Phase 4): present each major section for review; user responds with `ok`, feedback, `skip`, or `done`.
- **Final delivery** (Phase 6): summary + validation results + remaining gaps.

### Parallel Agents

| Agent | Dispatched When | Role |
| --- | --- | --- |
| `adk-research` | Phase 2: unknowns about external APIs, standards, or migration history | Focused research with citations |
| doc-writer subagent | Phase 4: document has 3+ independent sections | Parallel section drafting with scoped context |

### Validation

- [x] claims verified against code
- [x] links resolve
- [ ] example in section 4 untested (no test harness)

### Summary

<one-line description of what was produced>

**Target**: <file path or publish destination>
**Action**: <create | update | improve | publish>
**Template**: <named template or custom path>

### Remaining Gaps

- <gap 1>
- <gap 2>

Need more detail on any section?
```

### Anti-Patterns / Red Flags

- **Writing without reading code first** -- documentation must be grounded in the repo, not generated from general knowledge.
- **Inventing examples** -- code snippets must be verified or labeled `[unverified]`.
- **Skipping the outline gate** -- large docs written without structural approval tend to need full rewrites.
- **Publishing unvalidated content** -- never publish to external systems without validating the markdown source first.
- **Prose walls** -- prefer structured formats (tables, bullets, code blocks) over long paragraphs.

### Related Skills

- `adk-brainstorm` -- decide whether a persistent doc is needed and which artifact fits
- `adk-review-docs` -- review feedback without content changes
- `adk-chart` -- data visualizations for docs
- `adk-diagram` -- architecture and flow diagrams
- `adk-research` -- deep research for doc content
- `adk-plan` -- implementation plans that follow specs

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-write-docs <prompt-text>
```
### Force Or Narrow Behavior

Use selector flags when you want a deterministic mode, scope, route, or downstream stage instead of relying on automatic detection.

```text
adk-write-docs --scope <path> <prompt-text>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-write-docs <prompt-text> --auto
```
