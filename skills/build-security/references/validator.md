# `build-security` — four-phase validator

Run at every phase boundary. Log to `.temp/task-<slug>/validation/per-skill/build-security.md`.

## Phase 1 — pre-execution

- [ ] Gap is specific (weakness named) and the source is cited (CVE id / OWASP item / audit finding / threat-model entry).
- [ ] Three-tier classification done (Always / Ask / Never) per `references/three-tier-boundaries.md`.
- [ ] If "Never": skill REFUSES and explains; no further phases.
- [ ] If "Ask first": explicit user approval captured (even under `--mode fix`).
- [ ] `.temp/task-<slug>/notes/` exists.

## Phase 2 — mid-flow

- [ ] **Pre-commit secret scan ran** and is clean (`git diff --cached` searched for `password|secret|api[_-]?key|token|private[_-]?key`).
- [ ] Mitigation pattern picked from `references/owasp-patterns.md` (or documented exception).
- [ ] Validation is at the boundary (edge), not interleaved with business logic.
- [ ] Allowlist used over denylist where applicable.
- [ ] Vetted library used for crypto / auth / password hashing (no homegrown).

## Phase 3 — pre-handoff

- [ ] Regression test added — fails without the fix, passes with it.
- [ ] Repo-native typecheck + lint + tests pass.
- [ ] `npm audit` (or `pip-audit` / `cargo audit` / equivalent) shows the original CVE resolved (if applicable).
- [ ] Security headers verified (curl, `chrome-devtools` MCP, or middleware test) if header-related.
- [ ] Authz / authn contract tests pass if auth-related.
- [ ] No protection was weakened to make a test pass.
- [ ] If a secret was leaked, follow-up "rotate credential" item is in the residual risk section.

## Phase 4 — post-execution

- [ ] Final report exists with gap / mitigation / regression test / audit status / residual risk / follow-up.
- [ ] User acknowledged (or `--auto`).
