# Stage: General Document Writing

Use this stage as the default when the document type is generic, unclear, or does not match any specialized stage. This stage handles professional engineering documents of any kind.

For the three core engineering document types, prefer the dedicated stages:
- **RFC** -> `rfc` stage (pre-alignment: "should we do this?")
- **Tech Spec / TDD** -> `system-design` stage (implementation: "how will we build this?")
- **ADR** -> `adr` stage (durable decisions: "what did we decide?")

HLD and LLD are sections within a Tech Spec, not separate document types. If the user asks for `hld` or `lld`, consider whether they need a full Tech Spec (`system-design` stage).

## Type-Specific Phase Guidance

### Exploration
- Research the topic using web searches, official docs, and codebase analysis
- Scan for existing related documents in the repository
- Identify the target audience and appropriate depth

### Execute
- Write the document following a logical structure appropriate to the content
- Adapt the structure to fit the subject matter -- no rigid template
- Ground content in real code and data where applicable

## Document Structure

Adapt based on content. A reasonable default:

### Title and Metadata
- Document title
- Author, date, status
- Audience and purpose

### Executive Summary
Brief overview of the document's purpose and key points.

### Body Sections
Organized by logical flow. Structure depends on the content:
- For explanatory docs: background, concepts, details, examples
- For process docs: overview, steps, verification, troubleshooting
- For reference docs: overview, catalog, usage examples

### Conclusion / Next Steps
Summary and actionable follow-ups.

### References
Links to related documents, external resources, and source material.

## Child Agent Team

- `research-agent` for official docs, standards, and migration notes
- `code-snippet-agent` for examples grounded in the repository or ecosystem
- `doc-reviewer` for structure and clarity
- a diagram pass through `/diagram` when the topic benefits from visuals
- `source-publisher` if the final output is Confluence or Google Docs

## Writing Rules

- Produce professional, destination-ready documents with a clear audience and purpose.
- When the document describes real code, inspect the repository first instead of inventing APIs.
- Use consistent heading hierarchy.
- Include a summary section at the top of every deliverable.

## Type-Specific Output Format

Markdown by default. Structure varies based on the deliverable type.

## Validation Checklist

- Document has a clear purpose and audience
- Content is accurate and grounded in real data/code
- Structure is logical and easy to navigate
- No broken links or missing references
- Summary accurately represents the content
