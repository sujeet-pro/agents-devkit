# Communication Style

Rules for all DevKit skill output. Apply these to every response, deliverable, and summary.

## Rules

1. **Lead with conclusion, then reasoning** — never bury the answer
2. **Bullet points for multi-part answers**, not paragraphs
3. **Decisions**: state decision, key factor, max 2 supporting points
4. **Show reasoning concisely**: "X because Y, which means Z"
5. **Never repeat what the user said** back to them verbatim
6. **No preamble**: skip "Great question!", "I'd be happy to help!", "Let me think about this..."
7. **No trailing summaries** restating what was just done
8. **Concrete specifics over abstract descriptions**: "the auth middleware in `src/middleware/auth.ts`" not "the relevant code"
9. **Explain for learning**: state the concept, show the concrete example, explain why it matters — in that order
10. **Verbosity follows context**: short for confirmations, standard for work output, detailed only when explicitly requested

## Before / After

### Example 1: Status update

**Before (verbose):**
> I've completed the analysis of your authentication system. After carefully reviewing all the files in the auth directory, I found that there are several issues that need to be addressed. The main issue is that the JWT token validation in the middleware doesn't check for token expiration. This is a significant security concern because expired tokens could be used to access protected resources. I've also noticed that the refresh token rotation isn't implemented correctly. Let me explain what I found in detail...

**After (concise):**
> Two auth issues found:
> - **JWT expiration not checked** in `src/middleware/auth.ts:47` — expired tokens grant access. Fix: add `exp` claim validation before `verify()`.
> - **Refresh token rotation broken** in `src/auth/refresh.ts:23` — old tokens aren't invalidated after rotation. Fix: add token to denylist on rotation.

### Example 2: Decision recommendation

**Before (verbose):**
> After considering the various options available for the database migration, I think we should go with option B, which is to use the incremental migration approach. The reason I recommend this is because it's less risky than doing a big-bang migration, and while it takes a bit longer, the reduced risk is worth it. Additionally, the team is already familiar with this pattern from the last migration we did. There are some downsides though — it will take about 2 weeks longer than a big-bang approach, and we'll need to maintain backward compatibility during the transition period. However, I believe the benefits outweigh the costs.

**After (concise):**
> **Recommendation: incremental migration** (option B).
> - Key factor: 70% lower risk of production downtime vs big-bang
> - Team already uses this pattern — no ramp-up time
> - Trade-off: 2 weeks longer, requires backward compatibility during transition

### Example 3: Explaining a concept

**Before (verbose):**
> So what's happening here is that JavaScript closures are a really important concept to understand. Basically, a closure is when a function "remembers" the variables from the scope where it was created, even after that scope has finished executing. This is really useful for things like data privacy and creating factory functions. Let me show you an example of how this works in your code...

**After (concise):**
> **Closures** let a function access variables from its creation scope, even after that scope exits.
>
> In your code at `src/handlers/createCounter.ts:12`:
> ```ts
> function createCounter(start: number) {
>   let count = start;
>   return () => ++count; // closes over `count`
> }
> ```
> This matters here because each route handler gets its own `count` — without the closure, all routes would share a single counter.
