# Technical Deep-Dive Article Guidelines

Guidelines for writing and reviewing technical deep-dive articles. A deep-dive goes beyond documentation and tutorials to explain how something actually works internally, grounded in specifications and implementation source code.

**Audience**: Engineers who already use a technology and want to understand its internals -- how it works under the hood, why it behaves the way it does, and what the performance and correctness implications are.

---

## 1. Required Sections

Every technical deep-dive must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | What | Precise definition of the concept, feature, or mechanism |
| 2 | Why It Matters | Practical impact on real systems and engineering decisions |
| 3 | How It Works Internally | Detailed walkthrough of internals, from spec to implementation |
| 4 | Gotchas & Edge Cases | Behavior that surprises, traps the unwary, or breaks assumptions |
| 5 | Performance Characteristics | Benchmarks, complexity analysis, and empirical measurements |
| 6 | Alternatives & Comparisons | Other approaches that solve the same problem, with trade-offs |
| 7 | When to Use (and When Not To) | Decision framework for choosing this approach |
| 8 | References | Specifications, source code, papers, official design documents |

---

## 2. Content Standards

### What

- Start with a precise, one-paragraph definition. Avoid vague framing like "X is a powerful feature that..." -- state what it is, not how to feel about it.
- Identify which specification or standard defines this concept. Link to the exact section:
  - ECMAScript: [tc39.es/ecma262](https://tc39.es/ecma262/) with section number
  - Java: [Java Language Specification](https://docs.oracle.com/javase/specs/jls/se21/html/index.html) with chapter reference
  - HTTP: RFC 9110-9114 with section number
  - Go: [The Go Specification](https://go.dev/ref/adk-spec) with section name
  - Python: [Python Language Reference](https://docs.python.org/3/reference/) with section
  - Rust: [The Rust Reference](https://doc.rust-lang.org/reference/) with section
- State the version or edition of the spec you are referencing. Specs evolve; pin your claims.
- If the concept predates or spans multiple specifications, note the lineage.

### Why It Matters

- Explain the practical impact: what goes wrong when engineers misunderstand this, what performance cliff they hit, what bug they ship.
- Ground it in real scenarios:
  - **Weak**: "Understanding event loop internals helps write better async code."
  - **Strong**: "A microtask that schedules another microtask will starve the macrotask queue indefinitely. In Node.js, this means a recursive `process.nextTick` call will block all I/O callbacks, timers, and `setImmediate` -- your HTTP server stops responding while the CPU pegs at 100%."
- If there are well-known incidents, CVEs, or outages caused by misunderstanding this concept, reference them.

### How It Works Internally

This is the core of the deep-dive. Structure it as a layered walkthrough:

1. **Specification behavior**: What the spec says must happen. Quote or paraphrase the normative language. Link to the exact spec section.
2. **Implementation**: How a specific runtime/compiler/engine implements the spec. Trace through the actual source code:
   - V8 for JavaScript: [v8.dev/blog](https://v8.dev/blog/) and [chromium.googlesource.com/v8/v8](https://chromium.googlesource.com/v8/v8/)
   - HotSpot for Java: [OpenJDK source](https://github.com/openjdk/jdk)
   - CPython for Python: [github.com/python/cpython](https://github.com/python/cpython)
   - Go runtime: [github.com/golang/go/tree/master/src/runtime](https://github.com/golang/go/tree/master/src/runtime)
3. **Optimizations**: What the implementation does beyond the spec (JIT compilation, inline caches, hidden classes, escape analysis). These are where performance behavior diverges from naive spec reading.

- Use diagrams for any concept involving state machines, memory layouts, execution phases, or data structures.
- Include code examples that demonstrate behavior at each layer. The code should be minimal but complete enough to run:

```javascript
// Demonstrates microtask vs macrotask ordering
console.log('1: script start');

setTimeout(() => console.log('2: setTimeout'), 0);

Promise.resolve()
  .then(() => console.log('3: microtask 1'))
  .then(() => console.log('4: microtask 2'));

console.log('5: script end');

// Output: 1, 5, 3, 4, 2
// Why: microtask queue drains completely before the next macrotask
```

- Walk through the code in the surrounding text. Explain why the output is what it is, referencing the spec and implementation.

### Gotchas & Edge Cases

- Structure as a table or numbered list with: the gotcha, when it occurs, why it happens (link to spec/implementation), and the mitigation.

| Gotcha | When It Occurs | Root Cause | Mitigation |
|--------|---------------|------------|------------|
| `typeof null === 'object'` | Any null type check | Historical bug in first JS implementation, preserved for backward compatibility (ES spec 6.1.1) | Use `value === null` for null checks |
| `0.1 + 0.2 !== 0.3` | Any floating-point arithmetic | IEEE 754 double-precision representation | Use epsilon comparison or integer arithmetic for currency |

- Include version-specific gotchas: behavior that changed between versions of the spec or implementation.
- Include platform-specific gotchas: behavior that differs between implementations (V8 vs SpiderMonkey, HotSpot vs GraalVM, CPython vs PyPy).

### Performance Characteristics

- State the time and space complexity for the primary operations.
- Include benchmarks with full methodology:
  - **Environment**: Hardware (CPU, RAM, SSD/HDD), OS, runtime version.
  - **Methodology**: What was measured, how many iterations, warmup runs, statistical treatment (mean, median, p95, standard deviation).
  - **Tool**: What benchmarking tool was used (JMH for Java, BenchmarkDotNet for C#, hyperfine for CLI, criterion for Rust).
- Present results in tables, not prose:

| Operation | n=100 | n=10K | n=1M | Complexity |
|-----------|-------|-------|------|------------|
| Array.push | 0.001ms | 0.05ms | 4.2ms | Amortized O(1) |
| Array.unshift | 0.002ms | 12ms | 1,800ms | O(n) |
| Array.includes | 0.001ms | 0.8ms | 82ms | O(n) |

- Include raw numbers and the baseline. "3x faster" requires knowing the absolute values.
- Note JIT warmup effects, GC pauses, or other runtime artifacts that affect measurements.
- If citing external benchmarks, link the source and state whether you reproduced the results.

### Alternatives & Comparisons

- For each alternative, cover:
  - What it is and how it differs conceptually.
  - When it is a better choice (specific use case or constraint).
  - Performance comparison (reference the Benchmarks section or external data).
- Structure as a comparison table:

| Feature | HashMap | TreeMap | LinkedHashMap |
|---------|---------|---------|---------------|
| Ordering | None | Sorted by key | Insertion order |
| Get/Put complexity | O(1) amortized | O(log n) | O(1) amortized |
| Iteration order | Undefined | Ascending key | Insertion order |
| Memory overhead | Low | High (tree nodes) | Medium (linked list) |
| Best for | General-purpose lookup | Range queries, sorted iteration | LRU cache, ordered enumeration |

### When to Use (and When Not To)

- Provide a clear decision framework, not vague advice.
  - **Vague**: "Use X when you need performance."
  - **Clear**: "Use X when your working set fits in L2 cache (< 256KB on most modern CPUs), access patterns are sequential, and you can tolerate O(n) insertion. Switch to Y when random access dominates or the working set exceeds cache size."
- State anti-patterns explicitly: "Do NOT use X when..." with the specific failure mode.
- If the recommendation depends on scale, state the thresholds.

### References

- Primary sources first: language specifications, implementation source code, official design documents, academic papers.
- Secondary sources second: official blog posts, conference talks by implementors, reputable engineering blogs.
- Tertiary sources last: tutorials, StackOverflow answers, community blog posts. These are for practical examples, never as authoritative evidence.
- Number all references and cite them inline throughout the article: "As specified in the ES2024 spec [1], Section 27.7.5.1..."

---

## 3. Code Examples

- Every code example must demonstrate a specific behavior discussed in the text. No "hello world" filler.
- Examples must be complete enough to run: include imports, setup, and output.
- Show the actual output as a comment or separate block. Do not ask the reader to "try it and see."
- When demonstrating surprising behavior, show the naive expectation first, then the actual result, then explain why.
- Use expressive-code features: `title` for file paths, `collapse` for boilerplate, `{line ranges}` to highlight the key lines.

---

## 4. Common Issues

- **Starting from tutorials instead of specs**: The deep-dive should trace from the specification to the implementation. Blog posts and tutorials are secondary sources that may contain inaccuracies. Start from the source of truth.
- **Implementation without spec grounding**: Describing what V8 does without referencing what the ECMAScript spec requires. The implementation may diverge from the spec (optimization, bug), and the reader needs both perspectives.
- **Benchmarks without methodology**: Numbers without hardware specs, runtime versions, warmup strategy, and measurement tool are unreproducible noise.
- **Shallow comparisons**: "X is faster than Y" without stating the conditions. Almost every performance comparison has a crossover point where the winner changes.
- **Missing version pinning**: Stating "JavaScript works like X" without specifying ES2024, or "Java does Y" without specifying JDK 21. Behavior changes between versions; pin your claims.
- **Code examples that do not run**: Snippets missing imports, using undefined variables, or showing pseudo-code labeled as real code.

---

## 5. Review Checklist

- [ ] Concept is defined precisely with a link to the governing specification (section-level)
- [ ] Specification version or edition is pinned
- [ ] "Why it matters" includes a concrete, real-world scenario (not abstract platitudes)
- [ ] Internals walkthrough traces from spec behavior to implementation to optimizations
- [ ] Implementation source code is referenced with links (V8, HotSpot, CPython, etc.)
- [ ] Code examples are complete, runnable, and show actual output
- [ ] Gotchas include root cause (linked to spec/implementation) and mitigation
- [ ] Version-specific and platform-specific gotchas are noted
- [ ] Benchmarks include full methodology (hardware, runtime version, tool, statistical treatment)
- [ ] Performance claims include raw numbers and baselines, not just percentages or multipliers
- [ ] Alternatives are compared in a structured table with clear "best for" criteria
- [ ] Decision framework gives specific thresholds or conditions, not vague advice
- [ ] References prioritize specs and source code over blog posts
- [ ] All references are numbered and cited inline
- [ ] No TODO/TBD placeholders remain
