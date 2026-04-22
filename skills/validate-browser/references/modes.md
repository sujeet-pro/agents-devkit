# `validate-browser` — modes

| Mode | Behavior | Default? |
| --- | --- | --- |
| `verify-fix` | Read repro doc; walk steps; assert original error absent + expected state present | called by build-bugfix |
| `visual-check` | Per-viewport screenshot capture + diff vs baseline (≤0.5% pixel diff) | called by frontend-feature, frontend-mockup |
| `console-audit` | Collect console errors/warnings + failed network requests | always run as part of auto Phase D2 |
| `interaction-test` | Walk script of clicks/types/hovers; assert state per step | only when caller passes a script |
| `a11y-audit` | Inject axe-core; report violations with WCAG SC | called by frontend-feature, audit-site |

`--mode review` (default): run the audit, write findings; do NOT modify source.
`--mode fix`: for findings with documented auto-fix recipes (`references/auto-fix-recipes.md`), apply them. Re-run the audit at the end to confirm zero residual.
`--mode auto`: review then offer to run fix on auto-fixable findings.
