# <Project / Service Name>

> One-sentence purpose. Tell the reader what this ships and for whom.
> Cite the owning team, the primary language, and the deploy target.

## Overview

3-6 sentences. What does this solve? Who are the consumers? What's the
shape of the contract (REST API / library / CLI / service)? Link to a
design doc or ADR if deeper background matters.

## Install

Concrete prerequisites with exact versions (from `build.gradle.kts` /
`package.json` / `pyproject.toml` / `go.mod`). Include the one-line
command to run it locally, copied verbatim from `scripts/run.sh` or
the entrypoint file.

## Configuration

Table of env vars with `required`, `default`, and `source`
(file:line). No invented defaults. Copy from `application.yml` /
`.env.example` / config loader code.

## Usage

Smallest concrete example that exercises the contract. For a service:
a curl command + expected response. For a library: the 5-line import
and call. For a CLI: the one-liner invocation.

## Development

How to run tests, lint, and format — exact commands copied from
`package.json` scripts, `Makefile`, or `build.gradle.kts` tasks.

## Deployment

Where this runs, how it's deployed, link to the deploy workflow
(`.github/workflows/<name>.yml`). Note the rollback procedure or link
to the runbook.

## Observability

Primary dashboards (from `~/.config/adk/datadog.md.common_dashboards`),
key SLOs, where logs go, error-tracking project.

## Contributing

Branch naming, PR conventions (link to `.github/pull_request_template.md`
if present), how to run the pre-push checks locally.

## License

State the license; link to `LICENSE`.
