# visualize-diagram Validator

The validator gate `adk-visualize-diagram` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/visualize-diagram-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Diagram type chosen | Sequence / flow / state / ER / architecture / dependency / class / deployment — explicit | BLOCKER if unclear |
| Engine chosen | mermaid / drawio / excalidraw / graphviz — picked per content | BLOCKER if unclear |
| Source path chosen | Where the editable source lives is decided | BLOCKER without — orphan diagrams not allowed |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation (diagram quality)

Run after the diagram is rendered; verify it actually renders, has alt text, and works in light + dark mode.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| Source file written | Editable source (`.mmd` / `.drawio` / `.excalidraw` / `.dot`) saved alongside output | File presence |
| Renders without error | Engine rendered the source to the target format (svg / png) cleanly | Render command output |
| Light + dark variants | Both themes rendered (where the engine supports theming) | Both file paths present |
| Alt text written | Diagram has descriptive alt / `figcaption` | Alt-text check |
| Readable at target size | Text is legible at the target rendering size (no microscopic labels) | Size sanity check |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Output committed alongside source | Both source AND rendered output paths returned | File paths |
| Validator log written | All four phases captured | File path + size |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/visualize-diagram-<slug>-validator.md` for audit. Format:

```
## Phase 1
- <check>: OK | WARN | BLOCKER (<one-line evidence>)
- ...

## Phase 2
- <gate>: OK (<evidence>)
- ...

## Phase 3
- <check>: OK | WARN | BLOCKER (<one-line evidence>)
- ...

## Phase 4
- <check>: OK | WARN (<evidence>)
- ...

Final report: .temp/reports/visualize-diagram-<slug>.md
```
