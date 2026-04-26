<div align="center">

# DueSight

[![Python](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Tailwind](https://img.shields.io/badge/Tailwind-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Brave Search](https://img.shields.io/badge/search-Brave-FB542B?logo=brave&logoColor=white)](https://brave.com/search/api/)
[![Hackathon](https://img.shields.io/badge/AI%20Agent%20Economy-Hackathon%202026-7C3AED)](#)

**Elite B2B intelligence in ~2 minutes.**

</div>

![DueSight](docs/screenshot.png)

Weblink:https://duesight.vercel.app/

DueSight runs five research agents in parallel — competitive landscape, website, financials, legal/trust, and key people — then streams a consultant-grade 9-section report with a 0-100 risk score and an APPROVED / CONDITIONAL / REJECTED procurement verdict. First content appears at ~50s; full report at ~2:00.

## Quick start

```bash
git clone https://github.com/altimu-agent/duesight.git
cd duesight
cp .env.example .env  # add TOKENROUTER_API_KEY and BRAVE_API_KEY
pip install -r requirements.txt
uvicorn server:app --port 8000 --reload
```

Open http://127.0.0.1:8000.

CLI:

```bash
python src/agent.py "Stripe" --website stripe.com --industry payments
```

## Documentation

- [Architecture](docs/architecture.md) — fan-out / fan-in design, performance, project layout
- [API reference](docs/api.md) — endpoints and SSE event types
- [Report format](docs/report-format.md) — 9-section spec, risk levels, score reconciliation
- [Roadmap](REDESIGN_PLAN.md) — phased work
- [Master prompt](AGENT_PROMPT.md) — system prompt + scoring rules
