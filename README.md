# DueSight

Elite B2B business intelligence agent for the AI Agent Economy Hackathon (April 2026).

Given a company name and context, DueSight produces a **9-section consultant-grade report** across three dimensions:

1. **Competitive intelligence** — landscape, positioning comparison, where the company wins or loses
2. **Growth strategy** — website & conversion analysis, revenue leaks, concrete fixes and rewrites
3. **Due diligence** — structured risk assessment with a 0–100 risk score and APPROVED / CONDITIONAL / REJECTED verdict

The output should feel like something a company would pay $10K+ for.

## Stack

- Python 3
- OpenAI SDK pointing to TokenRouter (OpenAI-compatible endpoint)
- `https://api.tokenrouter.com/v1`

## Setup

```bash
cp .env.example .env
# Edit .env with your TOKENROUTER_API_KEY
pip install -r requirements.txt
python src/agent.py "Acme Field Services" --industry "oil and gas" --country "Ecuador" --contract-value 500000
```

Output is printed to stdout as markdown and saved to `output/<company_slug>_report.md`.

## Report Sections

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

## Risk Levels

| Score | Level |
|---|---|
| 0–30 | LOW |
| 31–60 | MEDIUM |
| 61–80 | HIGH |
| 81–100 | CRITICAL |

See [AGENT_PROMPT.md](AGENT_PROMPT.md) for the full master prompt and architecture.
