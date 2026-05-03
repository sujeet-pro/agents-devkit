# `audit-pr` — anti-patterns

## Verdict / scoring

- **Severity-tiering.** This skill is Pass / Warn / Fail per check, not Blocker / Critical / Should-Have. Don't sneak the 6-tier system in.
- **Marking nits as `Fail`.** Style noise is `Warn`. Lint warnings are `Warn`. Lint errors are `Fail`.
- **Marking missing tools as `Fail`.** If `axe-core` isn't installed, the a11y check is `N/A` with the install command, not a `Fail`. (Mis-attribution; the check didn't actually fail.)
- **Marking flaky checks as `Fail` on first run.** If a check is flaky (e.g. perf-regression with high variance), surface as `Inconclusive` and recommend re-run; don't gate on a single noisy data point.
- **Pretending an N/A check passed.** Be honest. `N/A` ≠ `Pass`. The verdict is `mixed` if any check is N/A.
- **Overriding a `Fail` silently.** Under `-i`, the user can override; the override is recorded in `results.md`. Under `--auto`, no overrides.

## Speed / parallelism

- **Running checks serial when independent.** Slow. The whole point of audit-pr is FAST. Parallelize.
- **Spawning more than 4 parallel subagents.** Coordination overhead grows past 4. Limit per the dispatcher rule.
- **Re-running a recently-completed check (no cache).** Within a session, cache lint / typecheck for 5 minutes (the diff hasn't moved that fast).
- **Running conditional checks irrelevant to the diff.** `a11y-regression` on a backend-only diff is wasted time. Detect and skip with reason.
- **Running deep semantic analysis.** That's `review-pr`. Audit-pr is a checklist.

## Tool selection

- **Defaulting to a heuristic when the repo has a tool.** Always prefer repo-native (`npm run lint` over a regex check; `tsc` over a heuristic).
- **Running global tools that conflict with repo-pinned versions.** Use `npx <tool>` or the repo's `node_modules/.bin/` to honor pinned versions.
- **Skipping the tool detection at preflight.** Detection lets the audit honestly mark `N/A` for missing tools.
- **Running `cargo clippy` on a Rust file in a Go repo.** Detect language by file extension + repo manifest, not by file extension alone.

## --fix-specific

- **Auto-fixing tests-added.** Writing tests is `/adk-code:code-test`'s job; not safely-fixable.
- **Auto-fixing perf-regression.** Investigation, not a fix; not safely-fixable.
- **Auto-fixing dep-licenses.** Replacing a dep is a `code-migrate` task; not safely-fixable.
- **Auto-fixing secrets-in-diff.** NEVER. Surface for the user to rotate the secret + force-push remove from history.
- **Pushing under `--fix` without asking.** Always asks. Even under `--auto --fix`.
- **Editing files outside the PR's changed-files list.** The auto-fix scope is the diff. Don't bring unrelated files in.
- **Continuing after a fix's verification fails.** If `npm run lint --fix` doesn't actually clear the lint errors (e.g. some are not auto-fixable), surface; don't pretend fixed.

## Posting

- **Posting by default.** This skill is informational; comment-posting is `review-pr`'s job. Use `--post-comment` for explicit opt-in.
- **Posting per-check verbose output.** Audit comments should be terse (verdict + per-check 1-liner); link to the full report for depth.
- **Re-posting on a propagation miss.** Same rule: never. Surface; user verifies in UI.
- **Posting to a closed PR.** Verify the PR is open before posting.

## Reporting

- **Verdict-buried-in-detail.** Lead with the verdict. The reader scans the verdict in 5 seconds; only the curious read the per-check section.
- **Padding green checks with prose.** A clean PR gets a 1-line "all 10 Pass". Don't elaborate.
- **Not surfacing the failing command + output for `Fail`.** Make failures actionable: include the exact command + the relevant output lines.
- **Re-litigating CI signals.** If CI has already run lint and is green, surface "lint: PASS (per CI; not re-run)" and move on.
- **Mixing audit results with review-pr findings.** If both ran on the same PR, the user sees them in different reports. Don't fold audit's Pass/Warn/Fail into review-pr's severity tiers.
