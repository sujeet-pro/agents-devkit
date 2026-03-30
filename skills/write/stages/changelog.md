# Stage: Changelog

Use this stage when the agent should draft or improve a changelog from git history with categorization, release formatting, and clear breaking-change summaries.

## Type-Specific Phase Guidance

### Exploration
- Verify the repository is a git repository and the `since` reference resolves to a valid git object
- Read git log between the specified range (tags, commits, or dates)
- Scan for existing CHANGELOG.md to match format conventions
- Identify PR/MR titles, commit messages, and linked issues

### Execute
- Categorize changes and write the changelog following the document structure below
- Highlight breaking changes prominently
- Link to PRs, issues, and relevant documentation

## Document Structure

### Release Header
```
## [version] - YYYY-MM-DD
```

### Categories
Use [Keep a Changelog](https://keepachangelog.com/) categories:

- **Added**: New features
- **Changed**: Changes in existing functionality
- **Deprecated**: Features that will be removed in future
- **Removed**: Features removed in this release
- **Fixed**: Bug fixes
- **Security**: Vulnerability fixes

### Breaking Changes
A dedicated section at the top of the release if any changes are breaking:
- What changed
- Migration steps
- Before/after code examples

### Entry Format
Each entry should:
- Start with a concise description of the change
- Reference the PR/MR number and link
- Credit the contributor if applicable
- Include migration notes for breaking changes

## Child Agent Team

- `git-analyzer` for reading and categorizing git history
- `pr-reader` for extracting PR descriptions and linked issues
- `doc-reviewer` for changelog format and completeness checking

## Writing Rules

- Follow the existing changelog format in the repository if one exists
- Group related changes together within categories
- Use past tense for descriptions
- Be specific about what changed, not just that something changed
- Breaking changes must include migration guidance

## Type-Specific Output Format

Markdown appended to or updating `CHANGELOG.md` in the repository root.

## Validation Checklist

- All significant commits are represented
- Breaking changes are clearly marked with migration steps
- PR/issue links are correct and working
- Categories are used consistently
- Format matches existing changelog conventions in the repo
