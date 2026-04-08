# Onboarding Guide: [Team/Project Name]

## Metadata

| Field | Value |
|-------|-------|
| Document Type | Onboarding Guide |
| Team | [team name] |
| Owner | [name] |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Target Audience | [New hires / New team members / External contributors] |

## Welcome

[1-2 paragraphs: what the team does, what the project is, and what a new member will be doing in their first weeks.]

## Prerequisites

Before starting, make sure you have:

- [ ] [Account/access requirement — e.g., GitHub org membership]
- [ ] [Tool requirement — e.g., Docker Desktop installed]
- [ ] [Environment requirement — e.g., VPN access]

## Day 1: Environment Setup

### 1. Clone the Repository

```bash
git clone [repo-url]
cd [repo-name]
```

### 2. Install Dependencies

```bash
[dependency install command]
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials:
# - DATABASE_URL: [how to get this]
# - API_KEY: [how to get this]
```

### 4. Verify Setup

```bash
[command to verify everything works]
```

Expected output: [what success looks like]

## Week 1: Getting Oriented

### Architecture Overview

[Brief description of the system architecture. Link to the full HLD/TDD if it exists.]

<!-- DIAGRAM: High-level architecture overview for new team members -->

### Key Repositories

| Repository | Purpose | Key Files |
|-----------|---------|-----------|
| [repo-name] | [what it does] | [important files to read first] |

### Communication Channels

| Channel | Purpose | Frequency |
|---------|---------|-----------|
| [Slack channel] | [what it's for] | [daily / as needed] |
| [Meeting name] | [what it's for] | [weekly / biweekly] |

### Starter Tasks

These tasks are designed to familiarize you with the codebase:

1. **[Task name]** — [description and what you'll learn]
2. **[Task name]** — [description and what you'll learn]
3. **[Task name]** — [description and what you'll learn]

## Development Workflow

### Branch Strategy

[How to name branches, when to branch from main, PR process.]

### Code Review

[Code review expectations, how to request reviews, turnaround time.]

### Testing

```bash
# Run tests
[test command]

# Run specific test
[specific test command]
```

### Deployment

[How deployments work, environments, who can deploy.]

## Key Concepts

### [Domain Concept 1]

[Explanation of a domain-specific concept the new member needs to understand.]

### [Domain Concept 2]

[Explanation of another key concept.]

## Troubleshooting

| Problem | Solution |
|---------|----------|
| [Common setup issue] | [How to fix it] |
| [Common development issue] | [How to fix it] |

## Resources

| Resource | Link | Description |
|----------|------|-------------|
| [Internal docs] | [link] | [what it covers] |
| [Runbook] | [link] | [operational procedures] |
| [Design docs] | [link] | [architecture decisions] |

## Points of Contact

| Role | Name | Best Way to Reach |
|------|------|-------------------|
| Team Lead | [name] | [Slack/email] |
| Mentor/Buddy | [name] | [Slack/email] |
| On-Call | [rotation] | [PagerDuty] |
