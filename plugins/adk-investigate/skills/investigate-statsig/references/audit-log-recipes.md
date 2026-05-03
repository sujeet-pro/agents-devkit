# `investigate-statsig` — audit log recipes

`Get_Audit_Logs` is the most underused Statsig tool. These recipes cover the high-value queries.

## Recipe 1 — last 60 minutes (default for `--use audit-log`)

**When:** "what just changed?" / "is anything Statsig-related causing the alert from 10m ago?"

```text
Get_Audit_Logs --since now-60m --until now
```

Filter to:
- `object_type in [gate, experiment, config, metric]`

Output: timeline grouped by object, sorted by recency.

---

## Recipe 2 — around a symptom timestamp (used by `investigate-rca`)

**When:** RCA. "What changed in Statsig in the 4-hour window around 13:00 UTC?"

```text
Get_Audit_Logs --since 2026-05-02T11:00Z --until 2026-05-02T15:00Z
```

Sort by `abs(entry.time - symptom_time)` ascending. Surface top 5.

This is the single most important diff-vs-deploy-timeline tool: deploys come from `gh run list`, but a gate flip at the same minute can be the *real* root cause that the deploy timeline doesn't show.

---

## Recipe 3 — per-actor (post-incident review)

**When:** "what did `<actor>` change in the last week?" — for postmortem retro, not for blame.

```text
Get_Audit_Logs --since now-7d --until now
filter to actor == <actor>
```

Surface as a per-day grouped list. Used in `/adk-investigate:investigate-rca`'s Contributing-Factors section to identify "process gaps" (e.g. "the gate was rolled out from 10% to 100% in one step; the gradual-rollout convention wasn't followed"), NOT to assign blame.

---

## Recipe 4 — per-object (gate / experiment history)

**When:** "show me all changes to `checkout_redesign` in the last 30 days".

```text
Get_Audit_Logs --since now-30d --until now
filter to object_id == checkout_redesign
```

Sort chronologically. Useful for understanding a gate's rollout history, and for catching "the rollout went from 10% to 100% suddenly" (vs the convention of staged rollouts).

---

## Recipe 5 — config / killswitch sweep (pre-deploy check)

**When:** "before I deploy, has anyone touched the relevant configs in the last hour?"

```text
Get_Audit_Logs --since now-1h --until now
filter to object_type == config
```

Used by `/adk-investigate:investigate-deploy` (cross-reference) to catch "config edited just before our deploy — verify the deploy doesn't accidentally revert it".

---

## Output shape

Each entry surfaces these four fields, always:

| Field | Example | Why |
| --- | --- | --- |
| `time` (UTC, ISO) | `2026-05-03T13:01:42Z` | Correlation anchor. |
| `object` | `gate:checkout_redesign` | What changed. |
| `action` | `targeting_rule_updated` | What kind of change. |
| `actor` | `alice` | Who. |

Plus a `Statsig` deep link to the audit-log entry in the console.

## Anti-patterns

- **Quoting raw audit-log JSON.** Aggregate first; one row per change; the four fields above + link.
- **Surfacing 50 entries.** Default to top 10 by recency or top 5 by time-delta from symptom. Operator drills in via the link.
- **Naming the actor as the cause.** The actor is metadata. The root cause is the system gap — "rollout was advanced 90% in one step" vs "Alice did a bad thing".
- **Treating an audit-log entry as the *only* evidence.** Always cross-reference: did the change correlate with a deploy? With a metric movement? With a log signal?

## Cross-skill rule

`/adk-investigate:investigate-incident` calls `Get_Audit_Logs` directly via this skill's recipes. `/adk-investigate:investigate-rca` does the same for ±2h around symptom. Don't duplicate the work; call this skill from those.
