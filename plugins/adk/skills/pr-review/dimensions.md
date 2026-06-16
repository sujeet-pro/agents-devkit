# pr-review — review dimensions + feature-flow tracing

Each dimension is a separate pass (a separate agent in the Workflow). A finding hangs off whichever dimension caught it. Skip a dimension only when it clearly doesn't apply, and say so.

- **correctness** — bugs, off-by-one, null/undefined handling, error swallowing, wrong invariants, race conditions in logic.
- **security** — input validation at trust boundaries, auth/authz checks, IDOR, injection (SQL/command/path/XSS/SSRF), secrets in the diff, broken access control, sensitive data in logs. (Spawn `security-auditor`.)
- **tests** — does coverage match the change? Behavior-named, not function-named? Happy + ≥1 boundary + ≥1 error per behavior? (Consult `test-engineer`.)
- **performance** — N+1 queries, hot-path allocations, unbounded loops, missing indexes (cross-check schema docs if linked).
- **api** — backward compatibility, versioning, breaking changes called out in the PR body. Evolve, don't break.
- **docs** — if linked Jira/Confluence describes behavior the PR changes, flag the drift between doc intent and diff.
- **observability** — logs/metrics/traces for new code paths, especially behind flags/experiments.
- **concurrency** — transactional boundaries, idempotency where needed, lock ordering.
- **feature-flow** — see below. Fires only when a flag/experiment/dynamic-config is in scope.
- **style / consistency** — only flag a deviation from a *confirmed* local pattern (Grep the worktree to prove the pattern exists).
- **pre-merge-sanity** — lint/typecheck clean, tests-added vs LOC, secrets, license headers on new files, accessibility on UI diffs, bundle size, doc-updated-for-behavior-change.

## Severity rubric (mirrors `persona.md`)

`blocker` (must fix; wrong behavior / security / data loss / breaking API) · `critical` (load-bearing + wrong, not P0) · `should-have` · `may-have` · `nitpick` (cap 3) · `question` (you lack context — ask, don't accuse) · `appreciation` (genuinely good work; posts as a general comment).

## Feature-flow tracing

When the diff adds a path behind a feature flag, experiment, or dynamic config:

1. **Find the reference** in the diff (the flag/experiment/config key).
2. **Resolve current state** via the `statsig` MCP (gate/experiment status, rollout %) plus a grep of the repo's config files for the same key.
3. **Check the rollout story**: is there a kill-switch path? a fallback behavior when the flag is off? a metric to watch? is the off-path tested?
4. **Flag any missing** of: no kill switch, no fallback, no metric, untested off-path. Cite the `file:line` of the flag check.

If the flag can't be resolved (Statsig unreachable, key not found), say so in the finding body and lower confidence — don't assert a state you couldn't verify.
