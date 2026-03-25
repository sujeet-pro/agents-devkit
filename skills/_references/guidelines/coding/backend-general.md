# Backend Service Review Guidelines

Use this alongside language-specific backend guidance for APIs, workers, integrations, and service-level code.

## 1. Contracts and Compatibility

- API and event contracts must be explicit, validated, and backward-compatible unless a breaking change is intentional.
- New endpoints or worker payloads should have request and response schemas.
- Changes that affect clients or downstream jobs must include migration notes or rollout guidance.

## 2. Reliability

- Validate timeout, retry, and idempotency behavior for network calls and queued work.
- Ensure background jobs can resume safely after partial failure.
- Check that error handling preserves enough context for support and incident response.

## 3. Persistence and Data Flow

- Query patterns should be bounded and index-aware.
- Schema changes should include data migration and rollback thinking.
- Avoid hidden write amplification, duplicate fetches, and unbounded fan-out.

## 4. Observability

- New flows should emit useful logs, metrics, and traces.
- Logs should support correlation by request ID, job ID, user ID, or domain entity.
- Do not introduce success-only instrumentation that hides failure paths.

## 5. Security and Abuse Resistance

- Validate authn/authz at service boundaries.
- Rate limits, quotas, and input validation should match the threat model.
- Protect secrets, internal URLs, and privileged operations from accidental exposure.

## 6. Documentation

- Public API changes should update docs or examples.
- Operational changes should update runbooks, config docs, or ADRs when they exist.
