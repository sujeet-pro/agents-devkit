# `investigate-incident` — next-action priorities

After naming a leading candidate, the report's `Next actions` section is ordered by **blast radius** (smallest first) and **reversibility** (most reversible first). The fixed priority order is:

```
1. Rollback              (smallest blast radius for deploy regressions)
2. Flag-off              (smallest for Statsig-related causes)
3. Restart hosts         (smallest for host-isolated issues)
4. Investigate-which-PR  (when the deploy diff has multiple suspects)
5. Escalate              (last resort)
```

## 1. Rollback

**When:**

- Leading candidate is a recent deploy.
- The deploy system supports rollback (workflow_dispatch, blue-green, canary cleanup).
- Rollback is reversible in <5–10 minutes.

**Cost:** typically 5 min. Reversible.

**Concrete shape:**

```markdown
1. **Rollback `a3f9c2e`** (blast radius: surgical; reversible in <5 min)
   Command: `gh workflow run rollback.yml -f sha=<previous-sha> --repo acme/checkout-api`
   Cost: ~5 min. Reversible.
   Verifies hypothesis: if metrics recover, root cause is confirmed.
```

**Constraints:**

- NEVER auto-trigger. The operator runs the command.
- Verify the deploy diff is relevant first (`gh pr view <pr>`); if the diff is unrelated, demote rollback.
- If multiple repos deployed in window, only rollback the one matching the leading-candidate evidence.

## 2. Flag-off

**When:**

- Leading candidate is a Statsig gate flip / experiment start.
- The gate has an off / kill switch.

**Cost:** seconds. Reversible.

**Concrete shape:**

```markdown
2. **Flag-off `checkout_redesign`** (blast radius: surgical; reversible in seconds)
   Action: in the Statsig console (https://console.statsig.com/.../gates/checkout_redesign), set rollout to 0% or hit the killswitch.
   Cost: <1 min. Reversible.
   Verifies hypothesis: if metrics recover, the gate flip was the cause.
```

**Constraints:**

- This skill does NOT toggle the gate (out of scope; uses the Statsig console).
- The Statsig audit log (`/adk-investigate:investigate-statsig --use audit-log`) should have surfaced the flip as a signal first.

## 3. Restart hosts

**When:**

- Errors are isolated to a subset of hosts / pods (not service-wide).
- Restart returns affected hosts to a known-good image / state.

**Cost:** 1–10 min depending on rollout strategy. Reversible (the bad code may come back, but the immediate symptom clears).

**Concrete shape:**

```markdown
3. **Restart affected pods** (blast radius: bounded; reversible)
   Command: `kubectl rollout restart deployment/checkout-api -n prod` (or operator's deploy CLI).
   Cost: ~3 min for rolling restart.
   Caveat: if the bad code is in the latest image, restart will reproduce the symptom; pair with rollback (option 1) for durable fix.
```

## 4. Investigate-which-PR

**When:**

- The deploy diff has multiple plausible suspects.
- A single rollback would revert too much.

**Cost:** 10–30 min. Manual.

**Concrete shape:**

```markdown
4. **Identify the offending PR** (blast radius: investigative)
   Steps:
   - `git log a3f9c2e^..a3f9c2e --pretty=oneline` to list commits in the deploy.
   - For each commit touching the affected service path, `git show <sha>`.
   - Identify the one PR most likely; revert it specifically (not the whole deploy).
   Cost: 10–30 min.
```

## 5. Escalate

**When:**

- Hypothesis confidence is low or "no leading hypothesis".
- The above options aren't applicable (no recent deploy, no Statsig flip, not host-isolated).
- The symptom is severe (P0/P1) and the on-call needs help.

**Cost:** depends on responder. Reversible (escalation isn't an action, it's a request).

**Concrete shape:**

```markdown
5. **Escalate to on-call channel** (blast radius: zero — this is a notify-and-wait)
   Action: post to `#platform-oncall` (from `slack.md.oncall_channel`) with:
   - The symptom + window
   - The link to this incident.md
   - The hypothesis (or "no leading hypothesis")
   - The actions already attempted (with timestamps)
   Cost: response time depends on availability.
```

## Ordering rule

The report's `Next actions` section ALWAYS lists actions in this priority order. If an action is not applicable (e.g. no recent deploy → no rollback option), it is omitted, not listed as N/A.

## Composability rule

Multiple actions can be sequenced:

```markdown
1. **Rollback `a3f9c2e`** — verifies hypothesis quickly.
2. **If rollback confirms the diagnosis:** queue `/adk-code:code-bugfix` for the proper fix.
```

The skill suggests; the operator decides.

## NEVER auto-trigger

This skill, in any mode (`--auto`, `-i`), does NOT execute any of these actions. It produces the command / link / instructions; the operator runs them.

A future explicitly write-enabled rollback workflow could opt into
auto-rollback for very high-confidence cases. This skill does not.
