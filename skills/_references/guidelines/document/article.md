# Technical Article Guidelines

Guidelines for writing and reviewing deep-dive technical articles. These target a principal engineer voice: peer-to-peer, exhaustive, spec-referenced, and design-reasoning-explicit.

---

## 1. Purpose & Audience

Technical articles are comprehensive explorations of a topic written for experienced engineers. The reader already knows the basics; they want depth, edge cases, design trade-offs, and evidence. The voice is that of a principal engineer sharing hard-won knowledge with peers, not a tutorial instructor explaining to beginners.

---

## 2. Required Sections

Every technical article must contain these sections in order:

| Section | Purpose |
|---------|---------|
| **Abstract** | A mental model or framework for thinking about the topic (NOT a section summary or academic abstract) |
| **Problem Context** | Why this matters, including historical background and motivation |
| **Deep Analysis** | Core content, divided into multiple sub-sections |
| **Edge Cases & Gotchas** | Exhaustive catalog of what others miss |
| **Benchmarks / Evidence** | Real data, comparisons, measurements |
| **Practical Application** | Code examples, step-by-step implementation |
| **Conclusion** | Synthesis, future directions, open questions |
| **Appendix** | Prerequisites, Terminology, Summary table, References |

---

## 3. Content Standards

### Abstract

- The abstract provides a mental model or framework, not a summary of sections.
  - **Wrong**: "This article covers X, then Y, then Z" (that is a table of contents)
  - **Wrong**: "We investigate the performance characteristics of..." (that is an academic abstract)
  - **Right**: "Think of connection pooling as a staffing problem. You're managing a team of workers (connections) who can each handle one task at a time. Hire too few and work queues up. Hire too many and you waste resources on idle salaries. The art is in the sizing — and the defaults are almost always wrong."
- The mental model should give the reader a lens through which to understand everything that follows.
- Keep it to 1 short paragraph.

### Problem Context

- Explain why this topic matters now. What changed? What broke? What scales differently than expected?
- Include relevant history: what did the previous generation of solutions look like, and why did they fail or become insufficient?
- Reference the specification or standard that governs the topic (RFC, W3C spec, language spec, etc.) with links.
- State the scope boundary: what this article covers and what it deliberately excludes.

### Deep Analysis

- Divide into 3-6 sub-sections, each covering a distinct facet of the topic.
- Every design decision must include explicit reasoning: "We chose X because Y, despite Z trade-off."
- Reference official specs, RFCs, and primary sources. Blog posts and StackOverflow are secondary sources; link them only for practical examples, never as authoritative evidence.
- When presenting an approach, acknowledge what it sacrifices: "This gains simplicity at the cost of flexibility" or "This optimizes for throughput at the expense of latency."
- Use diagrams for any concept that involves flow, hierarchy, or relationships between components.

### Edge Cases & Gotchas

- This section must be exhaustive. The value of a principal-engineer-level article is the edge cases that only surface in production.
- Structure as a numbered list or table with: the edge case, when it occurs, and the mitigation.
- Include platform-specific gotchas (OS differences, browser differences, version-specific behavior).
- Include failure modes: what happens when the happy path breaks, and how does the system degrade?

| Edge Case | When It Occurs | Mitigation |
|-----------|----------------|------------|
| Connection leak under retry | Retry logic creates new connection without closing failed one | Use connection pool with max lifetime; wrap retry in try-finally |
| Silent data truncation | VARCHAR column shorter than input | Validate input length at application layer; enable strict SQL mode |

### Benchmarks / Evidence

- Every performance claim must include methodology: hardware, software versions, sample size, and measurement tool.
- Present comparisons in tables or charts, not prose.
- Include raw numbers, not just percentages. "30% faster" means nothing without a baseline.
- Acknowledge confounding variables and state what was controlled for.
- If citing someone else's benchmarks, link the source and note whether you reproduced the results.

### Practical Application

- Code examples must be complete enough to run (include imports, configuration, error handling).
- Use expressive-code features throughout:
  - `title="path/to/file"` for all file-specific code
  - `collapse={ranges}` for imports and boilerplate
  - `{ranges}` to highlight the key lines being discussed
- Walk through the code in the surrounding text. Do not drop a code block without explanation.
- If the implementation has multiple valid approaches, show the recommended one in detail and mention alternatives with brief trade-off analysis.

### Conclusion

- Synthesize the key insights (do not summarize section by section).
- State what remains unsolved or uncertain.
- Point to future directions: upcoming spec changes, evolving best practices, areas needing further research.
- If applicable, state your recommendation clearly: "For most production systems, approach X is the right default."

### Appendix

The appendix must include all four sub-sections:

1. **Prerequisites**: What the reader should know before reading this article.
2. **Terminology**: Key terms used in the article with precise definitions.
3. **Summary Table**: A single table distilling the article's key comparisons or findings.
4. **References**: Numbered list of all sources cited, with URLs. Prefer official specs, documentation, and peer-reviewed sources.

---

## 4. Structure & Flow

- The article should read top-to-bottom without requiring the reader to jump around.
- Each section should build on the previous one: context establishes the problem, analysis explores solutions, edge cases stress-test the solutions, evidence validates them, practical application shows how to implement them.
- Use transitional sentences between major sections to maintain narrative flow.
- Heading hierarchy: one H1 (title), H2 for major sections, H3 for sub-sections within Deep Analysis and Appendix. Never skip levels.
- Target 3000-6000 words. Under 3000 likely lacks depth; over 6000 should be a series.

---

## 5. Common Issues

- **Tutorial voice**: "First, install X. Next, create a file called Y." Principal engineer articles explain *why*, not just *how*. Save the step-by-step for the Practical Application section.
- **Missing spec references**: Assertions about how a protocol, API, or language feature works must cite the relevant specification. "HTTP caches work like X" needs an RFC 9111 link.
- **Shallow edge cases**: Listing 2-3 obvious gotchas. The edge case section should be the most valuable part of the article; make it exhaustive.
- **Benchmark without methodology**: "X is faster than Y" without stating hardware, versions, sample size, and measurement approach. Unreproducible benchmarks are noise.
- **Implicit trade-offs**: Presenting a solution without stating what it sacrifices. Every architecture decision has costs; name them.
- **Uncollapsed code**: Long code blocks where imports and boilerplate distract from the key logic. Use expressive-code collapse.
- **No mental model in abstract**: Writing a section summary or academic abstract instead of providing a framework for understanding.
- **Stale references**: Linking to deprecated documentation or outdated specs. Always link the current version.

---

## 6. Review Checklist

- [ ] Abstract provides a mental model or framework, not a section summary
- [ ] Problem context includes historical background and motivation
- [ ] Scope boundary is stated (what is and is not covered)
- [ ] Official specs/RFCs are cited for protocol and language behavior claims
- [ ] Every design decision includes explicit reasoning and trade-off acknowledgment
- [ ] Edge cases section is exhaustive (not just 2-3 obvious items)
- [ ] Benchmarks include methodology (hardware, versions, sample size, tool)
- [ ] Performance claims include raw numbers, not just percentages
- [ ] Code examples use expressive-code features (title, collapse, highlight)
- [ ] Code examples are complete enough to run (imports, config, error handling)
- [ ] Conclusion synthesizes insights rather than summarizing sections
- [ ] Appendix includes Prerequisites, Terminology, Summary table, and References
- [ ] Voice is peer-to-peer (principal engineer), not tutorial or academic
- [ ] All external links are current and point to authoritative sources
