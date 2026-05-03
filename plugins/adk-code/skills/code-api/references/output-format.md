# `code-api` — output format

## Per-turn status

```
[adk-code:code-api] task=<slug> phase=<0|1|2|3|4|5|6|7> use-cases=<captured> candidates=<sketched> picked=<one> artifact=<produced> deprecation=<n/a|drafted>
```

## `.temp/task-<slug>/use-cases.md` (Phase 2)

```markdown
# Use cases — <slug>

## Contract being designed
<one sentence: REST endpoint set / RPC contract / SDK exports / CLI flags / types>

## Use case 1: <short label>
- Caller: <who>
- Input: <what state / args>
- Output: <what shape / value>
- Errors: <what can go wrong; what response>

## Use case 2: <short label>
…

## Use case 3: <short label>
…

## Out of scope (deliberate)
- <bullet> — <reason>
```

## `.temp/task-<slug>/candidates.md` (Phase 3)

```markdown
# Candidate contracts — <slug>

## Candidate A — <one-line summary>
### Shape
<URL pattern / method signature / type def / flag list — concrete>

### Pros
- <bullet>
- <bullet>

### Cons
- <bullet>
- <bullet>

### Use-case fit
- Use case 1: <fits / partial / poor> — <one line>
- Use case 2: <…>
- Use case 3: <…>

## Candidate B — <one-line summary>
…

## Candidate C — <one-line summary>
…
```

## `.temp/task-<slug>/design.md` (Phase 4)

```markdown
# Design — <slug>

## Picked
Candidate <A|B|C>: <one-line summary>

## Rationale
<1-2 paragraphs: why this candidate, what trade-offs we accept>

## Hyrum's Law caveats
### Guaranteed (the contract)
- <bullet>
- <bullet>

### Observable but unsupported
- <bullet> — <one-line caveat>
- <bullet> — <one-line caveat>

## Validation strategy
- Boundary validation: <what gets validated at the entry point>
- Internal trust: <what we assume internal callers do correctly>

## Versioning
- Version: <e.g. v1, v2, semver 1.0.0>
- Breaking-change policy: <see deprecation-plan.md if any>

## Alternatives considered (rejected)
- Candidate A: <one-line reason>
- Candidate C: <one-line reason>
```

## `.temp/task-<slug>/contract.<ext>` (Phase 5)

The actual artifact. Format depends on type:

- **REST**: OpenAPI YAML fragment.
- **RPC**: `.proto` file.
- **SDK**: `.d.ts` or `.ts` with type defs.
- **CLI**: `usage.txt` or commander spec.

Saved to either:
1. The repo's documented contract location (working tree edit).
2. `.temp/task-<slug>/contract.<ext>` if no documented location exists; the report recommends where to land it.

## `.temp/task-<slug>/deprecation-plan.md` (Phase 6, if `--breaking`)

```markdown
# Deprecation plan — <slug>

## Old contract
<what's going away; cite file/version>

## Migration path
- Step 1: <…>
- Step 2: <…>
- Step 3: <…>

## Deprecation window
<how long the old contract will continue to work; recommended: 1 major + 90 days>

## Warning emission
- <SDK: log warning on call to old API>
- <REST: include `Deprecation: true` header per RFC 8594>
- <CLI: emit deprecation message to stderr>

## Removal target
<version / date the old contract goes away>

## Communication plan
- Release notes: <where>
- Slack: <#channel + message>
- Partner email: <if applicable>
```

## `.temp/task-<slug>/report.md` (Phase 7)

```markdown
# code-api report — <slug>

## Contract
- Type: REST / RPC / SDK / CLI / types
- Status: NEW / EVOLUTION
- Repo: <owner/repo>

## Use cases
1. <one-line>
2. <one-line>
3. <one-line>

## Candidates considered
- A: <one-line>
- B: <one-line>
- C: <one-line>

## Picked
Candidate <X>. Rationale: <one paragraph; verbatim from design.md>.

## Hyrum's Law caveats
| Aspect | Status |
| --- | --- |
| <field/method/etc.> | guaranteed |
| <other> | observable but unsupported |

## Contract artifact
- File: `<path>` (in working tree) OR `.temp/task-<slug>/contract.<ext>` (under .temp; recommendation in report).
- Lines added: <N>

## Versioning
- Version: <…>
- Semver implications: <patch / minor / major>

## Deprecation plan (if --breaking)
- See `deprecation-plan.md`.
- Window: <…>
- Removal target: <…>

## Validation evidence
| Check | Status |
| --- | --- |
| Use cases captured | yes |
| Candidates sketched | <count> |
| Artifact produced | yes / pending |
| Deprecation plan (if breaking) | <yes / n/a> |

## Decisions
| Phase | Question | Picked | Rationale |
| --- | --- | --- | --- |
| 4 | candidate selection | B | matches use case 1 best |

## Residual risk / follow-ups
- <bullet>
- Implementation behind the contract — spawn `/adk-code:code-write`.
- Usage docs — spawn `/adk-docs:docs-write`.

## NOT done (deliberate)
- <bullet>

## Next steps
1. (optional) `/adk-review:review-code-changes` if the artifact is a working-tree change.
2. (optional) `/adk-docs:docs-publish-confluence` if the design needs a published RFC.
3. `/adk-code:code-write` for the implementation behind the contract.

## Artifact index
.temp/task-<slug>/
  prompt.txt
  use-cases.md
  candidates.md
  design.md
  contract.<ext>          (or in working tree)
  deprecation-plan.md     (if --breaking)
  report.md
```
