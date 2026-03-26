---
name: write-runbook
description: Use when you need to draft or directly revise a professional operational runbook for a service, deployment flow, or incident response path
user_invocable: true
arguments:
  - name: service
    description: "Service name or path to the service root directory"
    required: true
  - name: scope
    description: "Runbook scope: full, incident-response, deployment (default: full)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence (default: markdown)"
    required: false
---

# Operational Runbook

Use `skills/_references/agentic-teams.md`, `skills/_references/output-formats.md`, and `skills/_references/preflight-validations.md`.

Use this skill when the agent should create or directly improve the runbook. If you only want review comments, use `/devkit:review-doc`.

## Preflight

Before analyzing the service or launching child agents, run:

`zsh scripts/check-skill-deps.zsh write-runbook format=<format>`

If the runbook needs topology or deployment diagrams, inherit the `/devkit:diagram` preflight before rendering assets.

## Guideline Loading

Always load:

- `skills/_references/guidelines/document/general.md`
- `skills/_references/guidelines/document/runbook.md`
- `skills/_references/guidelines/coding/backend-general.md`
- `skills/_references/guidelines/coding/observability.md`

## Required Child Agents

Run at least these child agents in parallel:

- **Infrastructure analyzer**: scans the service codebase, configuration files (Docker, Kubernetes, Terraform, CI/CD configs), and environment setup. Documents service topology, dependencies, ports, health checks, resource limits, and deployment targets. Produces a service context brief.
- **Failure mode researcher** (`research-agent`): researches common failure patterns for the service's technology stack. Identifies known incident patterns, monitoring gaps, and recovery procedures. Produces a failure mode catalog with detection signals and remediation steps.
- **Procedure writer**: takes the infrastructure analysis and failure mode catalog to write step-by-step operational procedures. Produces deployment steps, rollback procedures, incident response playbooks, and monitoring guidance with copy-pasteable commands.
- **Diagram agent**: produces topology diagrams, deployment flow diagrams, and dependency maps through `/devkit:diagram` to clarify the service architecture visually.

## Workflow

1. **Analyze service.** Launch the infrastructure analyzer to scan the codebase and configuration.
2. **Research failure modes.** Launch the failure mode researcher for the detected technology stack.
3. **Draft procedures.** Launch the procedure writer with outputs from steps 1 and 2.
4. **Create diagrams.** Launch the diagram agent for topology and deployment flow visuals.
5. **Assemble runbook.** Merge all outputs into the runbook structure based on `scope`:
   - **full**: all sections
   - **incident-response**: Service Overview, Monitoring, Incident Response, Common Issues
   - **deployment**: Service Overview, Deployment, Rollback, Common Issues
6. **Review.** Check procedures are copy-pasteable and escalation paths are clear.

## Runbook Structure

### 1. Service Overview
Service name, purpose, team ownership, on-call rotation, and key contacts.

### 2. Architecture
Topology diagram, dependencies, data stores, message queues, and external integrations.

### 3. Deployment
Step-by-step deployment procedure, environment-specific configuration, feature flags, database migration steps, and pre-deployment checks.

### 4. Rollback
Step-by-step rollback procedure, rollback triggers, data rollback considerations, and verification after rollback.

### 5. Monitoring and Alerting
Key metrics, dashboard links, alert definitions, SLO/SLI targets, and log query examples.

### 6. Incident Response
Severity classification, triage steps, escalation paths, communication templates, and post-incident review process.

### 7. Common Issues
FAQ-style troubleshooting with symptoms, diagnosis steps, and resolution commands.

## Output

A professional runbook with all sections populated based on the `scope` argument. Every procedure must include copy-pasteable commands with placeholder values clearly marked.

## Final Step

Before delivering, verify all commands are syntactically correct and all escalation contacts are present.

## Adjacent Skills

- `/devkit:audit-security` for security review of the service
- `/devkit:write-system-design` for system design documentation
- `/devkit:write-onboarding` for new-team-member onboarding guides
- `/devkit:review-doc` for comment-only review of existing runbooks
