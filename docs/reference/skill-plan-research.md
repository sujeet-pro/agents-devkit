---
title: 'plan-research'
description: 'Run structured technical research with explicit evidence buckets - Verified, Inferred, Open - to answer a factual question about framework behavior, library APIs, upstream changes, or implementation patterns. Use when a task depends on external facts the agent cannot answer from memory and the codebase alone is not enough. Do not use for opinion-based decisions or for questions answerable from one known file.'
skill_name: plan-research
category: router
---
# ADK Plan / Research

Standalone task skill under the `@adk:plan` (a.k.a. `adk-plan`) category router. Resolves uncertainty with verified sources and explicit confidence levels. Every claim cites its source.

## When to use

- The answer depends on framework, library, or tool behavior.
- An upstream repo, spec, or API needs comparison or fact-check.
- The task is migration- or upgrade-related and needs breaking-change evidence.
- Attribution or provenance needs verification.

## When NOT to use

- The answer is in this repo - just read the file.
- Opinion-based decisions with no factual grounding -> `@adk:plan-brainstorm` (a.k.a. `adk-plan-brainstorm`)
- Implementation that already has a clear path -> `@adk:build-feature` (a.k.a. `adk-build-feature`)
- Internal team practice / convention questions - ask the human

## Inputs

| Input | Required | Notes |
| --- | --- | --- |
| `<question>` | yes | Single, answerable question |
| `<scope>` | optional | Path to limit repo inspection |
| `<source>` | optional | URL or repo id to narrow the external source set |
| `--auto` | optional | Skip approval gate |

## Workflow

1. **Define** - restate the question precisely; identify scope, sources, and what success looks like (comparison, recommendation, fact-check). Approval gate unless `--auto`.
2. **Repo scan** - inspect the local codebase first: grep for patterns, read relevant files, check `git log` for relevant history.
3. **External scan** - search official docs and maintained references. Prefer primary sources over community answers. Include access URL and date.
4. **Cross-reference** - place each finding in a bucket:
   - `Verified` - directly supported by code, config, official docs, or runtime output.
   - `Inferred` - strong conclusion from partial evidence; mark explicitly as inference.
   - `Open` - not yet verified; needs follow-up.
5. **Validate (per `plan-research-validator.md`)** - run the four-phase validator gate; capture evidence in `.temp/notes/plan-research-<slug>-validator.md` before the final report.
6. **Synthesize** - produce a recommendation with confidence (high / medium / low) and supporting evidence.
6. **Report** - findings-first markdown with citations, validation plan, and open questions.

## Evidence hierarchy

1. The repository itself (file paths, line numbers, git history).
2. Official documentation (vendor docs, language spec, RFC).
3. Maintained implementation references (well-supported OSS used as reference).
4. Reputable community answers (only when official is silent; mark `Inferred`).
5. Memory or general knowledge (never cite as `Verified`).

## Output format

```
## Research: <question>

## Key Findings
- <finding 1> [confidence: high/medium/low] - <source>
- <finding 2> [confidence: high/medium/low] - <source>

## Evidence

### Verified
- <claim> - <file path or URL with access date>

### Inferred
- <claim> - <reasoning>

### Open
- <unresolved question> - <why open>

## Conflicts
- <source A says X, source B says Y> - <analysis>

## Recommendation
<actionable recommendation with confidence>

## Validation Plan
- <how to verify the recommendation in this repo>

## Open Questions
- <remaining unknowns>

Need more detail on any section?
```

## Hard rules

- Start with the repo. Never skip to web search.
- Cite every claim. File path or URL. No bare assertions.
- Distinguish `Verified` / `Inferred` / `Open`. No unlabeled claims.
- Surface conflicts explicitly with both positions.
- Do not fabricate URLs. If a source cannot be located, mark the claim `Open`.

## Anti-patterns

- Presenting inference as verified fact.
- Compressing uncertainty into confident language.
- Citing memory instead of pulling the doc.
- Over-researching when the answer is already in the codebase.
- Answering the question without first asking whether it is the right question.

## Examples

| User says | Workflow |
| --- | --- |
| "How does Next.js App Router handle parallel routes in v14?" | Repo: check if Next is used; External: pull Next docs page on parallel routes; cite URL + date; write findings + small example. |
| "What breaks when we move from Express 4 to 5?" | External: pull Express 5 changelog and migration guide; Repo: grep for usages of changed APIs; produce per-callsite breaking-change report. |
| "Is `crypto.randomUUID` safe to use in a browser?" | External: MDN page; Repo: check current usage; verify target browser matrix; bucket findings. |

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-research-clarifying-questions.md`) and reports the choices.

1. **What is the single question you want answered, in one sentence?** — _How to pick:_ If it cannot be put in one sentence it is multiple questions — split them and pick the one that blocks progress.
2. **What confidence do you need: a quick scan (≤30 min, 80%) or thorough (90-95%)?** — _How to pick:_ Quick = decision is reversible. Thorough = decision is hard to reverse or affects production.
3. **Are there repos to clone for additional context?** — _How to pick:_ Pass URLs (HTTPS) or paths to local clones. If unsure, skip — research can run without code context.

**Default report:** Answer first (≤3 bullets), then evidence list with citations, then confidence label, then open questions.

**Detailed report (on request or `--verbose`):** Add: source-by-source notes table, ruled-out alternatives with one-line reason, freshness score per source, decision implications.

**Artifact:** `research-brief` — Markdown brief. Sections: Question, Answer (≤3 bullets), Evidence (numbered with URL + date + Verified/Inferred), Confidence, Open Questions, Recommended Decision.

**Artifact path:** .temp/reports/research-<slug>.md (raw notes in .temp/notes/research-<slug>-notes.md, cloned repos in .temp/reference-repos/<owner>__<repo>/)

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/plan-research-multi-repo.md` for full handling.

## Clarifying questions (default-ask)

When running without `--auto`, the skill asks these questions in order, one at a time. Under `--auto`, the skill picks the safest option for each (see `references/plan-research-clarifying-questions.md`) and reports the choices.

1. **What is the single question you want answered, in one sentence?** — _How to pick:_ If it cannot be put in one sentence it is multiple questions — split them and pick the one that blocks progress.
2. **What confidence do you need: a quick scan (≤30 min, 80%) or thorough (90-95%)?** — _How to pick:_ Quick = decision is reversible. Thorough = decision is hard to reverse or affects production.
3. **Are there repos to clone for additional context?** — _How to pick:_ Pass URLs (HTTPS) or paths to local clones. If unsure, skip — research can run without code context.

## Default vs detailed output

**Default report:** Answer first (≤3 bullets), then evidence list with citations, then confidence label, then open questions.

**Detailed report (on request or `--verbose`):** Add: source-by-source notes table, ruled-out alternatives with one-line reason, freshness score per source, decision implications.

**Artifact:** `research-brief` — Markdown brief. Sections: Question, Answer (≤3 bullets), Evidence (numbered with URL + date + Verified/Inferred), Confidence, Open Questions, Recommended Decision.

**Artifact path:** .temp/reports/research-<slug>.md (raw notes in .temp/notes/research-<slug>-notes.md, cloned repos in .temp/reference-repos/<owner>__<repo>/)

## Multi-repo context

Pass extra repos via `--repo <url-or-path>` (repeatable). URLs are cloned into `.temp/reference-repos/<owner>__<repo>/`; paths are read in place. Each repo is processed independently and findings/citations are tagged with the repo of origin. See `references/plan-research-multi-repo.md` for full handling.

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/plan-research-anti-patterns.md` | Things to avoid when running this skill. |
| `references/plan-research-artifact-format.md` | The deliverable's format and where it lives (.temp/ contract). |
| `references/plan-research-clarifying-questions.md` | The default-ask questions for this skill, with how-to-pick rubrics. |
| `references/plan-research-constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/plan-research-examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/interaction-contract.md` | Default-ask, explained-options, --auto contract every skill must follow. |
| `references/plan-research-multi-repo.md` | How to consume context from extra cloned or local-path repos. |
| `references/plan-research-output-format.md` | Default vs detailed report shapes; severity labels; verbosity rules. |
| `references/plan-research-persona.md` | The agent persona that drives this skill. |
| `references/plan-research-research-protocol.md` | Source ordering, stop conditions, evidence buckets, citation discipline. |
| `references/plan-research-working-artifacts.md` | Legacy: superseded by artifact-format.md; kept for back-compat. |
| `references/plan-research-validator.md` | The four-phase validator gate (pre-execution, mid-flow, pre-handoff, post-execution) this skill MUST run. |

<!-- adk:references:end -->
