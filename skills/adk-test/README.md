# adk-test

Verify behavior through acceptance, regression, or webapp-focused testing with explicit pass criteria and fresh evidence.

## Quick Start

```bash
npx adk-test "checkout flow" --mode acceptance
```

## What This Skill Does

Runs structured testing workflows against a target (feature, spec, path, or URL). Extracts or defines concrete test scenarios, executes checks in the selected mode, and reports pass/fail/blocked results backed by fresh evidence. Separates observed failures from root-cause hypotheses.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<target>` | plan, spec, path, feature name, or URL | required | What should be tested |
| `--mode` | `acceptance`, `regression`, `webapp` | `acceptance` | Keep the test strategy explicit |
| `--scope` | path or URL | none | Limit the validation surface |
| `--auto` | flag | off | Skip confirmations and execute with defaults |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required |
| --- | --- | --- |
| `git` | CLI command | yes |
| `python3` | CLI command | yes |
| Browser tooling | runtime | recommended for webapp mode |

## Skill Layout

```
skills/adk-test/
  SKILL.md                              # Skill definition and frontmatter
  README.md                             # This file
  scripts/
    preflight.py                        # Pre-flight dependency checks
  references/
    persona.md                          # Skill-specific persona
    workflow.md                         # Skill-specific workflow detail
    _shared/
      ai-guidelines-overview.md         # Shared ADK guidance
      constitution.md                   # Shared constitution
      output-format.md                  # Shared output format
      research-protocol.md              # Shared research protocol
```

## Workflow

1. Confirm what counts as passing and which surfaces are in scope.
2. Extract or define concrete scenarios before running checks.
3. Choose the smallest useful validation mode for the target.
4. Capture fresh pass, fail, skipped, or blocked evidence.
5. Separate observed failures from hypotheses about root cause.
6. Finish with coverage summary, open risks, and recommended next actions.

## Interaction Protocol

- **Confirm test target and mode** -- before running, confirm what will be tested and which mode applies.
- **Present test plan before executing** -- list scenarios to be checked and get approval.
- **Report with evidence** -- every pass/fail/blocked call includes supporting evidence.
- **Separate diagnosis from results** -- root-cause hypotheses are labeled separately from test outcomes.
- **Offer deeper passes** -- after initial results, offer to expand coverage or re-test.

## Output Format

- Test target
- Scenarios covered
- Pass/fail/blocked summary with evidence
- Follow-up and remaining blind spots

## Examples

Run acceptance tests for a checkout feature:
```
/adk-test checkout flow --mode acceptance --scope src/checkout/
```

Run regression tests after a login change:
```
/adk-test login regression --mode regression
```

Run webapp tests against a staging URL:
```
/adk-test https://staging.example.com --mode webapp --scope /dashboard
```

## What Success Looks Like

- [ ] Test target and mode are confirmed before execution
- [ ] Concrete scenarios are listed before any checks run
- [ ] Every pass/fail/blocked result has fresh evidence
- [ ] Blocked and untested scenarios remain visible
- [ ] Diagnosis is labeled separately from test results
- [ ] Coverage summary and remaining risks are reported
