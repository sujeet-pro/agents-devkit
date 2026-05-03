# `audit-pr` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User: PR URL"] --> P0["Phase 0: parse + slug + locate checkout"]
    P0 --> P1["Phase 1: preflight (mcp/gh + auth + tool detection per check)"]
    P1 --> P2["Phase 2: fetch (PR meta + diff + existing CI status)"]
    P2 --> P3["Phase 3: parallel fixed-set checks (max 4 at once)"]
    P3 --> Aggr["aggregate verdicts -> overall (PASS/WARN/FAIL/MIXED)"]
    Aggr --> P4["Phase 4: propose"]
    P4 --> Mode{"mode?"}
    Mode -- "auto/i (no --fix, no --post-comment)" --> P5a["Phase 5a: report-only"]
    Mode -- "+ fix" --> P5b["Phase 5b: auto-fix safely-fixable subset"]
    Mode -- "+ post-comment" --> P5cGate["Phase 5c: confirmation gate"]
    P5b --> P5bDone{"any safely-fixable to fix?"}
    P5bDone -- yes --> Apply["apply (lint --fix / prepend headers / regen TOC)"]
    P5bDone -- no --> P5a
    Apply --> ReVal["re-run affected checks"]
    ReVal --> Push{"any pushable changes?"}
    Push -- yes --> Gate["PUSH-GATE: ask"]
    Push -- no --> P5a
    Gate --> Approved{"approved?"}
    Approved -- yes --> Pushed["push (NEVER --force; NEVER protected)"]
    Approved -- no --> Hold["leave dirty for user"]
    Pushed --> P5a
    Hold --> P5a
    P5cGate --> Confirm{"approved?"}
    Confirm -- yes --> Post["post via gh pr comment + post-confirmation"]
    Confirm -- no --> P5a
    Post --> P5a
    P5a --> P6["Phase 6: report"]
```

## Parallel check fan-out (Phase 3)

```mermaid
flowchart LR
    Diff["PR diff + changed-file list"] --> Detect["detect: which conditional checks are relevant?"]
    Detect --> Fan["spawn parallel subagents (max 4 at once)"]
    Fan --> Group1["Group 1: lint, typecheck, secrets, license-headers"]
    Fan --> Group2["Group 2: tests-added, dep-licenses, doc-updated"]
    Fan --> Cond["Conditional: a11y / perf / bundle (only if triggered)"]
    Group1 --> Aggr["aggregate verdicts"]
    Group2 --> Aggr
    Cond --> Aggr
    Aggr --> Verdict["overall verdict per pass-warn-fail.md"]
```

## Auto-fix loop (Phase 5b)

```mermaid
flowchart TD
    Q["fix queue (safely-fixable subset only: lint, license-headers, docs-toc)"] --> Pop["pop next fix"]
    Pop --> Apply["apply (per check's fix-strategy)"]
    Apply --> ReVal["re-run the affected check"]
    ReVal --> Verdict{"new verdict?"}
    Verdict -- "now PASS" --> LogOk["update results.md; log to fix-log.md"]
    Verdict -- "still WARN/FAIL" --> LogPart["log: fix didn't clear; surface as 'partial; manual touch needed'"]
    LogOk --> More{"queue empty?"}
    LogPart --> More
    More -- no --> Pop
    More -- yes --> Push{"any new commits to push?"}
    Push -- yes --> Gate["PUSH-GATE"]
    Push -- no --> Done["fix-log.md done"]
```

## Verdict computation (Phase 4)

```mermaid
flowchart TD
    Results["per-check verdicts"] --> Counts["count: PASS, WARN, FAIL, N/A"]
    Counts --> Q1{"any FAIL?"}
    Q1 -- yes --> Fail["overall: FAIL"]
    Q1 -- no --> Q2{"any WARN?"}
    Q2 -- yes --> Warn["overall: WARN"]
    Q2 -- no --> Q3{"any N/A?"}
    Q3 -- yes --> Mixed["overall: MIXED"]
    Q3 -- no --> Pass["overall: PASS"]
```

## Post-comment gate (Phase 5c)

```mermaid
flowchart TD
    Flag["--post-comment set?"] --> Yes["build summary comment body"]
    Yes --> Confirm["confirmation gate: 'post audit summary to PR <num>?' [y/N]"]
    Confirm --> Decision{"approved?"}
    Decision -- no --> Skip["skip; surface in report"]
    Decision -- yes --> Post["gh pr comment <num> --body-file <summary>"]
    Post --> PCDone["POST-CONFIRMATION (5/10/20s; never re-post)"]
    PCDone --> Receipt["postback.md with receipt + confirmation"]
```

## Tool detection (Phase 1)

```mermaid
flowchart LR
    Start["Phase 1 tool detection"] --> ForEach["for each of 10 checks"]
    ForEach --> Cmd{"command -v <tool>?"}
    Cmd -- found --> Mark1["mark check 'executable'"]
    Cmd -- not found --> Mark2["mark check 'N/A (missing tool: <name>; install: <command>)'"]
    Mark1 --> Done["proceed to Phase 2"]
    Mark2 --> Done
```
