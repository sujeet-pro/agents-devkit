# Runbook: [Service/System Name] — [Scenario]

## Metadata

| Field | Value |
|-------|-------|
| Document Type | Operational Runbook |
| Service | [service name] |
| Owner | [team or on-call rotation] |
| Created | YYYY-MM-DD |
| Last Verified | YYYY-MM-DD |
| Related Alerts | [PagerDuty service / alert names] |
| Dashboards | [Grafana / Datadog dashboard links] |

## Overview

[One paragraph: what this runbook covers and when to use it. On-call engineers read this at 3 AM — be direct.]

## Prerequisites

- [ ] Access to [system/tool] — [how to get access if needed]
- [ ] VPN connected to [environment]
- [ ] CLI tools: [kubectl, aws, etc.]

## Diagnostics

### Quick Health Check

```bash
# Check service status
[command to verify service health]

# Check recent logs
[command to tail relevant logs]

# Check key metrics
[command or dashboard link]
```

### Symptom → Cause Mapping

| Symptom | Likely Cause | Go To |
|---------|-------------|-------|
| [What you observe] | [Most common cause] | [§ section link] |
| [Another symptom] | [Likely cause] | [§ section link] |

## Procedures

### Procedure 1: [Scenario Name — e.g., "High Latency"]

**Trigger**: [Alert name or observed condition]
**Severity**: [SEV1/SEV2/SEV3]
**Expected Resolution Time**: [X minutes]

#### Steps

1. **Verify the issue**
   ```bash
   [diagnostic command]
   ```
   Expected output: [what normal looks like]

2. **Identify the root cause**
   - Check [metric/log] for [pattern]
   - If [condition A]: proceed to step 3a
   - If [condition B]: proceed to step 3b

3a. **Fix: [Condition A resolution]**
   ```bash
   [remediation command]
   ```
   Verify: [how to confirm the fix worked]

3b. **Fix: [Condition B resolution]**
   ```bash
   [remediation command]
   ```
   Verify: [how to confirm the fix worked]

4. **Post-resolution**
   - [ ] Verify metrics have returned to normal
   - [ ] Update incident channel with resolution
   - [ ] Create follow-up ticket if root cause needs permanent fix

### Procedure 2: [Scenario Name — e.g., "Database Failover"]

**Trigger**: [Alert name or observed condition]
**Severity**: [SEV1/SEV2/SEV3]
**Expected Resolution Time**: [X minutes]

#### Steps

1. [Step-by-step with commands and verification]

## Escalation

| Severity | Response Time | Escalate To | Channel |
|----------|-------------|-------------|---------|
| SEV1 (Critical) | 15 min | [Team lead / VP Eng] | [PagerDuty / Phone] |
| SEV2 (Major) | 30 min | [Team lead] | [Slack channel] |
| SEV3 (Minor) | Next business day | [Team] | [Jira ticket] |

## Rollback Procedures

### Application Rollback

```bash
# Roll back to previous version
[rollback command]

# Verify rollback
[verification command]
```

### Database Rollback

```bash
# Roll back migration
[migration rollback command]

# Verify data integrity
[verification query]
```

## Architecture Reference

<!-- DIAGRAM: Service architecture showing dependencies relevant to troubleshooting -->

## Contact Information

| Role | Name | Contact |
|------|------|---------|
| Primary On-Call | [rotation] | [PagerDuty] |
| Service Owner | [name] | [email/Slack] |
| Database Admin | [name/team] | [email/Slack] |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| YYYY-MM-DD | [name] | Initial creation |
