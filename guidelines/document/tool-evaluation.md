# Tool Evaluation Document Guidelines

## 1. Purpose & Audience

This guideline defines how to write and review Tool Evaluation Documents. A tool evaluation provides a structured, repeatable process for comparing candidate tools against weighted criteria, grounded in hands-on testing rather than marketing claims.

**Primary audience:** Engineers conducting evaluations, technical leads making adoption decisions, and finance teams approving tool spend.

**When to use:** Before adopting any new tool, library, service, or platform that will be used in production or by multiple team members.

## 2. Required Sections

Every Tool Evaluation Document must include the following sections in order:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Problem Statement | Why are we evaluating? What gap or pain exists today? |
| 2 | Evaluation Criteria | Weighted, scored dimensions for comparison |
| 3 | Candidate Tools | Minimum 3 candidates with brief descriptions |
| 4 | Evaluation Matrix | Criteria x Candidates scoring table |
| 5 | POC Results | Hands-on testing outcomes against real use cases |
| 6 | Cost Analysis | Total cost of ownership including hidden costs |
| 7 | Risk Assessment | What can go wrong with each candidate |
| 8 | Migration Effort Estimate | Work required to adopt the recommended tool |
| 9 | Recommendation | Final pick with clear rationale tied to scores |

## 3. Content Standards

### 3.1 Problem Statement Must Justify the Evaluation

Do not start with "we want to evaluate X." Start with the problem:

Bad: "This document evaluates CI/CD tools."
Good: "Our current CI pipeline averages 45-minute build times, lacks caching, and has caused 3 incidents in the past quarter due to flaky infrastructure. We need a CI/CD solution that reduces build times below 15 minutes and improves reliability."

Include what happens if we do nothing (the cost of inaction).

### 3.2 Define and Weight Criteria Before Evaluating

Criteria must be established before looking at any candidate. This prevents retrofitting criteria to justify a predetermined choice.

Each criterion needs:

- **Name:** Clear, specific dimension (e.g., "p95 query latency at 10k QPS," not "performance")
- **Weight:** Percentage of total score (all weights must sum to 100%)
- **Scoring rubric:** What constitutes a 1, 3, and 5 for this criterion

Example criteria table:

| Criterion | Weight | Score 1 (Poor) | Score 3 (Acceptable) | Score 5 (Excellent) |
|-----------|--------|----------------|----------------------|---------------------|
| Build time (p50) | 25% | > 30 min | 10-30 min | < 10 min |
| SSO integration | 15% | Not supported | Via workaround | Native SAML/OIDC |
| Self-hosted option | 10% | No | Partial | Full feature parity |

### 3.3 Evaluate at Least Three Candidates

Two candidates creates a false binary. Three or more forces genuine comparison. If fewer than three viable candidates exist, document why and get explicit sign-off to proceed with fewer.

For each candidate, provide:

- Name and vendor/maintainer
- Current version and release cadence
- Community size or commercial support tier
- How it addresses the problem statement

### 3.4 POC Must Test Real Use Cases

A proof of concept must exercise actual workloads from your environment, not tutorial examples.

POC requirements:

- Test against at least 3 representative use cases from your actual workflow
- Use realistic data volumes (not toy datasets)
- Test failure modes (what happens when it breaks?)
- Measure actual performance, do not rely on vendor benchmarks
- Document the POC environment, duration, and who conducted it
- Record surprises: things that were harder or easier than expected

### 3.5 Cost Analysis Must Include Total Cost of Ownership

Licensing is the visible cost. The real cost includes everything below:

| Cost Category | What to Include |
|---------------|-----------------|
| Licensing/subscription | Per-seat, per-unit, tier costs for years 1-3 |
| Infrastructure | Hosting, compute, storage, network if self-hosted |
| Migration | Engineering hours to move from current tool |
| Training | Time for team to reach proficiency |
| Integration | Custom work to connect with existing systems |
| Operational | Ongoing maintenance, upgrades, monitoring |
| Opportunity cost | What the team cannot do while adopting this tool |

Always project costs for 1-year and 3-year horizons.

### 3.6 Risk Assessment Per Candidate

For each candidate, assess:

- **Vendor risk:** Could the vendor disappear, be acquired, or change pricing?
- **Lock-in risk:** How hard is it to leave once adopted? What is the exit cost?
- **Security risk:** Does it meet your security and compliance requirements?
- **Scaling risk:** Will it handle 10x your current load?
- **Integration risk:** Does it work with your existing stack without major modification?

### 3.7 Migration Effort Must Be Concrete

Do not say "migration will take some effort." Provide:

- Estimated engineering hours broken down by phase
- Required downtime or parallel-run period
- Rollback plan if migration fails
- Dependencies on other teams or systems
- Phased rollout plan if applicable

## 4. Structure & Flow

1. **Problem first** — Establish urgency and context before introducing tools.
2. **Criteria before candidates** — Prevent bias by defining what matters before seeing what is available.
3. **Data before opinion** — Present POC results and cost analysis before the recommendation.
4. **Recommendation last** — Let the evidence lead to the conclusion; do not front-load the answer.

## 5. Common Issues

| Issue | Problem | Fix |
|-------|---------|-----|
| Criteria defined after evaluation | Bias toward a preferred tool | Lock criteria with stakeholder sign-off before beginning evaluation |
| Only two candidates | False binary, no real comparison | Require minimum 3; document why if fewer |
| POC uses toy examples | Does not predict real-world behavior | Test with actual workloads and data volumes |
| Missing hidden costs | Budget surprise after adoption | Use the full TCO table; estimate training and migration hours |
| No exit strategy | Vendor lock-in discovered too late | Include lock-in risk score and data export feasibility for each tool |
| Vendor-provided benchmarks only | Numbers do not reflect your environment | Run your own benchmarks during POC |
| No stakeholder input on weights | Criteria do not reflect actual priorities | Review weights with stakeholders before scoring |

## 6. Review Checklist

Before approving a Tool Evaluation Document, verify every item:

- [ ] Problem statement explains the current pain and cost of inaction
- [ ] Evaluation criteria were defined and weighted before candidates were scored
- [ ] All criteria weights sum to 100%
- [ ] Each criterion has a clear scoring rubric (what is a 1, 3, 5)
- [ ] At least 3 candidates are evaluated (or fewer is explicitly justified)
- [ ] POC tested real use cases with realistic data, not just tutorials
- [ ] POC results include measured performance numbers, not vendor claims
- [ ] Cost analysis covers all TCO categories for 1-year and 3-year horizons
- [ ] Risk assessment covers vendor, lock-in, security, scaling, and integration risks
- [ ] Migration estimate includes hours, phases, downtime, and rollback plan
- [ ] Recommendation explicitly ties back to weighted scores and POC findings
- [ ] Document discloses any conflicts of interest or prior vendor relationships
- [ ] Stakeholders reviewed and approved criteria weights before scoring began
- [ ] The document has a version number and date
