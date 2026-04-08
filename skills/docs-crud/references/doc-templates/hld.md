# HLD-NNN: [System Name] — High Level Design

## Metadata

| Field | Value |
|-------|-------|
| Document Type | High Level Design |
| Document ID | HLD-NNN |
| Status | Draft |
| Owner | [name] |
| Created | YYYY-MM-DD |
| Last Updated | YYYY-MM-DD |
| Related Tech Spec | [TS-NNN link or N/A] |
| Repositories / Services | [repo or service names] |

## Review Tracker

| Reviewer | Role | Status | Date | Comments |
|----------|------|--------|------|----------|
| | | Not reviewed | -- | -- |

## 1. System Context

[Where the system sits in the broader ecosystem. Describe the system's purpose, its role in the overall architecture, intended users, and performance expectations.]

<!-- DIAGRAM: C4 Level 1 context diagram showing the system as a single box surrounded by actors and external dependencies -->

### Actors and Interactions

| Actor | Type | Interaction | Pattern |
|-------|------|-------------|---------|
| [Name] | [Human/System/Batch/3rd-party] | [What they do with the system] | [Sync API/Async messaging/File transfer] |

## 2. Architecture Overview

[High-level component layout. Focus on what each component does and why it exists as a separate unit, not how it is implemented internally.]

<!-- DIAGRAM: C4 Level 2 container diagram showing major components and their relationships with data flow direction -->

### Component Summary

| Component | Responsibility | Technology | Scaling Strategy |
|-----------|---------------|------------|-----------------|
| [Name] | [One sentence on what it owns] | [Key technology choice] | [Horizontal/Vertical/Serverless] |

## 3. Component Descriptions

### [Component A]

- **Responsibility**: [What this component owns — one to two sentences]
- **Inputs**: [Data it consumes — sources and formats]
- **Outputs**: [Data it produces — destinations and formats]
- **Boundaries**: [What this component does NOT do]

### [Component B]

- **Responsibility**: [What this component owns]
- **Inputs**: [Data it consumes]
- **Outputs**: [Data it produces]
- **Boundaries**: [What this component does NOT do]

## 4. Integration Points

| External System | Protocol | Data Format | Contract Owner | Failure Mode | Fallback | SLA |
|----------------|----------|-------------|----------------|-------------|----------|-----|
| [Name] | [REST/gRPC/Queue/File] | [JSON/Protobuf/CSV] | [Team] | [Timeout/Error behavior] | [Degraded behavior] | [Expected availability] |

### Hard vs Soft Dependencies

- **Hard** (system requires): [list]
- **Soft** (system degrades without): [list]

## 5. Data Flow

### Read Path

<!-- DIAGRAM: Sequence diagram showing the primary read path through the system -->

[Description of how data flows through the system for read operations.]

### Write Path

<!-- DIAGRAM: Sequence diagram showing the primary write path through the system -->

[Description of how data flows through the system for write operations.]

## 6. Non-Functional Requirements

| NFR Category | Target | Measurement | Basis |
|-------------|--------|-------------|-------|
| Performance | [p95 latency < Xms] | [APM tool] | [Current SLO] |
| Scalability | [X concurrent users] | [Load test] | [Growth projection] |
| Availability | [X% uptime] | [Uptime monitor] | [SLA commitment] |
| Security | [Encryption standard] | [Security audit] | [Compliance requirement] |
| Data Durability | [RPO = X minutes] | [Backup verification] | [Business requirement] |

### Capacity Estimates

| Metric | Current | 6 Months | 12 Months |
|--------|---------|----------|-----------|
| Requests/sec | [X] | [Y] | [Z] |
| Data volume | [X GB] | [Y GB] | [Z GB] |
| Storage growth/month | [X GB] | [Y GB] | [Z GB] |

<!-- CHART: line | Projected growth: requests per second over 12 months -->

## 7. Technology Choices

| Decision | Choice | Alternatives Considered | Justification | Trade-offs |
|----------|--------|------------------------|---------------|------------|
| [Database] | [PostgreSQL] | [DynamoDB, MongoDB] | [Strong consistency needs, team expertise] | [Operational overhead, scaling limits] |
| [Message Broker] | [Kafka] | [SQS, RabbitMQ] | [Ordering guarantees, replay capability] | [Infrastructure complexity] |

## 8. Deployment Architecture

<!-- DIAGRAM: Deployment diagram showing regions, availability zones, clusters, and component placement -->

- **Topology**: [Single-region / Multi-region, Active-Active / Active-Passive]
- **Scaling**: [Auto-scaling triggers and limits]
- **DR Strategy**: RPO = [X], RTO = [Y]

## 9. Monitoring & Observability

### Metrics

| Metric | Component | Threshold | Alert |
|--------|-----------|-----------|-------|
| [p99 latency] | [API Gateway] | [> 500ms] | [PagerDuty] |
| [Error rate] | [All services] | [> 1%] | [Slack + PagerDuty] |

### Logging

[What is logged, at what level, where logs are aggregated.]

### Tracing

[Distributed tracing strategy for cross-service requests.]

## Glossary

| Term | Definition |
|------|-----------|
| [Term] | [Definition] |
