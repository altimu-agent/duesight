# Report format

Every run produces a single markdown document with these nine sections in order:

| # | Section |
|---|---|
| 1 | Company Snapshot |
| 2 | Competitor Landscape |
| 3 | Positioning Comparison |
| 4 | Website & Conversion Analysis |
| 5 | Revenue Leaks (Top 3) |
| 6 | Fixes + Rewrites |
| 7 | Growth Strategy |
| 8 | Due Diligence Report (structured JSON) |
| 9 | Risk Scoring Logic |

Section 8 contains a complete due-diligence JSON object — identity, financial signals, legal/compliance, reputation, key personnel, recommendation (verdict + conditions), and sources.

## Risk levels

| Score | Level | Default verdict (calibratable to contract value) |
|---:|---|---|
| 0–30 | LOW | APPROVED |
| 31–60 | MEDIUM | CONDITIONAL |
| 61–80 | HIGH | CONDITIONAL or REJECTED |
| 81–100 | CRITICAL | REJECTED |

## Score reconciliation

The risk score is **pure arithmetic over the section-9 table**, clamped to [0, 100]. There is no LLM math in the final number.

After generation, a deterministic `reconcile_score` step in [src/agent.py](../src/agent.py) re-derives the canonical score from the section-9 adjustments table and surgically rewrites the JSON's `risk_score` and `risk_level` fields if the model's arithmetic disagreed. When this happens, the UI surfaces an amber `Score reconciled: table sum=X → clamped=Y` notice.

The full master prompt — including penalty/credit factors and the strict output rules — lives in [AGENT_PROMPT.md](../AGENT_PROMPT.md).
