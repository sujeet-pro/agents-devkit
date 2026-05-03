# `code-bugfix` — root-cause template

The `## Root cause` paragraph in `plan.md` is the most-read artifact of the bug fix. It is read by:

- The reviewer at PR time.
- Future-you, six months from now, reading the commit history.
- Other engineers triaging similar bugs.

Get it right.

## Shape

ONE sentence. Falsifiable. Specific.

```
The <component> <verb> <wrong thing> because <mechanism> when <condition>.
```

## Examples (good — one sentence each)

- `The lastNDays helper returns 6 days because 'from' uses 'subtract(7, day)' but 'to' uses 'subtract(1, day)' which excludes today; the user expectation is that "last 7 days" includes today.`
- `Cart.discount type was changed from 'Discount | null' to 'Discount | undefined' in commit a1b2c3, but the JSON parser still produces null for older clients, so 'discount?.amount' returns null.amount → TypeError.`
- `The signup pipeline catches and silently swallows enqueue errors (with a "fire and forget" comment), so transient queue outages produce a created user without a welcome email and no log line.`
- `The cache invalidation runs after 'db.commit()' returns but before read-replica replication acks; concurrent readers re-populate the cache from a stale read in the gap.`
- `useEffect runs the data-fetch on every render because the dependency array includes 'options' (an object literal), and React identity-checks the array; the literal is fresh on every render.`

## Anti-examples (bad)

| Wrong shape | Why it's wrong |
| --- | --- |
| `We should validate inputs more thoroughly.` | Not falsifiable. Doesn't name the cause. Reads as a generic recommendation. |
| `There's a race condition somewhere.` | Vague. "Somewhere" isn't a cause. |
| `The function returns the wrong value.` | Restates the symptom; doesn't name the mechanism. |
| `Bug.` | (Yes, agents have written this.) |
| `Looks like maybe the cache isn't being invalidated correctly.` | "Looks like maybe" — diagnose with evidence or stop and ask. |
| `Probably a null check issue.` | Generic. Specific cause? Name it. |
| `The code is wrong.` | Not actionable. |
| `It's intermittent so it's probably timing.` | Speculation. Either reproduce reliably or document the flake rate + investigate. |

## Required elements

| Element | Why |
| --- | --- |
| The component (file / function / endpoint / module) | Anchors the diagnosis to a place. |
| The verb (does X, returns Y, throws Z) | Says what the wrong thing is. |
| The wrong thing | Concrete output / behavior. |
| The mechanism | Why the code does the wrong thing. |
| The condition (when) | When the bug fires. |

## When to use 2 sentences instead of 1

The two-sentence allowance is rare:

1. **Context required.** "X was working until commit Y changed Z. Now, X does W when condition C, because the change in Y assumed Z but other code still relies on the old behavior."
2. **The cause has 2 dimensions.** "X uses === instead of ==, AND a recent type change made the values structurally different — together they cause the bug."

But still: short, falsifiable, specific.

## When the cause is upstream

If the cause is in a third-party library, an external service, or another repo:

```
## Root cause
Upstream: <library/service> has known bug <issue link / version> where <mechanism>.
Local impact: when our code calls <function> with <input>, the library <wrong behavior>.
Workaround: <one-sentence local mitigation pending upstream fix>.
```

This is the ONE place the root cause may run to 3 sentences. Otherwise: one.

## Confidence

State confidence at the end of the diagnosis section (not the `## Root cause` line itself):

```
## Root cause
<one sentence>

Confidence: high — verified by reading the commit history (commit a1b2c3
introduced the type change), the failing test reproduces 100% of the time,
and reverting the typed change makes the test pass.
```

| Level | Meaning |
| --- | --- |
| **high** | Verified by reading code + observing transition (red→green on revert or on patch). |
| **medium** | Hypothesis fits the evidence but not all alternatives are ruled out. |
| **low** | Best guess; needs more evidence. **STOP and surface** before patching. |
