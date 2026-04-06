# Stage: Onboarding Guide

Use this stage when the agent should create or directly refresh onboarding material for new team members, transfers, or contributors.

## Type-Specific Phase Guidance

### Exploration
- Analyze the repository structure, architecture, and module boundaries
- Scan for existing onboarding docs, READMEs, and setup guides
- Identify the development workflow: branching strategy, CI/CD, code review process
- Determine the environment setup requirements: dependencies, tools, configurations

### Execute
- Write the onboarding guide following the document structure below
- Include diagrams when they improve comprehension of architecture or workflows
- Test all setup steps on a clean environment if possible

## Document Structure

### Welcome and Overview
- Team/adk-project mission and goals
- Where this service/adk-project fits in the broader system
- Key contacts and communication channels

### Architecture Context
- High-level architecture diagram
- Key components and their responsibilities
- Data flow overview
- External dependencies and integrations

### Environment Setup
Step-by-step guide with exact commands:
- Required tools and versions
- Repository cloning and initial setup
- Environment variables and configuration
- Database setup and seeding
- Running the application locally
- Verifying the setup works

### Development Workflow
- Branching strategy and naming conventions
- How to create and submit PRs
- Code review process and expectations
- CI/CD pipeline overview
- Testing requirements before merge

### Codebase Tour
- Directory structure explanation
- Key files and their purposes
- Where to find common patterns
- Important abstractions and conventions

### Common Tasks
- How to add a new feature
- How to fix a bug
- How to write and run tests
- How to debug common issues
- How to deploy changes

### Resources and Further Reading
- Internal documentation links
- Relevant ADRs and design documents
- External resources for key technologies
- FAQ or common questions

## Child Agent Team

- `architecture-analyzer` for understanding codebase structure and module boundaries
- `workflow-documenter` for capturing development processes and CI/CD flows
- `environment-setup-writer` for creating tested setup instructions
- `diagram-agent` for architecture and workflow diagrams

## Writing Rules

- Write for someone who has never seen this codebase before
- All setup commands must be tested and working
- Include expected output for verification steps
- Use progressive disclosure: overview first, details later
- Link to deeper resources rather than duplicating them

## Type-Specific Output Format

Markdown file with architecture context, setup steps, workflow documentation, and diagrams. Typically placed at `docs/onboarding.md` or `docs/getting-started.md`.

## Validation Checklist

- Setup steps work on a clean environment
- Architecture diagrams are current and accurate
- All links and references are valid
- Development workflow matches actual team practices
- No tribal knowledge is assumed without explanation
