# `context-gather` — examples

## Example 1 — Jira ticket alone

**Input:** `https://acme.atlassian.net/browse/CHK-1234`

**Output (`context.md`):**

```markdown
## Sources
| URL | Type | Status |
| --- | --- | --- |
| https://acme.atlassian.net/browse/CHK-1234 | Jira | OK |

## Summary per source

### CHK-1234 — Checkout 5xx (Jira; updated 2026-05-03)
- Author: alice@acme.com
- Status: In Progress
- Priority: P1
- Summary (paraphrased): customers report intermittent 500s on /api/v1/cart/checkout since 13:00 UTC.
- Excerpts:
  - "rate ~3% since 13:05" (≤15w)
- Action items detected:
  - alice asked: "can someone check rollback risk?"

## Action items detected (consolidated)
- alice (Jira): can someone check rollback risk?

## Open questions
- No deploy SHA; consider /adk-investigate:investigate-deploy.
```

## Example 2 — Slack + Jira + GitHub PR (cross-referenced)

**Input:** Three URLs (one Jira, one Slack, one GitHub PR), all describing the same incident.

**Output:** Each summarized separately; `Cross-references` section explicitly links them. Action items consolidated. See `references/output-format.md` for the full shape.

## Example 3 — access-denied GDoc

**Input:** A GDoc URL the operator can't open.

**Output:**

```markdown
## Sources
| URL | Type | Status |
| --- | --- | --- |
| https://docs.google.com/document/d/abc... | GDoc | ACCESS DENIED |

## Summary per source

### (ACCESS DENIED) GDoc
- Source: https://docs.google.com/document/d/abc...
- Status: cannot read (workspace Google Drive connector returned 403).
- Suggested fix: open the doc in your browser to confirm access; if you have access there but not here, ask your Claude admin about the Google Drive connector scope.

## Open questions
- This source was inaccessible; analysis is incomplete.
```

## Example 4 — bare GitHub issue URL

**Input:** `https://github.com/acme/search-api/issues/142`

**Output:**

```markdown
## Sources
| URL | Type | Status |
| --- | --- | --- |
| https://github.com/acme/search-api/issues/142 | GitHub Issue | OK |

## Summary per source

### #142 — Search returns stale results after deploy (GitHub Issue; opened 2026-05-02)
- Author: bob@acme.com
- State: open
- Labels: bug, P2
- Summary (paraphrased): search results show stale data after deploys; cache invalidation seems off.
- Top comments (3):
  - charlie: "I see this too; cache TTL is 1h."
  - dave: "we should invalidate on deploy events."
  - bob: "I'll draft a fix tomorrow."
- Action items detected:
  - bob owns: "draft fix"
```

## Example 5 — markdown-link extraction

**Input:** `Check [this Confluence page](https://acme.atlassian.net/wiki/spaces/ENG/pages/12345/Auth+Architecture) and the [Jira ticket](https://acme.atlassian.net/browse/AUTH-99)`

**Output:** Two sources extracted from the markdown links. Same processing as bare URLs.
