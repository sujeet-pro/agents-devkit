---
name: audit-performance
description: Use when you need to audit application performance including bundle size, latency, memory usage, and code-level bottlenecks with prioritized recommendations
user_invocable: true
arguments:
  - name: scope
    description: "Audit scope: frontend, backend, full (default: full)"
    required: false
  - name: focus
    description: "Specific focus area: bundle-size, latency, memory, all (default: all)"
    required: false
---

# Performance Audit

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

## Preflight

Before analyzing the codebase or launching child agents, run:

`zsh scripts/check-skill-deps.zsh audit-performance`

## Guideline Loading

Always load:

- `skills/_references/guidelines/coding/general.md`

Then add scope-specific guidance:

- Frontend -> `skills/_references/guidelines/coding/frontend-nextjs.md`
- Backend -> `skills/_references/guidelines/coding/backend-general.md`

## Required Child Agents

Run at least these child agents in parallel:

- **Bundle analyzer** (when `scope` includes frontend): inspects build configuration (webpack, Vite, esbuild, Turbopack), analyzes dependency tree for large or duplicated packages, checks tree-shaking effectiveness, identifies code-splitting opportunities, and reviews asset optimization (images, fonts, CSS).
- **Code pattern reviewer**: scans for performance anti-patterns across the codebase including N+1 queries, missing indexes (by analyzing query patterns), synchronous operations that could be async, unnecessary re-renders (React), expensive computations without memoization, and memory leaks (event listeners, closures, caches without eviction).
- **Benchmark researcher**: uses `/devkit:research` with `depth=standard` to research performance benchmarks and best practices for the detected technology stack. Compares current patterns against industry recommendations.

## Workflow

1. **Detect technology stack.** Identify the frameworks, build tools, and runtime environment from package manifests, configuration files, and code patterns.

2. **Analyze bundle and build** (when `scope` includes frontend or `focus=bundle-size`):
   - Parse build configuration for optimization settings
   - Identify the largest dependencies and their impact on bundle size
   - Check for duplicate packages in the dependency tree
   - Review code-splitting configuration and dynamic imports
   - Check asset optimization (image formats, compression, lazy loading)
   - Review CSS strategy (unused CSS, CSS-in-JS overhead, critical CSS extraction)

3. **Analyze latency patterns** (when `focus` includes latency or all):
   - Identify API call patterns (waterfall requests, missing parallelization)
   - Review caching strategy (HTTP cache headers, in-memory caches, CDN usage)
   - Check database query patterns (N+1, missing pagination, unindexed lookups)
   - Review middleware and request pipeline for unnecessary overhead
   - Check for synchronous I/O in hot paths

4. **Analyze memory usage** (when `focus` includes memory or all):
   - Identify potential memory leaks (unclosed resources, growing caches, event listener accumulation)
   - Review data structure choices for memory efficiency
   - Check for large object retention in closures or global state
   - Review streaming vs. buffering strategies for large data

5. **Scan for anti-patterns.** The code pattern reviewer checks for:
   - Frontend: unnecessary re-renders, missing React.memo/useMemo/useCallback, layout thrashing, synchronous localStorage in render path, unoptimized images
   - Backend: N+1 queries, missing connection pooling, blocking I/O in async context, unbounded caches, missing pagination, inefficient serialization
   - General: regex backtracking, quadratic algorithms on user-sized input, excessive logging in hot paths

6. **Prioritize findings.** Rank each finding by:
   - Estimated impact (High/Medium/Low)
   - Effort to fix (Quick fix/Moderate/Major refactor)
   - Confidence level (measured vs. inferred)

7. **Generate report.** Merge child agent outputs with prioritized recommendations.

Save intermediary artifacts to `.temp/performance-audit/`.

## Output

A performance audit report containing:

- **Executive Summary**: overall performance posture with top 3-5 action items
- **Technology Stack**: detected frameworks, build tools, and runtime
- **Bundle Analysis** (frontend): dependency size breakdown, duplication, code-splitting gaps, and asset optimization opportunities
- **Latency Analysis**: API call patterns, caching gaps, database query issues, and middleware overhead
- **Memory Analysis**: potential leaks, data structure concerns, and resource management issues
- **Anti-Pattern Findings**: each finding with:
  - Description and affected file(s)
  - Impact estimate (with reasoning)
  - Recommended fix with code example
  - Effort estimate
- **Prioritized Recommendations**: findings ranked by impact-to-effort ratio
- **Quick Wins**: changes that can be made immediately with high confidence
- **Strategic Improvements**: larger efforts that require planning and testing
