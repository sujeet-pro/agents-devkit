# adk-review-docs

Review documentation for accuracy, completeness, clarity, style, and example quality.

## Quick Start

```
npx adk-review-docs docs/README.md
```

## What This Skill Does

Reviews documentation as the primary task. Checks docs against the actual code or behavior they describe. Evaluates across five dimensions: accuracy, completeness, clarity, style, and examples. Produces a prioritized list of findings with stable IDs, each tagged by dimension and severity.

## Command Reference

| Parameter | Values | Default | Description |
| --- | --- | --- | --- |
| `<path-or-url>` | file path, directory, or doc URL | required | What should be reviewed |
| `--focus` | `accuracy`, `completeness`, `clarity`, `style`, `examples`, `all` | `all` | Primary review dimension |
| `--auto` | flag | off | Skip confirmations; run end-to-end |
| `--help` | flag | off | Show the skill and stop |

## Dependencies

| Dependency | Required | Purpose |
| --- | --- | --- |
| `git` | yes | Read repo context and history |
| `python3` | yes | Run pre-flight checks |

## Skill Layout

```
adk-review-docs/
  SKILL.md              # Agent-facing skill definition
  README.md             # This file (human-facing docs)
  scripts/
    preflight.py        # Pre-flight dependency checker
  references/
    workflow.md          # Skill-specific workflow steps
    persona.md           # Reviewer persona and tone
    _shared/
      ai-guidelines-overview.md
      constitution.md
      research-protocol.md
      output-format.md
```

## Workflow

1. **Pre-flight** -- run `scripts/preflight.py` to verify dependencies.
2. **Confirm target** -- confirm the document path/URL, audience, and review dimension (skipped with `--auto`).
3. **Read document** -- read the document and the source material it claims to describe.
4. **Verify accuracy** -- check accuracy first, then completeness, clarity, style, and examples.
5. **Classify findings** -- assign severity, dimension, and stable F-IDs.
6. **Present findings** -- show the prioritized list grouped by file or section; wait for user response.
7. **Finalize** -- report top issues, residual risk, and the best next fix path.

## Interaction Protocol

### Confirmations

Before starting the review, the skill confirms:
- The document path, directory, or URL to review
- The review dimension focus
- The intended audience for the documentation

This step is skipped when `--auto` is passed.

### Findings Format

Each finding has a stable ID, severity, dimension, and one-line summary:

```
F-1  [Blocker]    [accuracy]      API endpoint documented as GET but code uses POST
F-2  [Critical]   [completeness]  Auth setup section missing entirely
F-3  [Should Have] [clarity]      Install steps assume macOS; unclear for Linux users
F-4  [May Have]   [examples]      Code example uses deprecated v1 API
F-5  [Nitpick]    [style]         Inconsistent heading capitalization
F-6  [Question]   [accuracy]      Is the 5-minute timeout still correct after v3 upgrade?
```

Severity levels: **Blocker** > **Critical** > **Should Have** > **May Have** > **Nitpick** > **Question**
Dimensions: **accuracy**, **completeness**, **clarity**, **style**, **examples**

### User Response

After seeing findings, respond with any combination of:

| Syntax | Meaning |
| --- | --- |
| `a-N` | Accept finding N |
| `r-N` | Reject finding N |
| `e-N` | Expand finding N (show detail) |
| `all` | Accept all findings |

Example: `a-1, a-2, r-5, e-6`

## Output Format

The review output contains six parts:

1. **Summary** -- one-line overview of the review result.
2. **Scope** -- what was reviewed (files, sections, URL).
3. **Findings** -- prioritized list with stable F-IDs, severity, and dimension.
4. **Validation** -- what was verified against code and what could not be checked.
5. **Risk** -- residual risk and blind spots (e.g., runtime behavior not testable).
6. **Next steps** -- recommended fix path and priority order.

## Examples

### Review a README

```
npx adk-review-docs docs/README.md
```

Reviews the README across all dimensions, presents findings with F-IDs.

### Review API docs with accuracy focus

```
npx adk-review-docs docs/api/ --focus accuracy
```

Compares API documentation against actual code behavior, flags mismatches.

### Review hosted docs in auto mode

```
npx adk-review-docs https://docs.acme.com/setup --focus completeness --auto
```

Skips confirmation, reviews hosted docs for completeness gaps.

## What Success Looks Like

- [ ] Document was fully reviewed against the source material
- [ ] Findings are prioritized with stable F-IDs, severity, and dimension
- [ ] Accuracy issues appear before style nits
- [ ] Each finding cites the doc section and supporting source
- [ ] Low-confidence findings are labeled as questions
- [ ] Missing code or runtime verification is called out
- [ ] User can accept, reject, or expand any finding
