# Incident Report / Postmortem Guidelines

Guidelines for writing and reviewing incident postmortems. A postmortem documents what happened during an incident, why it happened, and what the team will do to prevent recurrence — without assigning individual blame.

**Audience**: Engineering teams, management, and stakeholders who need to understand the incident and trust that corrective actions are in place.

---

## 1. Required Sections

Every incident report must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Executive Summary | 2-3 sentences accessible to non-technical stakeholders |
| 2 | Impact | Quantified user, business, and SLA impact |
| 3 | Timeline | Chronological events with timestamps |
| 4 | Root Cause Analysis | Systemic causes using 5 Whys or similar framework |
| 5 | Detection | How the incident was found and time to detect |
| 6 | Mitigation & Resolution | Steps taken to restore service |
| 7 | What Went Well / What Could Improve | Balanced retrospective |
| 8 | Action Items | Specific, assigned, time-bound follow-ups |

---

## 2. Content Standards

### Executive Summary
- Accessible to senior stakeholders who may not read the full report.
- State what happened, how many users were affected, how long it lasted, and the headline corrective action.
- One paragraph maximum.

### Impact
- Quantify everything: users affected, requests failed, revenue lost, SLA breached.
- Use charts to show error rate or latency during the incident window.
- If no data loss occurred, state that explicitly.

### Timeline
- All times in a single, explicit timezone.
- Every entry has a timestamp and a factual description of what happened.
- Include: detection time, declaration time, each diagnostic step, root cause identification, mitigation, resolution, and monitoring confirmation.

### Root Cause Analysis
- Use the 5 Whys or fishbone diagram to identify systemic causes.
- **Never assign blame to individuals.** Focus on process, tooling, and system gaps.
- Distinguish between the trigger (what started the incident) and contributing factors (what made it worse or harder to detect).

### Detection
- Document Time To Detect (TTD): how long between incident start and detection.
- State the detection method: alert, customer report, manual observation.
- Identify detection gaps: what could have caught this sooner.

### Action Items
- Every action item must have: a priority, an owner, a due date, and a tracking ticket.
- Categorize: preventive (stop it from happening), detective (catch it sooner), process (improve response).
- No action item should be "be more careful." Actions must be concrete and systemic.

---

## 3. Common Issues

- **Blame language**: "John deployed the bad config" instead of "A configuration change was deployed without staging validation."
- **Missing impact numbers**: "Some users were affected" — quantify it.
- **Vague action items**: "Improve monitoring" — specify what metric, what threshold, what tool.
- **Missing timeline entries**: Gaps between timestamps suggest undocumented investigation.
- **No follow-through tracking**: Action items without tickets are rarely completed.

---

## 4. Review Checklist

- [ ] Executive summary is accessible to non-technical stakeholders
- [ ] Impact is fully quantified (users, requests, revenue, SLA)
- [ ] Timeline has no gaps and uses a single timezone
- [ ] Root cause analysis identifies systemic causes, not individuals
- [ ] 5 Whys or equivalent framework is applied
- [ ] Detection method and TTD are documented
- [ ] What went well and what could improve are balanced
- [ ] Every action item has priority, owner, due date, and ticket
- [ ] No blame language anywhere in the document
- [ ] Charts or graphs illustrate the incident impact
