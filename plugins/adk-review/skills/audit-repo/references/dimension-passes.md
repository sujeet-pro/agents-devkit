# `audit-repo` — dimension passes

The 6 dimensions, each with: tools (preferred order), heuristics (fallback), what to surface as a finding vs as healthy, common pitfalls.

## Selecting which dimensions to run

Default: all 6. Subset via `--dimensions <list>`. Each dimension may be SKIPPED with reason if not applicable (e.g. `bundle-size`-style perf check on a backend-only repo).

## 1. Security

### Tools (preferred order)

| Tool | Language | Command | What it finds |
| --- | --- | --- | --- |
| npm audit | JS/TS | `npm audit --omit=dev --json` | known CVEs in production deps |
| pnpm audit | JS/TS | `pnpm audit --prod --json` | same |
| pip-audit | Python | `pip-audit --format json` | known CVEs in deps |
| safety | Python (legacy) | `safety check --json` | same |
| govulncheck | Go | `govulncheck ./...` | known CVEs in deps; reachability analysis |
| gosec | Go | `gosec -fmt json ./...` | static analysis: hardcoded creds, weak crypto, SQL injection |
| bandit | Python | `bandit -r src/ -f json` | static analysis: hardcoded creds, weak crypto, etc. |
| bundler-audit | Ruby | `bundle audit check --update` | known CVEs in deps |
| cargo-audit | Rust | `cargo audit --json` | known CVEs in deps |
| Trivy | container | `trivy fs --format json .` | container + dep CVEs |
| repo's own SAST | varies | per `.github/workflows/` | repo-specific |

### `security-reviewer` agent

After running the tools, delegate to `security-reviewer` for code-level review of:

- Auth surfaces (new endpoints; new role checks; new middleware)
- Input handling (SQL, command, deserialization, path traversal, XML)
- Output handling (XSS, log injection)
- Network (SSRF, CSRF, missing TLS)
- Crypto (insecure algos, hardcoded IV/keys)
- Secrets in code (regex + entropy + agent's threat surfaces)

The agent runs across the whole repo (or `--scope`). Findings are file-anchored.

### What's healthy in this dimension

- `npm audit` / `pip-audit` / `gosec` clean.
- 0 secrets in repo (after regex + entropy scan).
- All deps pinned (no version ranges with `^` / `~` for major-version drift).
- SECURITY.md present with reporting policy.
- `.github/workflows/` has security scan (Snyk, Dependabot, CodeQL, etc.).
- Branch protection on `main`/`master` (required reviewers, required checks).
- Secrets scanning enabled (GitHub secret scanning, gitleaks in CI, etc.).

### Common pitfalls

- Treating `npm audit` warnings (in dev deps) as production findings. They're not.
- Quoting the actual secret value when reporting `secret_in_diff`. NEVER. Name the type + file/line.
- Marking known-safe CVEs as findings (e.g. CVE in a transitive dep that the repo doesn't actually call). The agent should walk the call-graph.

## 2. Performance

### Tools

| Tool | Detection | Command |
| --- | --- | --- |
| repo's perf budget script | `package.json` has `perf-budget` script | `npm run perf-budget` |
| size-limit | `.size-limit.json` | `npx size-limit` |
| bundlesize | `bundlesize.config.js` | `npx bundlesize` |
| webpack-bundle-analyzer | `webpack.config.*` + analyzer plugin | repo-specific |
| pprof | Go | `go test -cpuprofile cpu.out ./...` (runs the test suite under profiler) |
| pyspy | Python | (manual; run as a separate session) |

### Heuristics (when no tool)

Read the top-20 hot-path files (most-changed, per inventory). Flag:

- n+1 queries (loop body contains `.find()` / `.get()` / `SELECT`).
- Unbounded loops (`while true` / no upper bound on input).
- Sync I/O on hot path (`requests.get` / synchronous file read in handler).
- Allocation in tight loop (large objects in inner loops).
- Missing index implied by query pattern (`WHERE created_at > ?` on a column with no index).
- Per-request work that should be per-process (`regexp.MustCompile` inside handler).
- O(n²) where O(n log n) is straightforward.

Cross-reference: `~/.config/adk/datadog.md.slo_thresholds` for the repo's documented SLOs.

### What's healthy

- Perf budget script passes.
- Bundle size within budget.
- p99 latency within SLO (per DD).
- 0 known n+1 queries on the critical paths.

### Common pitfalls

- Flagging "could be faster" without measurement. Only flag if there's a concrete budget (SLO, bundle budget) being violated, OR a code anti-pattern with known scale (e.g. n+1 in a loop over user-supplied count).
- Skipping the heuristic pass because no tool. The heuristics catch the obvious anti-patterns.

## 3. Quality

### Tools

| Tool | Language | Command |
| --- | --- | --- |
| eslint | JS/TS | `eslint --max-warnings 0 src/` |
| golangci-lint | Go | `golangci-lint run --new-from-rev <baseline>` |
| ruff | Python | `ruff check .` |
| flake8 | Python (legacy) | `flake8 src/` |
| clippy | Rust | `cargo clippy --no-deps -- -D warnings` |
| rubocop | Ruby | `rubocop` |
| radon (complexity) | Python | `radon cc src/ -s -a` |
| gocyclo | Go | `gocyclo -over 15 .` |
| complexity-report | JS | `complexity-report src/` |
| jscpd (duplication) | any | `jscpd src/` |
| sonarqube / sonarcloud | any | repo-specific |

### Heuristics

- God-class detection: files >500 LOC OR classes/structs with >20 methods/fields.
- Single-responsibility violations: file mixes 3+ unrelated concerns (heuristic: imports across 3+ unrelated subsystems).
- Dead code: exported function not referenced anywhere.
- Long function: >100 LOC for a single function.

### What's healthy

- Lint clean (0 errors, ≤acceptable warnings).
- Cyclomatic complexity P95 < 15.
- 0 god-classes (>500 LOC is the cutoff).
- Type-check strict mode enabled.

### Common pitfalls

- Listing every lint warning. Aggregate ("47 warnings, mostly `no-unused-vars` in test files").
- Treating "long function" as Critical. Most are May-Have or Nitpick.

## 4. Dependencies

### Tools

| Tool | Language | Command |
| --- | --- | --- |
| npm outdated | JS/TS | `npm outdated --json` |
| pnpm outdated | JS/TS | `pnpm outdated --format json` |
| pip-licenses | Python | `pip-licenses --format json` |
| pip list --outdated | Python | `pip list --outdated --format json` |
| go list -m -u all | Go | `go list -m -u -json all` |
| go-licenses | Go | `go-licenses csv ./...` |
| cargo outdated | Rust | `cargo outdated --format json` |
| cargo license | Rust | `cargo license --json` |
| bundle outdated | Ruby | `bundle outdated --parseable` |
| Dependabot alerts | GitHub | `gh api /repos/<repo>/dependabot/alerts --paginate` |

### Heuristics (when no tool)

- Scan `package.json` / `requirements.txt` / `go.mod` / etc. for major-version-old deps (e.g. React 18 when 19 is GA).
- Cross-reference vs known-CVE lists (NVD, GHSA).
- Identify "orphaned" deps (in manifest but not imported anywhere).

### What's healthy

- 0 known CVEs in production deps.
- All deps within 1 major version of latest.
- 0 orphaned deps.
- All deps in the repo's allow-list licenses.

### Common pitfalls

- Treating dev-dep updates as urgent. Usually not.
- Flagging the major-version upgrade as a single Should-Have. The actual work is `code-migrate`-shaped (week-scale).
- Ignoring lockfile drift between `package.json` and `package-lock.json` — this is a real (silent) issue.

## 5. Test coverage

### Tools

| Tool | Language | Command |
| --- | --- | --- |
| vitest --coverage | JS/TS | `npx vitest run --coverage --reporter json` |
| jest --coverage | JS/TS | `jest --coverage --json` |
| pytest --cov | Python | `pytest --cov=src --cov-report=json` |
| go test -cover | Go | `go test -coverprofile cover.out ./...` |
| cargo tarpaulin | Rust | `cargo tarpaulin --out json` |
| simplecov | Ruby | runs as part of `rspec` if configured |

### Heuristics (when no tool)

- Identify untested critical paths: directories matching `auth/`, `payment/`, `billing/`, `data-write/` with NO sibling `_test`/`.test.` files.
- Test-LOC vs prod-LOC ratio per directory (>0.3 = healthy).
- Disabled / skipped tests (`it.skip`, `t.Skip`, `@Disabled`).

### What's healthy

- Coverage >80% on critical paths.
- 0 disabled tests in the diff.
- Test suite runs in <5 min.
- Integration tests present (not just unit).

### Common pitfalls

- Citing line coverage as a sole metric. Branch coverage is more meaningful.
- Counting trivially-vacuous tests as "covered". The agent should sniff for tests that don't actually assert.
- Targeting 100% coverage. Diminishing returns past 80%; some paths are intentionally not covered (e.g. auto-generated code).

## 6. Architecture

### Tools

| Tool | Language | Command |
| --- | --- | --- |
| madge | JS/TS | `madge --json --circular src/` |
| pydeps | Python | `pydeps --max-bacon 0 --noshow --show-deps src/` |
| dependency-cruiser | JS/TS | `dependency-cruiser --output-type json src/` |
| go mod graph | Go | `go mod graph` (then process for cycles) |
| cargo modules | Rust | `cargo modules generate tree` |

### Heuristics

- Cyclic deps within `src/`.
- Boundary violations: files in `src/api/` import from `src/db/` directly (bypassing `src/services/`).
- "God modules": directories with >50 files.
- CODEOWNERS gaps: files under no team's ownership.
- Architectural drift: `docs/architecture.md` (or ADRs) describe a structure that the code doesn't follow.

### What's healthy

- 0 cyclic deps.
- All files have a CODEOWNER.
- Documented architecture matches code.
- Module sizes are bounded (<50 files per module).
- Clear layered structure (e.g. api → service → db) is followed.

### Common pitfalls

- Flagging "god module" without thinking about whether it's actually problematic. A `src/utils/` with 60 files might be fine if they're all small + cohesive.
- Treating cyclic deps as Blocker. Most are Should-Have unless they cause measurable harm.
- Auditing architecture without reading the repo's own architecture docs first. The repo may have an ADR explaining "yes, we know about this structure; here's why".

## Per-dimension parallelism

```
Group 1 (in parallel, max 4): security, performance, quality, deps
Group 2 (after Group 1):       test-coverage, architecture
```

If `--dimensions` subset, run the requested set in parallel groups of up to 4.

## De-noise

Same rules as `review-pr`:

1. Same root cause across multiple files → collapse to 1 finding + references.
2. Same dimension flagging the same item → pick highest-severity wording.
3. Cross-dimension findings → surface both, mark `discuss`.
4. Lint already covers it → don't re-raise in security/quality (the lint pass does it).
