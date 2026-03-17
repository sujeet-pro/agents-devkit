# General Document Review Guidelines

Baseline guidelines for reviewing ANY document type. Always loaded alongside type-specific guidelines.

---

## 1. Language & Grammar

- **Spelling**: No misspelled words. Use consistent spelling (US or UK English, not mixed).
- **Grammar**: Subject-verb agreement, correct tense usage, no sentence fragments.
- **Punctuation**: Consistent style (Oxford comma or not — pick one and stick with it).
- **Active voice**: Prefer active voice. Flag passive voice when it obscures the actor ("It was decided" → "The team decided").
- **Conciseness**: Flag filler words ("basically", "actually", "in order to", "it should be noted that"). Cut without losing meaning.

---

## 2. Terminology & Consistency

- Same concept must use the same term throughout the document.
- Define terms on first use if they might be unfamiliar to the audience.
- Acronyms must be expanded on first use: "Content Delivery Network (CDN)".
- Do not alternate between synonyms for the same thing (e.g., "user" vs "customer" vs "client" for the same entity).

---

## 3. Structure & Headings

- Heading hierarchy must be strictly sequential: H1 → H2 → H3. Never skip levels (no H1 → H3).
- Exactly one H1 per document (the title).
- Headings must be descriptive — a reader scanning headings alone should understand the document's structure.
- Sections should follow a logical flow: context before details, problem before solution.
- No empty sections or placeholder headings.

---

## 4. Links & References

- All links must be valid (no 404s, no placeholder URLs).
- Internal cross-references must resolve to existing sections or documents.
- External links should point to authoritative sources (official docs, specs, not random blog posts).
- Link text must be descriptive ("see the [authentication guide]" not "click [here]").

---

## 5. Images & Diagrams

- Every image must have alt text that describes the content (not just "diagram" or "screenshot").
- Diagrams must match the textual description — flag contradictions between text and visuals.
- Images should be referenced in the surrounding text ("As shown in Figure 1..." or "The diagram below illustrates...").
- Check that image files actually exist at the referenced paths.

---

## 6. Code Blocks

- Every code block must have a language identifier.
- Code must be syntactically valid for the declared language.
- Code examples should be realistic — include imports, proper types, error handling.
- Code should match the surrounding text description.
- Long code blocks should use collapse for boilerplate (see `coding/expressive-code.md`).

---

## 7. Tables

- Tables must have a header row.
- Column alignment should be consistent.
- No empty cells without explanation.
- Tables should be used for structured comparisons, not for layout.

---

## 8. Formatting Consistency

- List style must be consistent within a section (all bullets or all numbers, not mixed).
- Emphasis must be consistent (bold for key terms OR italic, not alternating randomly).
- Date formats must be consistent throughout (ISO 8601 `YYYY-MM-DD` preferred).
- Number formats must be consistent (thousands separator, decimal notation).

---

## 9. Audience Appropriateness

- Content depth should match the stated or implied audience.
- Jargon must be defined when the audience may not know it.
- Prerequisites must be stated if the document assumes prior knowledge.
- Tone should match the document type (formal for specs, conversational for blogs).

---

## 10. Completeness

- No TODO/TBD/FIXME markers left in the document.
- No stub sections with placeholder text.
- All claims should be supported (data, links, or reasoning).
- If a topic is mentioned, it should be explained or linked.

---

## 11. Review Checklist

- [ ] Spelling and grammar are correct
- [ ] Terminology is consistent throughout
- [ ] Heading hierarchy is sequential (H1 → H2 → H3)
- [ ] All links are valid and descriptive
- [ ] All images have alt text
- [ ] Code blocks have language identifiers and are syntactically valid
- [ ] Tables have headers and consistent formatting
- [ ] No TODO/TBD/FIXME markers remain
- [ ] Active voice is used where appropriate
- [ ] Document is audience-appropriate
