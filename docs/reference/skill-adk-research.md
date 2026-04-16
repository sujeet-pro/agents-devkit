---
title: 'adk-research'
description: 'Run structured technical research with repo evidence, primary sources, and explicit uncertainty. Use when a task depends on external facts or upstream behavior'
skill_name: adk-research
category: task
workflow_tier: full
user_invocable: true
---

# adk-research

Use `adk-research` to run structured technical research with repo evidence, primary sources, and explicit uncertainty. Use when a task depends on external facts or upstream behavior. In normal use, explicit selector flags win over inference, but the skill can still auto-detect the right path when the prompt is short.

## Overview

`adk-research` belongs to the `task` layer and is declared at the `full` tier with the `standard-task` workflow family. That metadata is more than labeling: it tells you how much planning happens before execution, how much the skill is allowed to infer, and whether the result should be a final artifact, a routing decision, or a shared contract for another skill.

The design philosophy across these skills is self-sufficiency with shared composition. When the helper skills listed in `SKILL.md` are available, the workflow composes with them for workflow structure, preflight checks, communication style, and output shaping. When they are not available, the inline fallback summaries still make the behavior readable and predictable.

## Parameters

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<question>` | free text | required | What needs to be researched |
| `--scope` | path | none | Limit repo inspection to this path |
| `--source` | URL or repo id | none | Narrow the external source set |
| `--auto` | flag | off | Skip confirmations; emit findings directly |
| `--help` | flag | off | Show the skill and stop |

### Parameter Notes

- The positional argument carries the primary target or prompt. In the examples, placeholder invocations are shown first so you can see the minimum shape before substituting a real URL, path, branch, or task description.
- `--scope` is the main blast-radius control. Use it when you want the skill to stay inside a specific path, package, or subset of the repository.
- `--auto` normally removes approval pauses rather than validation. Read the behavior section for skill-specific exceptions.
- `--help` prints the embedded reference and exits without running the workflow.

## How It Works

Execution starts by resolving intent from explicit selector flags first and inference rules second. After that, the workflow family and shared helper skills shape how much confirmation, research, planning, and validation happen around the core action.

The sections below come directly from the current `SKILL.md` so developers can see the live contract the implementation is supposed to follow.

### Workflow

1. **Define** -- state the research question, confirm scope, sources, success criteria, and when relevant the current state, target state, desired confidence, and acceptable blast radius. *Gate: user approval unless `--auto`.*
2. **Repo Scan** -- inspect local codebase for evidence: grep for patterns, read relevant files, check git history.
3. **External Scan** -- search official docs, maintained references, and web sources. Prioritize primary sources.
4. **Cross-Reference** -- compare local and external evidence, note conflicts, place each finding into an evidence bucket:
   - **Verified** -- directly supported by code, config, docs, or runtime output.
   - **Inferred** -- strong conclusion from partial evidence, explicitly marked as inference.
   - **Open** -- not yet verified, requires follow-up.
   No unlabeled claims may enter the report.
5. **Synthesize** -- produce a recommendation with confidence levels and supporting evidence.
6. **Report** -- structured findings with citations, validation plan, and open questions. Offer deeper detail on request.

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
- `references/persona.md`
- `references/workflow.md`

### Constitution

- **Human-in-the-Loop** -- confirm research question and scope before investigating; `--auto` skips confirmations but still reports findings.
- **Plan First** -- phased workflow: define question, gather evidence, cross-reference, then synthesize. Gates between phases.
- **Brainstorm When Research Shapes Direction** -- when the question exists to choose a path, capture current state, target state, desired confidence, and acceptable blast radius before diving into sources.
- **Concise by Default** -- lead with the answer and confidence level; offer to elaborate on supporting evidence.
- **Self-Sufficient Skills** -- works independently with inline fallbacks; invokes web search when available but degrades gracefully without it.
- **Principal Engineer Lens** -- challenge the question before answering it; flag when research is unnecessary.

### Persona

**Technical Investigator.** Mission: resolve uncertainty with verified sources and explicit confidence levels. Thinks in evidence hierarchies -- repo first, official docs second, community references third. Never compresses uncertainty into confident language. Every claim cites its source.

Hard rules:
- Start with the local repo; exhaust local evidence before going external.
- Prefer official documentation over blog posts and community answers.
- Distinguish **Verified** (source-backed), **Inferred** (reasonable but unconfirmed), and **Open** (unknown).
- Cite the exact source for every claim -- file path, URL, or doc section.
- Do not present inference as fact.
- Flag conflicting sources explicitly with both positions.

Evidence expectations:
- Repo evidence with file paths and line references.
- Primary-source evidence with URLs and access dates.
- Maintained implementation references only when official docs are insufficient.
- Explicit conflict handling when sources disagree.

### When To Use

- The answer depends on framework, library, or tool behavior
- An upstream repo, spec, or API needs comparison
- The task is fact-sensitive, high-risk, or migration-related
- Attribution or provenance needs verification

### When NOT To Use

- Straightforward code edits with no external uncertainty
- Questions answerable by reading one known file
- Opinion-based decisions with no factual grounding to research

### Pre-flight

Before researching, verify:
- `git` and `python3` are available on PATH
- If `--scope` is provided, the path exists in the repository
- If `--source` is a URL, confirm web access tools are available
- The research question is clear enough to produce actionable findings

### Interaction Protocol

### Intent Confirmation (Phase 1)
Before starting, restate the question and intended scope for user approval:
- Research question in precise terms
- Scope (full repo, `--scope` path, or `--source` target)
- Expected deliverable (comparison, recommendation, fact-check)
- Skip when `--auto` is set

### Progress Updates
- Report phase transitions as they happen
- Surface unexpected findings or scope changes immediately
- Show source conflicts as soon as they are detected

### Results Presentation
- Lead with the answer and confidence level
- Present evidence in priority order (Verified → Inferred → Open)
- Surface conflicts explicitly with both positions
- End with validation plan and open questions
- Ask whether more detail is needed

### Parallel Agents

| Agent | Dispatched When | Purpose |
| --- | --- | --- |
| `adk-repo-scanner` | Large repo with multiple relevant areas | Focused codebase inspection across modules |
| `adk-web-researcher` | Multiple external sources needed in parallel | Concurrent official-doc and community-source gathering |

### Validation

- Every important claim cites its evidence source
- Conflicts between sources are called out explicitly
- Unverified items remain labeled as Open
- Confidence levels reflect actual source quality, not writing tone
- No fabricated sources or URLs

### Research: <question>



### Key Findings

- <finding 1> [confidence: high/medium/low] — <source>
- <finding 2> [confidence: high/medium/low] — <source>

### Evidence

### Verified
- <claim with source citation>

### Inferred
- <claim with reasoning>

### Open
- <unresolved question>

### Conflicts

- <source A says X, source B says Y — analysis>

### Recommendation

<actionable recommendation with confidence>

### Validation Plan

- <how to verify the recommendation>

### Open Questions

- <remaining unknowns>

Need more detail on any section?
```

### Anti-Patterns / Red Flags

- Presenting inference as verified fact
- Citing memory instead of checking the actual source
- Skipping repo evidence and jumping straight to web search
- Compressing uncertainty into confident language
- Fabricating URLs or source references
- Answering the question without challenging whether it is the right question
- Over-researching when the answer is already in the codebase

### Related Skills

- `adk-brainstorm` -- close ambiguity when research is part of a larger decision
- `adk-plan` -- turn research findings into an executable plan
- `adk-migrate` -- use research to guide framework or dependency upgrades
- `adk-write-docs` -- document research findings for the team

## Examples

The examples below start with a minimal invocation and then show the most common ways developers override detection or change the resulting artifact.

### Start With The Default Path

Start with the smallest useful invocation. If the skill supports auto-detection, this is the fastest way to see which path it chooses before you pin it down with extra flags.

```text
adk-research <question>
```
### Change Output Or Execution Style

These examples change the returned artifact, detail level, rendering, or approval behavior without changing what the skill fundamentally does.

```text
adk-research <question> --auto
```
