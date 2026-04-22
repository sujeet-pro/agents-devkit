# `cicd-fix` — failure-class recipes

## lint
- Pattern: `eslint`, `ruff`, `golangci-lint` non-zero with rule citations.
- Auto-fix: `npm run lint -- --fix` (or `ruff check --fix` etc.). For unfixable rules, edit by hand.
- Validation: re-run lint locally; expect 0 violations.

## typecheck
- Pattern: `error TS####`, `mypy: ... has incompatible type`, `go vet:`.
- Auto-fix: parse the error; fix the type assertion / annotation / cast.
- Validation: `tsc --noEmit` / `mypy .` / `go vet ./...` exit 0.

## test (failure)
- Pattern: assertion failed, `Expected X but got Y`.
- Auto-fix: read failing test + tested code; decide if code is wrong (fix code) or test is wrong (update test, but ONLY if obviously stale and human-confirms).
- Validation: re-run that single test, then full suite.

## build
- Pattern: `Cannot find module`, `Unexpected token`, `error: ...`.
- Auto-fix: usually missing import OR a typo; fix; re-run build.

## dep-missing
- Pattern: `Cannot find module 'X'`, `package X not found`.
- Auto-fix: check `package.json` deps; if missing, `npm install X`; if lockfile wrong, `rm package-lock.json && npm install` (warn user; lockfile change is meaningful).

## snapshot-drift
- Pattern: snapshot test reports diff.
- Auto-fix: intentional behavior change? Yes → `npm test -- -u`; commit with explicit "update snapshots: <reason>" message. Unintentional → fix the code, do NOT update snapshots.

## flaky
- Pattern: known flaky (per `repo/.flaky-tests.json` or pattern), OR retry succeeds.
- Auto-fix: `gh run rerun <runId> --failed` ONCE. If still fails, re-classify as real.

## infra
- Pattern: `runner unavailable`, `registry timeout`, `npm ETIMEDOUT`.
- Auto-fix: `gh run rerun <runId>`. If 3 retries fail, escalate to user.

## (escalate without auto-fix)
- Missing secret: `Secret X not set` — user must add in GH settings.
- Auth: `401 unauthorized to ghcr.io` — user must check token.
- Permissions: `permission denied` — repo settings.
