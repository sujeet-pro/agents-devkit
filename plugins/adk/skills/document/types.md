# document — per-artifact contract

Each artifact: what to **lead with**, a **length cap**, the **must-include** sections, and a suggested local **draft path**. Match the repo's existing conventions where it has them.

| Artifact | Lead with | Cap | Must include | Suggested path |
|---|---|---|---|---|
| Runbook | the symptom | 2 pages | dashboard link, oncall channel, rollback step, escalation contact | `docs/runbooks/<service>.md` |
| ADR | the decision | 1 page | status, context, decision, consequences, alternatives (with why-rejected) | `docs/adr/<NNNN>-<slug>.md` |
| RCA | the impact | 2 pages | timeline, detection, mitigation, root cause, contributing factors, action items (5W) | `docs/rca/<date>-<slug>.md` |
| PR description | the risk | ½ page | summary, test plan, breaking changes, follow-ups | (paste into the PR; draft locally) |
| Commit message | imperative subject | 50-char subject, body wrapped at 72 | the *why* in the body, not the *what* | (draft locally) |
| Changelog entry | one sentence per item | — | grouped per the repo's existing convention (Keep-a-Changelog / semantic-release) | `CHANGELOG.md` section |
| Mermaid diagram | the system shape | 15 nodes | one diagram per concept; split if larger | `docs/diagrams/<slug>.md` |
| README (section) | what it is + first command | — | install, first run, where to go next | `README.md` |
| Migration guide | who must act + by when | 2 pages | before/after, step-by-step, rollback, deadline, owner | `docs/migrations/<slug>.md` |
| API reference | the endpoint/function signature | — | params, returns, errors, one example call per surface | `docs/api/<slug>.md` |
| Experiment report | the result + decision | 1 page | hypothesis, metric, result + confidence, decision, caveats | `docs/experiments/<slug>.md` |
| Incident summary | impact + status | ½ page | what, when, who's affected, current status, next update time | (draft locally) |
| Onboarding doc | day-one tasks | 1 page | env setup, first task, who to ask, where the docs live | `docs/onboarding.md` |
| Design doc | the problem + proposed approach | 3 pages | problem, goals/non-goals, proposed design, alternatives, risks, rollout | `docs/design/<slug>.md` |

## Voice per audience

- **engineer** — second person, present tense for "how it works", imperative for steps. Cite code.
- **pm** — outcome-first, less mechanism. Tie each section to user/business impact.
- **exec** — one-screen, decision + risk + cost. No mechanism unless it changes the decision.
- **mixed** — layered: an exec summary up top, engineer detail below. Never blended within a paragraph.

## Blameless tense

RCAs and incident summaries are third person, past tense, blameless. Name the system/process gap, never a person.
