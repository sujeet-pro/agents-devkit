# Runbook: <Scenario / Service / Procedure>

> One-sentence purpose. Written for the on-call engineer at 3am; every
> step is concrete and self-contained.

## Purpose

What does this runbook cover? What symptom or event triggers it? Link
to the alert rule / monitor / dashboard that normally fires.

## Preconditions

Bullet list of things that must be true before the procedure runs:
required permissions (link to the Okta group), required CLI tools
(with install one-liner), access to specific dashboards or Slack
channels.

## Severity + escalation target

- **Severity (default):** SEV-N, with the criteria that set it.
- **Primary owner:** handle / PagerDuty schedule id.
- **Escalation after N minutes without resolution:** handle / rotation.
- **Customer-comms trigger:** when to post in `#status` or notify
  support.

## Detection

How do we know the thing happened? List the monitor IDs (from
`~/.config/adk/datadog.md.common_dashboards`), the Slack alert
patterns, and the customer-report shapes.

## Steps

Numbered, imperative. Each step is runnable without context-switching.

1. **Acknowledge the page.** Post `ack` in `#platform-oncall` within
   5 minutes.
2. **Check the primary dashboard.** Open `<dashboard-url>`. Confirm
   the alert condition is still true.
3. **Triage hypothesis.** Run `adk-investigate:investigate-incident
   <alert-url>` to cross-reference recent deploys.
4. **Apply the mitigation.** Exact command, e.g.
   `kubectl -n prod rollout undo deploy/checkout-api`.
5. **Verify.** Wait 60s; check the dashboard for recovery; check
   `#status` for customer reports.

## Rollback

If mitigation makes things worse, how do you back out? Exact
commands. Link to the deploy workflow and the rollback procedure.

## Verification checklist

- [ ] Alert condition cleared.
- [ ] Error rate back under SLO threshold.
- [ ] No new customer reports in `#support-escalations` for 15 min.
- [ ] Post-incident record created in the incident tracker.

## Communication template

Copy-paste blocks for `#status`, `#platform-oncall`, and the customer
notification (if required). Fill placeholders before posting.

## Escalation

Who to page after N minutes of no resolution. Primary, secondary, and
last-resort. Include the specific reasons each person should be
involved (e.g. "DBA for schema-level mitigation").

## Post-incident

Link to the RCA template (`/adk-investigate:investigate-rca`) and the
post-mortem Confluence space.

## Last verified

- **Last drill or real incident:** YYYY-MM-DD
- **Owner:** team / handle
- **Next review:** YYYY-MM-DD (set 90 days out from last verified).
