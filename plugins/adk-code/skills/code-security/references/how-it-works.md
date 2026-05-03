# `code-security` — how it works (diagrams)

## Phase flow

```mermaid
flowchart TD
    Prompt["User prompt: vulnerability or hardening goal"] --> P0["Phase 0: prompt expand + CVE lookup"]
    P0 --> P1["Phase 1: preflight (commands + tests green)"]
    P1 --> P2["Phase 2: threat model (5 lines)"]
    P2 --> Approve2{"--auto?"}
    Approve2 -- no --> Gate2["Approval: confirm threat model"]
    Approve2 -- yes --> P3
    Gate2 --> P3["Phase 3: identify boundary (input + output)"]
    P3 --> P4["Phase 4: REPRODUCE exploit (failing security test)"]
    P4 --> Red{"Exploit test FAILS as expected?"}
    Red -- no --> Stop1["STOP: bug not reproducing — investigate"]
    Red -- yes --> P5["Phase 5: APPLY mitigation at boundary (implementer)"]
    P5 --> Green{"Exploit test PASSES now?"}
    Green -- no --> Wrong{"2nd wrong mitigation?"}
    Wrong -- no --> P5
    Wrong -- yes --> Stop2["STOP: wrong boundary or wrong mitigation"]
    Green -- yes --> P6["Phase 6: VALIDATE (full suite + typecheck + lint)"]
    P6 --> AllGreen{"All green?"}
    AllGreen -- no --> Stop3["STOP: regression detected"]
    AllGreen -- yes --> P7["Phase 7: security-reviewer agent over diff"]
    P7 --> Block{"Blocker findings?"}
    Block -- yes --> P5
    Block -- no --> P8["Phase 8: REPORT"]
    P8 --> Done["Hand-off: offer-depth question (sanitized)"]
```

## Threat-model decision tree

```mermaid
flowchart TD
    Start["Have a vulnerability or hardening request"] --> Q1{"Untrusted input source?"}
    Q1 -- "HTTP request body / params / headers" --> HTTP["HTTP boundary"]
    Q1 -- "file content (parsed)" --> File["File-parser boundary"]
    Q1 -- "deserialization (JSON/YAML/pickle/etc.)" --> Deser["Deserializer boundary"]
    Q1 -- "env var / config" --> Env["Env-var reader boundary"]
    Q1 -- "IPC / message queue" --> IPC["Message-consumer boundary"]
    HTTP --> Q2{"Privileged action?"}
    File --> Q2
    Deser --> Q2
    Env --> Q2
    IPC --> Q2
    Q2 -- "DB query" --> DB["DB boundary (parameterize / authorize)"]
    Q2 -- "shell exec" --> Shell["exec boundary (allowlist / no shell injection)"]
    Q2 -- "outbound HTTP" --> Out["outbound boundary (allowlist / SSRF guard)"]
    Q2 -- "filesystem write" --> FS["FS boundary (path canonicalization)"]
    Q2 -- "session issuance" --> Sess["session boundary (auth gate)"]
    DB --> ThreatActor["Identify actor + asset"]
    Shell --> ThreatActor
    Out --> ThreatActor
    FS --> ThreatActor
    Sess --> ThreatActor
    ThreatActor --> Residual["Define residual risk after mitigation"]
    Residual --> Done["5-line threat model written"]
```

## Mitigation-at-boundary protocol (Phase 5)

```mermaid
flowchart LR
    Plan["plan.md (mitigation at boundary)"] --> Impl["implementer subagent"]
    Impl --> Edit["Edit at the input boundary (per boundary.md)"]
    Edit --> Trust["Internal callers TRUST the validated input"]
    Trust --> Test["Re-run exploit test"]
    Test --> Pass{"Test PASSES?"}
    Pass -- yes --> Suite["Run full suite"]
    Pass -- no --> Reconsider["Reconsider boundary or mitigation"]
    Reconsider --> Plan
```

## Defense-in-depth (when it's right vs wrong)

```mermaid
flowchart TD
    Start["Considering 'defense in depth'"] --> Q1{"Is the proposed second layer the SAME check?"}
    Q1 -- yes --> Wrong["BAD: same check repeated; drift inevitable"]
    Q1 -- no --> Q2{"Is the second layer a COMPLEMENTARY defense?"}
    Q2 -- yes --> Q3{"Does it have its own threat model + cost analysis?"}
    Q3 -- yes --> Right["OK: layered defense (e.g. WAF + auth + audit log)"]
    Q3 -- no --> Reconsider["Add the threat model first"]
    Q2 -- no --> Wrong
    Wrong --> Boundary["Use boundary mitigation; remove redundancies"]
    Right --> Document["Document each layer's threat in design"]
```

## Disclosure decision tree

```mermaid
flowchart TD
    Start["Vulnerability fix produced"] --> Q1{"Is the vulnerability already public (e.g. published CVE)?"}
    Q1 -- yes --> Public["Commit message can reference CVE ID"]
    Q1 -- no --> Q2{"Internal-found, undisclosed?"}
    Q2 -- yes --> Coord["Use coordinated disclosure: fix-first, disclose later<br/>Generic commit message until disclosure"]
    Q2 -- no --> Ask["Ask the operator about disclosure timing"]
    Public --> CommitMsg["Generic commit message (still): 'auth fix per CVE-XXXX'"]
    Coord --> CommitMsg
    CommitMsg --> Deploy["Land fix → deploy → then update CVE record per org policy"]
```
