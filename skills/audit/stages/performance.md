# Performance Audit Stage

This stage is loaded when `--focus` includes `performance` or defaults to `all`.

## Scope

Audit application performance including bundle size, latency, memory usage, and code-level bottlenecks with prioritized recommendations.

## Sub-Focus

When `--focus performance` is combined with a performance sub-focus hint from context:

- **bundle**: prioritizes bundle size, code splitting, and asset optimization
- **latency**: prioritizes API call patterns, caching, and database queries
- **memory**: prioritizes memory leaks, data structures, and resource management

Without a sub-focus hint, all three dimensions are analyzed.

## Required Child Agents

Run at least these child agents in parallel:

- **bundle-analyzer**: dependency size breakdown, duplication, code-splitting gaps, and asset optimization opportunities. Checks tree-shaking effectiveness, dynamic imports, and lazy loading patterns.
- **latency-analyzer**: API call patterns, caching gaps, database query issues, and middleware overhead. Identifies N+1 queries, missing indexes, unnecessary serialization, and waterfall patterns.
- **memory-analyzer**: potential leaks, data structure concerns, and resource management issues. Checks event listener cleanup, closure references, large object retention, and stream handling.
- **anti-pattern-scanner**: performance anti-patterns with impact estimates. Identifies synchronous operations blocking the event loop, unnecessary re-renders, expensive computations without memoization, and unbounded growth patterns.

## Workflow

1. **Detect technology stack.** Identify frameworks, build tools, and runtime to determine which performance checks are relevant.
2. **Load coding guidelines.** Invoke `/adk-coding` to detect repo frameworks and load matching coding guidelines.
3. **Analyze bundle size** (frontend). Examine dependency tree, identify oversized packages, check for duplicates, evaluate code splitting strategy, and assess asset optimization.
4. **Analyze latency patterns.** Trace API call chains, check caching strategy, evaluate database query patterns, identify waterfall requests, and check middleware overhead.
5. **Analyze memory usage.** Scan for potential memory leaks, evaluate data structure choices, check resource cleanup, and identify unbounded growth patterns.
6. **Identify anti-patterns.** Scan for known performance anti-patterns specific to the detected technology stack. Estimate impact and effort for each finding.
7. **Synthesize findings.** Merge all child agent results, deduplicate, rank by impact-to-effort ratio, and produce the final report sections.

## Output Sections

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