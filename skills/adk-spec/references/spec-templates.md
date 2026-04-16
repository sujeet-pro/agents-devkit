# Spec Templates

Use these skeleton templates when drafting specifications. Expand, collapse, or adapt sections based on the topic scope. Every heading below is a prompt: fill it with evidence-backed content or mark it as an open question.

---

## PRD Template

```markdown
# PRD: <Title>

## Status
Draft | In Review | Approved

## Problem Statement
What problem does this solve? Who experiences it? What is the cost of not solving it?

## Target Users
| Persona | Description | Primary Goal |
| --- | --- | --- |
| | | |

## Success Metrics
| Metric | Target | Measurement Method |
| --- | --- | --- |
| | | |

## User Stories
### Must Have
- As a <persona>, I want <capability> so that <outcome>.

### Should Have
- As a <persona>, I want <capability> so that <outcome>.

### Nice to Have
- As a <persona>, I want <capability> so that <outcome>.

## Constraints
- Timeline:
- Technical:
- Compliance:
- Budget:

## Assumptions
- (list assumptions that, if wrong, would change the spec)

## Dependencies
- (list external systems, teams, or decisions this spec depends on)

## Scope Boundaries
### In Scope
-

### Out of Scope
-

## Open Questions
- (list unresolved items that need stakeholder input)
```

---

## Technical Specification Template

```markdown
# Technical Spec: <Title>

## Status
Draft | In Review | Approved

## Context
What is the current state? What architecture or systems does this touch? Why is a change needed?

## Goals
- (what this spec achieves when implemented)

## Non-Goals
- (what this spec explicitly does not cover)

## Architecture Overview
Describe the high-level design. Include a diagram reference if helpful.

## Interface Contracts
### Inputs
| Field | Type | Required | Description |
| --- | --- | --- | --- |
| | | | |

### Outputs
| Field | Type | Description |
| --- | --- | --- |
| | | |

### Error States
| Error | Code | Description | Resolution |
| --- | --- | --- | --- |
| | | | |

## Data Models
### <Model Name>
| Field | Type | Constraints | Description |
| --- | --- | --- | --- |
| | | | |

## Error Handling Strategy
- Retry behavior:
- Fallback paths:
- Circuit breaker:

## Security Considerations
- Authentication:
- Authorization:
- Data sensitivity:
- Input validation:

## Performance Requirements
| Metric | Target | Rationale |
| --- | --- | --- |
| Latency (p95) | | |
| Throughput | | |
| Resource ceiling | | |

## Migration and Backward Compatibility
- Breaking changes:
- Migration steps:
- Rollback plan:

## Observability
- Logging:
- Metrics:
- Alerting:

## Assumptions
-

## Open Questions
-
```

---

## API Specification Template

```markdown
# API Spec: <Title>

## Status
Draft | In Review | Approved

## Overview
What does this API do? Who are the consumers?

## Authentication
- Method:
- Token format:
- Scopes:

## Base URL
`<protocol>://<host>/<base-path>`

## Versioning Strategy
- Scheme (path, header, query):
- Current version:
- Deprecation policy:

## Endpoints

### <METHOD> <path>
**Description:** Brief description of what this endpoint does.

**Request:**
| Parameter | Location | Type | Required | Description |
| --- | --- | --- | --- | --- |
| | query/path/header/body | | | |

**Request Body:**
```json
{
}
```

**Response (success):**
```json
{
}
```

**Response (error):**
```json
{
  "error": {
    "code": "",
    "message": "",
    "details": []
  }
}
```

**Status Codes:**
| Code | Description |
| --- | --- |
| 200 | |
| 400 | |
| 401 | |
| 404 | |
| 500 | |

---

## Error Codes
| Code | HTTP Status | Description | Resolution |
| --- | --- | --- | --- |
| | | | |

## Rate Limiting
- Limit:
- Window:
- Header:
- Exceeded behavior:

## Pagination
- Strategy (cursor, offset):
- Default page size:
- Max page size:

## Webhooks (if applicable)
| Event | Payload Shape | Retry Policy |
| --- | --- | --- |
| | | |

## Open Questions
-
```

---

## Feature Specification Template

```markdown
# Feature Spec: <Title>

## Status
Draft | In Review | Approved

## Problem
What user problem does this feature solve?

## Goal
What is the desired outcome when this feature ships?

## User Flow (Happy Path)
1. User does X
2. System responds with Y
3. ...

## Edge Cases
| Scenario | Expected Behavior |
| --- | --- |
| | |

## Dependencies
| Dependency | Status | Impact if Unavailable |
| --- | --- | --- |
| | | |

## Rollback Plan
- Can the feature be disabled without data loss?
- Feature flag name:
- Rollback steps:

## Gradual Rollout (if applicable)
- Phases:
- Metrics to watch:
- Go/no-go criteria:

## Accessibility
-

## Internationalization
-

## Non-Functional Requirements
| Requirement | Target |
| --- | --- |
| Performance | |
| Security | |
| Availability | |

## Open Questions
-
```

---

## Acceptance Criteria Template

```markdown
# Acceptance Criteria: <Title>

## Status
Draft | In Review | Approved

## Requirement Reference
Link or restate the requirement being tested.

## Happy Path Scenarios

### Scenario: <name>
- **Given** <precondition>
- **When** <action>
- **Then** <expected outcome>

### Scenario: <name>
- **Given** <precondition>
- **When** <action>
- **Then** <expected outcome>

## Boundary Conditions

### Scenario: <name>
- **Given** <precondition at boundary>
- **When** <action>
- **Then** <expected outcome>

## Error and Negative Paths

### Scenario: <name>
- **Given** <precondition>
- **When** <invalid action or failure condition>
- **Then** <expected error handling>

## Performance Thresholds
| Metric | Threshold | Measurement |
| --- | --- | --- |
| | | |

## Environment Prerequisites
- (data setup, service dependencies, config flags needed to test)

## Pass / Fail Criteria
- A scenario passes when all "Then" conditions are met.
- A scenario fails when any "Then" condition is not met.
- The spec passes when all must-have scenarios pass.

## Open Questions
-
```
