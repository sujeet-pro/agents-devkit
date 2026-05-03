# `review-pr` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User: PR URL or '#N'"] --> P0["Phase 0: parse + ownership detect + slug + worktree"]
    P0 --> Own{"author.login == local user?"}
    Own -- yes --> SetOwn["ownership=own"]
    Own -- no --> SetPeer["ownership=peer"]
    SetOwn --> P1["Phase 1: preflight (mcp/gh + auth + branch protection + meta-info)"]
    SetPeer --> P1
    P1 --> P2["Phase 2: fetch context (pr metadata, diff, comments, reviews, threads, template, codeowners)"]
    P2 --> P3["Phase 3: full-scope review (parallel dimension passes)"]
    P3 --> P4["Phase 4: reconcile existing comments (still-open/resolved-confirmed/resolved-stale/pushback/clarify)"]
    P4 --> P5["Phase 5: propose findings (severity-sorted)"]
    P5 --> Mode{"mode?"}
    Mode -- "auto + peer" --> P6a["Phase 6a: post inline comments + post-confirmation"]
    Mode -- "auto + own" --> P6b["Phase 6b: validate + reply"]
    Mode -- "i" --> Walk["Walk each finding (accept/edit/discard)"]
    Walk --> P6a
    Mode -- "+ fix" --> P6c["Phase 6c: apply fixes + push (gated) + reply per addressed comment"]
    P6a --> P7["Phase 7: report"]
    P6b --> P7
    P6c --> P7
    P7 --> Done["report.md surfaced; offer-depth question"]
```

## Dimension fan-out (Phase 3)

```mermaid
flowchart LR
    Diff["Diff + post-diff file reads"] --> Fan["Spawn parallel dimension passes (max 4 at once)"]
    Fan --> Corr["correctness (code-reviewer)"]
    Fan --> Sec["security (security-reviewer)"]
    Fan --> Perf["performance (code-reviewer)"]
    Fan --> Test["tests (code-reviewer)"]
    Fan --> Doc["docs (code-reviewer)"]
    Fan --> Style["style (code-reviewer; only if lint covers it)"]
    Corr --> Aggr["aggregate raw-findings.md"]
    Sec --> Aggr
    Perf --> Aggr
    Test --> Aggr
    Doc --> Aggr
    Style --> Aggr
    Aggr --> Apply["apply review.md severity overrides + ignore lists + de-noise"]
    Apply --> Out["raw-findings.md ready for Phase 4"]
```

## Post-confirmation loop (Phase 6a)

```mermaid
flowchart TD
    Post["Post comments via gh / MCP -> capture receipt IDs"] --> Wait5["wait 5s"]
    Wait5 --> Refetch1["re-fetch comments"]
    Refetch1 --> Check1{"all receipt IDs found?"}
    Check1 -- yes --> Confirm["mark all confirmed; restore READ_ONLY=1"]
    Check1 -- no --> Wait10["wait 10s"]
    Wait10 --> Refetch2["re-fetch comments"]
    Refetch2 --> Check2{"all receipt IDs found?"}
    Check2 -- yes --> Confirm
    Check2 -- no --> Wait20["wait 20s"]
    Wait20 --> Refetch3["re-fetch comments"]
    Refetch3 --> Check3{"all receipt IDs found?"}
    Check3 -- yes --> Confirm
    Check3 -- no --> Surface["log unconfirmed; surface to user; NEVER re-post"]
    Confirm --> Done["postback.md complete"]
    Surface --> Done
```

## Ownership branch (Phase 0 + Phase 6)

```mermaid
flowchart TD
    P0["Phase 0: parse PR"] --> Detect{"detect ownership"}
    Detect --> Own["ownership=own"]
    Detect --> Peer["ownership=peer"]
    Peer --> P3p["Phase 3-5: review"]
    P3p --> P6aPeer["Phase 6a: post findings to peer"]
    P6aPeer --> Fix1{"--fix?"}
    Fix1 -- yes --> P6c1["Phase 6c: apply + push (gated) + reply"]
    Fix1 -- no --> P7p["Phase 7: report"]
    P6c1 --> P7p
    Own --> P3o["Phase 3-5: self-review + classify existing reviewer comments"]
    P3o --> P6bOwn["Phase 6b: draft + post replies"]
    P6bOwn --> Fix2{"--fix?"}
    Fix2 -- yes --> P6c2["Phase 6c: apply accepted reviewer feedback + push (gated) + reply with SHA"]
    Fix2 -- no --> P7o["Phase 7: report"]
    P6c2 --> P7o
```

## MCP / gh fallback decision

```mermaid
flowchart TD
    Pre["Phase 1 preflight"] --> Both{"both Docker MCP and gh CLI available?"}
    Both -- yes --> Pickgh["pick gh-cli (faster cold start)"]
    Both -- "MCP only" --> Pickmcp["pick github-docker"]
    Both -- "gh only" --> Pickgh
    Both -- neither --> Stop["stop with missing-thing list"]
    Pickgh --> Auth["gh api /user (assert authed)"]
    Pickmcp --> Auth2["MCP context.get_user (assert authed)"]
    Auth --> P2["proceed to Phase 2"]
    Auth2 --> P2
```

## --fix push gate (Phase 6c)

```mermaid
flowchart TD
    Fix["accepted findings -> fix queue"] --> Apply["apply each fix (inline or /adk-code:code-bugfix)"]
    Apply --> Validate["repo-native tests + typecheck + lint"]
    Validate --> Pass{"all green?"}
    Pass -- no --> Stop["surface failure; do NOT push"]
    Pass -- yes --> First{"first push of session?"}
    First -- yes --> Gate["ASK USER: 'push N commits to <branch>?'"]
    First -- no --> Branch{"target branch changed since last push?"}
    Branch -- yes --> Gate
    Branch -- no --> Push["git push origin <head> (NEVER --force)"]
    Gate --> Decision{"user approved?"}
    Decision -- yes --> Push
    Decision -- no --> Stop2["abort push; keep commits local"]
    Push --> Reply["post fix-applied reply per addressed comment"]
    Reply --> Resolve["mark comments resolved (after reply post-confirmation)"]
    Resolve --> Done["fix-log.md complete"]
```
