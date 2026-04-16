# adk-research

Run structured technical research with repo evidence, primary sources, and explicit uncertainty.

## Quick Start

```
npx adk-research "how does Next.js App Router handle parallel routes in v14?"
```

Or as a slash command:

```
/adk-research how does Next.js App Router handle parallel routes in v14?
```

## What This Skill Does

Runs structured technical research when correctness depends on verified sources rather than memory or intuition. Gathers evidence from the local repository first, then from official external sources, and separates findings into verified, inferred, and open categories. Every claim includes a source citation and confidence level.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<question>` | free text | required | What needs to be researched |
| `--scope` | path | none | Limit repo inspection to a specific area |
| `--source` | URL or repo id | none | Narrow the external source set |
| `--auto` | flag | off | Skip confirmations and emit findings without interactive approval |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Type | Required | Notes |
| --- | --- | --- | --- |
| `git` | command | yes | Must be on PATH |
| `python3` | command | yes | Must be on PATH |
| Web access | capability | no | Recommended for external source research; WebSearch and WebFetch tools |

## Skill Layout

```
adk-research/
  SKILL.md                                # Skill definition
  README.md                               # This file
  scripts/
    preflight.py                          # Pre-flight checks
  references/
    workflow.md                           # Workflow guidance
    persona.md                            # Persona guidance
    _shared/
      ai-guidelines-overview.md           # Shared AI guidelines
      constitution.md                     # Shared constitution
      research-protocol.md                # Shared research protocol
      output-format.md                    # Shared output format
```

## Workflow

1. State the research question clearly.
2. Gather repo evidence first.
3. Gather official-source evidence second.
4. Add maintained implementation references only when needed.
5. Separate verified findings, inference, and open questions.
6. Recommend changes only after evidence is compared.

## Interaction Protocol

- **Confirm research question and scope**: before starting, restate the question and intended scope for the user to approve (unless `--auto`).
- **Present findings with source citations**: every claim includes a source reference (file path, URL, or doc section).
- **Distinguish verified, inferred, and open**: findings are labeled as Verified (source-backed), Inferred (reasonable but unconfirmed), or Open (unknown, needs further investigation).
- **Confidence indicators**: each finding includes a confidence level (high, medium, low) based on source quality and corroboration.
- **Surface conflicts explicitly**: when sources disagree, present both positions and explain the discrepancy.
- **Recommend next steps**: after presenting findings, suggest what to do with the information.

## Output Format

Each research report includes:
- **Summary**: one-paragraph answer to the research question
- **Verified findings**: source-backed claims with citations and high confidence
- **Inferred findings**: reasonable conclusions with medium confidence
- **Open questions**: items that could not be resolved, with suggested investigation paths
- **Conflicts**: where sources disagree, with both positions presented
- **Remaining risk**: what could go wrong if findings are acted on
- **Recommended next steps**: what to do with the information

## Examples

Research a technical question:
```
/adk-research how does Next.js App Router handle parallel routes in v14?
```

Research with scoped repo context:
```
/adk-research --scope src/auth what authentication strategy is this project using and is it current best practice?
```

Research from a specific source:
```
/adk-research --source https://github.com/expressjs/express what breaking changes are in Express v5?
```

## What Success Looks Like

- [ ] Every important claim cites evidence (file path, URL, or doc section)
- [ ] Conflicts between sources are called out explicitly
- [ ] Unverified items remain labeled as open
- [ ] Findings are categorized as verified, inferred, or open
- [ ] Confidence levels are assigned to each finding
- [ ] Recommendations are based on compared evidence, not assumptions
