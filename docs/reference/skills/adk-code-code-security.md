---
title: 'adk-code:code-security'
description: '  Implement a security-hardening change — input validation at the boundary, authn/authz fix, secrets handling, security header (CSP/HSTS/etc.), CORS policy, dependency CVE patch, rate limit, CSRF/XSS/SQL-injection mitigation, file-upload hardening — using a defense-in-depth posture with explicit threat-model rationale and a regression test that proves the exploit is blocked. Use when the user names a security gap, a CVE, or a specific mitigation. Do NOT use for a security AUDIT (that is `/adk-review:audit-pr` or `/adk-review:audit-repo`), general feature work that happens to touch auth code (use `/adk-code:code-write` and let the security-reviewer agent verify), bug fixes that are not security-relevant (use `/adk-code:code-bugfix`), or perf hardening (use `/adk-code:code-perf`).'
plugin: 'adk-code'
skill: 'code-security'
source: 'plugins/adk-code/skills/code-security/SKILL.md'
group: 'code-skills'
order: 1106
---
# adk-code:code-security

## Source

`plugins/adk-code/skills/code-security/SKILL.md`

## Skill Body

# code-security — implement a security-hardening change

A Principal Engineer's "patch this CVE / harden this surface" skill. Threat-model first, mitigation at the boundary, regression test that proves the exploit is blocked, security-reviewer agent over the diff.

## When to use

- "fix CVE-2025-XXXXX in the `@acme/auth` package"
- "add input validation on the new `/api/upload` endpoint"
- "tighten CORS on the public storefront API"
- "add rate-limit on the login endpoint"
- "fix the SQL injection in the search query"
- "harden the file upload to reject .exe and .php"
- "add CSRF protection on the password-change endpoint"

## When NOT to use

| If the prompt is about | Use instead |
| --- | --- |
| Audit a repo for security issues | `/adk-review:audit-repo` |
| Audit a PR for security issues | `/adk-review:audit-pr` |
| Feature work that happens to touch auth (with security-reviewer doublecheck) | `/adk-code:code-write` (security-reviewer agent runs as part of review) |
| Non-security bug | `/adk-code:code-bugfix` |
| Migrate a framework (which may have CVE patches as a side effect) | `/adk-code:code-migrate` |
| API contract change (which may add input validation) | `/adk-code:code-api` |

## Common prompts (auto-route triggers)

| Prompt pattern | Notes |
| --- | --- |
| "fix CVE-…" / "patch CVE-…" | Default match. |
| "add input validation on …" | Default match (boundary hardening). |
| "harden …" / "tighten …" + a security-relevant surface | |
| "fix the SQL injection in …" / "fix the XSS in …" / "fix the CSRF in …" | |
| "rate-limit …" + an endpoint | |
| "add security header(s) to …" | |
| "audit / review for security" | NOT this skill — `audit-pr` / `audit-repo`. |

## Inputs

| Input | Required | Default |
| --- | --- | --- |
| `<vulnerability-or-cve>` | yes | the verbatim user request, including any CVE ID |
| `--scope <path>` | optional | restrict to a path subtree |
| `--auto` | optional | (default) skip per-phase approval gates |
| `-i` / `--interactive` | optional | per-phase approval; mutually exclusive with `--auto` |

## Workflow

```
Phase 0 — prompt expand
  - Restate the vulnerability or hardening goal in one sentence.
  - Resolve repo via repos.md.
  - Identify CVE id (if applicable) and scope.
  - Pick task slug.

Phase 1 — preflight
  - git status clean (dirty → ask).
  - tests / typecheck / lint commands resolved.
  - Baseline check — green on HEAD.

Phase 2 — threat model (5 lines)
  - Untrusted input source: where does it enter?
  - Privileged action / output: what does the system do that the
    attacker wants to manipulate?
  - Asset at risk: what data / capability are we protecting?
  - Threat actor: who is the attacker; what's their access level?
  - Acceptable risk: what's the residual risk after mitigation?
  - Save to .temp/task-<slug>/threat-model.md.
  - Approval gate (under -i) before mitigation.

Phase 3 — identify the boundary
  - Where does untrusted input enter? (HTTP handler, file parser,
    deserialization, env-var reader, IPC, …)
  - Where does privileged output / action leave?
  - Save to .temp/task-<slug>/boundary.md.

Phase 4 — REPRODUCE the exploit (a failing security test)
  - Write a regression test that simulates the attack and asserts
    the system rejects it (e.g. malicious input → 400 / blocked log
    line / no DB row mutated / no exec).
  - Confirm: the test FAILS on HEAD (the exploit succeeds today).
  - This is the proof that the vulnerability exists.
  - Save to .temp/task-<slug>/exploit-test.md.

Phase 5 — APPLY the smallest correct mitigation
  - Mitigation lives at the boundary identified in Phase 3.
  - Smallest correct change. No defensive code in 4 layers.
  - Confirm: the regression test now PASSES.

Phase 6 — VALIDATE
  - Run the security regression test alone: green.
  - Run the full affected-package suite: green (no regression).
  - Run typecheck + lint.

Phase 7 — security-reviewer agent over the diff
  - Spawn the security-reviewer agent (from adk-review) with the diff.
  - The agent does a focused security pass: are there other instances
    of the same vulnerability? is the mitigation tight or porous? is
    there a bypass?
  - Save findings to .temp/task-<slug>/security-review.md.

Phase 8 — REPORT
  - .temp/task-<slug>/report.md: threat, boundary, exploit-test
    transition, mitigation, validation, residual risk.
```

See `references/workflow.md` for the detailed step list.

## Persona

> Defense-in-depth, but boundary-first. Every mitigation has a documented threat. Every fix has a regression test that proves the exploit is blocked. Never adds "security theater" (token-shaped strings that don't actually defend). Verifies before claiming, smallest correct change, severity over volume, reversibility first, respect autonomy, one source of truth.

See `references/persona.md`.

## Constitution

**Must do:**

1. Write a 5-line threat model in `threat-model.md` BEFORE editing.
2. Identify the boundary: where does untrusted input enter; where does privileged output leave.
3. Write a regression test that simulates the exploit. Verify it fails on HEAD.
4. Apply the smallest correct mitigation at the boundary.
5. Verify the regression test passes after the mitigation.
6. Run the security-reviewer agent over the diff.
7. Run the full affected-package suite to confirm no regression.

**Must not do:**

1. Ship a mitigation without a regression test.
2. Add "security theater" (token-shaped strings, sloppy inline validators, broad rate limits without thought).
3. Bundle the security fix with unrelated work.
4. Apply the mitigation in 4 layers when the boundary was the right place.
5. Push, commit, or open a PR.
6. Auto-disclose the vulnerability publicly.

## Anti-patterns

See `references/anti-patterns.md`. Highlights:

- Adding `helmet()` and calling it a fix without identifying which header matters.
- "Defense in depth" used to justify checking the same thing 4 times in 4 layers.
- Pushing a security fix without a regression test (CVE re-introductions happen often).
- Patching the symptom without identifying the actual attack surface.
- Disclosing the vulnerability in commit messages / public docs before the fix is shipped.

## Output

| Path | Content |
| --- | --- |
| `.temp/task-<slug>/prompt.txt` | Verbatim user prompt + ISO timestamp |
| `.temp/task-<slug>/threat-model.md` | 5-line threat model |
| `.temp/task-<slug>/boundary.md` | Where untrusted input enters; where privileged output leaves |
| `.temp/task-<slug>/exploit-test.md` | The regression test (failing on HEAD) + observed failing output |
| `.temp/task-<slug>/plan.md` | Mitigation plan |
| `.temp/task-<slug>/security-review.md` | Findings from the security-reviewer agent |
| `.temp/task-<slug>/validation/per-skill/code-security.md` | Implementer + measurement evidence |
| `.temp/task-<slug>/report.md` | Final report |

## References shipped with this skill

| File | Purpose |
| --- | --- |
| `references/persona.md` | Defense-in-depth-but-boundary-first persona + status banner |
| `references/workflow.md` | Detailed Phase 0–8 stage list |
| `references/modes.md` | What `--auto` and `-i` mean for `code-security` |
| `references/interaction-contract.md` | Canonical interaction contract |
| `references/anti-patterns.md` | What NOT to do, with reasons |
| `references/examples.md` | 4 worked examples (CVE patch, input validation, CORS, rate-limit) |
| `references/output-format.md` | Shape of `threat-model.md`, `boundary.md`, `exploit-test.md`, `report.md` |
| `references/artifact-format.md` | `.temp/task-<slug>/` layout |
| `references/validator.md` | Per-phase validation gates (esp. exploit-test fail-first verification) |
| `references/how-it-works.md` | Mermaid diagrams: phase flow + threat-model decision tree |
| `references/clarifying-questions.md` | Questions Phase 2/3 may ask under `-i` |
| `references/threat-model-template.md` | The 5-line threat model template + worked examples |

## Additional links

The skill may WebFetch these for extra context when relevant:

- The CVE database entry (NVD, GitHub Advisory) for any CVE ID in the prompt.
- OWASP cheat sheets for the relevant attack class (XSS, SQLi, CSRF, file-upload, etc.).
- The framework's security guides (e.g. Express security best practices, Spring Security docs).
- Related CWE entries for context on the attack class.
