# Blog Post Guidelines

Guidelines for writing and reviewing blog posts. These ensure posts are engaging, scannable, opinionated, and deliver clear value to the reader.

---

## 1. Purpose & Audience

Blog posts are informal, opinion-driven pieces that share insights, experiences, or perspectives with a broad audience. Readers skim aggressively. Every sentence must earn its place. The bar: a reader who gives you 10 seconds of scanning should know if this post is worth their time.

---

## 2. Required Sections

Every blog post must contain these elements (not necessarily as explicit headings):

| Element | Purpose |
|---------|---------|
| **Hook / Opening** | Grab attention in the first 2 sentences |
| **Context / Problem** | Why this topic matters right now |
| **Thesis / Opinion** | The clear stance or insight being argued |
| **Supporting Arguments** | Evidence, examples, data backing the thesis |
| **Practical Takeaway** | What the reader can do with this information |
| **Conclusion / CTA** | Wrap up and direct the reader to a next action |

---

## 3. Content Standards

### Hook / Opening

- The first 2 sentences must create tension, surprise, or curiosity. Do not open with definitions, history, or throat-clearing.
  - **Weak**: "In today's fast-paced world, caching is important for web applications."
  - **Strong**: "Your Redis cache is lying to you. Here's how stale reads cost us 3 hours of debugging and $12K in incorrect billing."
- Techniques that work: a surprising claim, a concrete story, a provocative question, a counter-intuitive fact.
- Never open with "In this post, I will discuss..." -- that is a table of contents, not a hook.

### Context / Problem

- Establish why the reader should care in 2-3 paragraphs maximum.
- Ground the problem in a real scenario. Abstract problems do not engage readers.
- If the problem is technical, state the symptoms a reader would recognize: "You deploy on Friday, metrics look fine, then Monday morning your error rate is 10x."

### Thesis / Opinion

- State your position clearly and early. Blog posts are not research papers; the reader should know your stance by the end of the third paragraph.
  - **Weak**: "There are pros and cons to both approaches"
  - **Strong**: "Feature flags are strictly better than long-lived branches, and I'll show you why with data from 200 deployments"
- Wishy-washy hedging ("it depends", "there's no right answer") is acceptable only when followed by a clear framework for deciding.

### Supporting Arguments

- Use a mix of: personal experience, data/metrics, code examples, and external references.
- Each argument gets its own section with a scannable heading.
- One argument per section. Do not combine unrelated points.
- If making a technical claim, show evidence (benchmark, screenshot, log output, code diff).

### Practical Takeaway

- The reader must leave with something they can apply today.
- Frame as concrete actions: "Here's how to implement this", "Run this command to check your setup", "Add this to your CI pipeline."
- If the post is purely conceptual, the takeaway can be a mental model or decision framework.

### Conclusion / CTA

- Do not summarize the post (the reader just read it).
- End with one of: a call to action, a forward-looking thought, or a question that invites discussion.
- Keep it to 2-3 sentences maximum.

---

## 4. Structure & Flow

### Formatting Rules

- **Paragraphs**: 2-4 sentences maximum. Wall-of-text paragraphs lose blog readers instantly.
- **Headings**: Use scannable, descriptive headings. A reader skimming only headings should get the gist of the argument.
- **Lists**: Use bullet points for 3+ related items. Do not write lists as prose.
- **Bold**: Bold the key phrase in important paragraphs to aid scanning.
- **Code blocks**: If the post is technical, include working code examples. Use expressive-code features (title, collapse, highlight) per the expressive-code guidelines.
- **Images/diagrams**: One diagram is worth five paragraphs of explanation. Include architecture diagrams, flowcharts, or screenshots where they clarify.

### Length

- Target 800-1500 words for standard posts.
- Target 2000-3000 words for deep-dive posts (but use more headings and visuals to maintain scannability).
- If a post exceeds 3000 words, consider splitting into a series.

### Tone

- Conversational, not academic. Write as if explaining to a smart colleague over coffee.
- First person is fine ("I found that...", "We discovered...").
- Humor is welcome if natural; forced humor is worse than none.
- Avoid corporate speak: "leverage", "synergize", "ecosystem", "paradigm shift."

---

## 5. Common Issues

- **Burying the lead**: The interesting insight appears in paragraph 6. Move it to paragraph 1.
- **No opinion**: The post describes a technology without taking a stance. Every post needs a thesis.
- **Tutorial disguised as a blog**: Step-by-step instructions without insight or opinion belong in documentation, not a blog.
- **Missing code examples**: A technical claim without a code example is an unverified assertion.
- **Wall of text**: Paragraphs longer than 4 sentences. Break them up.
- **Clickbait without payoff**: A provocative title that the post does not deliver on. The content must match the hook.
- **No takeaway**: The reader finishes and thinks "so what?" Always answer the question "what should I do with this information?"
- **Throat-clearing intro**: Two paragraphs of background before getting to the point. Cut the preamble.

---

## 6. Review Checklist

- [ ] Opening hook creates tension, surprise, or curiosity in the first 2 sentences
- [ ] Does not open with a definition, history lesson, or "In this post..."
- [ ] Thesis/opinion is stated clearly by the third paragraph
- [ ] Each supporting argument has its own headed section
- [ ] Claims are backed by evidence (data, code, examples, references)
- [ ] Paragraphs are 2-4 sentences maximum
- [ ] Headings are scannable (a skim of headings conveys the argument)
- [ ] At least one practical takeaway the reader can apply immediately
- [ ] Code examples use expressive-code features (title, collapse, highlight)
- [ ] Conclusion does not merely summarize; it advances the conversation
- [ ] Tone is conversational and opinion-driven, not academic or wishy-washy
- [ ] Post length is appropriate (800-1500 standard, 2000-3000 deep-dive)
- [ ] No corporate jargon or filler words
