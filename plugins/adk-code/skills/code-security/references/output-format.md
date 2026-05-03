# `code-security` — output format

## Per-turn status

```
[adk-code:code-security] task=<slug> phase=<0|1|2|3|4|5|6|7|8> threat-model=<written> boundary=<identified> exploit-test=<red|green> mitigation=<applied> security-review=<done>
```

## `.temp/task-<slug>/threat-model.md` (Phase 2)

```markdown
# Threat model — <slug>

1. Untrusted input source: <where it enters>
2. Privileged action / output: <what the system does>
3. Asset at risk: <what's protected>
4. Threat actor: <who; access level>
5. Acceptable residual risk: <what attacker can still do>
```

EXACTLY 5 lines (the labels + content). See `references/threat-model-template.md` for examples.

## `.temp/task-<slug>/boundary.md` (Phase 3)

```markdown
# Boundary — <slug>

## Input boundary
- File: <path>:<line>
- Description: <one line>

## Output / action
- File: <path>:<line>
- Description: <one line>

## Mitigation location
The mitigation lives at the input boundary above (or as close to it as possible).
```

## `.temp/task-<slug>/exploit-test.md` (Phase 4)

```markdown
# Exploit test — <slug>

## Test
- File: <repo path>
- Test name: <behavior-named>
- Test code (excerpt):
  ```<lang>
  <test code>
  ```

## Behavior
<one-paragraph: what attack is simulated; what the assertion is>

## Failing output (verbatim, on HEAD before mitigation)
```
<paste the failing output>
```

## Confidence
high | medium | low — that this captures the vulnerability
```

## `.temp/task-<slug>/plan.md` (Phase 5)

```markdown
# Mitigation plan — <slug>

## Mitigation (one sentence)
<the smallest correct change at the boundary>

## Files touched
| File | Action | Why |
| --- | --- | --- |
| routes/upload.ts | edit | add allowlist + magic-byte check |

## Why this is at the right boundary
<one paragraph explaining why this layer, not deeper>

## Validation plan
- Re-run exploit test (must pass).
- Run full affected-package suite (must be green).
```

## `.temp/task-<slug>/security-review.md` (Phase 7)

```markdown
# Security-reviewer findings — <slug>

## Findings
| Severity | Finding | Status |
| --- | --- | --- |
| Blocker | <…> | fixed in this diff |
| Critical | <…> | fixed in this diff |
| Should-have | <…> | follow-up (see report.md) |
| Question | <…> | answered in report.md |

## Notes
<any additional context from the security-reviewer agent>
```

## `.temp/task-<slug>/report.md` (Phase 8)

```markdown
# code-security report — <slug>

## Threat (verbatim from threat-model.md)
1. Untrusted input: <…>
2. Privileged action: <…>
3. Asset: <…>
4. Actor: <…>
5. Residual risk: <…>

## Boundary
- Input: <path>:<line>
- Output / action: <path>:<line>

## Exploit test
- File: <path>::<test name>
- Red→green:
  - Before mitigation (on HEAD): <paste short failing output>
  - After mitigation: <paste short passing confirmation>

## Mitigation
| File | +N / -M | Role |
| --- | --- | --- |
| routes/upload.ts | +18 / -2 | added 4 boundary checks |

## Security-review findings
| Severity | Finding | Status |
| --- | --- | --- |
| Blocker | (none) | — |
| Critical | (none) | — |
| Should-have | also add Content-Disposition: attachment | fixed in this diff |
| Question | AV scanning? | out of scope per threat model |

## Validation evidence
| Command | Exit | Notes |
| --- | --- | --- |
| `<exploit test>` | 0 | red→green confirmed |
| `<full package suite>` | 0 | <count> passed |
| `<typecheck>` | 0 | clean |
| `<lint>` | 0 | clean |
Full logs: `.temp/task-<slug>/validation/per-skill/code-security.md`

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 5 | mitigation library | `express-rate-limit` | matches repo's existing usage |

## Residual risk / follow-ups
- <bullet> — <reason>
- account-lockout (deeper defense than rate-limit) — out of scope; spawn separate `code-security` task.

## NOT done (deliberate)
- <bullet> — <reason>

## Disclosure status
- Vulnerability disclosure: <internal-only / coordinated / public>.
- Disclosure timing: <e.g. "after fix lands in production; expected 2026-05-10">.

## Next steps
1. `/adk-review:review-code-changes` before push.
2. (recommended) `/adk-review:audit-repo --scope <area>` to sweep for similar patterns.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  threat-model.md
  boundary.md
  exploit-test.md
  plan.md
  security-review.md
  validation/per-skill/code-security.md
  report.md
```

## Hand-off note shape

```
Threat: <one sentence>
Boundary: <input → action>
Exploit-test: <file::name> — red on HEAD, green after mitigation
Mitigation: <one sentence>
Security-review: <0 blockers / N should-haves>
Next: /adk-review:review-code-changes <slug>
```

Plus the offer-depth question.
