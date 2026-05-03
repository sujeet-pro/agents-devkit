---
# ~/.config/adk/slack.md
# Slack channels of record. Used by adk-investigate:investigate-incident
# and investigate-rca.

incident_channel: "#incidents"
deploys_channel: "#deploys"
oncall_channel: "#platform-oncall"
team_channel: "#platform-team"
on_call_users:
  - "@alice"
  - "@bob"
  - "@charlie"
---

# Notes

- Read access goes through the claude.ai workspace Slack connector.
- The incident channel is scraped during incident triage to surface team discussion.
- The on-call list is informational — adk doesn't escalate; it reports the current on-call so the operator can mention them.
