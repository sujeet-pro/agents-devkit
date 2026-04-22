# Clarifying Questions (default-ask mode)

When running without `--auto`, the skill asks the user the questions below in order, one at a time, and waits for an answer before moving on. Each question presents 2-3 explained options where applicable; the "How to pick" guidance below is the rubric the user (or the skill under `--auto`) uses to choose.

Under `--auto`, the skill picks the option marked `(default)` in each question (and otherwise the safest option) without asking, and lists every choice it auto-picked in the final report.

### Question 1
**Q:** Which spec type do you need: PRD (product), RFC (engineering proposal), functional spec (what), or technical spec (how)?

**How to pick:** PRD = stakeholder-facing, focuses on user value + acceptance criteria. RFC = peer-reviewed proposal, focuses on trade-offs. Functional = what behavior. Technical = how to build it.

### Question 2
**Q:** Who is the audience and what decision will they make?

**How to pick:** Engineering implementers → technical detail. PMs/leadership → outcome and trade-offs. Reviewers → comparison vs alternatives.

### Question 3
**Q:** What are the must-have requirements vs nice-to-haves?

**How to pick:** List 3-7 must-haves. Nice-to-haves go in a separate section so they do not block sign-off.

## Standard option-presentation shape

Where the answer is multiple-choice (mode, focus, depth, severity filter, etc.), present each option as:

```
### Option <A | B | C>: <short label>
- What it does: <one sentence>
- Pros: <2-3 bullets>
- Cons: <2-3 bullets>
- Best when: <one sentence with a concrete signal>
- Blast radius: surgical | bounded | transformative
- Reversibility: easy | moderate | hard
```

Mark exactly one option `(default)` and say in one sentence why it is the safest pick for the current evidence.
