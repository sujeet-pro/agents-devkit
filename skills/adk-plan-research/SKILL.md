---
name: adk-plan-research
description: Run structured technical research with explicit evidence buckets - Verified, Inferred, Open - to answer a factual question about framework behavior, library APIs, upstream changes, or implementation patterns. Use when a task depends on external facts the agent cannot answer from memory and the codebase alone is not enough. Do not use for opinion-based decisions or for questions answerable from one known file.
---

# ADK Plan / Research

Standalone task skill under the `adk-plan` category router. Resolves uncertainty with verified sources and explicit confidence levels. Every claim cites its source.

## When to use

- The answer depends on framework, library, or tool behavior.
- An upstream repo, spec, or API needs comparison or fact-check.
- The task is migration- or upgrade-related and needs breaking-change evidence.
- Attribution or provenance needs verification.

## When NOT to use

- The answer is in this repo - just read the file.
- Opinion-based decisions with no factual grounding -> `adk-plan-brainstorm`
- Implementation that already has a clear path -> `adk-build-feature`
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
5. **Synthesize** - produce a recommendation with confidence (high / medium / low) and supporting evidence.
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

<!-- adk:references:start -->

## References shipped with this skill

These files live in `references/` next to this `SKILL.md`. Read them when the skill activates; they are inlined here so the skill is fully self-contained (no cross-skill or shared sources).

| File | Purpose |
| --- | --- |
| `references/anti-patterns.md` | Things to avoid when running this skill. |
| `references/constitution.md` | Non-negotiable rules and working/communication discipline. |
| `references/examples.md` | Example trigger phrases, invocation, and report shape. |
| `references/output-format.md` | Verbosity modes, result shape, severity labels. |
| `references/persona.md` | The agent persona that drives this skill. |
| `references/research-protocol.md` | Default research order and evidence buckets. |
| `references/working-artifacts.md` | The .temp/ rule for intermediate artifacts. |

<!-- adk:references:end -->
