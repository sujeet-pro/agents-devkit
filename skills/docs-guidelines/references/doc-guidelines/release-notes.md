# Release Notes Guidelines

Guidelines for writing and reviewing release notes, changelogs, and "what's new" documents. Release notes communicate changes to users and stakeholders in terms they understand and can act on.

**Audience**: End users, administrators, developers integrating with the product, and internal stakeholders tracking product evolution.

---

## 1. Required Sections

Every release notes document must include the following sections in order.

| # | Section | Purpose |
|---|---------|---------|
| 1 | Summary | Headline changes in 1-2 sentences |
| 2 | Highlights | Featured changes with context |
| 3 | What's New | All features and improvements |
| 4 | Bug Fixes | Resolved issues |
| 5 | Breaking Changes | Changes requiring user action |
| 6 | Deprecations | Features being phased out |
| 7 | Known Issues | Unresolved issues in this release |

Optional sections: Compatibility, Upgrade Instructions, Contributors.

---

## 2. Content Standards

### Summary
- One to two sentences summarizing the most important changes.
- Focus on user impact, not internal changes.
- Example: "This release adds real-time notifications and improves API response time by 40%."

### Highlights
- Feature 2-3 changes that deserve special attention.
- Provide context: why the change was made and how it benefits users.
- Include screenshots, diagrams, or charts where visual changes are significant.

### What's New
- Organize by category: Features, Improvements, Performance.
- Describe each change in terms the user understands: "You can now filter reports by date range" not "Added DateRangeFilter component."
- Link to detailed documentation for complex features.

### Bug Fixes
- Describe the bug from the user's perspective, not the developer's.
- Good: "Fixed an issue where exported CSV files contained duplicate rows."
- Bad: "Fixed race condition in ExportService batch processor."

### Breaking Changes
- Use a warning callout — these need immediate attention.
- For each breaking change: what changed, why, and the exact migration steps.
- Include code examples for API changes.

### Deprecations
- State what is deprecated, what replaces it, and when it will be removed.
- Give users a clear timeline to migrate.

### Known Issues
- Include a workaround for each known issue.
- Link to tracking tickets so users can follow progress.

---

## 3. Common Issues

- **Developer language**: Writing for other developers instead of users. "Refactored middleware pipeline" means nothing to users.
- **Missing migration steps**: Breaking changes without concrete migration instructions.
- **No version numbers**: Users need to know exactly which version contains which changes.
- **Buried breaking changes**: Breaking changes must be prominently visible, not hidden in a long list.
- **Missing "known issues"**: Omitting known issues reduces trust when users discover them.

---

## 4. Review Checklist

- [ ] Summary focuses on user impact, not internal changes
- [ ] Highlights provide context (why, not just what)
- [ ] Features are described in user-facing language
- [ ] Bug fixes describe the symptom, not the implementation
- [ ] Breaking changes are prominently marked with migration steps
- [ ] Deprecations include replacement and removal timeline
- [ ] Known issues have workarounds
- [ ] Version number and date are clearly stated
- [ ] Links to detailed documentation are present for complex features
- [ ] Performance improvements include before/after numbers
