# Principal Engineer Lens

A questioning framework applied before committing to significant work. Ask yourself these questions, then present findings concisely to the user.

## When to Apply

- Complexity >= Medium
- Architectural changes (new modules, changed boundaries, new dependencies)
- New abstractions (interfaces, base classes, shared utilities)
- Significant effort (>2 hours estimated work)

## The Five Questions

1. **"Do we need this?"** — Is the problem real? Is it already solved by existing code, a library, or an established pattern in this codebase?

2. **"What's the simplest version?"** — What is the minimum viable approach that solves the actual problem, not the imagined future problem?

3. **"What are the alternatives?"** — Are there 2-3 other ways to achieve this? What are their trade-offs in effort, risk, and maintenance?

4. **"What are the maintenance costs?"** — What does this add to the ongoing burden? New dependencies, complexity, testing surface, deployment considerations?

5. **"Will this make sense in 6 months?"** — Will someone reading this code, doc, or decision understand why it was done without asking the author?

## Presenting Findings

Use this format when surfacing PE findings to the user:

```
### Principal Engineer Check

**Need**: [Yes — clearly needed / Maybe — consider alternative / Questionable — here's why]
**Simplest version**: [description of minimum viable approach]
**Trade-off**: [key trade-off of recommended vs simple approach]
**Maintenance cost**: [Low/Medium/High — with one-line justification]
```

Keep it to 4 lines. If the answer to all five questions is straightforward, collapse to a single line: "PE check: clearly needed, simple approach, low maintenance."

## Examples

### Example 1: Unnecessary new layer

User asks for a caching layer for API responses. PE check reveals the database already has query caching enabled and response times are under 50ms. Redirect to configuring the existing database cache TTL instead of building a new caching layer.

**Outcome**: Saved a new dependency, a new failure mode, and cache invalidation complexity.

### Example 2: Premature abstraction

User asks to build a plugin system for three notification channels (email, Slack, webhook). PE check finds only email is used today, Slack is "planned," and webhook is speculative. Recommend implementing email directly with a clean interface, making it straightforward to extract a plugin system later if a second channel materializes.

**Outcome**: Shipped in 1 day instead of 5. The plugin system was never needed.

### Example 3: Right-sized solution

User asks to migrate from REST to GraphQL for a 40-endpoint API. PE check identifies that the real pain is 3 endpoints with over-fetching problems. Recommend adding sparse fieldsets (JSON:API style) to those 3 endpoints instead of a full migration.

**Outcome**: 90% of the performance benefit at 10% of the effort and zero ecosystem disruption.
