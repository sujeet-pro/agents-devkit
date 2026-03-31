# Document Research and Fact-Checking Guidelines

Deep research is **mandatory** for all document writing. Doc-writing always uses `--deep` research (4 agents). Every technical claim must be verified against authoritative sources before it appears in a document.

## Research Depth by Document Type

Each document type has specific research needs. Use this table to determine what to research and how deeply.

| Document Type | Research Depth | Key Sources | What to Research Per Section |
|---------------|---------------|-------------|------------------------------|
| **RFC** | Exhaustive | Specs, prior art, competing approaches, maintainer design rationale | Problem statement: root cause analysis. Alternatives: real-world adoption data. Proposal: spec-level detail. Risks: production failure modes |
| **TDD / Tech Spec** | Exhaustive | Architecture docs, source code, performance benchmarks, dependency changelogs | Design: component interactions. APIs: exact signatures and contracts. Data model: migration paths. Non-functional: measured baselines |
| **ADR** | Thorough | Decision drivers, team constraints, prior ADRs, production metrics | Context: quantified problem. Options: real pros/cons from adopters. Decision: evidence for the choice. Consequences: operational impact |
| **HLD** | Thorough | System architecture, infrastructure docs, capacity data, vendor SLAs | Components: responsibility boundaries. Integration: protocol specs. Scaling: measured capacity. Failure modes: real incident patterns |
| **LLD** | Exhaustive | Source code, API contracts, test suites, performance profiles | Implementation: exact code paths. Edge cases: from source and issues. Error handling: failure mode catalog. Performance: benchmarked numbers |
| **PRD** | Thorough | User research, analytics, competitive analysis, market data | Problem: user evidence. Requirements: feasibility checks. Success metrics: industry benchmarks. Constraints: technical feasibility |
| **Article / Deep Dive** | Exhaustive | Specs, source code, maintainer blogs, changelogs, benchmarks | Each section: spec-referenced claims. Examples: tested code. Edge cases: from source. Evolution: version-by-version changes |
| **Blog** | Focused | Official docs, maintainer recommendations, practical examples | Key claims: verified against docs. Examples: tested and working. Opinions: clearly labeled as such |
| **Changelog** | Targeted | Git history, issue tracker, release notes, migration guides | Each entry: linked to commit/PR. Breaking changes: migration path verified. Deprecations: replacement documented |
| **Runbook** | Thorough | Production configs, monitoring dashboards, incident history, source code | Each procedure: tested against real environment. Thresholds: from production data. Escalation: verified contacts |
| **System Design Article** | Exhaustive | Architecture specs, performance data, vendor docs, production metrics | Each component: measured characteristics. Trade-offs: quantified. Alternatives: real adoption data |
| **Tool Evaluation** | Comprehensive | All compared tools' docs, benchmarks, license terms, community health | Each criterion: measured or verified. Pricing: current and projected. Limitations: from real usage |
| **API Reference** | Exhaustive | Source code, OpenAPI specs, test suites, existing client usage | Each endpoint: exact request/response shapes from code. Auth: tested flows. Errors: complete catalog from source |
| **Project Docs** | Focused | Repo structure, CI/CD configs, deployment scripts, existing README | Setup: tested from clean state. Architecture: matches current code. Config: all env vars documented |
| **Migration Guide** | Exhaustive | Both old and new version docs, changelogs, breaking change lists, source code | Each step: tested migration path. Breaking changes: complete catalog. Rollback: verified procedure |
| **Onboarding** | Focused | Repo structure, team processes, existing docs, CI/CD pipeline | Setup: tested from fresh clone. Workflows: verified with team. Tools: current versions and configs |

## Section-Level Research Protocol

For each section of the document being written:

1. **Identify claims** -- What factual statements does this section make?
2. **Find primary sources** -- For each claim, locate the authoritative source (spec, official docs, source code).
3. **Verify specifics** -- Check exact numbers, defaults, limits, API signatures against source.
4. **Check currency** -- Is this information current for the version being documented?
5. **Note gaps** -- If a claim cannot be verified, flag it for removal or mark as unverified.

## Source Priority Order

| Priority | Source Type | Use For |
|----------|-----------|---------|
| 1 | **Specifications** (RFCs, WHATWG, ECMA, W3C, IETF) | Authoritative behavior, edge cases, guarantees |
| 2 | **Official Documentation** (vendor docs, framework guides) | API details, recommended patterns |
| 3 | **Core Maintainer Content** (project leads' posts/talks) | Design rationale, "why" behind decisions |
| 4 | **Source Code** (repos, reference implementations) | Actual behavior, undocumented limits |
| 5 | **Peer-reviewed Papers** (ACM, IEEE, arXiv) | Theoretical foundations, benchmarks |
| 6 | **Industry Expert Blogs** (recognized engineers) | Practical insights, war stories |
| 7 | **Community Q&A** (Stack Overflow, GitHub issues) | Narrow implementation details only |

Always prefer higher-priority sources. Lower-priority sources supplement but never override.

## Fact-Checking Rules

- Verify all numbers, limits, defaults, and algorithmic behaviors against primary sources.
- Confirm version-specific behavior -- behavior often changes between major versions.
- Use absolute dates and version numbers (e.g., "As of Node.js 20 (April 2023)..." not "recently").
- If you cannot verify a claim, **label it as unverified** or omit it.
- Cross-reference with source code when docs are ambiguous.

## Version Evolution Requirements

When writing about topics where behavior has changed:

1. **State the current version explicitly**: "As of React 18...", "In Node.js 20+..."
2. **Note previous behavior**: When behavior differs materially, add a callout.
3. **Explain the change**: Why did the previous approach have problems?

## Research Output Contract

When `/adk-doc-writing` invokes `/adk-research --deep`, the research output must include:

- **Key findings** with inline citations and source URLs
- **Per-subtopic sections** with confidence ratings (high/medium/low)
- **Code examples** when relevant, tested and working
- **Risks and tradeoffs** with evidence
- **Sources list** ordered by authority level

This structured output feeds directly into the document drafting phase. The doc-writing skill uses findings to populate each section with verified, cited content.

## References Formatting

References in the final document should appear in a dedicated section:

```markdown
## Appendix

### References

- [Spec Name](url) - Section or relevant clause
- [Official Docs](url) - Implementation details
```

## Update-Document Requirements

When updating an existing document:

- Always perform fresh research, even when updating a small section.
- Verify existing claims for drift or outdated behavior.
- Check if new versions have been released since the document was written.
- Replace or augment references with newer primary sources when available.
- Add version evolution notes if behavior has changed since the original writing.
