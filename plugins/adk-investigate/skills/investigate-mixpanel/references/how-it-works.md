# `investigate-mixpanel` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Prompt["User question + optional --use --time --funnel-id --cohort-id"] --> P0["Phase 0: prompt-expand + resolve events / funnels / cohorts"]
    P0 --> P1["Phase 1: preflight (workspace MCP + meta-info)"]
    P1 --> Branch{"--use?"}
    Branch -- usage-summary --> US["Get-Events top N<br/>+ Run-Query DAU/WAU<br/>+ baseline"]
    Branch -- funnel --> F["Get-Report by funnel-id<br/>OR Run-Query ad-hoc<br/>+ baseline + low-traffic check"]
    Branch -- cohort --> C["Get-Report cohort retention<br/>+ control cohort<br/>+ low-traffic check"]
    US --> Exec["Phase 2: execute via Mixpanel MCP"]
    F --> Exec
    C --> Exec
    Exec --> P3["Phase 3: summarize + baseline deltas + Mixpanel UI links"]
    P3 --> P4["Phase 4: emit mixpanel.md"]
    P4 --> Done["return path to caller"]
```

## --use selection decision tree

```mermaid
flowchart TD
    Q["User question"] --> Q1{"Mentions 'funnel' / 'convert' / 'step' / 'drop-off'?"}
    Q1 -- yes --> F["--use funnel"]
    Q1 -- no --> Q2{"Mentions 'cohort' / 'retention' / 'segment' / 'users who did X'?"}
    Q2 -- yes --> C["--use cohort"]
    Q2 -- no --> Q3{"Mentions 'DAU' / 'WAU' / 'top events' / 'active users'?"}
    Q3 -- yes --> U["--use usage-summary"]
    Q3 -- no --> Default["--use usage-summary (default)"]
```

## Funnel-vs-cohort modeling decision

```mermaid
flowchart TD
    Q["What's the question?"] --> Q1{"Is it 'X% of users go from A to B'?"}
    Q1 -- yes --> F["Funnel — sequence of events"]
    Q1 -- no --> Q2{"Is it 'how do users in segment X behave over time'?"}
    Q2 -- yes --> C["Cohort — defined population + retention curve"]
    Q2 -- no --> Q3{"Is it 'top events / DAU / WAU'?"}
    Q3 -- yes --> R["Saved Report — Get-Report by id"]
    Q3 -- no --> Q4{"Is it free-form aggregation across many properties?"}
    Q4 -- yes --> Run["Run-Query (JQL or formula)"]
    Q4 -- no --> Ask["Ask one clarifying question"]
```

## Baseline computation

```mermaid
flowchart LR
    Window["[from, to]"] --> Prior["[from - duration, to - duration]"]
    Window --> SameLastWeek["[from - 7d, to - 7d]"]
    Prior --> Compare["Delta vs prior equal-duration window"]
    SameLastWeek --> Compare2["Delta vs same-period last week (preferred when window is week-aligned)"]
    Compare --> Report
    Compare2 --> Report
```

## Tracking-change detection

```mermaid
flowchart TD
    Step["Funnel step count drops >50% vs baseline"] --> Check1["Lexicon: was the event renamed in window?"]
    Check1 -- yes --> Flag["FLAG: tracking change, not product regression"]
    Check1 -- no --> Check2["Deploy timeline: was the SDK version changed?"]
    Check2 -- yes --> Flag2["FLAG: SDK / track() change, verify before naming product cause"]
    Check2 -- no --> Real["Likely real product regression; correlate with DD"]
```
