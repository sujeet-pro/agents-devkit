# Research Methodology

How to conduct effective technical research. These guidelines apply to all research tasks regardless of the downstream consumer.

## Research Workflow

1. **Clarify scope and constraints**
   - Identify the exact technologies, versions, and boundaries of the research topic.
   - If the request says "latest", verify the current version explicitly with sources.
   - Note what has changed from previous versions when version-awareness matters.

2. **Breadth-first survey**
   - Quick landscape pass to identify canonical concepts, common pitfalls, and edge cases.
   - Identify recent changes: breaking changes, new APIs, deprecated patterns.
   - Use this pass to structure subtopics before deep dives.

3. **Collect primary sources (strict priority)**
   - **Specifications**: RFCs, WHATWG/W3C, ECMAScript, IETF, OpenAPI specs, language specs.
   - **Official documentation**: Vendor docs, framework guides, standards body publications.
   - **Core maintainer content**: Blog posts, talks, and design docs from project leads.
   - **Source code**: Reference implementations, actual library code, test suites.

4. **Read implementations**
   - Inspect the local codebase when it is the subject of research.
   - Read source code for behavior not obvious in docs -- this is where edge cases live.
   - Check GitHub issues/PRs for design rationale and known limitations.

5. **Deep-dive per subtopic**
   - For each subtopic, gather sources that justify claims, limits, defaults, and edge cases.
   - Prefer primary sources; use expert blogs only to supplement, never replace.
   - Look for design rationale: why was this choice made?

6. **Cross-check and triangulate**
   - Validate claims across at least two reputable sources.
   - Flag contradictions and resolve them explicitly.
   - When sources disagree, prefer: spec > official docs > core maintainer > industry expert.

7. **Record citations with context**
   - Every technical claim must map to a source.
   - Note the version/date of sources for time-sensitive content.
   - Keep a running references list while researching, prioritized by authority.

## Source Priority Order

| Priority | Source Type | Use For |
|----------|-----------|---------|
| 1 | **Specifications** (RFCs, WHATWG, ECMA, W3C, IETF) | Authoritative behavior, edge cases, guarantees |
| 2 | **Official Documentation** (vendor docs, framework guides) | API details, recommended patterns |
| 3 | **Core Maintainer Content** (project leads' posts/talks) | Design rationale, "why" behind decisions |
| 4 | **Source Code** (GitHub repos, reference implementations) | Actual behavior, undocumented limits |
| 5 | **Peer-reviewed Papers** (ACM, IEEE, arXiv) | Theoretical foundations, benchmarks |
| 6 | **Industry Expert Blogs** (recognized engineers) | Practical insights, war stories |
| 7 | **Community Q&A** (Stack Overflow, GitHub issues) | Narrow implementation details only |

Always prefer higher-priority sources. Lower-priority sources supplement but never override higher ones.

## Fact-Checking Rules

- Verify all numbers, limits, defaults, and algorithmic behaviors against primary sources.
- Confirm version-specific behavior -- behavior often changes between major versions.
- Use absolute dates and version numbers (e.g., "As of Node.js 20 (April 2023)..." not "recently").
- If you cannot verify a claim, **label it as unverified** or omit it.
- Cross-reference with source code when docs are ambiguous.
- Distinguish clearly between facts, opinions, and inferred best practices.

## Research Quality Signals

- **High confidence**: Claim verified against spec or official docs, corroborated by source code.
- **Medium confidence**: Claim from official docs or core maintainer, not contradicted elsewhere.
- **Low confidence**: Single source, expert blog only, or docs are ambiguous.

Always assign a confidence level per finding or per section in the output.

## Anti-Patterns

- Citing a blog post for behavior that has a spec -- always go to the spec.
- Treating Stack Overflow answers as authoritative for current behavior -- they age poorly.
- Omitting version numbers -- "React supports X" is meaningless without a version.
- Conflating a framework's recommendation with the underlying platform's behavior.
- Presenting inferred best practices as established facts.
