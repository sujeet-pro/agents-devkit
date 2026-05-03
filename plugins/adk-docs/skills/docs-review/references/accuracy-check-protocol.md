# Accuracy-check protocol

How `docs-review` verifies every "the code does X" claim in Phase 2.
Produces `claims.md`; feeds Phase 4 triage.

## Step 1 — parse claims from the doc

A *claim* is any sentence (or table cell, or code fence) that asserts
a fact about behavior, structure, version, or configuration. Candidate
patterns:

- "The service does X" / "returns Y" / "retries on Z".
- "Run `<command>`".
- "Set `<env var>` to …".
- "Uses version `<X.Y.Z>` of `<library>`".
- "File `<path>` contains …".
- "Endpoint `<METHOD /path>` accepts …".
- Any code fence (its presence asserts the snippet matches reality).

Skip non-claims: opinions, future plans, rationale for a past decision
unless the rationale is falsifiable.

## Step 2 — locate the code that should support the claim

For each claim, pick one of:

| Claim shape | Where to look |
| --- | --- |
| Path / filename mentioned | Open that path; if missing, check `git log --all -- <path>` for renames |
| Symbol mentioned (class / function / env var) | `Grep` the symbol across the repo |
| Command mentioned | Read `scripts/`, `Makefile`, `package.json` scripts, `build.gradle.kts` tasks |
| Library / framework version | Open `package.json` / `pyproject.toml` / `go.mod` / `build.gradle.kts` / `Cargo.toml` |
| Config key | Open `application.yml` / `.env.example` / config loader |
| HTTP endpoint | Open the router (`routes.ts` / Spring `@RestController` / Flask `@app.route`) |

## Step 3 — adjudicate

For each claim, pick a status:

- `OK` — the code confirms the claim.
- `wrong` — the code contradicts the claim. Record:
  - `code: <file>:<lines>` — where the contradiction lives.
  - `expected: <what the doc says>` / `actual: <what the code does>`.
- `stale-but-correct` — the content matches current code, but the
  doc's timestamp is >180d old AND the cited files have been touched
  since. Signal, not a finding by itself.
- `unverifiable` — the claim can't be checked from the repo (e.g.
  "customers report X"). Record the reason.

## Step 4 — log to `claims.md`

```markdown
# Claims — <slug>

## claim #1
- **Doc location**: `README.md:18`
- **Claim**: "Runs on Node 18"
- **Code check**: opened `package.json:engines.node`, `.nvmrc`.
- **Status**: wrong
- **Code**: `package.json:engines.node: ">=20"`, `.nvmrc: 20.11.0`.
- **Fix (candidate)**: replace "Node 18" with "Node 20".

## claim #2
- **Doc location**: `README.md:44`
- **Claim**: "requires Postgres"
- **Code check**: `docker-compose.yml:22-30` shows `postgres:15-alpine`.
- **Status**: OK (note: could tighten to "Postgres 15")
```

## Step 5 — surface Phase 4 inputs

`claims.md` feeds the triage step. Rules:

- Every `wrong` becomes a Finding (severity decided by topic
  load-bearingness; see `references/output-format.md` rubric).
- Every `unverifiable` appears in the review's Residual Risk section
  with the reason — not a Finding.
- `OK` claims are listed in the claim count; not repeated as findings.

## Load-bearingness heuristics

These topics raise severity:

- Install / setup (first-run UX for every new reader).
- Authentication / authorization (security).
- Rollback / recovery (on-call during incident).
- Payment / billing (customer-visible money).
- Data-retention / privacy (legal).

These topics lower severity:

- Aesthetic tweaks (heading depth, em-dash vs en-dash).
- FAQ answers that aren't decision-influencing.
- Historical context paragraphs.

## Guardrails

- Never run a *mutating* command as part of verification (`--help`
  only; read config files; no `curl POST`).
- Never exfiltrate secrets — if verifying an env var requires reading
  its value, just verify the var is referenced in code, not its value.
- When the code is ambiguous (multiple branches / feature flags), say
  so in the claim status. Mark `wrong` only when you're sure.
