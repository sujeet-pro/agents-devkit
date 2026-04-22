# `frontend-mockup` — state checklist

For every interactive surface, demonstrate every applicable state:

- [ ] **default** — resting state
- [ ] **hover** — pointer over (desktop)
- [ ] **focus** — keyboard focus ring visible
- [ ] **active** — pressed / tap-down
- [ ] **disabled** — non-interactive; visibly muted; ARIA `aria-disabled="true"`
- [ ] **loading** — pending / spinner / skeleton
- [ ] **empty** — no data; helpful CTA
- [ ] **error** — failure; recoverable; actionable message

Skip a state only if it does not apply to the surface (e.g., a static heading has no hover state).

For non-interactive content (lists, panels), at minimum show: default + empty + loading + error.
