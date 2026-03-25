---
name: write-blog
description: Use when you need to draft or directly revise a professional software engineering blog post, changelog-style update, or technical announcement
user_invocable: true
arguments:
  - name: topic
    description: "Blog post, update, or announcement topic"
    required: false
  - name: source
    description: "Existing blog path or URL to revise in place"
    required: false
  - name: audience
    description: "Audience: developers, managers, general (default: developers)"
    required: false
  - name: tone
    description: "Tone: conversational, technical, opinionated (default: conversational)"
    required: false
  - name: format
    description: "Output format: markdown, google-doc, confluence, pdf (default: markdown)"
    required: false
---

# Blog

Use `/devkit:write-doc` with `doc-type=blog` and a shorter narrative format, but keep the content anchored in software development, engineering decisions, or delivery updates.

This skill owns both first drafts and direct revisions. If you only want comments, use `/devkit:review-doc`.

Run in parallel:

- research
- code or example extraction
- editorial review

Make the final post polished, technically grounded, and ready for publication.
