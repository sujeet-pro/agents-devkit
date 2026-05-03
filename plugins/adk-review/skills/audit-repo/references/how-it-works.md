# `audit-repo` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User: /adk-review:audit-repo [<path>]"] --> P0["Phase 0: resolve repo + slug + dimensions/scope"]
    P0 --> P1["Phase 1: preflight (in git repo + meta-info + tool detection per dimension)"]
    P1 --> P2["Phase 2: inventory (languages + frameworks + tools + top-20 largest + top-20 most-changed)"]
    P2 --> P3["Phase 3: parallel dimension passes (max 4 at once)"]
    P3 --> P4["Phase 4: aggregate (severity-sort + Top-10 + group remaining + healthy assembly + recommendations)"]
    P4 --> P5["Phase 5: propose Top-10"]
    P5 --> Mode{"mode?"}
    Mode -- "interactive" --> Walk["walk Top-10; allow re-tier/discard/merge"]
    Mode -- "auto" --> Show["show Top-10 + per-dimension counts"]
    Walk --> P6["Phase 6: write full report (audit-<slug>.md + evidence/)"]
    Show --> P6
    P6 --> P7["Phase 7: surface report + Top-3 + suggest follow-ups"]
```

## Inventory (Phase 2)

```mermaid
flowchart LR
    Repo["repo path"] --> Detect["detect: language LOC, frameworks, tools, observability"]
    Detect --> Langs["languages by LOC (cloc / tokei / scc / git ls-files+wc)"]
    Detect --> Frame["frameworks (package.json / requirements.txt / go.mod / Cargo.toml + content sniff)"]
    Detect --> Dep["dep manager (pnpm/yarn/npm; uv/pip/poetry; go mod; cargo; bundler; etc.)"]
    Detect --> Test["test framework (vitest/jest/mocha; pytest; go test; cargo test; rspec)"]
    Detect --> Lint["lint tool (eslint; ruff/flake8/black; golangci-lint; clippy)"]
    Detect --> CI["CI provider (.github/workflows; .gitlab-ci.yml; jenkinsfile; circleci)"]
    Detect --> Obs["observability (datadog/sentry/newrelic refs in code/CI)"]
    Detect --> Top["top-20 largest files (find / wc -l); top-20 most-changed (git log)"]
    Langs --> Inv["inventory.md"]
    Frame --> Inv
    Dep --> Inv
    Test --> Inv
    Lint --> Inv
    CI --> Inv
    Obs --> Inv
    Top --> Inv
```

## Dimension passes (Phase 3, parallel groups)

```mermaid
flowchart LR
    Inv["inventory.md (informs each pass)"] --> Fan["spawn parallel subagents (max 4 at once)"]
    Fan --> Group1["Group 1: security + performance + quality + deps"]
    Fan --> Group2["Group 2 (after group 1): test-coverage + architecture"]
    Group1 --> Sec["security (security-reviewer + npm/pip/go audit)"]
    Group1 --> Perf["performance (code-reviewer + perf-budget script + heuristics)"]
    Group1 --> Qual["quality (code-reviewer + lint + complexity)"]
    Group1 --> Dep["deps (code-reviewer + outdated/audit/license)"]
    Group2 --> Test["test-coverage (code-reviewer + coverage tool)"]
    Group2 --> Arch["architecture (code-reviewer + dep-graph + sample top-20 files)"]
    Sec --> Aggr["per-dimension files written"]
    Perf --> Aggr
    Qual --> Aggr
    Dep --> Aggr
    Test --> Aggr
    Arch --> Aggr
```

## Aggregation (Phase 4)

```mermaid
flowchart TD
    PerDim["per-dimension findings"] --> Collate["collate all findings"]
    Collate --> Apply["apply review.md severity_bar overrides + ignore_in_repos filter"]
    Apply --> Sort["sort by severity (B>C>S>M>N>Q); within tier, by impact-area breadth"]
    Sort --> Top10{">=10 findings?"}
    Top10 -- yes --> PickTop["pick Top-10"]
    Top10 -- no --> AllTop["surface all (no padding)"]
    PickTop --> Group["remaining findings: group per dimension"]
    AllTop --> Group
    Group --> Healthy["assemble 'what's healthy' from per-dimension sub-sections (top 5 across dims)"]
    Healthy --> Reco["build recommendations: sort by severity AND effort; reference appropriate /adk-code:* skill"]
    Reco --> Out["aggregation complete; ready for Phase 5"]
```

## Top-10 selection

```mermaid
flowchart TD
    All["all findings post-override"] --> Severity["sort: Blocker -> Critical -> Should-Have -> May-Have -> Nitpick -> Question"]
    Severity --> Breadth["within tier, sort by impact-area breadth (5 endpoints affected > 1 endpoint affected)"]
    Breadth --> Take["take top 10 (or fewer if fewer real findings)"]
    Take --> Cards["build per-finding cards (severity + file:line + dim + confidence + evidence + issue + impact + recommended action + effort + references)"]
    Cards --> Out["Top-10 ready"]
```

## Time budget (when --time-budget <minutes>)

```mermaid
flowchart TD
    Start["start with --time-budget <N>"] --> Track["track elapsed seconds"]
    Track --> Reach{"elapsed >= N*60 ?"}
    Reach -- no --> Continue["continue current phase"]
    Reach -- yes --> Wrap["wrap up: stop further work; assemble what we have"]
    Wrap --> Partial["mark report as PARTIAL in methodology section"]
    Partial --> ListSkipped["list skipped dimensions + recommended re-run command"]
```

## --scope <path> filter

```mermaid
flowchart LR
    Repo["repo (whole)"] --> Filter["apply --scope <path>"]
    Filter --> Inv["inventory limited to scope"]
    Filter --> Files["all file walks limited to scope"]
    Inv --> P3["Phase 3 dimension passes (still all 6, but limited input)"]
    Files --> P3
    Note["Note: deps and CI dimensions are inherently repo-wide; --scope only affects code-shaped dimensions (security, performance, quality, test-coverage, architecture)."]
```
