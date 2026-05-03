# `code-security` — mode contract

`code-security` supports `--auto` (default) and `-i` / `--interactive`. Does **not** support `--fix` — mutation IS the goal.

## `--auto` (default)

- Skips per-phase approval gates.
- Picks the documented `(default)` option at every decision.
- **Still writes the threat model.** Auto does NOT skip Phase 2.
- **Still writes the failing exploit test.** Auto does NOT skip Phase 4.
- **Still runs the security-reviewer agent.** Auto does NOT skip Phase 7.
- **Still verifies the exploit test went red→green.** That's the proof.
- Refuses any irreversible destructive op.

## `-i` / `--interactive`

- Mutually exclusive with `--auto`.
- Per-phase approval gates:
    - Phase 0 — confirm the vulnerability + scope.
    - Phase 2 — review the threat model (operator may know context the skill doesn't, e.g. "the actor here is a partner integration, not external").
    - Phase 3 — confirm the boundary identification (most-valuable gate; operator may know architecturally where the right boundary is).
    - Phase 4 — review the exploit test (operator may know a sharper attack pattern).
    - Phase 5 — review the mitigation diff.
    - Phase 7 — review the security-reviewer findings.
    - Phase 8 — confirm the report.

## `--scope <path>`

- Optional, composes with `--auto` and `-i`.
- Restricts reads / edits to a path subtree.
- Useful when the vulnerability is in a specific package of a monorepo.

## What `code-security` will NEVER do, even under `--auto`

1. Skip the threat model.
2. Skip the exploit test (the proof of the vulnerability).
3. Skip the security-reviewer agent pass.
4. Add "security theater" — checks that don't actually defend.
5. Disclose the vulnerability publicly — not in commit messages, not in PR descriptions, not in docs — until the fix is shipped + the org's disclosure policy permits.
6. Bundle the security fix with unrelated work.
7. Apply mitigation in 4 layers when the boundary is the right place.
8. Push, commit, or open a PR.
9. Auto-publish a CVE record.
10. Continue past a Blocker finding from the security-reviewer agent.

## What `--auto` MAY do without asking

- Pick between two equivalent mitigations at the same boundary (e.g. zod vs joi for input validation if the repo uses both — pick whichever has higher usage; record in Decisions).
- Apply the mitigation suggested by the upstream CVE advisory if it's a clear match.
- Set the deprecation default to "fail closed" (reject) on any ambiguity.

## Composition

- Called from `/adk-core:auto`, the chain is typically `auto → code-security → review-code-changes`. `auto` propagates flags down.
- Called as a follow-up to `/adk-review:audit-repo` or `audit-pr` — the audit identifies the issues; `code-security` fixes one of them per task.
- Called directly with `--auto`, runs end-to-end.
- Called directly with `-i`, runs interactively.

## Invalid combinations

- `--auto -i` — refused at parse.
- `--fix` — silently ignored. `code-security` always mutates.

## Disclosure handling under `--auto`

`--auto` defaults to **CONSERVATIVE disclosure**:

- Commit message: generic ("input validation fix on /api/foo"; "rate-limit on login"; "CVE patch in @acme/auth"). Does NOT include exploit details.
- PR description: same.
- The report (`report.md`) — internal artifact under `.temp/` — DOES include exploit details for the operator's records.
- The operator handles the public disclosure timing per the org's policy.

If the operator wants the disclosure handled differently (e.g. immediate disclosure for an already-public CVE), they pass `-i` and override the defaults.
