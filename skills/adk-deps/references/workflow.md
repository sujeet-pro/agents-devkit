# ADK Deps Workflow

## Default Flow
1. detect package managers present in the project directory
2. inventory all dependencies (direct and transitive where tooling allows)
3. run analysis based on the selected action and focus area
4. generate findings ordered by severity
5. propose an action plan for any issues found
6. execute approved updates if requested
7. validate: tests pass, lock file consistent, no new vulnerabilities

## Audit Flow
1. scan for known CVEs using native audit tools (npm audit, pip-audit, cargo audit)
2. check advisory databases via web search when native tools are unavailable
3. classify findings by severity (critical, high, medium, low)
4. report each finding with CVE ID, affected package, current version, and fix version
5. recommend remediation ordered by severity and ease of fix

## Update Flow
1. identify outdated dependencies using native tools
2. check changelogs and release notes for breaking changes
3. group updates into batches by risk level:
   - patch updates (low risk): apply together
   - minor updates (medium risk): apply per package group
   - major updates (high risk): apply one at a time
4. apply each batch, run tests, and verify lock file after each
5. roll back any batch that breaks tests

## Check Flow
1. quick health summary: total dependency count, direct vs transitive
2. staleness report: how many are behind latest, by how much
3. known-issue scan: any active CVEs or deprecation notices
4. output a concise dashboard table

## Plan Flow
1. identify target major version upgrades
2. analyze the dependency graph for cascading effects
3. pull migration guides and breaking-change notes
4. estimate effort and risk per upgrade
5. output a sequenced upgrade plan with rollback checkpoints

## Validation Rules
- run the smallest relevant repo-native commands first
- lock file must be consistent after every change
- test suite must pass after every update batch
- no new vulnerabilities introduced by updates
- if a claim cannot be verified, say so explicitly
