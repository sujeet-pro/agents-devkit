# doc-site-setup Validator

The validator gate `adk-doc-site-setup` MUST run at every phase boundary and before declaring the run complete. Skipping the validator is a hard rule violation.

The validator has four phases. Each phase has explicit checks with `BLOCKER` / `WARN` / `OK` outcomes. The validator's check log lives at `.temp/notes/doc-site-setup-<slug>-validator.md`.

## Phase 1: Pre-execution gate

Run before doing any meaningful work. Every check below either passes (`OK`), surfaces a warning (`WARN` — proceed with note), or blocks (`BLOCKER` — stop until resolved).

| Check | Pass criteria | If fail |
| --- | --- | --- |
| Repo target valid | Path is a git repo with write permission | BLOCKER otherwise |
| No existing setup conflict | If `pagesmith.config.json5` already present: prompt before overwriting | BLOCKER without user choice |
| Node + npm reachable | `node --version` succeeds; npm available | BLOCKER otherwise |

## Phase 2: Mid-flow gates

Insert one gate between each major workflow phase from `SKILL.md`. Each gate confirms the prior phase produced the evidence the next phase needs.

| Gate | Between phases | Pass criteria | If fail |
| --- | --- | --- | --- |
| `context-gathered` | After Read / Fetch context, before Plan / Implement | All sources listed in this skill's research protocol have been read | BLOCKER — finish reading |
| `plan-approved` | After Plan, before Execute | Plan presented; user approved (or `--auto` picked default) | BLOCKER — wait |
| `work-complete` | After Execute, before Validate | Every artifact this skill produces has been written / staged | BLOCKER — finish the work |

(Skills with more or fewer phases may add or drop gates as appropriate; the principle is "no phase advances without evidence the prior phase finished".)

## Phase 3: Pre-handoff validation (doc site setup)

Run after the site is scaffolded; verify the build works, search indexes, and the prj-doc-site-* skills landed.

| Check | Pass criteria | Evidence captured |
| --- | --- | --- |
| `npm install` succeeded | @pagesmith/docs + diagramkit installed | npm output |
| Configs written | `pagesmith.config.json5` + `diagramkit.config.json5` parse | Parse check |
| docs/ tree scaffolded | guide + reference sections present with `meta.json5` + `README.md` | Tree listing |
| npm scripts wired | `docs:dev` / `docs:build` / `docs:preview` present in `package.json` | Script presence |
| prj-doc-site-* skills installed | Project-level skills landed in `.agents/skills/` (and mirrored) | Skill listing |
| Hello-world page renders | `docs:build` succeeds with the seeded hello-world page + diagram | Build output |
| Pagefind index built | Search index present in build output | Index path |

## Phase 4: Post-execution validation

Run after Phase 3; finalize the deliverable.

| Check | Pass criteria | Evidence |
| --- | --- | --- |
| Build verified | Built site listed | Build path |
| Validator log written | All four phases captured | File path + size |
| Manual follow-up | Deploy step + custom domain + branding listed if not done | Follow-up list |

## Failure / rollback

- **Phase 1 BLOCKER**: STOP. Surface the missing prerequisite. Do not proceed even under `--auto`.
- **Phase 2 BLOCKER**: STOP at the gate. Fix the prerequisite (e.g., finish reading context) and re-enter the gate.
- **Phase 3 BLOCKER**: STOP. Do not declare success. Fix the failing check, then re-run Phase 3.
- **Phase 4 partial failure**: Record what is wrong; do not declare success. Surface in the manual follow-up.

## Status banner

The validator sets the run's status banner from this skill's `*-persona.md`. Use the actual status labels from this skill's persona; the four-phase contract is the same.

## Evidence written to .temp/

The validator writes its check log to `.temp/notes/doc-site-setup-<slug>-validator.md` for audit. Format:

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

Final report: .temp/reports/doc-site-setup-<slug>.md
```
