# Feedback Document Guidelines

Guidelines for writing and reviewing feedback documents. These ensure feedback is specific, evidence-based, and actionable rather than vague or personality-driven.

---

## 1. Purpose & Audience

Feedback documents create a written record of observations and suggestions shared between colleagues, from managers to reports, or from peers. The audience is the feedback recipient and (optionally) their manager. The document must be clear enough that someone reading it months later can understand exactly what was observed and what was recommended.

---

## 2. Required Sections

Every feedback document must contain these sections in order:

| Section | Purpose |
|---------|---------|
| **Context** | When and where the observation occurred |
| **Observations** | Specific behaviors witnessed |
| **Impact** | Effect on team, project, or outcomes |
| **Suggestions** | Actionable improvements |
| **Strengths Acknowledgment** | What is working well |
| **Action Items** | Agreed next steps with owners and timelines |

---

## 3. Content Standards

### The SBI Model

All feedback must follow the Situation-Behavior-Impact (SBI) model:

| Component | What to Write | Example |
|-----------|---------------|---------|
| **Situation** | Specific time, place, or event | "During the sprint planning meeting on March 5th" |
| **Behavior** | Observable action, not interpretation | "You interrupted the product manager three times while they were presenting the requirements" |
| **Impact** | Measurable or observable effect | "The team missed two key acceptance criteria that had to be added mid-sprint, causing a 2-day delay" |

### Context

- State the specific event, meeting, project, or time period.
- Include enough detail that the recipient can recall the situation.
- If feedback spans multiple events, list each separately rather than generalizing.

### Observations

- Describe behaviors, not personality traits or intent.
  - **Wrong**: "You don't care about quality"
  - **Right**: "The last three PRs were submitted without unit tests, and two had regressions caught in staging"
- Never use absolute language: "you always", "you never", "every time". These are rarely accurate and trigger defensiveness.
- Stick to first-hand observations. If citing secondhand reports, state that explicitly: "Two team members reported that..."
- Separate fact from interpretation. State what you saw, then (if needed) state your interpretation as a separate sentence: "I observed X. My interpretation is Y."

### Impact

- Quantify impact where possible: time lost, bugs introduced, customer complaints, team morale indicators.
- When quantification is impossible, describe the effect qualitatively: "This created confusion about ownership" or "The client expressed frustration in the follow-up email."
- Connect the behavior to a business or team outcome, not to personal feelings (unless the feedback is specifically about interpersonal dynamics).

### Suggestions

- Every suggestion must be actionable: the recipient should know exactly what to do differently.
  - **Weak**: "Communicate better with the team"
  - **Strong**: "Post a brief status update in the project channel by 10am each day covering: what you completed, what you are working on, and any blockers"
- Suggestions should be forward-looking, not punitive.
- Offer 1-3 suggestions per observation. More than 3 overwhelms.
- Where possible, frame suggestions as experiments: "Try X for two weeks and let's see if it helps."

### Strengths Acknowledgment

- Include at least one genuine strength for every piece of critical feedback.
- Strengths must be as specific as the critique. Generic praise ("you're great") undermines the entire document's credibility.
  - **Weak**: "You're a hard worker"
  - **Strong**: "Your investigation of the memory leak was thorough. The root cause analysis you shared saved the team an estimated 2 days of debugging"
- Place strengths before or interspersed with critiques, not tacked on at the end as an afterthought.

### Action Items

- Every action item must have: a description, an owner, and a timeline.
- Use a table or checklist format for clarity.
- Include actions for both parties where applicable (the feedback giver may also have commitments).

| Action | Owner | Timeline |
|--------|-------|----------|
| Add unit tests to all PRs before requesting review | Recipient | Starting immediately |
| Schedule weekly 1:1 to discuss testing strategies | Manager | By end of week |
| Share team testing guidelines document | Manager | Within 2 weeks |

---

## 4. Structure & Flow

- Open with context so the recipient knows exactly what event or period is being discussed.
- Present observations factually before stating impact (let the reader connect the dots first).
- Follow critique with suggestions immediately, so the recipient knows the path forward.
- Acknowledge strengths genuinely, not as a rhetorical device to soften criticism.
- Close with action items that both parties agree on.
- Keep the document focused: one theme per feedback document is better than a grab bag of unrelated observations.

---

## 5. Common Issues

- **Personality judgments**: "You're disorganized" instead of describing specific disorganized behaviors. Always describe actions, not character.
- **Stale feedback**: Delivering feedback about something that happened months ago. Feedback loses value rapidly; document and deliver within 1-2 weeks.
- **All negative**: A document with zero strengths signals the writer is not paying attention to the whole picture, or the situation requires a performance improvement plan, not a feedback document.
- **All positive**: If there are no suggestions for improvement, the feedback lacks development value. Everyone has growth areas.
- **Unilateral action items**: Action items imposed without discussion. Feedback is a conversation; action items should be agreed upon, not dictated.
- **Hearsay without attribution**: "Everyone thinks you..." is neither specific nor verifiable. State who observed what, or limit to your own observations.
- **Emotional language**: "I was really frustrated when..." shifts focus from the behavior to the writer's feelings. State the impact on outcomes, not emotions.

---

## 6. Review Checklist

- [ ] Context identifies a specific event, meeting, or time period
- [ ] Observations describe behaviors, not personality traits
- [ ] No absolute language ("always", "never", "every time")
- [ ] Impact is quantified or concretely described
- [ ] Each critique is paired with an actionable suggestion
- [ ] Suggestions are forward-looking and framed as experiments where possible
- [ ] At least one genuine, specific strength is acknowledged
- [ ] Strengths are as detailed and evidence-based as critiques
- [ ] Action items have owners and timelines
- [ ] Tone is direct, respectful, and professional
- [ ] Feedback is timely (within 1-2 weeks of the observed behavior)
- [ ] SBI model is followed for each observation
