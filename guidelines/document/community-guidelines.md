# Community Guidelines Document Review Guidelines

## 1. Purpose & Audience

This guideline defines how to write and review Community Guidelines Documents. Effective community guidelines create a safe, productive environment by setting clear behavioral expectations, contribution processes, and enforceable accountability mechanisms.

**Primary audience:** Maintainers drafting community guidelines, contributors reading them, and moderators enforcing them.

**When to use:** When creating or revising the governance and participation rules for any open-source project, internal platform, or developer community.

## 2. Required Sections

Every Community Guidelines Document must include the following sections:

| # | Section | Purpose |
|---|---------|---------|
| 1 | Code of Conduct | Behavioral expectations with specific enforcement actions |
| 2 | Contributing Guide | PR process, commit conventions, testing requirements |
| 3 | Communication Channels | Where and how to ask questions, report issues, discuss proposals |
| 4 | Governance Model | Decision-making process, roles, and how authority is distributed |
| 5 | Licensing | What license applies, what contributors agree to |
| 6 | Reporting & Escalation Process | How to report violations, who handles them, how reporters are protected |

## 3. Content Standards

### 3.1 Code of Conduct Must Have Specific Enforcement

Vague behavioral rules without consequences are decorative, not functional.

Bad: "Be respectful and kind to each other."
Good: "Harassment, personal attacks, and discriminatory language are prohibited. Violations result in the following actions depending on severity:

| Severity | Example | Action | Duration |
|----------|---------|--------|----------|
| Minor | Dismissive tone, unconstructive criticism | Private warning from moderator | N/A |
| Moderate | Personal insults, repeated minor violations | Temporary ban from communication channels | 7-30 days |
| Severe | Threats, doxxing, discrimination | Permanent ban from all project spaces | Permanent |

Every enforcement action requires:

- A specific reference to the violated rule
- Documentation of the incident (private, accessible only to moderators)
- Notification to the violator with the rule cited and action taken
- An appeal process with a different moderator than the one who issued the action

### 3.2 Contributing Guide Must Be Actionable

A contributor reading this section for the first time should be able to submit a valid PR without asking anyone for help.

Required subsections:

- **Getting started:** How to set up the development environment (exact commands, not "install dependencies")
- **Branch and PR conventions:** Branch naming, PR title format, description template
- **Commit conventions:** Commit message format with examples (e.g., Conventional Commits)
- **Testing requirements:** What tests must pass, how to run them, minimum coverage threshold if applicable
- **Review process:** How many approvals are needed, expected turnaround time, who can merge
- **First-time contributors:** Label or tag for beginner-friendly issues, mentorship availability

### 3.3 Communication Channels Must Be Unambiguous

For each channel, specify:

| Channel | Purpose | Response Time | Who Monitors |
|---------|---------|---------------|-------------|
| GitHub Issues | Bug reports, feature requests | 48 hours for triage | Maintainers |
| Discord #help | Quick questions, setup help | Best effort, no SLA | Community + Maintainers |
| Mailing list | Design proposals, RFCs | 1 week discussion period | Core team |

Do not list channels without stating their purpose. If a channel exists but is not actively monitored, say so explicitly.

### 3.4 Governance Model Must Define Decision-Making

Address these questions clearly:

- **Who can make decisions?** List roles (Maintainer, Committer, Contributor, User) with their authority.
- **How are decisions made?** Consensus, vote, maintainer discretion — state which and when.
- **How do people earn roles?** Specific criteria, not "demonstrated commitment" (e.g., "5 merged PRs and nomination by a maintainer").
- **How are roles revoked?** Under what circumstances and by what process.
- **How are disputes resolved?** Escalation path when consensus fails.

### 3.5 Licensing Must Be Explicit

State the license in plain language in addition to linking the LICENSE file:

- What license the project uses and what it permits
- Whether contributors must sign a CLA (Contributor License Agreement)
- What happens to contributions (are they irrevocably licensed under the project license?)
- Any patents or trademark considerations

### 3.6 Reporting Process Must Protect Reporters

This is the most sensitive section. Get it right:

- **Multiple reporting channels:** Email, form, and at least one option that does not require a GitHub account
- **Confidentiality guarantee:** Reports are visible only to the moderation team, not all maintainers
- **No retaliation policy:** Explicit statement that retaliation against reporters is itself a severe violation
- **Response timeline:** How quickly a reporter will receive acknowledgment (e.g., within 48 hours)
- **Investigation process:** Who investigates, how evidence is gathered, how the subject is notified
- **Conflict of interest:** What happens if a report involves a moderator (escalation to a different person)

## 4. Structure & Flow

1. **Code of Conduct first** — Sets the tone before any process discussion.
2. **Contributing Guide second** — The most frequently referenced section for active participants.
3. **Communication Channels third** — People need to know where to go after reading the first two sections.
4. **Governance after process** — Most readers do not need governance details; those who do will have context from earlier sections.
5. **Licensing near the end** — Important but referenced less frequently.
6. **Reporting last** — Sensitive content that benefits from being in a dedicated, easy-to-find section.

Keep the main document concise. Link to detailed sub-documents (e.g., full CLA text, detailed governance charter) rather than inlining everything.

## 5. Common Issues

| Issue | Problem | Fix |
|-------|---------|-----|
| "Be nice" without enforcement | No accountability, rules are ignored | Define specific behaviors, severity levels, and consequences |
| Contributing guide assumes expertise | New contributors cannot get started | Include exact setup commands and a "first contribution" walkthrough |
| No response time commitments | Reporters and contributors feel ignored | State expected response times per channel, even if it is "best effort" |
| Governance is a single person | Bus factor of 1, no accountability | Define at least 2 maintainers and a succession process |
| CLA buried in legalese | Contributors do not understand what they are agreeing to | Add a plain-language summary above the legal text |
| Reporting goes to public channels | Reporters are exposed, violations go unreported | Provide private channels (email, form) and guarantee confidentiality |
| No path to maintainership | Contributors plateau and leave | Document specific, measurable criteria for role advancement |

## 6. Review Checklist

Before publishing a Community Guidelines Document, verify every item:

- [ ] Code of Conduct lists specific prohibited behaviors, not just general principles
- [ ] Enforcement actions are defined with severity levels, examples, and durations
- [ ] An appeal process exists and involves a different person than the original enforcer
- [ ] Contributing guide includes exact setup commands for the development environment
- [ ] Branch naming, commit format, and PR conventions are documented with examples
- [ ] Testing requirements specify what must pass and how to run tests locally
- [ ] Review process states number of required approvals and expected turnaround time
- [ ] Each communication channel has a stated purpose, response expectation, and owner
- [ ] Governance model defines roles, how they are earned, and how decisions are made
- [ ] Dispute resolution process exists for when consensus fails
- [ ] License is stated in plain language with CLA requirements if applicable
- [ ] Reporting process offers at least one private, non-GitHub channel
- [ ] Confidentiality and no-retaliation guarantees are explicitly stated
- [ ] Response timeline for reports is committed to (e.g., acknowledgment within 48 hours)
- [ ] Conflict-of-interest procedure exists for reports involving moderators
- [ ] Document has a version number and last-updated date
