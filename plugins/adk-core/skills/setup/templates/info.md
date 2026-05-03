---
# ~/.config/adk/info.md
# Operator profile. Used by every skill to personalize tone.
# Required: name, email. Everything else is optional.

name: Your Name
email: you@example.com
role: Principal Engineer
team: Platform
default_editor: nvim         # cursor | vscode | nvim | vi | etc.
notify:
  on_error: terminal         # terminal | silent
  on_completion: silent      # terminal | silent
---

# Notes

Free-form prose here for context Claude can reference. Examples:

- "I prefer concise PR descriptions; lead with the risk."
- "I'm timezone IST; defer non-urgent comments to my morning."
- "I sign reviews 'sj'."
