# Research and Fact-Checking Guidelines

Deep research is **mandatory** for both new articles and updates. Always validate technical claims against authoritative sources. The goal is factually correct, reference-backed content.

## Research Workflow

1. **Clarify scope and versions**
   - Identify the exact spec/version or product release you are writing about.
   - If the request says "latest", verify the current version explicitly with sources.
   - Note what has changed from previous versions (for version-aware content).

2. **Survey the topic (breadth first)**
   - Do a quick landscape pass to identify canonical concepts, common pitfalls, and edge cases.
   - Identify what has changed in recent versions (breaking changes, new APIs, deprecated patterns).
   - Use this to outline the article before deep dives.

3. **Collect primary sources first (strict priority)**
   - **Specifications**: RFCs, WHATWG/W3C, ECMAScript, IETF, OpenAPI specs, etc.
   - **Official documentation**: Vendor docs, framework docs, standards body publications
   - **Core maintainer content**: Blog posts, talks, and design docs from project leads (e.g., Dan Abramov for React, Ryan Dahl for Node/Deno, Evan You for Vue)
   - **Source code**: Reference implementations, actual library code

4. **Read relevant implementations**
   - Inspect the local codebase when it is the subject of the article.
   - Read source code for behavior not obvious in docs—this is where edge cases live.
   - Check GitHub issues/PRs for design rationale and known limitations.

5. **Section-level deep research**
   - For each section, gather sources that justify claims, limits, defaults, and edge cases.
   - Prefer primary sources; use industry expert blogs only to supplement, not replace, primary sources.
   - Look for design rationale: why was this choice made?

6. **Cross-check and triangulate**
   - Validate claims across at least two reputable sources.
   - Flag contradictions and resolve them explicitly in the article.
   - When sources disagree, prefer: spec > official docs > core maintainer > industry expert.

7. **Capture spec quotes and design rationale**
   - Use short quotes (<= 25 words) to highlight nuanced or lesser-known details.
   - Quote the spec directly when it clarifies a subtle behavior.
   - Quote core maintainer explanations for design decisions.

8. **Record citations with context**
   - Every technical claim must map to a source.
   - Note the version/date of sources for time-sensitive content.
   - Keep a running References list while writing, prioritized by authority.

## Source Priority Order (Strict Hierarchy)

| Priority | Source Type                 | Examples                                  | Use For                                        |
| -------- | --------------------------- | ----------------------------------------- | ---------------------------------------------- |
| 1        | **Specifications**          | RFCs, WHATWG, ECMA-262, W3C, IETF         | Authoritative behavior, edge cases, guarantees |
| 2        | **Official Documentation**  | Vendor docs, MDN, framework guides        | API details, recommended patterns              |
| 3        | **Core Maintainer Content** | Blog posts/talks by project leads         | Design rationale, "why" behind decisions       |
| 4        | **Source Code**             | GitHub repos, reference implementations   | Actual behavior, undocumented limits           |
| 5        | **Peer-reviewed Papers**    | ACM, IEEE, arXiv (for algorithms/systems) | Theoretical foundations, benchmarks            |
| 6        | **Industry Expert Blogs**   | Recognized engineers' technical blogs     | Practical insights, war stories                |
| 7        | **Community Q&A**           | Stack Overflow, GitHub issues             | Narrow implementation details only             |

**Core maintainer examples:**

- React: Dan Abramov, Sebastian Markbåge, Andrew Clark
- Node.js: Matteo Collina, James Snell, original Ryan Dahl posts
- V8: Benedikt Meurer, v8.dev blog
- TypeScript: Anders Hejlsberg, Ryan Cavanaugh, orta
- Rust: Niko Matsakis, boats
- Go: Rob Pike, Russ Cox

**Industry expert blog examples:**

- web.dev (Chrome DevRel)
- Julia Evans (systems/networking)
- Brendan Gregg (performance)
- Martin Kleppmann (distributed systems)

Always prefer higher-priority sources. Lower-priority sources supplement but never override higher ones.

## Fact-Checking Rules

- Verify all numbers, limits, defaults, and algorithmic behaviors against primary sources.
- Confirm version-specific behavior and edge cases—behavior often changes between major versions.
- Use absolute dates and version numbers when referencing timelines (e.g., "As of Node.js 20 (April 2023)..." not "recently").
- If you cannot verify a claim, **label it as a hypothesis** or omit it.
- Cross-reference with source code when docs are ambiguous.

## Version Evolution Requirements

When writing about topics where behavior has changed:

1. **State the current version explicitly**: "As of React 18...", "In Node.js 20+...", "Since ES2022..."
2. **Note previous behavior**: When behavior differs materially from prior versions, add a callout
3. **Explain the change**: Why did the previous approach have problems? What drove the new design?

**Example format:**

```markdown
## Suspense for Data Fetching

As of React 18, Suspense works with concurrent features to handle async data.

> **Prior to React 18:** Suspense only worked for code splitting via `React.lazy()`. Data fetching required patterns like render-as-you-fetch with external libraries. The synchronous rendering model meant loading states had to be managed manually.

The concurrent model allows React to "pause" rendering while waiting for data, eliminating waterfall fetches.
```

This helps readers who:

- Encounter older code or documentation
- Need to maintain backward compatibility
- Want to understand why current patterns exist

## References Formatting

References should be a dedicated section in the Appendix:

```
## Appendix

### References

- [Spec Name](https://example.com) - Section or relevant clause
- [Official Docs](https://example.com) - Implementation details
```

## Update-Article Requirements

- Always perform fresh research, even when updating a small section.
- Read the existing article and relevant code before drafting changes.
- Verify existing claims for drift or outdated behavior—APIs and defaults change.
- Check if new versions have been released since the article was written.
- Replace or augment references with newer primary sources when available.
- Add version evolution notes if behavior has changed since the original writing.

## Research Depth by Article Type

| Article Type                  | Research Depth | Key Sources                                                  |
| ----------------------------- | -------------- | ------------------------------------------------------------ |
| **API/Library deep dive**     | Exhaustive     | Specs, source code, maintainer blogs, changelogs             |
| **Concept explanation**       | Thorough       | Specs, academic papers, canonical implementations            |
| **How-to/Pattern**            | Focused        | Official docs, maintainer recommendations, source code       |
| **Comparison**                | Comprehensive  | All compared items' specs/docs, benchmarks, design rationale |
| **Debugging/Troubleshooting** | Targeted       | Source code, issue trackers, error handling paths            |

All types require primary sources. The depth determines how many secondary sources you triangulate with.
