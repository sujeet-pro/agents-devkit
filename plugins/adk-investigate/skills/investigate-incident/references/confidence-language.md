# `investigate-incident` — confidence language

Every root-cause claim states confidence as `low | medium | high` — anchored to evidence, not vibes. This file is the rubric.

## The three levels

### `high` confidence

**When:**

- ≥3 independent signals agree on the same candidate cause.
- AND the implicated artifact (PR diff, gate flip target) directly touches the affected code path.
- AND no contradicting signal.

**What it allows:**

- Strong recommendation of a specific remediation (rollback / flag-off).
- Operator may execute the remediation without further investigation.

**Example:**

> "Confidence: high — DD log shows new NPE class first seen at 13:02 (Source 1); deploy `a3f9c2e` ran at 12:58 (Source 2); PR #2841 diff touches `OrderService.computePrice` (Source 3); Slack thread by Bob in `#incidents` named the same deploy (Source 4)."

### `medium` confidence

**When:**

- 2 independent signals agree on the candidate.
- AND the implicated artifact plausibly touches the affected area but isn't directly confirmed.
- OR 3+ signals agree but one is contradicting.

**What it allows:**

- Recommendation of a specific remediation, with a "verify before executing" caveat.
- Operator typically wants to confirm one more signal before acting (e.g. read the PR diff in full).

**Example:**

> "Confidence: medium — DD metrics show p99 doubled at 13:02 (Source 1); deploy `a3f9c2e` ran at 12:58 (Source 2). PR diff overlaps the affected service but doesn't obviously touch the slow path; recommend verifying with `gh pr view 2841` before rolling back."

### `low` confidence

**When:**

- 1 signal correlates with the candidate (typically temporal correlation only).
- OR multiple signals correlate but each is weak in isolation.
- OR the candidate is plausible but no source directly confirms.

**What it allows:**

- The hypothesis is labeled "leading candidate", NOT "root cause".
- The recommended action is "probe to upgrade confidence" before any remediation.

**Example:**

> "Confidence: low — only DD metrics show the latency spike. No deploy in window. No Slack pre-knowledge. The 'downstream timeout' log line suggests an upstream cause but no direct evidence."

### `n/a` (no leading hypothesis)

**When:**

- 0 sources name a candidate.
- The signals don't converge on any single cause.

**What it allows:**

- The hypothesis is "no leading hypothesis".
- The recommended actions are probes only — status pages, infra dashboards, additional source pulls.

**Example:**

> "No leading hypothesis. p99 spike with no correlated deploy, no log error class, no Slack pre-knowledge. Suggest checking upstream dependencies (Stripe status page, internal payment-gateway dashboard) and pulling the Datadog event stream for non-deploy events."

## Rules for confidence statements

1. **Always cite the source count.** "3 independent signals" or "1 signal only".
2. **Always name the sources.** "DD logs + deploy timeline + Slack" — not "multiple sources".
3. **Always say what would upgrade confidence.** For `low` and `medium`, name the probe.
4. **Never inflate confidence.** A vibes-driven "high" hides that the evidence is weak.
5. **Never deflate confidence to avoid commitment.** If 4 sources agree, say `high` — the operator can act.

## Anti-rules

- "I think it's the deploy." That's not a confidence statement; it's a guess.
- "I'm 80% sure." Don't quantify with percentages — use the three levels.
- "It's probably the deploy, low confidence." Use `low` cleanly, not "low (but really probably yes)".
- "All signals agree, high confidence." Specify HOW MANY signals and WHICH ones.

## Cross-skill rule

`/adk-investigate:investigate-experiment` and `/adk-investigate:investigate-rca` use the same confidence language. The vocabulary is consistent across the plugin so the operator builds intuition.
