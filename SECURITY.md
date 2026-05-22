# Security Policy

## Supported Versions

Security fixes target the current `main` branch and the latest tagged release
candidate once `v4.0.0-rc1` is published. Older untagged snapshots are not
maintained separately.

## Reporting a Vulnerability

Please report suspected vulnerabilities by email to `sujeet@onequince.com`.
Do not open a public GitHub issue for security-sensitive reports.

Include as much of the following as you can:

- Affected commit, branch, tag, or release candidate.
- Affected skill, agent integration, MCP server, helper script, or workflow.
- Reproduction steps and expected impact.
- Relevant logs or screenshots with credential values removed.
- Whether the issue is already being exploited or is only theoretical.

The maintainer will acknowledge receipt as soon as practical, triage the issue,
and coordinate a fix or disclosure plan before public details are shared.

## Credential Safety

This project treats credential handling as a hard security boundary. The
credential-safety posture is defined in `shared/constitution.md` section VII:

- Never paste, print, upload, or attach raw credential values.
- Never include values from environment variables ending in `_CRED`, `_CREDS`,
  `_SECRET`, `_TOKEN`, `_KEY`, `_PAT`, `_PASSWORD`, or `_API_KEY`.
- Use presence-only diagnostics such as "set" or "unset" when checking whether
  credentials exist.
- Validate credentials by exercising the target service and emitting only a
  boolean or status code.

If a credential value is exposed in an issue, PR, log, chat transcript, or CI
output, treat it as compromised and rotate it.

## Public Discussion

After a fix is available, the maintainer may publish a short advisory or release
note with affected versions, impact, mitigation, and credit. Please avoid
sharing exploit details publicly until coordinated disclosure is complete.
