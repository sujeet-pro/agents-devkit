# `audit-pr` — check catalog

The 10 fixed checks. Each entry: detection trigger, command, pass/warn/fail thresholds, fix-strategy, references.

## 1. lint-clean

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | always |
| Tool detection | `command -v eslint` / `golangci-lint` / `ruff` / `cargo clippy` / `flake8` / `rubocop` (in this priority) |
| Command (per language) | JS/TS: `npm run lint -- --max-warnings 0 <changed-files>`<br>Go: `golangci-lint run --new-from-rev <baseline> <changed-files>`<br>Python: `ruff check <changed-files>`<br>Rust: `cargo clippy --no-deps -- -D warnings`<br>Ruby: `rubocop <changed-files>` |
| Pass | exit 0; 0 errors, 0 warnings |
| Warn | exit 0; 0 errors, ≥1 warnings |
| Fail | exit non-zero (errors present) |
| Auto-fix? | YES (`--fix` mode for the tool) |
| Reference | the repo's `eslint.config.js`, `golangci.yml`, `pyproject.toml`, `clippy.toml`, etc. |

## 2. typecheck-clean

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | tool detected (TypeScript: `tsc`; Python: `mypy`; Go: `go build`; Rust: `cargo check`) |
| Tool detection | `command -v tsc` / `mypy` / `go` / `cargo` |
| Command (per language) | TS: `tsc --noEmit -p tsconfig.json` (scoped to changed files where possible)<br>Python: `mypy <changed-files>`<br>Go: `go build ./...`<br>Rust: `cargo check --all-targets` |
| Pass | exit 0 |
| Warn | (no warn tier — typecheck is binary) |
| Fail | exit non-zero |
| Auto-fix? | NO (semantic; would require code changes) |
| Reference | `tsconfig.json`, `mypy.ini`, `go.mod`, `Cargo.toml` |

## 3. tests-added

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | always (heuristic) |
| Tool | git diff stat |
| Command | `git diff <baseline>...HEAD --stat -- '*test*' '*_test*' '*.spec.*'` for tests-LOC; `git diff <baseline>...HEAD --stat` for total-LOC; subtract for prod-LOC |
| Pass | tests-LOC ≥ 0.3 × prod-LOC OR prod-LOC ≤ 50 (small change) OR no prod-LOC change |
| Warn | tests-LOC > 0 but < 0.3 × prod-LOC AND prod-LOC > 50 |
| Fail | tests-LOC = 0 AND prod-LOC > 50 |
| Auto-fix? | NO (writing tests is `/adk-code:code-test`'s job) |
| Reference | none — pure heuristic. `~/.config/adk/review.md.test_coverage_threshold` may override the 0.3 ratio. |
| Notes | The 0.3 ratio is a heuristic; the actual coverage tool (Istanbul / Coverage.py / etc.) gives better signal. If the repo runs coverage in CI, prefer the CI signal. |

## 4. secrets-in-diff

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | always |
| Tool | combination: regex (fast) + entropy (medium) + delegate to `security-reviewer` agent for confirmation |
| Command (regex pre-pass) | `git diff <baseline>...HEAD | rg '(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{40}|glpat-[A-Za-z0-9_-]{20}|xoxb-[A-Za-z0-9-]{50,}|BEGIN PRIVATE KEY|BEGIN RSA PRIVATE KEY|BEGIN OPENSSH PRIVATE KEY)'` |
| Command (entropy fallback) | for each long string in the diff, compute Shannon entropy; flag strings with entropy >4.5 in code positions where secrets are common (e.g. `=`-anchored values) |
| Pass | no matches; no high-entropy strings in suspicious positions |
| Warn | (no warn tier — binary) |
| Fail | any match (regex OR confirmed by agent) |
| Auto-fix? | NEVER. Mitigation requires user action: rotate + remove from history. |
| Reference | `security-reviewer` agent's threat surfaces |
| Privacy | NEVER quote the secret value verbatim in `per-check/secrets-in-diff.md`. Name the type + file:line. |

## 5. license-headers

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | new source files in the diff (added; not modified) |
| Tool | none (heuristic) |
| Command | for each new source file: `head -n 5 <file>` and check against the repo's license header pattern (read from `~/.config/adk/review.md.license_header_template` OR detect from existing files in the repo) |
| Pass | all new source files have the header (or no new source files) |
| Warn | (no warn tier — binary) |
| Fail | any new source file without the header |
| Auto-fix? | YES (prepend the header to each new source file) |
| Reference | `~/.config/adk/review.md.license_header_template`; `.github/license-header.txt` if present |
| Notes | "source file" = the repo's source extensions per language (`.ts`, `.tsx`, `.js`, `.go`, `.py`, `.rs`, `.rb`, `.java`, `.kt`, etc.). NOT data files (`.json`, `.yaml`, `.md`). |

## 6. dep-licenses

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | dep-manifest changed (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, etc.) |
| Tool detection | `command -v npm-license-checker` / `pip-licenses` / `go-licenses` / `cargo-license` |
| Command (per language) | JS/TS: `npx license-checker --json --production --onlyAllow <repo-allow-list>`<br>Python: `pip-licenses --format json --packages <new-packages>`<br>Go: `go-licenses csv ./...`<br>Rust: `cargo license --json` |
| Pass | all new deps in the repo's allow-list (configurable via `~/.config/adk/review.md.allowed_licenses`; defaults: MIT, BSD-2-Clause, BSD-3-Clause, Apache-2.0, ISC, Unlicense) |
| Warn | new dep with `unknown` license |
| Fail | new dep with disallowed license (e.g. AGPL when repo policy disallows; GPL when repo policy disallows for closed-source repos) |
| Auto-fix? | NO (replacing a dep is `/adk-code:code-migrate`'s job) |
| Reference | `~/.config/adk/review.md.allowed_licenses` (operator's allow-list) |

## 7. doc-updated

| Field | Value |
| --- | --- |
| Always run | yes |
| Trigger | always (heuristic) |
| Tool | none |
| Command | check whether `CHANGELOG.md`, `README.md`, or any file under `docs/` was touched in the diff |
| Pass | docs touched OR small change (prod-LOC ≤ 50) OR test-only change |
| Warn | small change (prod-LOC ≤ 100) without docs touched |
| Fail | large change (prod-LOC > 100) without docs touched AND no test-only filter |
| Auto-fix? | LIMITED — only docs-toc (regenerate the TOC if it's stale); writing the actual docs is `/adk-docs:docs-changelog` or `/adk-docs:docs-write`'s job |
| Reference | `~/.config/adk/docs.md.changelog_path` (defaults: `CHANGELOG.md`); `~/.config/adk/docs.md.runbook_path` |

## 8. a11y-regression (conditional)

| Field | Value |
| --- | --- |
| Always run | NO |
| Trigger | UI files in the diff (`.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.astro`) |
| Tool detection | `command -v axe-core` / `pa11y`; OR repo's a11y test (e.g. `npm run test:a11y`) |
| Command | repo's `test:a11y` if present; else `npx @axe-core/cli <touched-pages>`; else `pa11y <touched-pages>` |
| Pass | 0 violations on touched components |
| Warn | warnings only (e.g. WCAG AA-best-practice) |
| Fail | errors (WCAG A or AA violations) |
| Auto-fix? | NO (often requires UX judgment) |
| Reference | `axe-core` rules; the repo's a11y test config |
| N/A reason | "no UI files touched" — surfaces in report |

## 9. perf-regression (conditional)

| Field | Value |
| --- | --- |
| Always run | NO |
| Trigger | hot-path files touched (per `~/.config/adk/datadog.md.slo_thresholds` repo→service mapping; the touched files belong to a service with documented SLOs) |
| Tool detection | repo's perf budget script (e.g. `npm run perf-budget`, `cargo bench`) |
| Command | repo-specific |
| Pass | within budget |
| Warn | within 10% over budget |
| Fail | >10% over budget |
| Auto-fix? | NO (perf investigation is `/adk-code:code-perf` + `/adk-investigate:investigate-datadog`) |
| Reference | `~/.config/adk/datadog.md.slo_thresholds` for the budget; the repo's perf-budget script |
| N/A reason | "no hot-path files touched (per datadog.md.slo_thresholds)" |

## 10. bundle-size (conditional)

| Field | Value |
| --- | --- |
| Always run | NO |
| Trigger | frontend repo with bundle-budget config (detect: `package.json` has a `bundlesize` / `size-limit` field, OR `bundlesize.config.js` / `.size-limit.json` exists) |
| Tool detection | `command -v size-limit` / `bundlesize` |
| Command | `npm run build:bundle-stats` then `npx size-limit` (or repo-specific equivalent) |
| Pass | within budget for all entries |
| Warn | within 5% over budget for any entry |
| Fail | >5% over budget for any entry |
| Auto-fix? | NO (manual investigation needed: tree-shake, code-split, etc.) |
| Reference | the repo's bundle-budget config |
| N/A reason | "not a frontend repo with bundle-budget config" |

## Adding a new check

This catalog is intentionally fixed at 10. New checks belong in:

- **`audit-repo`** if it's a repo-wide concern (not PR-specific).
- A future `audit-org` if it's an org-wide concern (across multiple repos).
- A separate skill if it's deep enough to warrant one.

If a custom check IS specifically PR-shaped, propose it as a future `audit-pr` v0.2 catalog entry; don't ad-hoc add to a single run.

## Per-language notes

The catalog adapts per the repo's primary language (from `~/.config/adk/repos.md.repos[<name>].primary_language`). If the repo is polyglot, the skill runs the appropriate tool per file (e.g. eslint for `.ts`, golangci-lint for `.go`, ruff for `.py`).

If `primary_language` isn't set, fall back to: detect the most-common file extension in the diff; pick the corresponding tool; run only that.

## Per-repo overrides via `~/.config/adk/review.md`

```yaml
ignore_in_repos:
  acme/legacy-monolith:
    - bundle-size            # repo doesn't have a budget
    - a11y-regression        # legacy CLI app; no UI

allowed_licenses:
  - MIT
  - BSD-2-Clause
  - BSD-3-Clause
  - Apache-2.0
  - ISC

test_coverage_threshold: 0.3   # default; the heuristic ratio for tests-added

license_header_template: |
  # Copyright 2026 Acme Inc.
  # SPDX-License-Identifier: MIT
```

Surfaced in `validation/per-skill/audit-pr.md` so the user can debug "why did this check skip?".
