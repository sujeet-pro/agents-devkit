# `code-security` — workflow detail

## Phase 0 — prompt expand

1. **Restate** the vulnerability or hardening goal in one sentence.
2. **Resolve repo** via `cwd → .git → repos.md`.
3. **Identify CVE / issue ID** if present in the prompt. WebFetch the entry from NVD / GitHub Advisory for context.
4. **Pick task slug**: `secure-<scope>-<symptom>` (e.g. `secure-search-sqli`, `secure-upload-validation`, `secure-cve-2025-12345`).
5. **Create** `.temp/task-<slug>/`. Write `prompt.txt` (without quoting the exploit details if they're sensitive).
6. **Approval gate** unless `--auto`.

## Phase 1 — preflight

1. `git status` clean. Dirty → ask.
2. Branch — protected → prompt `secure/<slug>` (or `fix/<slug>` for CVE).
3. Resolve test / typecheck / lint commands.
4. Tests pass on HEAD (baseline = green; security fix on red is unverifiable).

## Phase 2 — threat model (5 lines)

Write `.temp/task-<slug>/threat-model.md` with exactly 5 lines:

1. **Untrusted input source**: where does it enter the system?
2. **Privileged action / output**: what does the system do that the attacker wants to manipulate?
3. **Asset at risk**: what data / capability are we protecting?
4. **Threat actor**: who is the attacker; what's their access level (unauthenticated external / authenticated user / authenticated admin / insider / supply-chain)?
5. **Acceptable residual risk**: after mitigation, what's the worst the attacker can still do?

Example:

```
1. Untrusted input: q parameter on GET /api/search.
2. Privileged action: SQL query against orders table.
3. Asset: orders table contents (incl. customer email + total).
4. Actor: unauthenticated external user.
5. Residual risk: parameterized queries are immune to SQL syntax injection. NoSQL-injection variants do not apply (PostgreSQL only). Side-channel timing attacks possible but out of scope.
```

**Approval gate** under `-i`. Under `--auto`, proceed.

See `references/threat-model-template.md` for more examples.

## Phase 3 — identify the boundary

Two questions:

1. **Where does untrusted input enter the system?**
    - HTTP handler? Specific route + line.
    - File parser? Specific function.
    - Deserialization? Specific deserializer.
    - Env-var reader? Specific reader.
    - IPC / message queue? Specific consumer.

2. **Where does the privileged output / action leave?**
    - DB query construction? Specific function.
    - Shell exec? Specific exec call.
    - Outbound HTTP? Specific client.
    - Filesystem write? Specific writer.

Save to `.temp/task-<slug>/boundary.md`:

- Input boundary: `<path>:<line>` — `<one-line description>`.
- Output / action: `<path>:<line>` — `<one-line description>`.

**Mitigation lives between these two points.** Anywhere closer to the input or output than necessary is fine; anywhere "deeper" inside the system is layered defense (and usually unnecessary if the boundary is well-defended).

## Phase 4 — REPRODUCE the exploit (failing security test)

1. **Author a regression test** that simulates the attack:
    - For SQL injection: send a payload that would alter the query (`'; DROP TABLE …; --`) and assert the response is 400 (not 500 with stack trace; not 200 with extracted data).
    - For XSS: render user-supplied HTML and assert it's escaped or rejected.
    - For CSRF: send a request without the token and assert 403.
    - For auth bypass: skip auth headers and assert 401.
    - For file upload: send a `.php` / `.exe` and assert rejected.
    - For unbounded input: send 100MB and assert rejected with 413.
    - For CVE: use the published reproducer if available; else construct one from the advisory.

2. **Run the test on HEAD**. Confirm it FAILS (the exploit succeeds today). Capture the failing output.

3. **Save** `.temp/task-<slug>/exploit-test.md`:
    - The test code (or reference to where it lives in the repo).
    - The observed failing output.
    - Confidence that this captures the vulnerability: high / medium / low.

If the test passes unexpectedly: STOP. Either the exploit was misunderstood, the bug is already fixed, or the test is wrong.

## Phase 5 — APPLY the smallest correct mitigation

1. **Mitigation lives at the boundary** identified in Phase 3.
2. Spawn the `implementer` subagent with `threat-model.md` + `boundary.md` + `exploit-test.md`.
3. Apply the smallest correct change:
    - For SQL injection: parameterize the query.
    - For XSS: HTML-escape on output (or use a safe templating library that does it by default).
    - For CSRF: add token check at the boundary.
    - For auth: add the auth check at the boundary handler.
    - For file upload: add a content-type / extension allowlist + magic-number check.
    - For input bounds: add `Content-Length` cap + body parser limit.
    - For CVE: apply the patch from the upstream advisory.
4. **Re-run the exploit test**. Confirm it now PASSES (the exploit is blocked).
5. If still failing: STOP. The mitigation is wrong. Re-think.
6. No drive-by hardening. No "while I'm here" sprinkling.

## Phase 6 — VALIDATE

1. **Exploit test alone**: green.
2. **Full affected-package suite**: green (no regression).
3. **Typecheck + lint**: green.
4. Capture all to `.temp/task-<slug>/validation/per-skill/code-security.md`.
5. If any pre-existing test went red: that's a regression — STOP, don't ship the fix.

## Phase 7 — security-reviewer agent over the diff

1. Spawn the security-reviewer agent (from `adk-review/agents/security-reviewer.md`) with:
    - The diff.
    - `threat-model.md`.
    - `boundary.md`.
2. The agent does a focused security pass:
    - Are there other instances of the same vulnerability in this codebase?
    - Is the mitigation tight or porous (any bypass)?
    - Does the mitigation introduce a new vulnerability?
    - Is the mitigation at the right layer (boundary), or scattered?
3. Save findings to `.temp/task-<slug>/security-review.md`.
4. Findings tier: Blocker / Critical / Should-Have / Question.
    - **Blocker** → MUST fix before claiming done; loop back to Phase 5.
    - **Critical** → SHOULD fix in the same diff; surface explicitly.
    - **Should-Have / Question** → list as residual risk + follow-up.

## Phase 8 — REPORT

Write `.temp/task-<slug>/report.md`:

- **Threat** — verbatim from `threat-model.md`.
- **Boundary** — input + output points.
- **Exploit test** — file::name, red→green transition.
- **Mitigation** — table: file, +N/-M, role.
- **Security-review findings** — table: severity, finding, status (fixed in this diff / follow-up).
- **Validation evidence** — full suite + exploit test + lint + typecheck.
- **Decisions** — every auto-pick.
- **Residual risk / follow-ups** — bullet list.
- **Disclosure status** — has the vulnerability been disclosed? when can it be? (often: after fix lands in production).
- **Next steps** — typical: `/adk-review:review-code-changes` before push; consider `/adk-review:audit-repo` for sweep.

End with the offer-depth question.

## Loop control

- After 2 wrong mitigations (regression test still failing), STOP. The diagnosis or boundary identification is wrong.
- After security-reviewer flags a Blocker, fix in this diff (loop back to Phase 5). Never ship a Blocker.
- If the vulnerability is upstream (in a third-party library), the fix is `code-migrate` (upgrade) or a documented workaround at the boundary; don't try to patch the third-party.
- If the threat model reveals the issue is broader (e.g. "this vulnerability is in 14 places"), STOP — the right scope is `audit-repo`, not a single `code-security` task.

## Disclosure handling

For CVEs / discovered vulnerabilities:

- The fix lands BEFORE public disclosure.
- The commit message + PR description should NOT include exploit details (use a generic "input validation fix" until disclosure).
- After deployment + disclosure (per the org's disclosure policy), the operator updates documentation / CVE record.
- The skill never auto-publishes a CVE record.
