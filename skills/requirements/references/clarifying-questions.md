# `requirements` — clarifying questions (the 12)

Ask in order, one at a time. Skip any whose answer is obvious from `context.md`. Under `--auto`, fill the conservative default and ask the user to confirm en bloc.

1. **What is the outcome?** — _How to pick:_ One sentence. "Users can X" or "the system Y when Z". Reject vague verbs like "improve", "enhance".
2. **Who are the users?** — _How to pick:_ Internal (eng, ops, support, finance) or external (customer, prospect, anonymous). Multiple types is fine; list all.
3. **When does this trigger?** — _How to pick:_ User action, scheduled job, system event, response to another action. Be specific.
4. **What does the system do, step by step?** — _How to pick:_ 3-7 bullets. If you have more, you have multiple features (split).
5. **What flows in (inputs) and out (outputs)?** — _How to pick:_ Data shape, format, units, validation rules.
6. **How do we know it works (success measures)?** — _How to pick:_ Testable. "Button visible in Chrome/Safari/Firefox at 360/768/1280" is testable. "Looks good" is not.
7. **What MUST be there for v1 (P0)?** — _How to pick:_ 3-7 items max. If more, the scope is too big — split.
8. **What would be nice but not blocking (P1+)?** — _How to pick:_ Anything that can ship later without blocking the user benefit.
9. **What are we explicitly NOT doing (non-goals)?** — _How to pick:_ Critical. Anything ambiguous re: scope. "Server-side export — out of scope" prevents an entire wasted day.
10. **What edge cases?** — _How to pick:_ empty / max / overflow / network-fail / unauthorized / concurrent / partial-data / cancelled.
11. **What constraints?** — _How to pick:_ tech (framework, perf), business (cost, timeline), regulatory (GDPR, accessibility WCAG 2.2 AA), platform (browser support, mobile).
12. **What is still open?** — _How to pick:_ Anything you cannot answer now. Will be re-surfaced in `scoping`.
