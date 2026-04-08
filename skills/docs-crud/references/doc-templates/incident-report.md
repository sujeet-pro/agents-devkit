# Incident Report: [Incident Title]

## Metadata

| Field | Value |
|-------|-------|
| Document Type | Incident Postmortem |
| Incident ID | INC-NNN |
| Severity | [SEV1 / SEV2 / SEV3] |
| Status | [Draft / In Review / Final] |
| Incident Commander | [name] |
| Author | [name] |
| Date of Incident | YYYY-MM-DD |
| Date of Report | YYYY-MM-DD |
| Duration | [X hours Y minutes] |
| Affected Services | [service names] |

## Executive Summary

[2-3 sentences accessible to senior stakeholders: what happened, how many users were affected, how long it lasted, and what we are doing to prevent recurrence.]

## Impact

| Metric | Value |
|--------|-------|
| Users affected | [number and segment] |
| Duration of impact | [start time — end time (timezone)] |
| Requests failed | [number or percentage] |
| Revenue impact | [$ amount or "none"] |
| SLA impact | [SLA breach details or "within SLA"] |
| Data loss | [description or "none"] |
| Customer communications sent | [number and channel] |

<!-- CHART: line | Error rate and latency during the incident timeline -->

## Timeline

All times in [timezone].

| Time | Event |
|------|-------|
| HH:MM | [Alert fired / Issue detected — how it was detected] |
| HH:MM | [Incident declared, IC assigned] |
| HH:MM | [First diagnostic action taken] |
| HH:MM | [Root cause identified] |
| HH:MM | [Mitigation applied] |
| HH:MM | [Service restored] |
| HH:MM | [Incident resolved, monitoring confirmed] |

## Root Cause Analysis

### What Happened

[Technical description of the failure chain. Be specific about the sequence of events.]

### Why It Happened

[Use the 5 Whys or equivalent framework to identify systemic causes, not individual blame.]

1. **Why** did [symptom]? — Because [cause 1]
2. **Why** did [cause 1]? — Because [cause 2]
3. **Why** did [cause 2]? — Because [cause 3]
4. **Why** did [cause 3]? — Because [root cause]

### Contributing Factors

- [Factor that made the incident worse or harder to detect]
- [Process gap that delayed response]

<!-- DIAGRAM: Failure chain showing the sequence from trigger to user impact -->

## Detection

| Aspect | Details |
|--------|---------|
| How detected | [Alert / Customer report / Manual observation] |
| Time to detect (TTD) | [X minutes from incident start] |
| Detection gap | [What could have detected this sooner] |

## Mitigation and Resolution

[Step-by-step description of what was done to restore service.]

1. [Action taken and result]
2. [Action taken and result]
3. [Final verification]

## What Went Well

- [Effective response action]
- [Process or tool that helped]

## What Could Be Improved

- [Detection gap]
- [Response delay]
- [Communication issue]
- [Process gap]

## Action Items

| # | Action | Priority | Owner | Due Date | Ticket |
|---|--------|----------|-------|----------|--------|
| 1 | [Specific preventive action] | P0 | [name] | YYYY-MM-DD | [JIRA-NNN] |
| 2 | [Detection improvement] | P1 | [name] | YYYY-MM-DD | [JIRA-NNN] |
| 3 | [Process improvement] | P1 | [name] | YYYY-MM-DD | [JIRA-NNN] |
| 4 | [Documentation update] | P2 | [name] | YYYY-MM-DD | [JIRA-NNN] |

## Lessons Learned

[Key takeaways that apply beyond this specific incident. What systemic changes should the organization consider?]

## Appendix

### Relevant Logs

```
[Key log entries that illustrate the failure]
```

### Relevant Metrics

<!-- CHART: line | Key service metrics before, during, and after the incident -->

### Related Incidents

| Incident | Date | Similarity |
|----------|------|-----------|
| [INC-NNN] | [date] | [How it relates] |
