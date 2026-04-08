# Stage: Operational Runbook

Use this stage when the agent should create or directly improve an operational runbook for a service, deployment flow, or incident response path.

## Type-Specific Phase Guidance

### Exploration
- Analyze the service: architecture, dependencies, deployment topology, monitoring setup
- Scan for existing runbooks, incident post-mortems, and operational documentation
- Identify common failure modes, alert conditions, and escalation paths
- If the runbook needs topology or deployment diagrams, inherit the `/diagram` preflight

### Execute
- Write the runbook following the document structure below
- Every procedure must be copy-paste executable -- no ambiguity
- Include verification steps after every action

## Document Structure

### Service Overview
- Service name, team ownership, and escalation contacts
- Architecture summary with dependency diagram
- SLA/SLO targets

### Prerequisites
- Required access (AWS accounts, VPN, SSH keys, dashboards)
- Required tools and their versions
- Environment setup steps

### Alert Playbooks
For each alert:
- Alert name and severity
- What it means (symptom, not just metric name)
- Diagnostic steps with exact commands
- Remediation steps with exact commands
- Verification that the fix worked
- When to escalate and to whom

### Deployment Procedures
- Pre-deployment checklist
- Step-by-step deployment process with exact commands
- Rollback procedure with exact commands
- Post-deployment verification steps

### Incident Response
- Severity classification guide
- Communication templates (status page, Slack, email)
- Escalation matrix by severity and time-of-day
- Post-incident review process

### Maintenance Procedures
- Scheduled maintenance tasks with cadence
- Database maintenance (backups, migrations, cleanup)
- Certificate rotation
- Dependency updates

### Troubleshooting Guide
- Common issues with diagnosis and resolution steps
- Log locations and useful queries
- Key metrics and their healthy ranges
- Useful debugging commands

## Child Agent Team

- `service-analyzer` for reading service architecture, configs, and deployment scripts
- `ops-researcher` for gathering operational best practices and existing incident data
- `procedure-writer` for creating step-by-step executable procedures
- `diagram-agent` for topology and deployment diagrams

## Writing Rules

- Every command must be copy-paste ready with actual values or clearly marked placeholders
- Include expected output for diagnostic commands so the operator can verify
- Use checklists for multi-step procedures
- Time estimates for each major procedure
- Assume the reader is under stress during an incident -- be direct and unambiguous

## Type-Specific Output Format

Markdown file in the service's documentation directory (e.g., `docs/runbook/` or `runbooks/`).

## Validation Checklist

- All alerts have corresponding playbooks
- Every procedure has verification steps
- Commands are copy-paste ready
- Escalation paths are complete with contact information
- Diagrams accurately reflect current architecture
- No placeholder values left unresolved
