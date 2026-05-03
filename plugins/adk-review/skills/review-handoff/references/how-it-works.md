# `review-handoff` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User: /adk-review:review-handoff"] --> P0["Phase 0: resolve task slug + repo"]
    P0 --> Empty{"slug found?"}
    Empty -- no --> Stop["stop with 'no recent task'"]
    Empty -- yes --> P1["Phase 1: preflight (meta-info + post-to target reachable if set)"]
    P1 --> P2["Phase 2: parallel gather (.temp/task-slug/*, git state, env, info.md)"]
    P2 --> P3["Phase 3: synthesize 10 sections -> handoff.md"]
    P3 --> Mode{"mode?"}
    Mode -- "interactive" --> Walk["walk each section; allow edits"]
    Mode -- "auto" --> Show["show full doc"]
    Walk --> P5{"--post-to set?"}
    Show --> P5
    P5 -- no --> P6["Phase 6: report + suggest natural follow-up"]
    P5 -- yes --> Confirm["Phase 5: CONFIRMATION GATE (always asks, even under --auto)"]
    Confirm --> Approved{"user approved?"}
    Approved -- no --> P6
    Approved -- yes --> Post["post to slack/jira/pr"]
    Post --> PCQ{"target == pr?"}
    PCQ -- yes --> PC["POST-CONFIRMATION (5/10/20s; never re-post)"]
    PCQ -- no --> Postback["write handoff-postback.md"]
    PC --> Postback
    Postback --> P6
```

## Phase 2 input fan-in

```mermaid
flowchart LR
    Task[".temp/task-slug/*"] --> Reads["read all files"]
    Reads --> Prompt["prompt.txt"]
    Reads --> SkillPlan["skill-plan.md"]
    Reads --> Context["context.md"]
    Reads --> ReviewArt["review/*.md"]
    Reads --> FbArt["feedback/*.md"]
    Reads --> InvArt["investigation/*.md"]
    Reads --> CodeArt["code/*.md"]
    Reads --> Validation["validation/per-skill/*"]
    Reads --> Report["report.md (if exists)"]
    Git["git commands"] --> Branch["branch + dirty + commits + diff + stash"]
    Env["env commands"] --> Tools["editor/shell/pwd/tool versions"]
    Meta["~/.config/adk/"] --> Info["info.md (operator name)"]
    Meta --> Repos["repos.md (build/test command)"]
    Meta --> Slack["slack.md (channels, only for --post-to slack)"]
    Prompt --> Synth["Phase 3: synthesize"]
    SkillPlan --> Synth
    Context --> Synth
    ReviewArt --> Synth
    FbArt --> Synth
    InvArt --> Synth
    CodeArt --> Synth
    Validation --> Synth
    Report --> Synth
    Branch --> Synth
    Tools --> Synth
    Info --> Synth
    Repos --> Synth
```

## Synthesis (Phase 3)

```mermaid
flowchart TD
    InData["all read inputs"] --> Build["build 10 sections per handoff-template.md"]
    Build --> S1["1. Task summary (operator voice)"]
    Build --> S2["2. Decisions (table)"]
    Build --> S3["3. Work completed (cite SHA + artifact)"]
    Build --> S4["4. Remaining work (numbered)"]
    Build --> S5["5. Blockers (table; common case empty)"]
    Build --> S6["6. Key files touched"]
    Build --> S7["7. Files NOT touched (deliberately) - heuristic candidates"]
    Build --> S8["8. Git state (branch, last 10, diff truncated to 200 lines)"]
    Build --> S9["9. Environment (anonymized; names only)"]
    Build --> S10["10. Next step (sentence + exact command)"]
    S1 --> Anon["anonymize: strip env-var values; redact secrets"]
    S2 --> Anon
    S3 --> Anon
    S4 --> Anon
    S5 --> Anon
    S6 --> Anon
    S7 --> Anon
    S8 --> Anon
    S9 --> Anon
    S10 --> Anon
    Anon --> Length["enforce length budget (warn at 300 lines)"]
    Length --> Archive["if prior handoff.md exists, move to .archive/<iso-ts>/"]
    Archive --> Write["write handoff.md"]
```

## --post-to PR (with post-confirmation)

```mermaid
flowchart TD
    Posted["gh pr comment <num> --body-file handoff.md"] --> Receipt["capture receipt ID"]
    Receipt --> Wait["wait 5s"]
    Wait --> Refetch["re-fetch PR comments"]
    Refetch --> Check{"receipt ID visible?"}
    Check -- yes --> Confirm["mark confirmed; write handoff-postback.md"]
    Check -- no --> Wait2["wait 10s"]
    Wait2 --> Refetch2["re-fetch"]
    Refetch2 --> Check2{"visible?"}
    Check2 -- yes --> Confirm
    Check2 -- no --> Wait3["wait 20s"]
    Wait3 --> Refetch3["re-fetch"]
    Refetch3 --> Check3{"visible?"}
    Check3 -- yes --> Confirm
    Check3 -- no --> Surface["log unconfirmed; surface to user; NEVER re-post"]
```

## --post-to Slack (truncated; full doc separate)

```mermaid
flowchart TD
    Doc["handoff.md (full, ~120 lines)"] --> Truncate["build Slack-friendly truncated view (per output-format.md)"]
    Truncate --> SlackMsg["~10-line Slack message: bullets + next-step + link"]
    SlackMsg --> Confirm["confirmation gate"]
    Confirm --> Approved{"approved?"}
    Approved -- no --> Skip["skip; surface to user"]
    Approved -- yes --> Post["post via Slack workspace connector"]
    Post --> URL["capture message URL"]
    URL --> Postback["write handoff-postback.md"]
    Note["NOTE: full handoff.md remains in .temp/; user separately publishes (Confluence/Gist) and updates the Slack message link if needed"]
```
