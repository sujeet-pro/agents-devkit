# `review-code-changes` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User runs in repo (or with prompt)"] --> P0["Phase 0: detect repo + baseline + slug"]
    P0 --> P1["Phase 1: preflight (writeable + meta-info + cheap lint pre-pass)"]
    P1 --> P2["Phase 2: gather scope (branch + staged + unstaged + untracked)"]
    P2 --> Scope["unified scope map; mtime_t0 recorded per file"]
    Scope --> P3["Phase 3: parallel dimension passes"]
    P3 --> Mtime{"any in-scope file's mtime > mtime_t0?"}
    Mtime -- yes --> Annot["annotate affected findings as dirty_during_review"]
    Mtime -- no --> P4
    Annot --> P4["Phase 4: propose (severity-sort + per-source tag)"]
    P4 --> Mode{"mode?"}
    Mode -- "auto/i (no fix)" --> P5a["Phase 5a: report-only"]
    Mode -- "+ fix" --> P5b["Phase 5b: apply each + validate (tests + typecheck + lint)"]
    P5b --> ValOk{"validation green?"}
    ValOk -- yes --> Continue["next fix in queue"]
    ValOk -- no --> Stop["stop applying further; surface failure"]
    Continue --> Done5b{"queue empty?"}
    Done5b -- no --> P5b
    Done5b -- yes --> P6["Phase 6: report"]
    P5a --> P6
    Stop --> P6
    P6 --> Surf["surface report; suggest next step"]
```

## Baseline detection

```mermaid
flowchart TD
    Start["resolve baseline"] --> Q1{"--base-branch arg?"}
    Q1 -- yes --> Use1["use arg (source: arg)"]
    Q1 -- no --> Q2{"git rev-parse @{upstream} succeeds?"}
    Q2 -- yes --> Use2["use upstream (source: tracking)"]
    Q2 -- no --> Q3{"git rev-parse origin/branch succeeds?"}
    Q3 -- yes --> Use3["use origin/branch (source: remote)"]
    Q3 -- no --> Q4{"git rev-parse main succeeds?"}
    Q4 -- yes --> Use4["use main (source: main)"]
    Q4 -- no --> Q5{"git rev-parse master succeeds?"}
    Q5 -- yes --> Use5["use master (source: master)"]
    Q5 -- no --> Q6{"--auto?"}
    Q6 -- yes --> UseFP["use HEAD~1 (source: first-parent); surface warning"]
    Q6 -- no --> Ask["ask user for explicit base-branch"]
```

## Scope source fan-in

```mermaid
flowchart LR
    Repo["working tree"] --> Branch["git diff baseline...HEAD"]
    Repo --> Staged["git diff --cached"]
    Repo --> Unstaged["git diff"]
    Repo --> Untracked["git ls-files --others --exclude-standard"]
    Branch --> Map["unified scope map (file -> kind)"]
    Staged --> Map
    Unstaged --> Map
    Untracked --> Map
    Map --> Filter["apply --scope path filter"]
    Filter --> Out["scope.md + per-source counts"]
```

## Dimension fan-out (Phase 3)

```mermaid
flowchart LR
    Scope["scope map + file content"] --> Fan["spawn parallel passes (max 4 at once)"]
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
    Aggr --> Apply["apply review.md overrides + de-noise + scope-source tag"]
```

## --fix loop (Phase 5b)

```mermaid
flowchart TD
    Queue["accepted findings, severity-sorted"] --> Pop["pop next finding"]
    Pop --> Trivial{"trivial (style/nit/simple bug)?"}
    Trivial -- yes --> InEdit["inline edit"]
    Trivial -- no --> Delegate["delegate to /adk-code:code-bugfix"]
    InEdit --> Validate["run repo-native tests + typecheck + lint"]
    Delegate --> Validate
    Validate --> Pass{"all green?"}
    Pass -- no --> StopAll["STOP applying further fixes; surface failure"]
    Pass -- yes --> Log["append to fix-log.md"]
    Log --> More{"queue empty?"}
    More -- no --> Pop
    More -- yes --> Surf["surface 'fixes applied; eyeball with `git diff`, then commit + push'"]
```

Note: NO push step. NO commit step (working tree stays dirty for the user to inspect + commit themselves).
