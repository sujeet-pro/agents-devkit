# ADK Write Docs Workflow

## Phase 1: Discover

**Goal**: understand what exists, what is missing, and what the user needs.

**Steps**:
1. Inventory existing docs in the target area (glob for `*.md`, check `docs/` structure).
2. Identify stale content (docs older than recent code changes in the same area).
3. Identify gaps (code paths or features without corresponding documentation).
4. Determine the lifecycle action: `create`, `update`, `improve`, or `publish`.
5. Identify the audience and select or confirm the template.
6. If the user has not yet decided whether they need a doc or which artifact fits, run the shared brainstorming workflow first.

**Gate**: confirm scope, action, audience, and template with the user. Skip if `--auto`.

**Edge cases**:
- If the target path already exists and `--action create` is set, warn and suggest `update` instead.
- If `--type` and `--template` are both provided, `--template` takes precedence.
- If no template matches, offer to proceed with a generic structure or ask the user.

## Phase 2: Research

**Goal**: collect all evidence needed for accurate documentation.

**Steps**:
1. Read source code in `--scope` (or infer scope from the doc target).
2. Read existing related docs for context and cross-references.
3. Check git history for recent changes relevant to the doc topic.
4. Dispatch `adk-research` for unknowns: external API behavior, domain standards, migration history, or vendor documentation.
5. Compile an evidence inventory: what is confirmed, what is inferred, what is still unknown.

**Validation rules**:
- Every fact in the evidence inventory must have a source label.
- Unknowns that `adk-research` cannot resolve become open questions in the final doc.

## Phase 3: Plan

**Goal**: propose a document structure the user can approve before drafting begins.

**Steps**:
1. Select the template: load the matching file from `doc-templates/` (see `doc-templates/README.md` for the full index: adr, api-reference, erd, guide, hld, incident-report, lld, onboarding, prd, project, reference, release-notes, rfc, runbook, status-report, tdd). If `--template` is provided, fetch the custom template instead.
2. Map evidence to template sections.
3. Identify sections that need original writing vs. sections that can be populated from existing content.
4. Carry forward the artifact preference and chosen route from the brainstorming workflow when available.
5. Present a numbered outline with section titles, estimated content type (prose, table, code block), and any flagged gaps.

**Gate**: user approves or adjusts the outline. Skip if `--auto`.

**Edge cases**:
- Custom templates from URLs: fetch and parse before planning. If the fetch fails, fall back to a generic structure and inform the user.
- If the template has mandatory sections the evidence cannot support, flag them in the outline as `[needs input]`.

## Phase 4: Draft

**Goal**: write the document from verified evidence following the approved outline.

**Steps**:
1. Write sections in outline order, presenting each for review unless `--auto`.
2. For documents with 3+ independent sections, dispatch parallel doc-writer subagents with scoped context per section.
3. Follow the selected `doc-templates/` skeleton (headings, tables, boilerplate). Preserve template structure unless the user explicitly asked to deviate.
4. Label any claim that cannot be verified as `[unverified]`.
5. Include code examples only when verified or labeled `[untested]`.

**User responses during interactive drafting**:
- `ok` or `next` -- approve the section and continue
- feedback text -- revise the current section before continuing
- `skip` -- move to the next section
- `done` -- finalize with content written so far

**Edge cases**:
- If `--action improve`, read the existing doc first and propose targeted improvements rather than rewriting from scratch.
- If `--action update`, preserve the existing structure and only modify sections affected by the new evidence.

## Phase 5: Validate

**Goal**: verify the document is accurate and usable before delivery.

**Checks**:
- [ ] Code examples compile or run (test in sandbox if available).
- [ ] Internal links resolve to existing files or headings.
- [ ] CLI commands produce expected output.
- [ ] No orphaned `[unverified]` claims remain without justification.
- [ ] Template structure is preserved (no missing mandatory sections).
- [ ] Terminology matches repo conventions.

**Edge cases**:
- If code examples cannot be tested (no test harness, external dependency), label them `[untested]` and note in the validation summary.
- If links point to files that will be created later (e.g., companion docs), label them `[pending]`.

## Phase 6: Deliver

**Goal**: present the completed document with transparency about quality and gaps.

**Steps**:
1. Write the document to the target path.
2. Present the delivery summary:
   - what was produced (path, action, template)
   - diff summary (for `update` and `improve` actions)
   - validation results (checklist)
   - remaining gaps or open questions
3. If `--publish` is set, execute the publish step only after the markdown source is validated.
4. Ask whether more detail is needed on any section.

**Publish edge cases**:
- If the publish destination is unreachable, save the markdown locally and report the publish failure.
- If `--publish-update` is set but the target page does not exist, create instead and inform the user.
- Never claim a publish succeeded unless the write actually completed.

## Validation Rules (Summary)

- Claims are grounded in code or cited sources.
- The chosen template structure is followed intentionally.
- Uncertain or unverified items stay labeled.
- Publish steps are only claimed when the destination write actually ran.
- Code examples are tested or labeled `[untested]`.
- Links are verified or labeled `[pending]`.
