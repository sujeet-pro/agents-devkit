# `docs-changelog` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Start["User prompt: from-tag + to-tag"] --> P0["Phase 0: resolve repo + CHANGELOG path + slug"]
    P0 --> P1["Phase 1: preflight (tags resolve, style detection)"]
    P1 --> P2["Phase 2: git log + classify commits"]
    P2 --> Has{"Any commits in range?"}
    Has -- no --> Stop["Stop: empty range"]
    Has -- yes --> P3["Phase 3: draft changelog-entry.md"]
    P3 --> P4["Phase 4: validate"]
    P4 --> Pass{"All gates pass?"}
    Pass -- no --> P3
    Pass -- yes --> Fix{"--fix?"}
    Fix -- no --> Report["Final report"]
    Fix -- yes --> Exists{"Target version block exists?"}
    Exists -- yes --> Ask["Ask opt-in to overwrite"]
    Exists -- no --> Insert
    Ask -- yes --> Insert["Backup + insert + git add"]
    Ask -- no --> Defer["Leave entry in .temp/; skip write"]
    Insert --> Revalidate["Re-read CHANGELOG.md; confirm minimal diff"]
    Revalidate --> Report
    Defer --> Report
```

## Style detection

```mermaid
flowchart TD
    Start["Read first 100 lines of CHANGELOG.md"] --> Kac{"`### Added` / `### Fixed` headers present?"}
    Kac -- yes --> KaC["keep-a-changelog"]
    Kac -- no --> Sem{"`## [X.Y.Z](compare-url) (YYYY-MM-DD)` pattern + `### Features` / `### Bug Fixes`?"}
    Sem -- yes --> SemR["semantic-release"]
    Sem -- no --> Free["free-form (mirror release-header pattern)"]
```

## Breaking-change surfacing

```mermaid
flowchart TD
    Commit["Each commit in range"] --> Break{"Subject has `!` OR body has `BREAKING CHANGE:`?"}
    Break -- yes --> CollectBreak["Collect into Breaking changes group"]
    Break -- no --> NormalGroup["Classify per type"]
    CollectBreak --> FirstSection["Breaking changes = FIRST section in version block"]
    NormalGroup --> OtherSections["Added / Changed / Fixed / etc."]
```
