# How `auto` works

## Phase flow

```mermaid
flowchart TD
    Prompt["User prompt"] --> A["Phase A: expand + classify + create .temp/task-slug/"]
    A --> Links{"Links to Jira / Confluence / Slack / GDocs / GitHub?"}
    Links -- yes --> CG["context-gather -> context.md"]
    Links -- no --> B
    CG --> B["Phase B: requirements + scoping (brainstorm-facilitator subagent)"]
    B --> ScopeOK{"Scope locked?"}
    ScopeOK -- no --> B
    ScopeOK -- yes --> C["Phase C: dispatch per-task subagents (parallel via Task tool)"]
    C --> Imp["implementer + build-feature/bugfix/refactor"]
    C --> Test["test-engineer + build-test"]
    C --> Doc["doc-writer + docs-write"]
    C --> Design["frontend-design (plan mode = 5 samples)"]
    Design --> Mockup["frontend-mockup -> preview/sample-1..5.html"]
    Mockup --> Pick["User picks 1 of 5"]
    Pick --> Imp
    Imp --> D1["Phase D1: review-local + per-skill validators"]
    Test --> D1
    Doc --> D1
    D1 --> Ui{"UI touched OR preview/*.html exists?"}
    Ui -- yes --> D2["Phase D2: validate-browser (verify-fix / visual-check / console-audit / a11y-audit)"]
    Ui -- no --> Push
    D2 --> Push["Phase D3: publish-commit + publish-github"]
    Push --> Watch["cicd-monitor (gh pr checks --watch)"]
    Watch --> CI{"CI green?"}
    CI -- no --> Fix["cicd-fix (parse failed-job logs + apply fix)"]
    Fix --> C
    CI -- yes --> Done["Final report -> .temp/task-slug/report.md"]
```

## Domain classification decision tree

```mermaid
flowchart TD
    Start["User prompt"] --> Q1{"Code change required?"}
    Q1 -- yes --> Q2{"Bug fix or new behavior?"}
    Q2 -- bug fix --> BB["build-bugfix"]
    Q2 -- new behavior --> Q3{"UI involved?"}
    Q3 -- yes --> FD["frontend-design then frontend-mockup then frontend-feature"]
    Q3 -- no --> BF["build-feature"]
    Q1 -- no --> Q4{"Doc deliverable?"}
    Q4 -- yes --> DW["docs-write"]
    Q4 -- no --> Q5{"Review existing PR?"}
    Q5 -- yes --> RP["review-pr"]
    Q5 -- no --> Q6{"Audit?"}
    Q6 -- repo --> AR["audit-repo"]
    Q6 -- site --> AS["audit-site"]
    Q6 -- pr --> AP["audit-pr"]
    Q6 -- no --> Q7{"Investigate incident?"}
    Q7 -- yes --> OI["observability-incident"]
    Q7 -- no --> Q8{"Bootstrap something?"}
    Q8 -- repo AI --> AI["adopt-ai-in-repo"]
    Q8 -- doc site --> DS["doc-site-setup"]
    Q8 -- new app --> RC["frontend-react-csr"]
    Q8 -- no --> Ask["Ask one clarifying question"]
```

## Subagent dispatch matrix

See `references/dispatch-matrix.md` for the full matrix; this diagram shows the most common parallelisable groups.

```mermaid
flowchart LR
    Dispatcher["dispatcher (in auto Phase C)"] --> ImpGroup["Implementation group (sequential)"]
    Dispatcher --> DocGroup["Doc group (parallel)"]
    Dispatcher --> ReviewGroup["Review group (after implementation)"]
    ImpGroup --> Implementer["implementer + build-* skill"]
    ImpGroup --> Tester["test-engineer + build-test"]
    DocGroup --> DocWriter["doc-writer + docs-write"]
    ReviewGroup --> SelfReview["code-reviewer + review-local"]
    ReviewGroup --> SecReview["security-reviewer + audit-repo (when sensitive)"]
    ReviewGroup --> Browser["validate-browser (when UI)"]
```
