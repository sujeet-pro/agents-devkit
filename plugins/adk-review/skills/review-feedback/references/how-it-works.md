# `review-feedback` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User: PR URL or '#N'"] --> P0["Phase 0: parse + slug + locate checkout"]
    P0 --> P1["Phase 1: preflight (mcp/gh + auth + meta-info + branch protection)"]
    P1 --> P2["Phase 2: fetch all reviewer comments (inline + issue + reviews + threads)"]
    P2 --> P3["Phase 3: classify each comment + group related"]
    P3 --> P4["Phase 4: propose classifications"]
    P4 --> Mode{"--fix?"}
    Mode -- no --> P5a["Phase 5a: draft replies only (STOP)"]
    Mode -- yes --> P5aFix["Phase 5a: draft replies (with SHA placeholders)"]
    P5aFix --> P5b["Phase 5b: apply each grouped fix + validate"]
    P5b --> ValOk{"all green?"}
    ValOk -- no --> StopAll["stop applying; surface failure; user decides"]
    ValOk -- yes --> P5c["Phase 5c: PUSH-GATE (asks even under --auto --fix)"]
    P5c --> Push{"approved?"}
    Push -- no --> Hold["hold commits local; surface for manual push"]
    Push -- yes --> Pushed["push to PR head branch (NEVER --force)"]
    Pushed --> P5d["Phase 5d: post replies + post-confirmation + resolve apply-* threads"]
    P5d --> P6["Phase 6: report"]
    P5a --> P6
    StopAll --> P6
    Hold --> P6
```

## Classification fan-out (Phase 3)

```mermaid
flowchart LR
    Comments["all open comments + threads"] --> ForEach["for each: read body + read code at target"]
    ForEach --> Q1{"underlying issue still in code?"}
    Q1 -- no --> AR["already-resolved"]
    Q1 -- yes --> Q2{"reviewer suggested a fix?"}
    Q2 -- yes --> Q3{"suggestion is correct + complete?"}
    Q3 -- yes --> AS["apply-as-stated"]
    Q3 -- partially --> AM["apply-with-modification (write the modification rationale)"]
    Q2 -- no --> Q4{"issue is architectural / multi-file?"}
    Q4 -- yes --> DS["discuss-not-fix (link a follow-up)"]
    Q4 -- no --> Q5{"we agree the issue exists?"}
    Q5 -- yes --> AM
    Q5 -- no --> WF["wont-fix (write concrete reasoning)"]
    AR --> Group["group related (per comment-grouping.md)"]
    AS --> Group
    AM --> Group
    DS --> Group
    WF --> Group
    Group --> Out["classification.md + grouping table"]
```

## --fix loop (Phases 5b, 5c, 5d)

```mermaid
flowchart TD
    Queue["grouped fix queue (apply-* classifications only)"] --> Pop["pop next grouped fix"]
    Pop --> Trivial{"trivial?"}
    Trivial -- yes --> InEdit["inline edit"]
    Trivial -- no --> Delegate["delegate to /adk-code:code-bugfix"]
    InEdit --> Validate["repo-native tests + typecheck + lint"]
    Delegate --> Validate
    Validate --> Pass{"all green?"}
    Pass -- no --> StopAll["STOP applying; surface; user decides skip/abort"]
    Pass -- yes --> Commit["commit (per logical fix; OR squash if --squash-fixes)"]
    Commit --> More{"queue empty?"}
    More -- no --> Pop
    More -- yes --> PushGate["PUSH-GATE: ask user (always, even --auto --fix)"]
    PushGate --> User{"approved?"}
    User -- no --> Hold["hold local; surface"]
    User -- yes --> Push["git push origin <head> (NEVER --force)"]
    Push --> FillSHA["fill <commit-sha> placeholders in replies-draft.md"]
    FillSHA --> Post["post each reply (capture receipt IDs)"]
    Post --> PC["post-confirmation: 5s/10s/20s retry budget; never re-post"]
    PC --> ConfMap["per-reply: confirmed|unconfirmed"]
    ConfMap --> Resolve["for each apply-* with confirmed reply: resolveReviewThread"]
    Resolve --> Done["replies-postback.md complete"]
```

## Post-confirmation (delegates to review-pr's protocol)

```mermaid
flowchart TD
    Posted["posted replies; receipt IDs captured"] --> Wait["wait 5s"]
    Wait --> Refetch["re-fetch comments"]
    Refetch --> Check{"all IDs visible?"}
    Check -- yes --> Confirm["mark all confirmed"]
    Check -- no --> Wait2["wait 10s"]
    Wait2 --> Refetch2["re-fetch"]
    Refetch2 --> Check2{"all IDs visible?"}
    Check2 -- yes --> Confirm
    Check2 -- no --> Wait3["wait 20s"]
    Wait3 --> Refetch3["re-fetch"]
    Refetch3 --> Check3{"all IDs visible?"}
    Check3 -- yes --> Confirm
    Check3 -- no --> Surface["log unconfirmed; surface to user; NEVER re-post"]
    Confirm --> Resolve["proceed to thread-resolution for apply-* only"]
    Surface --> NoResolve["DO NOT resolve threads with unconfirmed replies"]
```

## Thread-resolution decision

```mermaid
flowchart TD
    AfterPC["after post-confirmation"] --> ForEach["for each comment with confirmed reply"]
    ForEach --> Class{"classification?"}
    Class -- "apply-as-stated" --> Resolve["resolveReviewThread"]
    Class -- "apply-with-modification" --> Resolve
    Class -- "discuss-not-fix" --> Open["leave thread OPEN (reviewer accepts/counters)"]
    Class -- "wont-fix" --> Open
    Class -- "already-resolved" --> OpenSig["leave OPEN; reply text says 'marking to resolved' as a signal"]
    Resolve --> Done
    Open --> Done
    OpenSig --> Done
```
