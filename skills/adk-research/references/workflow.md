# ADK Research Workflow

## Phases

### Phase 1: Define
State the research question clearly and confirm scope, sources, success criteria, and when relevant the current state, target state, desired confidence, and acceptable blast radius.

**Inputs:** user question, `--scope`, `--source` flags
**Actions:**
- Parse the research question into a precise, answerable form
- Identify scope (full repo, specific path, or external source)
- Determine what a successful answer looks like
- If the question is part of choosing a direction, carry forward the shared brainstorming inputs and confidence target
- Present confirmation summary to user

**Gate:** User approval required. Skip when `--auto` is set.

**Outputs:** confirmed research question, scope, success criteria

### Phase 2: Repo Scan
Inspect the local codebase for evidence relevant to the research question.

**Actions:**
- Grep for patterns, imports, and usages related to the question
- Read relevant source files, configs, and documentation
- Check git history for related changes, migrations, or decisions
- Record findings with exact file paths and line references
- Note gaps where repo evidence is insufficient

**Outputs:** local evidence with source citations, identified gaps

### Phase 3: External Scan
Search official docs, maintained references, and web sources for evidence.

**Actions:**
- Search official documentation for the technology in question
- Check changelogs, release notes, and migration guides
- Search maintained implementation references when official docs are insufficient
- Record findings with URLs and access context
- Prioritize primary sources over community content

**Outputs:** external evidence with source citations

### Phase 4: Cross-Reference
Compare local and external evidence, identify conflicts, and label findings.

**Evidence Bucket Discipline:** every finding must be placed in exactly one bucket before it enters the report.

| Bucket | Criteria | Example |
| --- | --- | --- |
| **Verified** | Directly supported by code, config, docs, or runtime output | "Express 5 removed `app.del()` — confirmed in changelog v5.0.0" |
| **Inferred** | Strong conclusion from partial evidence, marked as inference | "Likely uses connection pooling based on driver defaults, not confirmed in config" |
| **Open** | Not yet verified, requires follow-up | "Unknown whether rate limiting applies to WebSocket connections" |

**Actions:**
- Compare repo evidence against external sources
- Identify agreements, conflicts, and gaps
- Place each finding in its evidence bucket (Verified / Inferred / Open) — no unlabeled claims
- Assign confidence levels (high, medium, low) based on source quality and corroboration
- Document conflicts with both positions and analysis
- Ensure every claim cites its exact source (file path, URL, doc section)

**Outputs:** bucket-labeled findings, conflict analysis, confidence assessments

### Phase 5: Synthesize
Produce a recommendation with confidence levels and supporting evidence.

**Actions:**
- Formulate an actionable recommendation based on verified evidence
- Support with Inferred findings where Verified evidence is unavailable
- Flag Open items that could affect the recommendation
- Recommend the next route when the research result should feed a spec, plan, docs artifact, or build decision
- Propose a validation plan to confirm the recommendation

**Outputs:** recommendation with evidence chain, validation plan

### Phase 6: Report
Present structured findings with citations, validation plan, and open questions.

**Actions:**
- Format findings using the standard research output template
- Include all citations with source references
- Separate open questions from confirmed findings
- Offer deeper detail on request

**Outputs:** structured research report

## Validation Rules
- Every important claim cites its evidence source
- Conflicts between sources are called out explicitly
- Unverified items remain labeled as Open
- Confidence levels reflect actual source quality, not writing tone
- No fabricated sources or URLs

## Auto Mode Behavior
When `--auto` is set:
- Phase 1 (Define): skip user approval, proceed with parsed question
- Phases 2-5: execute without intermediate check-ins
- Phase 6 (Report): still reports full results with all citations
- Validation rules still apply in full
