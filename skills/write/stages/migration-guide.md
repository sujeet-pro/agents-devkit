# Stage: Migration Guide

Use this stage when the agent should produce or directly update a migration guide mapped to real codebase files for a framework, library, or version upgrade.

## Type-Specific Phase Guidance

### Exploration
- Scan the codebase for all usage of the source framework/library
- Read official migration guides, changelogs, and breaking change lists for the target version
- Identify affected files and the scope of changes needed
- Assess available codemods or automation tools

### Deep Research
- Map breaking changes to specific files in the codebase
- Evaluate effort and risk for each migration step
- Identify available codemods, migration scripts, or automation
- Research common pitfalls from community migration experiences

### Execute
- Write the migration guide following the document structure below
- Every step must reference specific files in the codebase
- Include before/after code examples for each breaking change

## Document Structure

### Overview
- What is being migrated (from version X to version Y)
- Why the migration is needed
- Estimated effort and timeline
- Risk assessment summary

### Prerequisites
- Required tool versions
- Backup and rollback strategy
- Feature flag setup if applicable

### Breaking Changes Inventory
For each breaking change:
- Description of the change
- Affected files in the codebase (with paths)
- Before/after code examples
- Available codemod or automated fix
- Manual steps if no automation exists

### Step-by-Step Migration Plan
Ordered steps with:
- Description of what to change
- Files affected
- Exact commands or code changes
- Verification command to confirm the step succeeded
- Rollback procedure for this step

### Risk Register
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| ... | ... | ... | ... |

### Testing Strategy
- What tests to run after each phase
- New tests needed for changed behavior
- Performance regression testing plan

### Rollback Plan
- How to revert the migration at each stage
- Data migration rollback considerations
- Feature flag configurations for gradual rollout

## Child Agent Team

- `usage-analyzer` for finding all usage of the source framework/library in the codebase
- `changelog-researcher` for reading official migration guides, changelogs, and breaking change lists
- `migration-planner` for mapping breaking changes to specific files and creating step-by-step plan
- `risk-assessor` for evaluating effort, risk, and identifying codemods or automation available

## Writing Rules

- Every step must reference real files in the codebase
- Include verification commands after each step
- Order steps to minimize risk (low-risk changes first)
- Flag steps that require downtime or coordination

## Type-Specific Output Format

Markdown file with file-mapped steps, verification guidance, risk register, and rollback notes.

## Validation Checklist

- All affected files are identified and referenced
- Before/after examples match real code patterns in the repo
- Steps are ordered to minimize risk
- Rollback procedure exists for each phase
- Verification commands are provided for each step
