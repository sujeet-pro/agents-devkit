# Staged rollout plan

The default rollout shape for any user-visible change. Each stage has a **dwell time** (minimum time to observe) and **gate signals** (error rate, latency, business KPI). Advance only when gates are green for the dwell time.

## Default stages

| Stage | Audience | Dwell time | Gate signals |
| --- | --- | --- | --- |
| **0 — Off in prod** | Nobody (deploy-only) | until next stage | Deploy succeeded; no error spike on serve path. |
| **1 — Internal / dogfood** | Eng team + employee accounts | ≥ 30 min (≥ 1 business day for big changes) | No new errors; manual smoke pass. |
| **2 — 1% canary** | Random 1% of eligible traffic | ≥ 1 hour (active period) | error rate ≤ baseline + 0.5%; p95 within +10%; no business KPI drop > 1%. |
| **3 — 10%** | Random 10% | ≥ 4 hours | Same gates as Stage 2 with tighter thresholds. |
| **4 — 50%** | Random 50% | ≥ 24 hours | Same gates. |
| **5 — 100%** | All eligible traffic | ≥ 24 hours before flag removal | Same gates. |
| **6 — Cleanup** | Flag removed from code | ≤ 2 weeks after Stage 5 | Code-side flag check removed; flag retired in flag store. |

## Adjustments by blast radius

| Blast radius | Suggested adjustment |
| --- | --- |
| Internal-only feature | Stages 0 → 1 → 5 (skip 2/3/4). |
| Logged-in non-paying users | Stages 0 → 1 → 2 → 4 → 5. |
| Paying customers | Full stages 0 → 1 → 2 → 3 → 4 → 5 with longer dwells. |
| Public/unauthenticated traffic | Full stages with very tight gate thresholds. |
| Partner API consumers | Stages 0 → 1 → 2 (named partners) → 3 (small partners) → 4 → 5; coordinate with partner support. |

## Gate signal thresholds (tighten per surface)

- **Error rate:** stage rate ≤ baseline + 0.5 percentage points (frontend) / 0.1 pp (backend).
- **Latency p95:** stage p95 ≤ baseline × 1.10.
- **Business KPI:** stage KPI ≥ baseline × 0.99 (must not drop more than 1%).
- **Client errors (web-vitals):** stage CWV "good" share ≥ baseline.
- **Manual smoke:** at least one named human runs the critical-path scenarios per stage.

## Rollback triggers

ANY of the following triggers an immediate rollback (flag flip OR revert+redeploy, whichever is faster):

- Error rate spikes ≥ baseline + 1 pp at any stage.
- p95 latency spikes ≥ baseline × 1.50 at any stage.
- Business KPI drops > 5% at any stage.
- Customer-reported regression with reproducible repro.
- Security alert tied to the change.
- On-call's gut tells them something is off — gut overrides metrics.

## Re-launch after rollback

Treat as a fresh launch. Start from Stage 1 (or wherever the regression was hit minus one stage), with a postmortem note and the specific signal that previously failed under explicit watch.
