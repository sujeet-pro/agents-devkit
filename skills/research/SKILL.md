---
name: research
description: Conduct deep, comprehensive research on a topic with citations and organized findings
user_invocable: true
arguments:
  - name: topic
    description: "Topic to research"
    required: true
  - name: depth
    description: "Research depth: quick, standard, exhaustive (default: standard)"
    required: false
  - name: output
    description: "Output format: markdown, outline, notes (default: markdown)"
    required: false
  - name: save
    description: "File path to save research output (optional)"
    required: false
---

# Deep Research Skill

Conduct deep, comprehensive research on any topic using web search and retrieval. Produce well-organized, fully-cited findings in the user's preferred format.

## Instructions

Follow each phase in order. Communicate progress to the user between phases.

---

## Phase 1: Scope & Plan

### 1.1 Analyze the Topic

Break the topic down into:
- **Core question**: What is the fundamental thing the user wants to understand?
- **Sub-questions**: What specific questions need to be answered to fully address the topic? (Generate 3-8 sub-questions depending on depth)
- **Scope boundaries**: What is explicitly in-scope and out-of-scope?
- **Key terms**: What search terms and keywords will be most effective?

### 1.2 Determine Research Depth

Based on the `depth` argument (default: `standard`):

| Depth | Agents | Searches per Agent | Expected Time | Best For |
|-------|--------|--------------------|---------------|----------|
| `quick` | 1 | 3-5 | 1-2 min | Quick fact-checking, simple questions |
| `standard` | 3 | 5-8 each | 3-5 min | Most research tasks, technical topics |
| `exhaustive` | 5 | 8-12 each | 5-10 min | Deep dives, competitive analysis, academic topics |

### 1.3 Present Research Plan

Show the user:

```
## Research Plan: [Topic]

**Depth**: [quick/standard/exhaustive]
**Estimated scope**: [N] sub-questions across [N] research agents

### Sub-questions:
1. [Sub-question 1]
2. [Sub-question 2]
...

### Research agents:
- Agent 1: [Name] — [Focus area]
- Agent 2: [Name] — [Focus area]
...

Proceed with this plan? (or suggest adjustments)
```

Wait for user confirmation before proceeding. If the user suggests adjustments, modify the plan accordingly.

---

## Phase 2: Multi-Agent Research

### 2.1 Agent Definitions

Spawn research agents based on the depth setting:

#### Quick (1 agent)

1. **General Research Agent**: Covers the main topic broadly. Performs 3-5 web searches, fetches the most relevant pages, and extracts key information.

#### Standard (3 agents)

1. **Foundational Agent**
   - Focus: Core concepts, definitions, established knowledge, historical context
   - Search strategy: Wikipedia, official documentation, textbooks, foundational papers
   - Goal: Build the knowledge base that everything else references

2. **Current State Agent**
   - Focus: Latest developments, recent publications, current best practices, trends
   - Search strategy: Recent articles, blog posts, conference talks, release notes, news
   - Goal: Capture what is happening NOW and where things are heading

3. **Practical Agent**
   - Focus: Real-world implementations, case studies, code examples, tutorials, benchmarks
   - Search strategy: GitHub repos, Stack Overflow, engineering blogs, case studies
   - Goal: Ground the research in practical, actionable information

#### Exhaustive (5 agents)

All 3 standard agents, plus:

4. **Comparison Agent**
   - Focus: Alternative approaches, competing solutions, trade-offs, decision frameworks
   - Search strategy: "X vs Y" comparisons, benchmark studies, migration guides, decision matrices
   - Goal: Help the user understand the landscape of options

5. **Critical Analysis Agent**
   - Focus: Limitations, common pitfalls, failure modes, controversial aspects, criticisms
   - Search strategy: Post-mortems, critical reviews, "problems with X", community discussions
   - Goal: Provide a balanced view including downsides and risks

### 2.2 Research Execution

For each agent, execute the following loop:

```
for each sub-question assigned to this agent:
    1. Formulate 2-3 search queries using WebSearch
    2. Review search results and identify the most relevant URLs
    3. Use WebFetch to retrieve full content from the top 2-3 URLs per query
    4. Extract key facts, quotes, data points, and insights
    5. Record the source URL and publication date for every piece of information
    6. If initial results are insufficient, formulate follow-up queries
```

### 2.3 Source Quality Assessment

For each source, assess:
- **Authority**: Is this from a recognized expert, official documentation, or reputable publication?
- **Recency**: When was this published? Is the information still current?
- **Relevance**: Does this directly address the research question?
- **Corroboration**: Is this claim supported by multiple independent sources?

Prefer:
- Primary sources over secondary sources
- Official documentation over blog posts
- Peer-reviewed content over opinion pieces
- Recent content over older content (for time-sensitive topics)
- Multiple corroborating sources over single sources

### 2.4 Progress Updates

After each agent completes, briefly inform the user:
```
[Agent Name] complete — found [N] relevant sources covering [brief summary of findings]
```

---

## Phase 3: Synthesize

### 3.1 Merge Findings

Combine all agent findings into a unified knowledge base:

- **Deduplicate**: Remove redundant information that multiple agents found
- **Resolve contradictions**: When sources disagree, note both perspectives and explain the disagreement
- **Cross-reference**: Link related findings from different agents (e.g., the Foundational Agent's definition with the Practical Agent's implementation example)
- **Identify gaps**: Note any sub-questions that could not be adequately answered

### 3.2 Organize Structure

Create a logical document structure:

1. **Key Takeaways** (3-5 bullet points summarizing the most important findings)
2. **Background / Context** (foundational knowledge needed to understand the topic)
3. **Main Findings** (organized by sub-topic, not by agent)
4. **Practical Implications** (actionable takeaways, code examples, recommendations)
5. **Comparisons & Alternatives** (if exhaustive depth or if naturally relevant)
6. **Limitations & Caveats** (what to watch out for, what might change)
7. **Sources** (complete list of all referenced URLs)

### 3.3 Citation Rules

- Every factual claim MUST include a citation with a source URL
- Use inline citations: `[Source Name](URL)` or numbered references `[1]`
- If a claim could not be verified by any source, explicitly mark it: "*[Unverified]*"
- Distinguish clearly between:
  - **Facts**: Verified by reliable sources
  - **Expert opinions**: Attributed to specific people or organizations
  - **Speculation/Predictions**: Clearly labeled as forward-looking
- Include publication dates for time-sensitive information: `[Source Name, Jan 2026](URL)`

---

## Phase 4: Output

### 4.1 Format Based on Output Setting

#### Markdown (default)

Full research document with:
- Title and date
- Key Takeaways section at the top
- Headings and subheadings (`##`, `###`)
- Inline citations with links
- Code blocks for technical content
- Tables for comparisons
- Blockquotes for direct quotes from sources
- Numbered source list at the bottom

Example structure:
```markdown
# Research: [Topic]
*Conducted: [Date] | Depth: [quick/standard/exhaustive]*

## Key Takeaways
- Finding 1 — [Source](url)
- Finding 2 — [Source](url)
- Finding 3 — [Source](url)

## 1. Background
...

## 2. [Main Topic Area]
...

## 3. [Another Topic Area]
...

## Limitations & Caveats
...

## Sources
1. [Source Name](URL) — accessed [date]
2. [Source Name](URL) — accessed [date]
...
```

#### Outline

Hierarchical outline with key points:
```
# [Topic]

## 1. [Major Area]
  - Key point A ([Source](url))
    - Supporting detail
    - Supporting detail
  - Key point B ([Source](url))
    - Supporting detail

## 2. [Major Area]
  - Key point C ([Source](url))
  ...
```

#### Notes

Bullet-point notes organized by topic:
```
# [Topic] — Research Notes

## Key Takeaways
- ...

## [Subtopic 1]
- Fact or finding ([source](url))
- Fact or finding ([source](url))
- Open question: ...

## [Subtopic 2]
- ...
```

### 4.2 Save or Display

If `save` path is specified:
- Write the output to the specified file path
- Confirm: "Research saved to [path]"
- Also display a brief summary (Key Takeaways + source count) in the conversation

If `save` is NOT specified:
- Output the full research document directly in the conversation
- If the output is very long (>200 lines), suggest saving to a file

### 4.3 Follow-Up

After presenting the research, offer:

> "Research complete. Would you like me to:
> - **Dive deeper** into any specific section
> - **Search for more** on a particular sub-topic
> - **Reformat** the output (markdown/outline/notes)
> - **Save** to a file
> - **Summarize** into a shorter format"

---

## Research Quality Rules

1. **ALL information must be cited** with source URLs. No unsourced claims.
2. **Clearly mark unverified claims** — if something cannot be confirmed, say so.
3. **Distinguish facts from opinions** — attribute opinions to their sources.
4. **Prefer primary sources** — official docs, original papers, firsthand accounts.
5. **Include publication dates** for time-sensitive information.
6. **Note when information might be outdated** — especially for fast-moving technical topics.
7. **Be honest about gaps** — if a question cannot be fully answered, say so rather than speculating.
8. **Avoid bias** — present multiple perspectives on controversial or debated topics.
9. **Use precise language** — avoid vague qualifiers like "many people think" without attribution.
10. **Separate what is known from what is uncertain** — use confidence indicators where appropriate.
