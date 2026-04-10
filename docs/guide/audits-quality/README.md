---
title: Audits & Quality
description: Run security, performance, dependency, and codebase audits with automated testing
order: 6
---

# Audits & Quality

Use `audit` when you want findings and prioritization without modifying code. Use `test` when the job is walking through acceptance checks against a plan, spec, or deliverable.

> **Quick start:** `/adk:audit <prompt-text>` is the easiest way to ask for a quality pass without deciding the focus up front.

## Scenarios

- [Run A Focused Audit](#run-a-focused-audit)
- [Scope Or Publish The Result](#scope-or-publish-the-result)
- [Run User Acceptance Testing](#run-user-acceptance-testing)

---

## Run A Focused Audit

`audit` can stay broad or narrow itself to one dimension. Start broad when you are not sure what matters most, then switch to a focus flag once you know the lens you want.

```text
/adk:audit <prompt-text>
/adk:audit review this service for quality and security issues
/adk:audit --focus security
/adk:audit --focus performance
/adk:audit --focus dependency
/adk:audit --focus codebase --scope <path>
```

Use `--focus security` for auth and data-handling risk, `--focus performance` for latency or memory concerns, `--focus dependency` for package risk, and `--focus codebase` for broader structural quality.

---

## Scope Or Publish The Result

The same audit can be packaged differently depending on what the output needs to do next.

```text
/adk:audit --format pr
/adk:audit --publish
```

Use `--format pr` when the findings should read like a remediation checklist and `--publish` when the audit needs to land in a document destination instead of staying in the conversation.

---

## Run User Acceptance Testing

Use `test` when you want ADK to turn a spec, plan, or other source document into guided acceptance testing.

```text
/adk:test <path>
/adk:test ./docs/specs/auth-spec.md
/adk:test <path> --scope <path>
/adk:test <path> --mode auto-approve
```

This is the right path when you want a structured walkthrough of expectations rather than a code audit.

---

## Which Skill To Use?

| Scenario | Skill | Key Parameters |
|----------|-------|----------------|
| Broad or focused audit | `audit` | `<prompt-text>`, `--focus`, `--scope` |
| PR-style remediation checklist | `audit` | `--format pr` |
| Publish the audit artifact | `audit` | `--publish` |
| Acceptance testing from a spec or plan | `test` | `<path>`, `--scope`, `--mode` |

## Related Skills

- **[`code-review-repo`](/reference/skill-code-review-repo/)** when you want a holistic repository review with improvement planning.
- **[`dev-build`](/reference/skill-dev-build/)** when an audit finding turns into implementation work.
- **[`plan`](/reference/skill-plan/)** when the audit results need to become sequenced remediation work.
