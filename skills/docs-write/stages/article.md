# Stage: Technical Article

This stage covers deep technical articles with research, diagrams, and code examples. It owns both first drafts and direct revisions.

## Type-Specific Phase Guidance

### Exploration
- Research the topic deeply: academic papers, official docs, conference talks, authoritative blog posts
- Identify what existing coverage exists and where this article adds unique value
- Determine the appropriate depth based on audience and topic complexity
- If the article covers real code, inspect the repository first

### Brainstorm
- Present 2-3 angle/depth options for the article
- Discuss audience level: beginner, intermediate, expert
- Determine the narrative structure: tutorial, explainer, opinion, case study

### Deep Research
- Cross-reference findings from multiple authoritative sources
- Gather benchmark data, performance numbers, and real-world examples
- Identify and address potential counterarguments or edge cases

### Execute
- Write the article following the document structure below
- Maintain a consistent depth and rigor throughout
- Include diagrams where they significantly aid comprehension

## Document Structure

### Title and Subtitle
Clear, descriptive title. Subtitle provides additional context.

### Abstract / TL;DR
2-3 sentence summary of the article's thesis and key findings.

### Introduction
- Problem or question being addressed
- Why it matters and who should care
- Roadmap of what the article covers

### Background
- Prerequisite knowledge the reader needs
- Key concepts and definitions
- Historical context if relevant

### Main Body
Structured into logical sections, each building on the previous:
- Technical explanations with supporting evidence
- Code examples grounded in real implementations
- Diagrams for architecture, data flow, or complex concepts
- Comparisons or benchmarks when evaluating approaches

### Discussion
- Analysis of findings or approach
- Trade-offs and limitations
- When this approach does and does not apply

### Conclusion
- Summary of key insights
- Practical recommendations
- Future directions or open questions

### References
- Cited sources with full URLs
- Further reading recommendations

## Child Agent Team

- `adk-research-agent` for deep research on the topic
- `code-example-agent` for creating and testing code examples
- `diagram-agent` for architecture and flow diagrams
- `fact-checker` for verifying claims, versions, and benchmarks
- `adk-doc-reviewer` for structure, flow, and readability

## Type-Specific Output Format

Markdown file with embedded diagrams. All claims should be sourced. Code examples include language tags and are tested where possible.

## Validation Checklist

- Abstract accurately summarizes the article
- All technical claims are sourced or verifiable
- Code examples are correct and tested
- Diagrams are clear and referenced in the text
- Narrative flow is logical and builds progressively
- No unsupported opinions presented as facts
