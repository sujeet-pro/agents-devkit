# Code Review Comment Template

Every non-trivial review comment **must** follow this canonical format. The goal is that the PR author can immediately answer all of these just by reading the comment:

- What is wrong?
- When does it fail?
- What happens today?
- What should happen instead?
- Why is it worth fixing now?
- What is the likely fix?

---

## Canonical Format

````md
[<PRIORITY>][<PRINCIPLE>] <Short, specific title>

**Summary**
- Confidence: <score>/100
- Agent: devkit (skill plugin tool)
- Principle violated: <principle>

**Issue**
<What is wrong, in which code path, and under what condition.>

**Where it fails**
- **Case 1:** <scenario>
  - Current behavior: <actual>
  - Expected behavior: <expected>
- **Case 2:** <scenario>
  - Current behavior: <actual>
  - Expected behavior: <expected>

**Why it matters**
<Impact in practical terms.>

**Suggested fix**
<Concrete recommendation.>

```<lang>
<code snippet>
```

**Suggested tests**
- <test>
- <test>
````

---

## Priority Labels

Use exactly one of these labels:

| Priority | When to use |
|---|---|
| `Blocker` | Must be fixed before merge — correctness, security, or data loss risk |
| `Critical` | Should be fixed before merge — significant reliability or performance concern |
| `Should Have` | Improves quality materially — maintainability, consistency, or moderate risk |
| `May Have` | Nice to have — minor improvement, style, or future-proofing |
| `Nitpick` | Cosmetic or stylistic preference — safe to ignore |
| `Question` | Confidence is lower — asking for author context without overstating the issue |

## Principle Labels

Use one or more:

`Correctness` · `Reliability` · `Security` · `Performance` · `Maintainability` · `Consistency` · `Testability` · `Observability` · `Accessibility` · `Documentation`

---

## Writing Rules for "Where it fails"

- Include **2–3 representative cases**, not every possible case.
- Prefer **real inputs / states / flows** over generic wording.
- Show **current vs expected** behavior explicitly for each case.
- Include an **edge case** when the bug is conditional or non-obvious.
- Avoid vague phrasing like "this may break in some cases".

A good case looks like this:

```md
- **Case 1:** New users without a profile
  - Current behavior: `user.profile.id` throws at runtime
  - Expected behavior: return a validation error or handle missing profile safely
```

Not this:

```md
- This might fail for some users
```

---

## Title Rules

Make the title describe the actual problem, not just the area.

**Prefer:**
- `Potential null dereference when accessing user.profile.id`
- `N+1 query pattern in order list endpoint`
- `Missing authorization check for admin-only action`

**Avoid:**
- `Bug in profile code`
- `Performance issue`
- `Needs refactor`

---

## Section Guidance

### Issue
- 1–3 sentences describing the exact problem in the current code path.
- Call out the condition or trigger that makes the issue happen.
- Reference the specific file and line range.

### Where it fails
- 2–3 concrete scenarios with current vs expected behavior.
- Use real-world language: name the user type, the API call, the data state.
- An edge case is required when the bug is conditional or timing-dependent.

### Why it matters
- 1–2 sentences on impact: user-facing bug, silent data corruption, retry storm, security gap, maintainability risk, etc.
- Avoid generic "this could be a problem" — state the actual consequence.

### Suggested fix
- 1–2 sentences describing the recommended approach and why it addresses the root cause.
- Include a minimal code snippet in the appropriate language.
- Do not over-prescribe — the author owns the implementation.

### Suggested tests
- 2–3 test cases that cover the scenarios described in "Where it fails".
- Phrase as behavior: "returns error when profile is missing", not "add test for null check".

---

## Adapting the Template by Priority

### Blocker / Critical
Use the full template with all sections. These comments justify the detail.

### Should Have / May Have
The full template is recommended. You may abbreviate "Where it fails" to 1–2 cases if the issue is straightforward.

### Nitpick
Use a shortened form — title, a 1–2 sentence issue description, and a suggested fix. Skip "Where it fails" and "Suggested tests" unless they add real clarity.

```md
[Nitpick][Maintainability] Unused import `lodash/merge`

**Issue**
`lodash/merge` is imported but not used after the refactor in this PR.

**Suggested fix**
Remove the import.
```

### Question
Use the title and a 1–3 sentence description of what you're asking about. Do not include a suggested fix unless you have a concrete recommendation.

```md
[Question][Correctness] Is the retry count intentionally unbounded here?

**Issue**
The retry loop at `src/client.ts:42` has no max-attempts guard. If this is intentional (e.g., the upstream guarantees eventual success), it would help to add a comment. Otherwise, consider adding a cap.
```

---

## Examples

### Example 1 — Correctness Issue

````md
[Blocker][Correctness] Potential null dereference when accessing `user.profile.id`

**Summary**
- Confidence: 97/100
- Agent: devkit (skill plugin tool)
- Principle violated: Correctness, Reliability

**Issue**
The code reads `user.profile.id` before verifying that `user.profile` exists. This path is reachable for users created through the lightweight signup flow.

**Where it fails**
- **Case 1:** Newly created user without a profile row
  - Current behavior: request throws when evaluating `user.profile.id`
  - Expected behavior: return a validation error or short-circuit safely
- **Case 2:** Backfilled legacy user with partial data
  - Current behavior: runtime exception in the request path
  - Expected behavior: handle missing profile explicitly and avoid a 500
- **Case 3:** Test fixtures that omit profile setup
  - Current behavior: tests may pass accidentally if this branch is not exercised
  - Expected behavior: missing profile should be handled consistently in all environments

**Why it matters**
User-facing correctness issue that produces a 500 for valid request flows. Behavior depends on data shape rather than explicit validation.

**Suggested fix**
Guard `user.profile` before dereferencing it, and fail with a controlled error if the profile is required.

```ts
if (!user.profile) {
  throw new BadRequestError("profile is required");
}
const profileId = user.profile.id;
```

**Suggested tests**
- returns a controlled error when `profile` is missing
- succeeds when `profile.id` is present
````

### Example 2 — Performance Issue

````md
[Should Have][Performance] N+1 query pattern in order list endpoint

**Summary**
- Confidence: 91/100
- Agent: devkit (skill plugin tool)
- Principle violated: Performance

**Issue**
The endpoint fetches orders first and then loads customer data inside a loop, resulting in one additional query per order.

**Where it fails**
- **Case 1:** Small result set (5 orders)
  - Current behavior: 6 queries executed
  - Expected behavior: related data fetched in a single batched query
- **Case 2:** Larger result set (100 orders)
  - Current behavior: 101 queries, increasing latency and DB load
  - Expected behavior: query count remains stable as order count grows
- **Case 3:** High-traffic tenants
  - Current behavior: amplifies database pressure under concurrent load
  - Expected behavior: endpoint scales without per-row lookups

**Why it matters**
Turns a reasonable endpoint into a latency hotspot as data volume grows. Not obvious in local testing, costly in production.

**Suggested fix**
Fetch the related customer data eagerly or batch it rather than querying inside the loop.

```ts
const orders = await db.order.findMany({
  where: { tenantId },
  include: { customer: true },
});
```

**Suggested tests**
- verifies query count does not grow linearly with result size
- validates response shape remains unchanged after batching
````

### Example 3 — Maintainability Issue

````md
[Should Have][Maintainability] Pricing rules duplicated across checkout paths

**Summary**
- Confidence: 88/100
- Agent: devkit (skill plugin tool)
- Principle violated: Maintainability, Consistency

**Issue**
Tax and discount calculation logic is implemented in both `checkout/cart.ts` and `checkout/retry.ts` with slightly different conditions, creating two sources of truth for the same business rule.

**Where it fails**
- **Case 1:** Future change to discount policy
  - Current behavior: one path may be updated while the other is missed
  - Expected behavior: pricing rules defined once and reused
- **Case 2:** Retry flow vs first-time checkout
  - Current behavior: same cart can produce different totals depending on code path
  - Expected behavior: totals consistent across entry points

**Why it matters**
Creates a realistic risk of pricing inconsistencies in production. Business rules are safer when centralized.

**Suggested fix**
Extract pricing into a shared function and have both paths call it.

```ts
function calculateFinalPrice(input: PricingInput): Money {
  const discounted = applyDiscounts(input.basePrice, input.discounts);
  return applyTax(discounted, input.taxRegion);
}
```

**Suggested tests**
- same cart produces the same total in checkout and retry paths
- tax/discount rule changes covered through shared logic tests
````
