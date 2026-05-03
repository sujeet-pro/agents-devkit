# `review-pr` — dimension passes

The per-dimension checklists used by Phase 3. Each pass is its own subagent invocation (parallel, max 4 at once).

## Selecting which dimensions to run

By default, all six run in parallel. Skip a dimension when:

| Dimension | Skip when |
| --- | --- |
| correctness | rename / move / config-only diff |
| security | diff doesn't touch a boundary, auth path, data store, or dependency manifest |
| performance | non-hot-path / one-shot scripts (use repo's perf budget signals; see `code-perf` for finding hot paths) |
| tests | diff is test-only or pure refactor with green tests |
| docs | internal refactor; no public surface change; no behavior change |
| style | repo's lint config is silent on the rule |

The user can subset via `--dimensions security,perf`.

## Correctness pass (code-reviewer agent)

| Check | Triggers | Severity floor |
| --- | --- | --- |
| Logic errors | New conditional with off-by-one risk; inverted boolean; wrong operator (`==` vs `===` in JS / `=` vs `==` in Go) | Should-Have |
| Branch coverage | New `if` / `switch` / `match` arm with no test | Should-Have |
| Error handling | Caught exception silently swallowed; error wrapped without context; new error path with no log | Critical |
| Nullability | New return without null-check on a known-nullable contract; deref of an Optional / Maybe / pointer | Critical |
| Race conditions | Read-modify-write outside a lock on shared state; `go func() { ... shared ... }()` without sync | Critical |
| Resource leaks | Open file / socket / connection / context with no `defer` / `try-with` / `using` | Should-Have |
| Off-by-one | Loop termination, slice bounds, range conversions | Should-Have (Blocker if security implication) |
| Type safety | New `any` / `interface{}` / `unknown` where the actual type is knowable | May-Have |
| Concurrency | Goroutine leak; channel never closed; select without `default` and no timeout | Should-Have |
| Behavior preservation (refactor) | Refactor PR that changes observable behavior | Critical |

## Security pass (security-reviewer agent)

Threat surfaces walked, in roughly this order (cheap-and-common first):

| Surface | What to grep for | Notes |
| --- | --- | --- |
| Secrets | `AKIA[0-9A-Z]{16}`, `ghp_[A-Za-z0-9]{36}`, `sk-[A-Za-z0-9]{40}`, `glpat-[A-Za-z0-9_-]{20}`, BEGIN PRIVATE KEY | Name the type / file / line; NEVER quote the bytes |
| SQL injection | string concat into `db.query()` / `cursor.execute()` / `db.Raw(...)` | Suggest parameterization, not escape |
| Command injection | `exec`, `system`, `subprocess.call(shell=True)`, `os.popen`, backticks in shell scripts | Suggest argv-form, not string-form |
| Path traversal | `..` in user-supplied paths; `os.path.join(user_input, ...)` without normalization | Suggest sandboxing the path |
| Unsafe deserialization | `pickle.loads`, `yaml.load` (not safe_load), `XMLDecoder` without `defusedxml`, `Marshal/Unmarshal` of attacker-controlled data | Suggest the safe variant |
| XSS | `dangerouslySetInnerHTML`, `innerHTML`, `v-html`, template interpolation of user input without escaping | Suggest framework default escaping |
| SSRF | New outbound HTTP to user-supplied URL; URL parser without scheme allow-list | Suggest allow-list |
| CSRF | New POST/PUT/DELETE without CSRF token middleware in a session-cookie auth context | Suggest framework's CSRF middleware |
| Auth bypass | New protected endpoint without the same auth wrapper as siblings; new role check pattern that diverges | Read sibling handlers; flag divergence |
| Broken access control | Resource-by-ID lookup without tenant / owner filter | Suggest the ownership check |
| Insecure crypto | `md5`, `sha1`, `RC4`, `DES`, custom AES mode without IV | Suggest framework default (e.g. `crypto.subtle`, BCrypt for passwords) |
| Hardcoded secrets in env defaults | `default = "sk-..."` in config schema | Block; flag as `secret_in_diff` |
| Logging PII | Logger statement that includes a user object / password field / token | Suggest redaction |
| Dependency CVE | New dep added in `package.json` / `requirements.txt` / `go.mod` / `Gemfile` | Run `npm audit` / `pip-audit` / `govulncheck` if quick; otherwise flag as `Question` |
| Build supply chain | New GitHub Action without SHA pin; `curl | sh` in a CI script | Suggest pinning + checksum |

See the `security-reviewer` agent for the full threat-model checklist.

## Performance pass (code-reviewer agent)

| Check | Triggers | Severity floor |
| --- | --- | --- |
| n+1 queries | Loop over rows that calls a per-row `Find` / `SELECT` / `Get` | Critical (Blocker if observed regression) |
| Unbounded loops | `while True` / `for { }` / `loop {}` without bounded exit on user input | Critical |
| Allocation in tight loop | `make([]T, ...)` / `new T()` / `[]` inside a hot loop | Should-Have |
| Sync I/O on hot path | `requests.get` / synchronous file read / fsync inside a request handler | Should-Have |
| Missing index | New query pattern (e.g. `WHERE created_at > ?`) on a column with no index | Should-Have |
| Cache-busting | Per-request work that should be per-process (e.g. `regexp.MustCompile` inside a handler) | Should-Have |
| Inefficient algorithm | Obvious O(n²) where O(n log n) is straightforward (sort then merge) | May-Have |
| Memory pressure | Large allocation that could be streamed (e.g. `ReadAll` on a multi-GB file) | Should-Have |
| Missing pagination | New endpoint that returns an unbounded list | Should-Have |

Cross-reference with `~/.config/adk/datadog.md.slo_thresholds` if available — if a finding affects a path with a documented SLO, bump severity by one tier.

## Tests pass (code-reviewer agent)

| Check | Triggers | Severity floor |
| --- | --- | --- |
| New behavior, no test | New public function / endpoint / branch with no test in the diff | Critical (Blocker if critical path: auth, payment, data write) |
| Missing edge case | New function that handles a list, but no test for empty / single / max | Should-Have |
| Missing error path | New error type / branch with no test asserting the error | Should-Have |
| Disabled test | `t.Skip` / `it.skip` / `@Disabled` added in this diff | Critical (always — explain why) |
| Removed regression test | Test deleted that was covering a known bug | Blocker |
| Vacuous test | Test that doesn't assert anything meaningful (e.g. `assert(fn() != null)` when `fn()` always returns non-null) | Should-Have |
| SUT mocked | Test that mocks the function under test instead of its dependencies | Critical |
| Test isolation | Test that depends on test order or shared state without cleanup | Should-Have |
| Flaky test introduced | Test that uses `time.Now()`, real network, real DB without containerization | Should-Have |
| Coverage drop | New file with 0% coverage when the rest of the package is >80% | Should-Have |

## Docs pass (code-reviewer agent)

| Check | Triggers | Severity floor |
| --- | --- | --- |
| Public API undocumented | New exported function / class / endpoint / CLI flag with no docstring | Critical |
| Behavior change, no CHANGELOG | Diff alters a documented behavior; no CHANGELOG.md entry | Should-Have |
| README out of date | README references a flag / command / file that the diff removed | Should-Have |
| Runbook out of date | runbook step that the diff invalidates | Should-Have |
| Missing migration note | DB migration / schema change without a migration note in the PR body | Should-Have |
| ADR / RFC missing | Architectural change with no ADR (per repo's ADR convention if any) | May-Have |
| Comment / code mismatch | Code says one thing; the function comment claims another | Should-Have |
| Stale link | New link to a doc that the diff renamed/removed | May-Have |
| Public-API breaking change | Removal / signature change of a documented public API; no `@deprecated` shim and no version bump in the manifest | Critical |

## Style pass (code-reviewer agent — only if lint covers it)

| Check | Triggers | Severity floor |
| --- | --- | --- |
| Lint rule the repo runs but lint missed | A pattern matching a custom rule the repo ships in its lint config | May-Have |
| File-level convention divergence | snake_case in a camelCase file; tabs in a spaces file | Nitpick |
| Unused import / variable | Lint should catch this; if it doesn't, raise as Nitpick | Nitpick |
| Naming inconsistency | New function named `getUser` in a file where every other function is `fetch_user` | Nitpick |
| Comment style divergence | `// TODO:` vs `// FIXME:` vs `// NOTE:` mixing within a file | Nitpick |

**Important:** Style findings are appropriate ONLY when they violate a tool the repo already runs. If `eslint` / `golangci-lint` / `flake8` is silent on the rule, do not file the finding. Add the rule to the lint config (different PR) or let it go.

## Per-dimension parallelism

The dispatcher (in `agents/dispatcher.md`) spawns at most 4 parallel subagents at once. The default plan is:

```
Group 1 (in parallel): correctness, security, performance, tests
Group 2 (after Group 1): docs, style
```

If the user passes `--dimensions security,perf`, only those two run.

## De-noise (after all passes)

Before writing `raw-findings.md`:

1. **Same root cause across multiple lines.** Collapse to 1 finding + `references` to the others. (E.g. "missing role check" raised on 4 endpoints in the same handler file → 1 Blocker with 4 references.)
2. **Same dimension flagging the same line.** Pick the highest-severity wording.
3. **Conflicting findings across dimensions.** Surface both, mark as `discuss-with-author`. (Rare: e.g. "performance says cache this; security says don't cache user-specific data".)
