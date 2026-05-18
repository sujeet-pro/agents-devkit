---
title: 'guidelines/performance'
description: '1. **Measure first.** No "this might be slow" without a profile. No "this is faster" without a benchmark.'
source: 'shared/guidelines/performance.md'
group: 'shared-guidelines'
order: 6306
---
# shared/guidelines/performance

> Source: `shared/guidelines/performance.md`

# guideline: performance

> Loaded when the task involves a perf regression, optimization, capacity question, or budget.

## Hard rules

1. **Measure first.** No "this might be slow" without a profile. No "this is faster" without a benchmark.
2. **Budgets are per-route, per-query, per-endpoint.** Number them: "API p99 < 200ms", "page LCP < 2.5s", "query < 100ms cold".
3. **One change at a time** when optimizing. Profile, change one thing, re-profile.
4. **Cache invalidation is a problem**. Don't add a cache without a plan for invalidating it.
5. **Pre-optimization is debt**. Default to the simple solution; optimize when measurement shows you must.

## Common bottlenecks (look for these)

- **N+1 queries**: ORM in a loop without `.includes()` / `.select_related()`. Profile + batch.
- **Sync over async**: `requests.get` in an async handler. Use the async client.
- **Allocation in hot paths**: object creation inside a tight loop. Reuse / pool.
- **Cold cache thundering herd**: many requests miss simultaneously after invalidation. Lock or stagger.
- **Cardinality explosion**: a metric / log with user_id as tag. Hits storage and query cost.
- **Front-end JS over budget**: unnecessary deps, unused exports, no code split, no compression.

## Profiling tools (by context)

- **Backend latency**: APM (Datadog, NewRelic) for prod; py-spy / async-profiler / pprof local.
- **Backend memory**: heap dump → diff over time. Watch for growing structures.
- **DB query**: `EXPLAIN ANALYZE`, slow-query log, query plan.
- **Frontend**: Lighthouse for synthetic; RUM (Datadog RUM) for real users; Chrome DevTools Performance tab for local.

## Caching layers (in order of placement)

1. CDN (static / edge cache) → biggest win for read-heavy public content.
2. Reverse proxy (Varnish / Cloudflare) → near-edge for dynamic but cacheable.
3. App cache (Redis / Memcached) → per-tenant / per-user.
4. Process memory (LRU cache in code) → for re-used computations in a single process.
5. DB query cache → bounded; usually not enough by itself.

## Anti-patterns

- "Faster" without measurement. Show the before/after numbers.
- Caching everything. Cache what you've shown is slow + cacheable.
- Premature parallelism. Async + concurrency adds complexity; show you need it.
- Hand-rolled coroutine schedulers. Use the platform's (asyncio / Tokio / Goroutines).
- Caching mutable shared state without invalidation. Use staleness annotations.

## Cite when reviewing

- The profile output (link to flame graph, APM trace, DB query plan).
- The metric / monitor showing the regression.
- `observability.md` for the metric naming + tags.
