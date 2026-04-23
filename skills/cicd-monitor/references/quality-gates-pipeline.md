# Quality gates pipeline — CI/CD discipline

Optional reference loaded by `cicd-monitor` (and recommended for `cicd-fix`). Encodes the "Shift Left", "Faster is Safer", "feature flags > long-lived branches" disciplines.

## The principles

- **Shift Left.** Catch problems where they're cheapest to fix — pre-commit > PR > main > prod. Every gate that fails on prod is a process failure.
- **Faster is Safer.** A 10-minute pipeline that lands 50 small changes per day is safer than a 60-minute pipeline that lands 5 large changes. Small, fast = fewer surprises per change.
- **Quality gates, not optional checks.** Gates that can be skipped will be skipped. Use branch protection.
- **Feed failures back to the agent.** The agent's `cicd-fix` should be able to read the failed-job logs (`gh run view --log-failed`) without human intervention.

## Default gate ordering (PR-time)

```
   PR opened / pushed
        │
        ▼
   ┌─ lint ─┐         ← fast (≤ 30 s); fails fast on style
   ├─ typecheck ─┤    ← (≤ 60 s); contract-level errors
   ├─ unit tests ─┤   ← (≤ 60 s); fast feedback on logic
   └─ build ─┘        ← (≤ 90 s); proves it compiles
        │
        ▼
   ┌─ integration tests ─┐  ← (≤ 5 min); collaborating modules
   ├─ e2e (critical only) ─┤ ← (≤ 5 min); user-journey smoke
   ├─ npm audit ─┤             ← CVE check
   └─ bundle size ─┘           ← perf budget gate
        │
        ▼
   ┌─ deploy preview (optional) ─┐
   └─ a11y / lighthouse on preview ─┘
```

Total target: **< 10 minutes** for a PR. If you blow this, parallelize harder, cache more aggressively, or trim scope.

## Caching strategy

- **Lockfile-keyed dep cache.** `actions/cache@v4` keyed on `package-lock.json` (or equivalent).
- **Build cache.** `vite` / `webpack` / `tsc --build` incremental cache, keyed on source SHA.
- **Test cache.** `vitest --changed`, `nx affected:test`, `turbo run test`.
- **Module graph cache.** For monorepos, only build/test the affected packages.

## Branch protection (main)

- Required reviews ≥ 1 (≥ 2 for high-risk paths).
- Required status checks: lint, typecheck, unit, integration, build, audit (and any other "must-pass" gates).
- Dismiss stale reviews on new push.
- No force-push.
- No deletes.
- Signed commits if the org enforces it.
- "Require branches to be up to date before merging" ON for high-risk repos; OFF if your CI is too slow.

## Failure feedback loop

When a gate fails:

1. The CI surface (GitHub Actions UI / `gh pr checks`) shows red.
2. `cicd-monitor` (this skill) detects the failure within the watch loop.
3. `cicd-monitor` captures `gh run view --log-failed` for the failing job.
4. Hands off to `@adk:cicd-fix` (a.k.a. `adk-cicd-fix`) with the log content.
5. `cicd-fix` parses, identifies root cause, applies fix, pushes.
6. Loop returns to step 1.

If a gate is flaky:

- Quarantine first (skip it with a tracked owner + ticket).
- Diagnose async; do not "just rerun until green" repeatedly.
- Repeated reruns mask the flake instead of fixing it.

## Gate ordering rationale

- **Lint first** — catches style/format issues in seconds; fails fast on the cheapest signals.
- **Typecheck before tests** — typed errors usually cause test errors; surfacing them first saves a slow test run.
- **Unit tests before integration** — fast, deterministic, isolated.
- **Build before integration tests** — many integration tests need the build artifact.
- **Bundle size check after build** — needs the artifact.
- **Audit anywhere** — independent; can run in parallel.
- **E2E last in PR** — slowest, most flake-prone; minimal "critical only" set on PR, full suite on main.

## What NOT to do

- "Quick PR, skip CI" — never. Even doc-only PRs go through lint at minimum.
- Manual testing as the only signal — manual is supplemental, not primary.
- A gate that's been "broken for weeks but we ignore it" — it's not a gate.
- Adding a gate without an SLA / dwell time — gates that take 30 min for a 5-line PR are gates nobody respects.
- Disabling a flaky test "for the sprint" — the disable becomes permanent.

## Recommended monitor cadence (for `cicd-monitor`)

- Poll interval: **every 30 s** during active CI run.
- Backoff: 30 s → 60 s → 120 s after the first 5 min if no state change.
- Hard timeout: **30 min** after the run started (configurable per repo).
- On failure: capture failed-job logs, post a brief summary, hand off to `cicd-fix`.
- On success: confirm and exit cleanly.
- On cancel/skip: report, do not retry automatically.
