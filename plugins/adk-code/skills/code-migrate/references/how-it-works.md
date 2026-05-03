# `code-migrate` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Prompt["User prompt: from X to Y"] --> P0["Phase 0: prompt expand + resolve versions"]
    P0 --> P1["Phase 1: preflight (commands resolved + baseline GREEN)"]
    P1 --> Baseline{"Baseline green?"}
    Baseline -- no --> Stop1["STOP: migration on red is unverifiable"]
    Baseline -- yes --> P2["Phase 2: WebFetch upstream migration guide"]
    P2 --> Curate["Curate quotes (≤15 words) into migration-notes.md"]
    Curate --> P3["Phase 3: inventory call-sites per rule"]
    P3 --> P4["Phase 4: plan groups + sequence"]
    P4 --> Approve4{"--auto?"}
    Approve4 -- no --> Gate4["Approval: confirm group sequence"]
    Approve4 -- yes --> P5
    Gate4 --> P5["Phase 5: execute group-by-group"]
    P5 --> Group["Apply group N"]
    Group --> Val["Per-group validation (typecheck + scoped tests)"]
    Val --> Result{"Green?"}
    Result -- yes --> More{"More groups?"}
    More -- yes --> Group
    More -- no --> P6["Phase 6: final validation (build + full test + typecheck + lint + smoke)"]
    Result -- no --> StopGroup["STOP: surface; operator decides"]
    P6 --> AllGreen{"All green?"}
    AllGreen -- yes --> P7["Phase 7: report"]
    AllGreen -- no --> StopFinal["STOP: investigate"]
    P7 --> Done["Hand-off"]
```

## Group sequencing decision tree

```mermaid
flowchart TD
    Start["Have all rules from inventory"] --> Q1{"Does the guide require a specific order?"}
    Q1 -- yes --> Honor["Honor the guide's order"]
    Q1 -- no --> Q2{"Is the dependency version bump backwards-compatible<br/>with both old and new patterns?"}
    Q2 -- yes --> CodeFirst["Code migration first; version bump LAST"]
    Q2 -- no --> Mixed["Read the guide's Note about ordering"]
    Mixed --> CodeFirst
    Honor --> Order["Final group sequence"]
    CodeFirst --> SubOrder{"Within source code: low-blast-radius first?"}
    SubOrder -- yes --> Mech["mechanical groups → manual groups → version bump"]
    Mech --> Order
```

## Per-group execution loop

```mermaid
flowchart LR
    Plan["plan.md (Groups table)"] --> Pick["Pick next group"]
    Pick --> Apply["Implementer applies group's changes"]
    Apply --> Val["typecheck + scoped tests"]
    Val --> Green{"Green?"}
    Green -- yes --> Log["Append to validation log; pick next"]
    Green -- no --> Recover["Smallest fix attempt"]
    Recover --> ReVal["Re-run validation"]
    ReVal --> Green2{"Green?"}
    Green2 -- yes --> Log
    Green2 -- no --> Stop["STOP: surface; operator decides<br/>(continue / revert / re-plan)"]
    Log --> More{"More groups?"}
    More -- yes --> Pick
    More -- no --> Final["Phase 6 final validation"]
```

## Migration-guide-fetch protocol

```mermaid
flowchart TD
    Start["Phase 2 begin"] --> Identify["Identify canonical guide URL for X→Y"]
    Identify --> Fetch["WebFetch the guide"]
    Fetch --> Available{"Guide reachable + has content?"}
    Available -- no --> Stop["STOP: surface; skill REQUIRES authoritative source"]
    Available -- yes --> Curate["Curate to migration-notes.md (≤15 word quotes)"]
    Curate --> Source["Cite source URL + ISO timestamp"]
    Source --> Mark["Mark each rule: applies / partial / no"]
    Mark --> Done["Phase 2 done"]
```

## What "tool replacement" looks like

```mermaid
flowchart TD
    Start["Tool A → Tool B (e.g. Jest → Vitest)"] --> R["Read both tools' migration guides<br/>(source + destination)"]
    R --> P["Plan groups (often shape: add B alongside A → migrate APIs → switch entrypoint → remove A)"]
    P --> G1["Group 1: install B; create B's config"]
    G1 --> G2["Group 2: migrate API surface (mechanical)"]
    G2 --> G3["Group 3: any manual cases"]
    G3 --> G4["Group 4: switch entrypoint (npm scripts / build pipeline)"]
    G4 --> G5["Group 5: regenerate any auto-generated artifacts (snapshots, etc.)"]
    G5 --> G6["Group 6: remove A from devDeps"]
    G6 --> Final["Phase 6 final validation"]
```
