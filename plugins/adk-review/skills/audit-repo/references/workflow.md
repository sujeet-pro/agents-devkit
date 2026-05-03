# `audit-repo` — workflow detail

Detailed phase-by-phase stage list. Logs to `.temp/reports/audit-<slug>-evidence/methodology.md` (and to `validation/per-skill/audit-repo.md` for the universal validator).

## Phase 0 — prompt expand

1. **Resolve repo path.**
   - If `<repo-path>` arg → use it.
   - Else → CWD walk-up to `.git`. Stop with "not a git repo" otherwise.
2. **Slug.** `audit-<repo-name>-<YYYY-MM-DD>` (date-stamped because audits are point-in-time snapshots; re-running tomorrow gets a different slug).
3. **Determine dimensions subset** (default: all 6).
4. **Determine `--scope <path>` filter** if set.

## Phase 1 — preflight

1. **In a git repo.** `git rev-parse --is-inside-work-tree` → true.
2. **`bin/adk-info repos --check`** returns 0.
3. **Tool detection per `references/dimension-passes.md`.** For each dimension, detect repo-native tools. Mark `executable` or `N/A (missing tool: <name>; install: <command>)`.
4. **Read the repo's meta-docs:** `README.md`, `SECURITY.md`, `CONTRIBUTING.md`, `CODEOWNERS`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules`, `docs/architecture.md` (if present), `docs/adr/` (if present). Cache for the dimension passes.

## Phase 2 — inventory

Per `references/inventory.md`. Outputs `audit-<slug>-evidence/inventory.md`:

```markdown
# Inventory — <repo>

## Languages (by LOC)
| Language | LOC | % of total |
| --- | --- | --- |
| TypeScript | 12,400 | 62% |
| Python | 5,200 | 26% |
| Markdown | 1,200 | 6% |
| YAML | 800 | 4% |
| Other | 400 | 2% |

## Framework / runtime
- Primary: Next.js 15 (App Router)
- Secondary: FastAPI 0.110 (for the data backend)
- Node version: 22.7.0 (per .nvmrc)

## Dep manager
- Node: pnpm 9.15
- Python: uv 0.4

## Test framework
- Node: Vitest 2.1
- Python: pytest 8.3 + coverage.py

## Lint tool
- Node: eslint 9.x + @typescript-eslint
- Python: ruff 0.7

## Type-check
- Node: tsc 5.6 (`tsconfig.json` strict mode: yes)
- Python: mypy 1.13 (strict mode: no — `disallow_untyped_defs: false`)

## CI provider
- GitHub Actions (4 workflows: build, test, deploy-staging, deploy-prod)

## Deployment
- Frontend: Vercel
- Backend: AWS ECS Fargate (per `infrastructure/ecs.tf`)

## Observability
- Datadog (per .github/workflows/deploy-prod.yml — DD_API_KEY referenced)
- Sentry (per src/lib/sentry.ts)

## Top 20 largest files (by LOC)
| File | LOC |
| --- | --- |
| src/billing/calculator.ts | 1,820 |
| src/api/legacy-orders.ts | 1,640 |
| ... |

## Top 20 most-changed files (last 6 months, by commit count)
| File | Commits |
| --- | --- |
| src/api/checkout.ts | 47 |
| src/billing/calculator.ts | 32 |
| ... |

## Repo metadata
- Total commits: 4,820
- Active contributors (last 30d): 8
- Open PRs: 12
- Open issues: 47
- Last release tag: v2.4.1 (2026-04-15)
```

The inventory takes ~1-2 minutes; informs every dimension pass.

## Phase 3 — dimension passes

Spawn parallel subagents (max 4 at once per dispatcher rule). Each loads the appropriate agent. Each writes `audit-<slug>-evidence/<dimension>.md`.

Per `references/dimension-passes.md`:

| Dimension | Agent | Repo-native tools (preferred) | Heuristics (fallback) |
| --- | --- | --- | --- |
| security | `security-reviewer` | `npm audit`, `pip-audit`, `gosec`, `govulncheck`, `bundler-audit`, `cargo audit`, plus repo's SAST if any | per `security-reviewer`'s threat surfaces |
| performance | `code-reviewer` | repo's perf budget script (e.g. `npm run perf-budget`); profile output if available | top-20 hot-path files (most-changed); n+1 / unbounded loop / sync-IO heuristics |
| quality | `code-reviewer` | `eslint --max-warnings 0`, `golangci-lint --new-from-rev`, `ruff`, `cargo clippy`; cyclomatic complexity (`radon`, `gocyclo`, `complexity-report`) | god-class detection (>500 LOC; >20 methods); duplication (jscpd if available) |
| deps | `code-reviewer` | `npm outdated`, `pip list --outdated`, `go list -m -u all`, `cargo outdated`; license tools per `audit-pr`'s catalog | manual cross-reference vs known-CVE lists |
| test-coverage | `code-reviewer` | `pytest --cov`, `vitest --coverage`, `go test -cover`, `cargo tarpaulin`; CI's coverage report if available | identify untested critical paths (auth, payment, data write) |
| architecture | `code-reviewer` | dep-graph tools (`madge`, `pydeps`); CODEOWNERS / module boundaries | sample top-20 largest files; cyclic-dep detection; boundary violations |

### Each dimension's output

```markdown
# <dimension> — <repo>

## Summary
<one paragraph — what was checked, what was found at high level>

## Findings
| Severity | File:line | Issue | Confidence |
| --- | --- | --- | --- |
| Blocker | <file:line> | <one-line> | high |
| ... |

## Tool runs
| Tool | Command | Output (link to evidence file) |
| --- | --- | --- |
| npm audit | `npm audit --omit=dev` | per-finding/sec-001-npm-audit.txt |
| ... |

## What's healthy in this dimension
| Observation | Evidence |
| --- | --- |
| 0 known CVEs in production deps | npm audit clean |
| ... |

## Coverage
- What was checked: <list>
- What was NOT checked: <list, with reason>
```

Run all 6 dimensions in parallel groups (e.g. group 1: security + performance + quality + deps; group 2: test-coverage + architecture).

## Phase 4 — aggregate

Per `references/aggregation.md`:

1. **Collect all findings** from per-dimension reports.
2. **Apply `~/.config/adk/review.md.severity_bar` overrides.**
3. **Sort by severity** (Blocker → Critical → Should-Have → May-Have → Nitpick → Question).
4. **Within severity, sort by impact-area breadth** (e.g. "missing input validation in 5 endpoints" ranks above "missing input validation in 1 endpoint").
5. **Pick the Top-10.** If fewer than 10 real findings exist, surface fewer (don't pad).
6. **Group remaining findings per dimension.**
7. **Build the "what's healthy" section** by collating the per-dimension `What's healthy in this dimension` sub-sections; pick the top 5 across dimensions.
8. **Build recommendations** sorted by severity AND effort (low-effort high-impact first); each recommendation references the appropriate `/adk-code:*` skill or other action.

## Phase 5 — propose

1. **Show Top-10 + per-dimension counts.**
2. **Mode branch:**
   - `-i`: walk each Top-10 finding; allow re-tier / discard. Allow user to add a finding the heuristic missed.
   - `--auto`: keep aggregation as-is.
3. **Approval gate** (unless `--auto`): user confirms Top-10 before writing the report.

## Phase 6 — write report

1. Write the full report to `.temp/reports/audit-<slug>.md` per `references/output-format.md`:
   - Section 1: Executive summary (≤½ page; lead with verdict).
   - Section 2: Top-10 (severity-sorted; file-anchored).
   - Section 3: Per-dimension detail (1 page per dimension).
   - Section 4: What's healthy (top 5 across dimensions).
   - Section 5: Recommendations (prioritized by severity + effort).
   - Section 6: Methodology + scope (what was/wasn't covered; tools used; time taken).
2. Write per-dimension detail to `.temp/reports/audit-<slug>-evidence/<dimension>.md`.
3. Write per-finding evidence (when needed; for findings that warrant deeper exhibits — long tool outputs, deep dep-tree dumps, etc.) to `.temp/reports/audit-<slug>-evidence/per-finding/<id>.md`.

## Phase 7 — final

1. **Surface to user:** the report path + the verdict + the Top-3 findings (the most-pressing).
2. **Suggest natural follow-ups.** Each Top-10 finding may map to:
   - `/adk-code:code-security` for security findings.
   - `/adk-code:code-perf` for performance findings.
   - `/adk-code:code-test` for test-coverage findings.
   - `/adk-code:code-refactor` for architecture findings.
   - `/adk-code:code-migrate` for major dep upgrades.
   - For each, suggest the skill + the right scope filter.

## Loop control

- **Same dimension fails 3 times in a row.** Surface to user (likely a tool config issue or repo state issue).
- **Inventory takes >2 minutes.** Surface progress; consider `--scope` to narrow.
- **Total report exceeds 1200 lines.** Warn the user; suggest `--scope <subdir>` to focus.
- **More than 4 parallel subagents.** Refuse — coordination overhead grows past 4.
- **Tool output exceeds 10MB.** Truncate in the per-dimension report; reference the full output by path.

## Key differences from `audit-pr`

| Concern | `audit-pr` | `audit-repo` |
| --- | --- | --- |
| Scope | single PR diff | whole repo (or `--scope <subdir>`) |
| Verdict model | Pass/Warn/Fail per check | severity-tiered findings (B/C/S/M/N/Q) |
| Findings count | 10 fixed checks | unlimited (de-noised; Top-10 surfaced) |
| Modes | auto, interactive, fix | auto, interactive only (no `--fix`; read-only) |
| Comment posting | `--post-comment` opt-in | NEVER (read-only) |
| Output location | `.temp/task-<slug>/audit/` | `.temp/reports/audit-<slug>.md` (audits are task-independent) |
| Healthy findings | not surfaced (focus is gating) | REQUIRED section |
| Tool detection | per check | per dimension |
| Run time | seconds-to-minutes | minutes-to-tens-of-minutes |
