# Agent Skill Landscape Research

Date: 2026-03-25

This note captures the external patterns used to reshape AKIT.

## Key References

- Anthropic Claude Code skills and subagents docs
- Cursor documentation for custom modes, model routing, and background agents
- Google Gemini CLI repository and extension docs
- GitHub's official MCP server and `spec-kit`
- open-source skill packs such as Superpowers

## What These Sources Suggest

1. Shared `SKILL.md`-style packs are now a common portability layer.
2. Agentic workflows work best when the parent owns orchestration and child agents have clear, non-overlapping roles.
3. Source-native integrations matter more than generic shell glue for review posting.
4. Multi-provider mode should respect the host platform:
   - Cursor should stay inside Cursor
   - other hosts can fan out to installed CLIs when needed
5. Review and documentation flows benefit from one consistent pipeline:
   - ingest source
   - parallel role-based analysis
   - markdown artifact
   - optional postback to the origin

## Resulting AKIT Changes

- standardized child-agent contract across skills
- explicit GitHub + Bitbucket MCP routing for PR workflows
- stronger software-development focus across the catalog
- new codebase review capability
- source-aware document publishing and review postback rules
