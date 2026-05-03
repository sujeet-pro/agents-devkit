# `code-test` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Prompt["User prompt"] --> P0["Phase 0: prompt expand + framework + test type"]
    P0 --> P1["Phase 1: preflight (commands resolved + baseline GREEN)"]
    P1 --> Baseline{"Baseline green?"}
    Baseline -- no --> Stop1["STOP: tests on red is unverifiable"]
    Baseline -- yes --> P2["Phase 2: read target + existing tests + AGENTS.md"]
    P2 --> P3["Phase 3: enumerate behaviors (happy + boundary + error per)"]
    P3 --> Approve3{"--auto?"}
    Approve3 -- no --> Gate3["Approval: confirm behavior list"]
    Approve3 -- yes --> P4
    Gate3 --> P4["Phase 4: author tests (test-engineer subagent)"]
    P4 --> ForEach["For each behavior trio"]
    ForEach --> Author["Author 3 tests"]
    Author --> Run["Run tests"]
    Run --> Green{"Green?"}
    Green -- no --> Iterate["Iterate up to 3 times"]
    Iterate --> Run
    Green -- yes --> Mutate["Apply SUT mutation"]
    Mutate --> RunMutated["Run tests"]
    RunMutated --> Red{"Red?"}
    Red -- yes --> Restore["Restore SUT"]
    Restore --> RunRestored["Run tests"]
    RunRestored --> Green2{"Green?"}
    Green2 -- yes --> Log["Log fail-first evidence"]
    Log --> More{"More behaviors?"}
    More -- yes --> ForEach
    More -- no --> P5["Phase 5: validate (full suite + typecheck + lint + coverage)"]
    Red -- no --> Reconsider["Mutation didn't exercise test path; reconsider"]
    Green2 -- no --> Stop2["STOP: restore failed; investigate"]
    P5 --> AllGreen{"All green?"}
    AllGreen -- yes --> P6["Phase 6: report"]
    AllGreen -- no --> Stop3["STOP: investigate"]
    P6 --> Done["Hand-off"]
```

## Behavior-enumeration decision tree

```mermaid
flowchart TD
    Start["Have a target module"] --> Q1{"What does the public API do?"}
    Q1 --> Behaviors["List 3-7 distinct behaviors"]
    Behaviors --> ForEach["For each behavior"]
    ForEach --> Q2{"What's the most common positive case?"}
    Q2 --> Happy["Happy path test"]
    ForEach --> Q3{"What's the input value at the EDGE of acceptance?"}
    Q3 --> Boundary["Boundary test"]
    ForEach --> Q4{"What's the input value at the EDGE of rejection?"}
    Q4 --> Error["Error test"]
    Happy --> Trio["Trio = happy + boundary + error"]
    Boundary --> Trio
    Error --> Trio
    Trio --> Done["3 tests per behavior"]
```

## Test-type decision tree

```mermaid
flowchart TD
    Start["Have a target"] --> Q1{"Forced by --unit/--integration/--e2e?"}
    Q1 -- yes --> Honor["Use the forced type"]
    Q1 -- no --> Q2{"Pure function with no IO deps?"}
    Q2 -- yes --> Unit["unit"]
    Q2 -- no --> Q3{"Touches DB / HTTP / file system?"}
    Q3 -- yes --> Integration["integration"]
    Q3 -- no --> Q4{"User-facing flow (browser, CLI, full HTTP API)?"}
    Q4 -- yes --> E2E["e2e (only if harness exists)"]
    Q4 -- no --> Default["unit (default)"]
```

## Fail-first protocol

```mermaid
flowchart LR
    Test["New test (assumes implementation exists)"] --> RunInit["Run test"]
    RunInit --> InitGreen{"Green?"}
    InitGreen -- no --> Iterate["Iterate (test or impl bug)"]
    Iterate --> RunInit
    InitGreen -- yes --> Mutate["Mutate SUT (return wrong / throw / no-op)"]
    Mutate --> RunMut["Run test"]
    RunMut --> MutRed{"Red?"}
    MutRed -- yes --> Restore["Restore SUT"]
    Restore --> RunFinal["Run test"]
    RunFinal --> FinalGreen{"Green?"}
    FinalGreen -- yes --> Log["Log fail-first transition"]
    FinalGreen -- no --> Investigate["Restore failed; investigate"]
    MutRed -- no --> Reconsider["Mutation didn't exercise path; pick different mutation"]
    Reconsider --> Mutate
```

## When --coverage is requested

```mermaid
flowchart LR
    P5["Phase 5 begin"] --> Suite["Run full suite"]
    Suite --> CovBefore["Snapshot coverage BEFORE the new tests"]
    CovBefore --> CovAfter["Snapshot coverage AFTER the new tests"]
    CovAfter --> Delta["Compute delta (lines, branches)"]
    Delta --> ReportTbl["Add delta table to report.md"]
    ReportTbl --> Gaps["Identify remaining gaps"]
    Gaps --> Residual["List remaining gaps in residual risk"]
```

Note: most coverage tools compare a single run's coverage against a baseline. The skill captures coverage from BEFORE running on HEAD (Phase 1), then again at Phase 5 with the new tests; the delta is computed by subtraction.
