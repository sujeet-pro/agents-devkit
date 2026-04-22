# Examples for `adk-docs-review`

Concrete inputs the skill expects and the shape of what comes back.

## Trigger phrases

- "Review the README before I publish v3"
- "Check the runbook against the current code"
- "Run `adk-docs-review` on docs/onboarding.md"
- "Review this Confluence page: https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345"
- "The migration guide hasn't been touched in a year — see what drifted"

## Sample invocations

```
adk-docs-review docs/README.md
```

Local mode, all-focus, dry-run report.

```
adk-docs-review docs/runbooks/oncall.md --focus accuracy,freshness --source src/oncall/
```

Local mode, narrow focus, explicit source-of-truth.

```
adk-docs-review https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345 --mode confluence
```

Confluence mode, dry-run by default; report shows reconciliation + findings; awaits approval to post.

```
adk-docs-review https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345 --mode confluence --post-mode post --auto
```

Confluence mode, `--auto`: skips approval gates, picks documented defaults (focus=all, reconciliation=validate-then-keep), validates, posts inline + footer comments.

```
adk-docs-review docs/integration-guide.md --repo https://github.com/org/service-a --repo https://github.com/org/service-b
```

Local mode, multi-repo: validates the integration guide against source-of-truth in two external repos.

## Sample output (Confluence mode, dry-run, condensed)

````text
DOC-REVIEW-DRAFT

## Doc Review: System Design — Auth Service
- Target: https://your-org.atlassian.net/wiki/spaces/ENG/pages/12345
- Mode: confluence
- Source-of-truth: services/auth/ (host repo, head=abc123)
- Focus: all
- Reconciliation: validate-then-keep
- Post mode: dry-run

## Verdict
needs-fixes (1 Blocker, 3 Critical, 6 Should Have)

## Existing-comment reconciliation
- Threads inspected: 5
- Kept open (still apply): 2
- Resolved-confirmed: 2
- Resolved-stale (restated): 1
- (other counts: 0)

## Findings

### Blockers
F1 — see card below.

### Critical
F2, F3, F4 — see cards below.

(Should Have, Nitpicks, Questions omitted in this excerpt)

***

### F1 [Blocker][Issue][accuracy] Documented JWT secret env var name no longer exists

Doc location: section "Configuration" → "Required env vars"
Source-of-truth: `services/auth/src/config.ts:18-32` (verified 2026-04-21)
Action: post new inline comment
Anchor text: "JWT_SECRET_KEY"

Why post this comment:
- The env var was renamed in the v3 cutover; any new operator following this doc will fail to boot the service.
- Two existing inline comments mention "Configuration" but neither caught this specific rename.

Exact comment to post (rendered as Markdown on the Confluence page):

    **[Blocker][accuracy] Documented JWT secret env var name no longer exists**

    **Confidence:** 95/100 | **Dimension:** accuracy | **Source-of-truth:** `services/auth/src/config.ts:18-32` (verified 2026-04-21)

    **Issue Explanation:**
    The page lists `JWT_SECRET_KEY` as a required env var. The current source (`services/auth/src/config.ts:18-32`) reads `AUTH_JWT_SECRET` instead. The rename happened in `commit 7f3a91c` two months ago. Any new operator following the doc as-written will see the service boot with a fallback signing key, which is logged as a warning but is otherwise silent - no clear failure mode.

    **Suggested Fix:**
    Replace `JWT_SECRET_KEY` with `AUTH_JWT_SECRET` in the "Required env vars" table. Add a note that the old name was deprecated in v3 and is no longer read at all.

    **Impact:**
    Services boot with a development-grade signing key, breaking SSO and token rotation in any environment where this doc is the primary onboarding source.

Reviewer explanation:
The deployment runbook (page 12348) already references `AUTH_JWT_SECRET` correctly, so this is a localized drift on this page only.

***

(F2, F3, F4 omitted in this excerpt)

## Validation
- Phase 1 (pre-execution): OK
- Phase 2 (mid-flow): OK
- Phase 3 (pre-post): OK (10 findings, 0 duplicates)
- Phase 4: N/A (dry-run)
- Validator log: .temp/notes/doc-review-confluence-12345-validator.md

Need more detail on any finding? Reply with `F<n>` to expand, or `--verbose` for everything.
````

## Sample output (after `--post-mode post` approval, condensed)

```
DOC-POSTED 10 inline + footer

## Postback summary
- Inline comments posted: 10 (IDs: confluence:ic_5012, ...)
- Reconciliation replies posted: 3
- Footer summary comment: YES (confluence:fc_5023)
- Verdict posted: needs-fixes
- Failed to post: none
- Validator log: .temp/notes/doc-review-confluence-12345-validator.md
```
