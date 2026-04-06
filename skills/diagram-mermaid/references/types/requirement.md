# Requirement Diagram

**Directive:** `requirementDiagram`

**Syntax:**

```
requirementDiagram
    requirement req_name {
        id: REQ-001
        text: Requirement description
        risk: low
        verifymethod: test
    }

    functionalRequirement func_req {
        id: REQ-002
        text: Functional requirement
        risk: medium
        verifymethod: inspection
    }

    element impl_element {
        type: module
        docRef: src/module.ts
    }

    impl_element - satisfies -> req_name
    func_req - derives -> req_name
    req_name - refines -> func_req
    element - traces -> req_name
```

Verify methods: `analysis`, `demonstration`, `inspection`, `test`.
Risk levels: `low`, `medium`, `high`.

**Example:**

```
%% Diagram: Auth Requirements
%% Type: requirement
requirementDiagram
    requirement auth_system {
        id: AUTH-001
        text: System shall authenticate users via OAuth2
        risk: high
        verifymethod: test
    }

    functionalRequirement token_mgmt {
        id: AUTH-002
        text: System shall issue and validate JWT tokens
        risk: medium
        verifymethod: test
    }

    performanceRequirement auth_perf {
        id: AUTH-003
        text: Authentication shall complete within 200ms
        risk: low
        verifymethod: demonstration
    }

    element auth_module {
        type: module
        docRef: src/auth/index.ts
    }

    element token_service {
        type: service
        docRef: src/auth/token.ts
    }

    token_mgmt - derives -> auth_system
    auth_perf - refines -> auth_system
    auth_module - satisfies -> auth_system
    token_service - satisfies -> token_mgmt
```
