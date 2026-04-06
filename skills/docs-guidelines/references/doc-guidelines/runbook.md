# Operational Runbook Guidelines

Guidelines for writing and reviewing operational runbooks. A runbook is a step-by-step guide for diagnosing and resolving operational issues. It is read under pressure -- at 3am during an incident -- so clarity, precision, and completeness are non-negotiable.

**Audience**: On-call engineers, SREs, and platform engineers who need to diagnose and resolve incidents quickly. The reader may not be an expert on the affected system.

**Reference**: Aligned with Google SRE Book Chapter 14 ([Managing Incidents](https://sre.google/sre-book/managing-incidents/)) and PagerDuty Incident Response documentation ([response.pagerduty.com](https://response.pagerduty.com/)).

---

## 1. Required Sections

Every runbook must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Overview | What this runbook covers, when to use it |
| 2 | Prerequisites | Access, tools, and permissions needed before starting |
| 3 | Alert Response | Mapping from alert names to initial actions |
| 4 | Diagnosis | Decision tree for identifying the root cause |
| 5 | Resolution Procedures | Step-by-step fixes for known failure modes |
| 6 | Escalation | When and how to escalate, with contact information |
| 7 | Post-Incident | What to do after the incident is resolved |

---

## 2. Content Standards

### Overview

- State the system or service this runbook covers in one sentence.
- List the alerts or symptoms that should lead an engineer to this runbook.
- Include a link to the system's architecture diagram, HLD, or service catalog entry.
- State the SLA/SLO targets for the service:

| SLO | Target | Measurement |
|-----|--------|-------------|
| Availability | 99.95% | Successful responses / total responses (5-minute windows) |
| Latency | p99 < 200ms | Server-side request duration |
| Error rate | < 0.1% | 5xx responses / total responses |

- State the business impact of an outage: what user-facing functionality is degraded or lost.

### Prerequisites

- List everything the on-call engineer needs before they can act:
  - **Access**: VPN, cloud console, database credentials, Kubernetes contexts, SSH keys.
  - **Tools**: CLI tools that must be installed (`kubectl`, `aws`, `gcloud`, database client).
  - **Dashboards**: Links to Grafana/Datadog/CloudWatch dashboards for this service.
  - **Logs**: Where to find logs (log aggregator URL, log group names, useful queries).
  - **Permissions**: IAM roles, RBAC permissions, or approval workflows required.
- For each prerequisite, include the command or link to verify access:

```bash
# Verify Kubernetes access
kubectl auth can-i get pods -n production

# Verify database connectivity
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"
```

### Alert Response

- Map each alert name to its initial response. Structure as a lookup table -- the on-call engineer should be able to find their alert in seconds:

| Alert Name | Severity | Initial Action | Link to Procedure |
|------------|----------|----------------|-------------------|
| `service-api-high-error-rate` | P1 | Check recent deploys, then go to Procedure 5.1 | [5.1 High Error Rate](#51-high-error-rate) |
| `service-api-high-latency` | P2 | Check database metrics, then go to Procedure 5.2 | [5.2 High Latency](#52-high-latency) |
| `service-db-replication-lag` | P2 | Check replica status, then go to Procedure 5.3 | [5.3 Replication Lag](#53-replication-lag) |
| `service-disk-space-critical` | P1 | Check log volume, then go to Procedure 5.4 | [5.4 Disk Space](#54-disk-space) |

### Diagnosis

- Structure diagnosis as a decision tree. At 3am, the engineer needs a flowchart, not a wall of text.
- Each decision point should be a question answerable by running a command or checking a dashboard:

```
Is the error rate elevated?
├─ YES → Are the errors 5xx or 4xx?
│   ├─ 5xx → Was there a recent deploy? (check deploy dashboard)
│   │   ├─ YES → Go to Procedure 5.1a (Deploy Rollback)
│   │   └─ NO → Check database connectivity → Go to Procedure 5.1b
│   └─ 4xx → Check for upstream client changes → Go to Procedure 5.1c
└─ NO → Is latency elevated?
    ├─ YES → Go to Diagnosis: High Latency
    └─ NO → Is the alert a capacity warning? → Go to Diagnosis: Capacity
```

- For each diagnostic step, provide the exact command to run and what the expected vs abnormal output looks like:

```bash
# Check recent deploys
kubectl rollout history deployment/api-server -n production
# Expected: last deploy > 1 hour ago
# Abnormal: last deploy within the incident window

# Check database connection pool
curl -s http://localhost:8080/metrics | grep 'db_pool'
# Expected: db_pool_active < db_pool_max * 0.8
# Abnormal: db_pool_active == db_pool_max (pool exhaustion)
```

### Resolution Procedures

- Number each procedure and give it a descriptive name (e.g., `5.1 High Error Rate After Deploy`).
- Every procedure must include:
  1. **Numbered steps**: What to do, in order.
  2. **Exact commands**: Copy-pasteable. No "run the appropriate command" -- state the command.
  3. **Expected output**: What success looks like after each step.
  4. **Rollback instructions**: How to undo this step if it makes things worse.
  5. **Verification**: How to confirm the issue is resolved.

Example procedure:

```markdown
#### 5.1a Deploy Rollback

**When**: Error rate spike correlates with a recent deployment.

1. Identify the previous stable revision:
   ```bash
   kubectl rollout history deployment/api-server -n production
   ```
   Note the revision number before the current one.

2. Roll back to the previous revision:
   ```bash
   kubectl rollout undo deployment/api-server -n production --to-revision=<N>
   ```
   Expected: `deployment.apps/api-server rolled back`

3. Monitor error rate dashboard for 5 minutes.
   Expected: error rate returns to baseline within 2-3 minutes.

4. If error rate does not decrease:
   - This deploy was not the cause. Re-deploy the current version:
     ```bash
     kubectl rollout undo deployment/api-server -n production
     ```
   - Continue diagnosis at Procedure 5.1b.

**Verification**: Error rate below 0.1% for 10 consecutive minutes.
```

### Escalation

- Define escalation triggers -- specific conditions that mean the on-call engineer should not solve this alone:
  - P1 incident exceeding 15 minutes without progress.
  - Data loss suspected or confirmed.
  - Security breach indicators.
  - Multiple services affected (potential infrastructure issue).
- Provide contact information in a table:

| Role | Name / Team | Contact | Availability |
|------|-------------|---------|--------------|
| Service owner | Platform Team | #platform-oncall (Slack), PagerDuty escalation | 24/7 |
| Database admin | DBA Team | #dba-oncall (Slack) | Business hours; PagerDuty after hours |
| Security | Security Response | #security-incident (Slack), security@company.com | 24/7 |
| Infrastructure | Infra Team | #infra-oncall (Slack) | 24/7 |

- State how to escalate: Slack message, PagerDuty override, phone call. Be specific.

### Post-Incident

- After the incident is resolved:
  1. **Verify resolution**: Run the verification steps from the resolution procedure. Confirm dashboards show normal behavior for at least 15 minutes.
  2. **Communicate**: Notify stakeholders. State what happened, when it started, when it was resolved, and what the impact was.
  3. **Create follow-up items**: File tickets for root cause fix, monitoring improvements, and runbook updates.
  4. **Schedule blameless review**: Post-mortem within 48 hours. Focus on the system, not the person. Reference [Etsy's blameless post-mortem culture](https://www.etsy.com/codeascraft/blameless-postmortems/) and Google SRE Chapter 15.
  5. **Update this runbook**: If the diagnosis or resolution steps were missing, wrong, or unclear, update them now while the incident is fresh.

---

## 3. Writing Style

- **Imperative mood**: "Check the error rate" not "You should check the error rate."
- **One action per step**: "Run X. Check the output." not "Run X and if the output shows Y then run Z."
- **No ambiguity**: "Run `kubectl get pods -n production`" not "Check the pods."
- **Expected output**: After every command, state what success and failure look like.
- **Copy-pasteable commands**: Use actual values or clearly marked placeholders (`<PLACEHOLDER>`). Never use prose where a command will do.
- **Links over descriptions**: Link to the dashboard, do not describe where to find it.

---

## 4. Common Issues

- **Missing commands**: "Check the database" without specifying which command to run, which host to connect to, or what query to execute.
- **No expected output**: The engineer runs the command but does not know what normal looks like, so they cannot distinguish healthy from degraded.
- **No rollback instructions**: A procedure that changes system state without explaining how to undo the change if it makes things worse.
- **Stale contact information**: Escalation contacts that no longer work for the team. Review quarterly.
- **Assuming expertise**: The on-call engineer may be covering this service for the first time. Spell out everything.
- **Missing verification**: The procedure ends without a step to confirm the incident is actually resolved.
- **Walls of text**: Runbooks are read under stress. Use numbered steps, tables, and decision trees. Long paragraphs are skipped.

---

## 5. Maintenance

- Review every runbook quarterly and after every incident that used it.
- After each incident, update the runbook with:
  - New failure modes discovered.
  - Commands or steps that were missing or incorrect.
  - Diagnostic steps that were slow or misleading.
- Track the last-reviewed date at the top of the runbook.
- Assign an owner (team, not individual) responsible for keeping the runbook current.

---

## 6. Review Checklist

- [ ] Overview states the system, associated alerts, SLOs, and business impact
- [ ] Prerequisites list all access, tools, dashboards, and log locations with verification commands
- [ ] Alert response table maps every alert to an initial action and procedure link
- [ ] Diagnosis uses a decision tree, not narrative prose
- [ ] Every diagnostic step includes the exact command and expected vs abnormal output
- [ ] Resolution procedures have numbered steps, exact commands, expected output, and rollback instructions
- [ ] Each procedure ends with a verification step
- [ ] Escalation triggers are defined with specific conditions
- [ ] Escalation contacts include name/adk-team, contact method, and availability
- [ ] Post-incident section covers verification, communication, follow-ups, and blameless review
- [ ] Commands are copy-pasteable (actual values or clearly marked placeholders)
- [ ] No TODO/TBD placeholders remain
- [ ] Last-reviewed date is present and within the last quarter
