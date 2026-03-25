# System Design Article Guidelines

Guidelines for writing and reviewing system design deep-dive articles. These target experienced engineers who want to understand how to architect a system end-to-end: from problem framing through scaling, failure modes, and observability.

**Audience**: Senior, staff, and principal engineers evaluating architectural approaches, preparing for design reviews, or documenting systems they have built.

---

## 1. Required Sections

Every system design article must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Problem Statement | Real-world framing of what the system must do |
| 2 | Requirements | Functional and non-functional, quantified |
| 3 | High-Level Design | Architecture overview with diagram |
| 4 | Component Deep-Dive | Detailed design of each major component |
| 5 | Data Model & Storage | Schema design, storage choices, data flow |
| 6 | Trade-Off Analysis | Explicit comparison of alternatives |
| 7 | Scaling Considerations | How the system grows |
| 8 | Failure Modes | What breaks and how to recover |
| 9 | Monitoring & Alerting | How you know the system is healthy |
| 10 | References | Sources, papers, real-world implementations |

---

## 2. Content Standards

### Problem Statement

- Frame the problem in real-world context, not abstract terms.
  - **Abstract**: "Design a distributed key-value store."
  - **Real-world**: "Design the session storage layer for an e-commerce platform serving 50M monthly active users across three geographic regions, where a lost session means an abandoned cart."
- State who cares about this system and why. What is the business impact of getting it wrong?
- Include scale parameters upfront: user count, request volume, data volume, geographic distribution.
- Reference real systems that solve similar problems (DynamoDB, Cassandra, Redis) to anchor the reader's mental model.

### Requirements

- Split into **Functional Requirements** (what the system does) and **Non-Functional Requirements** (how well it does it).
- Quantify every non-functional requirement:

| Requirement | Bad | Good |
|---|---|---|
| Latency | "Low latency" | "p99 read latency < 10ms within same region" |
| Throughput | "High throughput" | "100K writes/sec sustained, 500K reads/sec peak" |
| Storage | "Store lots of data" | "5TB active dataset, 50TB archive, 10% monthly growth" |
| Availability | "Highly available" | "99.99% availability (52.6 minutes downtime/year)" |
| Durability | "Data should not be lost" | "99.999999999% (11 nines) durability, RPO < 1 second" |

- Derive numbers from the problem statement. Show the math: "50M MAU, 10% daily active, average 5 requests per session = 25M requests/day = ~290 QPS average, ~1500 QPS peak (5x)."
- State what is explicitly out of scope.

### High-Level Design

- Include an architecture overview diagram showing all major components and their interactions.
- Label every arrow: protocol (HTTP, gRPC, TCP), data format (JSON, Protobuf, Avro), and direction (request/response, pub/sub, streaming).
- Show the read path and write path separately if they differ.
- Identify the stateless and stateful components. Stateful components are where the hard problems live.
- Include a data flow diagram showing how a request moves through the system from client to storage and back.

### Component Deep-Dive

- For each major component, cover:
  - **Responsibility**: What it owns, stated in one sentence.
  - **Internal design**: Data structures, algorithms, or patterns used.
  - **Interface**: What it exposes (API contract, message schema).
  - **Dependencies**: What it requires from other components.
  - **Failure behavior**: What happens when this component fails.
- Use sequence diagrams for complex multi-step interactions.
- Show code snippets for non-obvious algorithms (consistent hashing, bloom filters, conflict resolution).

### Data Model & Storage

- Show the schema or data model with field types, constraints, and indexes.
- Justify the storage technology choice: why this database/store for this workload.
- Discuss partitioning/sharding strategy: partition key selection, hot partition mitigation, rebalancing.
- Cover replication: sync vs async, consistency model (strong, eventual, causal), conflict resolution.
- Estimate storage requirements with arithmetic: "100M records x 2KB avg = 200GB, with 3x replication = 600GB."

### Trade-Off Analysis

- Present alternatives in a structured comparison table:

| Approach | Pros | Cons | Best When |
|----------|------|------|-----------|
| Consistent hashing | Even distribution, minimal reshuffling on node changes | Complexity, virtual nodes needed for balance | Large-scale distributed caches |
| Range-based sharding | Efficient range queries, simple implementation | Hot spots on sequential writes, manual split management | Time-series or lexicographically ordered data |
| Hash-based sharding | Even distribution, simple to implement | No range queries, reshuffling on cluster resize | Uniform access patterns, point lookups |

- For each trade-off, state the decision criteria: what matters most for this specific system.
- Reference how real companies solved the same trade-off. Cite the original paper or engineering blog:
  - Amazon DynamoDB: [Dynamo paper (DeCandia et al., 2007)](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf)
  - Google Spanner: [Spanner paper (Corbett et al., 2012)](https://research.google/pubs/pub39966/)
  - Facebook TAO: [TAO paper (Bronson et al., 2013)](https://www.usenix.org/conference/atc13/technical-sessions/presentation/bronson)

### Scaling Considerations

- Address both horizontal and vertical scaling. State which applies to each component and why.
- **Read scaling**: Caching layers (local, distributed, CDN), read replicas, denormalization.
- **Write scaling**: Sharding, partitioning, write-behind caching, event sourcing.
- **Caching strategy**: What to cache, cache invalidation approach, cache-aside vs write-through vs write-behind, thundering herd mitigation.
- **CDN**: What content to serve from CDN, cache-control headers, purge strategy.
- Include capacity planning: at what scale does each component become the bottleneck? What is the plan when it does?
- Show scaling thresholds: "Below 10K QPS, a single primary with read replicas suffices. Above 10K QPS, introduce sharding."

### Failure Modes

- For each failure scenario, document:

| Failure | Blast Radius | Detection | Recovery | Data Impact |
|---------|-------------|-----------|----------|-------------|
| Primary DB failure | All writes, stale reads | Health check timeout (5s) | Automatic failover to replica (30s) | Writes during failover window lost unless using sync replication |
| Cache node failure | Increased DB load for cached keys | Missed health checks | Auto-replace node, warm from DB | None (cache is derived) |
| Network partition between regions | Region isolation, split-brain risk | Cross-region heartbeat failure | Automatic region failover for reads, manual for writes | Depends on consistency model |

- Discuss cascading failures: when component A fails, what happens to B and C?
- Cover thundering herd: what happens when a failed component recovers and all clients reconnect simultaneously?
- Describe circuit breaker and bulkhead patterns where applicable.
- Reference real-world incidents where possible (public post-mortems from companies).

### Monitoring & Alerting

- Define the key metrics for each component: latency percentiles, error rates, throughput, saturation.
- Specify alerting thresholds tied to SLO targets: "Alert when p99 latency exceeds 50ms for 5 consecutive minutes (SLO: p99 < 100ms)."
- Include the four golden signals (Vargo & Burns, Google SRE Book): latency, traffic, errors, saturation.
- Describe dashboards: what an operator sees during normal operation vs during an incident.
- Cover distributed tracing for cross-service request paths.

### References

- Cite original papers, RFCs, and official documentation over blog posts.
- Include links to real-world engineering blogs that describe production implementations of the patterns discussed.
- Reference the Google SRE Book, DDIA (Kleppmann), and relevant system-specific documentation where applicable.

---

## 3. Diagrams

- Every system design article must include at minimum:
  1. Architecture overview diagram
  2. Data flow diagram (read and write paths)
- Additional diagrams as needed: sequence diagrams for complex interactions, ER diagrams for data models, deployment diagrams for infrastructure.
- Diagrams must be consistent with the text. If the text says three replicas, the diagram must show three replicas.
- Label everything: components, protocols, data formats, direction of flow.
- Keep diagrams focused. A single diagram with 20+ components is unreadable. Break into sub-system diagrams.

---

## 4. Common Issues

- **Abstract problem framing**: "Design a URL shortener" without specifying scale, geography, or access patterns. The design depends entirely on these parameters.
- **Unquantified requirements**: "Low latency" and "highly available" are not requirements. They are wishes. Put numbers on them.
- **Missing the math**: Stating "100K QPS" without showing how it was derived from the problem parameters. Back-of-envelope calculations build credibility and catch errors.
- **Trade-offs presented without criteria**: A table of pros and cons is incomplete without stating what matters most for this system and why.
- **Happy-path-only design**: The system works perfectly when everything is up. What happens when the primary database fails? When a network partition isolates a region? When a deploy introduces a bug?
- **Scaling as an afterthought**: "We can add more nodes" is not a scaling strategy. Address partitioning, rebalancing, state management, and capacity planning.
- **No real-world references**: System design does not happen in a vacuum. Reference how companies at similar scale solved similar problems.

---

## 5. Review Checklist

- [ ] Problem is framed in real-world context with specific scale parameters
- [ ] Functional and non-functional requirements are separated and quantified
- [ ] Back-of-envelope calculations derive QPS, storage, and bandwidth from problem parameters
- [ ] Architecture diagram shows all major components with labeled interactions
- [ ] Read path and write path are shown separately if they differ
- [ ] Each component has a deep-dive covering responsibility, internals, interface, dependencies, and failure behavior
- [ ] Data model includes schema, storage justification, partitioning strategy, and replication model
- [ ] Trade-offs are presented in structured tables with decision criteria
- [ ] Real-world references cite original papers or engineering blogs, not just tutorials
- [ ] Scaling strategy addresses read scaling, write scaling, caching, and capacity thresholds
- [ ] Failure modes include blast radius, detection, recovery, and data impact
- [ ] Cascading failures and thundering herd scenarios are addressed
- [ ] Monitoring covers the four golden signals with alerting thresholds tied to SLOs
- [ ] All diagrams are consistent with the text
- [ ] No TODO/TBD placeholders remain
