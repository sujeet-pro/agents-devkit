# Industry Anti-patterns

What NOT to design / build per industry. Adapted from the UI-UX Pro Max reasoning rules (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), trimmed to the highest-signal items per category.

These are NOT absolute laws — they are strong defaults backed by user research per industry. Override with explicit reasoning ONLY when there's evidence the audience expects the otherwise-anti-pattern.

## Universal anti-patterns (all industries)

- Emojis as structural icons.
- Layout-shifting hover states.
- Color as the only indicator of state / meaning.
- `100vh` (use `100svh`).
- Disabled buttons that look tappable.
- Tap targets smaller than 44pt / 48dp.
- Animations that ignore `prefers-reduced-motion`.
- Carousels that auto-rotate faster than 8 seconds (most users hate them; accessibility nightmare).
- Sign-up walls before any value is shown.
- Modal interrupts on first page view.

## Tech & SaaS

| Don't | Why |
| --- | --- |
| AI-purple / AI-pink gradients | Visually dated; reads "AI bubble" rather than "credible product". |
| Glassmorphism on data-dense screens | Reduces contrast; data harder to read. |
| Cute illustrations on enterprise dashboards | Reads "consumer toy"; loses trust with admin users. |
| Bento grids for live data | Bento grids imply static showcase; live data needs scannable list / table. |

## Finance & Fintech

| Don't | Why |
| --- | --- |
| AI-purple / AI-pink gradients | Reads "speculative crypto / AI" — opposite of trust. |
| Bright neon colors | Opposite of stability / safety perception. |
| Skeuomorphic dollar bills / vault icons | Reads gimmicky; modern fintech uses minimal abstract iconography. |
| Big celebratory animations on transfers | Money flows are serious; minimal feedback is more trustworthy. |
| Hidden fees in micro-text | Regulatory and trust nightmare. |

## Healthcare & Medical

| Don't | Why |
| --- | --- |
| Dark mode as default | Most healthcare contexts are well-lit; dark mode reduces glanceability. |
| Casual / playful language | Patients are stressed; clear, calm, professional copy is correct. |
| Red as a primary brand color | Red == danger / blood in healthcare context. |
| Stock-photo doctors with too-perfect smiles | Reads inauthentic; reduces trust. |
| Auto-playing patient testimonials with audio | Privacy and accessibility issues. |

## E-commerce

| Don't | Why |
| --- | --- |
| Hidden shipping costs until checkout | #1 cart abandonment trigger. |
| Forced account creation before guest checkout | #2 cart abandonment trigger. |
| Tiny "Add to cart" buttons on mobile | Conversion killer; CTA should be prominent. |
| Auto-rotating product carousels | Users miss the products that aren't on screen. |
| Pop-ups within 5 seconds of landing | Bounce trigger. |

## Beauty / Spa / Wellness

| Don't | Why |
| --- | --- |
| Bright neon palettes | Opposite of calm / premium feel. |
| Brutalist or sci-fi aesthetics | Misaligned with relaxation / self-care mood. |
| Aggressive sales copy / countdown timers | Reads spammy; breaks the calm brand. |
| Stock-photo "happy spa lady" | Reads cliché; modern wellness uses real, diverse imagery. |

## Restaurants / Food

| Don't | Why |
| --- | --- |
| Hidden menus (PDF-only menus, behind QR codes that need login) | Conversion killer; menus must be HTML and crawlable. |
| Tiny food photos | Food is the product; show it big. |
| Auto-playing video with sound | Universally hated. |
| Slow-loading food carousels with heavy images | Mobile users on the go bounce. |

## Children's apps / Education for kids

| Don't | Why |
| --- | --- |
| In-app purchases without parental gate | Regulatory issue; violates trust. |
| Ads that look like content | Regulatory issue (FTC); violates trust. |
| Dark patterns (false-urgency, hidden cost) | Same as above + child-safety failure. |
| Tiny text (< 18px) | Kids' reading ability varies; large text is correct default. |

## B2B / Enterprise

| Don't | Why |
| --- | --- |
| Consumer-style emoji-heavy UI | Loses credibility with procurement / IT. |
| Hiding pricing | Procurement teams can't even shortlist your product. |
| Marketing-only landing page with no product detail | Buyers want specs, integrations, security docs upfront. |
| Removing the existing pattern users have been trained on | High switching cost; preserve familiar patterns when possible. |

## Gaming / Entertainment

| Don't | Why |
| --- | --- |
| Aggressive monetization on first session | Bounce trigger; let the user fall in love first. |
| Long unskippable intros | Players bounce; respect their time. |
| Loot-box patterns disguised as "surprise rewards" | Regulatory in many regions; trust nightmare. |

## Government / Public Services

| Don't | Why |
| --- | --- |
| Branded marketing aesthetics | Public services should look neutral and authoritative. |
| Decorative imagery that competes with the form | Forms are the product; minimize chrome. |
| Color-only error indication | Accessibility-mandatory by law in many regions. |

## Crypto / Web3

| Don't | Why |
| --- | --- |
| Cyberpunk neon for an exchange | Reads "speculative meme" rather than "store of value". |
| Hidden gas fees | Trust + regulatory issue. |
| Wallet UI that doesn't show the destination address before signing | Phishing exposure. |

## How to use this list

When generating `design-system/MASTER.md` (per `<task>-design-system-master.md`):

1. Identify the industry from the user's product description.
2. Pull the matching section above (or "Universal" if no industry match).
3. Add the `Don't` rows to MASTER section 9 (Anti-patterns) with industry tag.
4. When implementing components, validator's Phase 3 cross-checks the work against this list.

## When to override

If the design intent explicitly contradicts an anti-pattern (e.g., a fintech app deliberately leaning into "speculative meme" aesthetics for a Gen-Z trading product), DOCUMENT the override in `design-system/MASTER.md` section 9 with the reasoning. The validator's Phase 3 surfaces such overrides as WARN, not BLOCKER.
