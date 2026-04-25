# Vendor & Supplier Due Diligence Agent — Build Prompt

## Overview

Build an AI agent that automates vendor/supplier due diligence for B2B companies. Given a company name and industry context, the agent researches public sources and produces a structured risk assessment report that would otherwise take a procurement team 2-3 weeks to compile manually.

The target customer is a procurement or operations manager at a mid-size company (50-500 employees) who needs to evaluate 20-50 vendors per year before signing contracts. Today they do this manually: Google searches, LinkedIn lookups, government registry checks, reference calls. The agent replaces 80% of that work in under 5 minutes.

---

## What the Agent Does

Given input like:
```
Company: Acme Field Services
Industry: Oil & gas field services
Country: Ecuador
Contract value: $500,000
```

The agent:
1. Searches for the company across public web sources
2. Checks business registries (government databases, LinkedIn, Crunchbase, etc.)
3. Looks for legal issues, news, negative signals
4. Assesses financial health indicators (funding, revenue signals, employee count trends)
5. Checks certifications (ISO, industry-specific)
6. Identifies key personnel and their backgrounds
7. Produces a structured JSON + human-readable report with a risk score (0-100)

---

## Tools the Agent Must Have

- **Web search** — search for company name + news, reviews, incidents
- **Web scraping / fetch** — extract structured data from LinkedIn, company websites, government registries
- **Structured output** — produce a JSON report + markdown summary

---

## Output Format

The agent must return a report with these sections:

```json
{
  "company": "Acme Field Services",
  "risk_score": 72,
  "risk_level": "MEDIUM",
  "summary": "One-paragraph executive summary",
  "sections": {
    "identity": {
      "legal_name": "",
      "country": "",
      "registration_number": "",
      "founded_year": "",
      "employee_count": "",
      "website": ""
    },
    "financial_health": {
      "signals": [],
      "funding_history": [],
      "revenue_estimate": "",
      "red_flags": []
    },
    "legal_compliance": {
      "certifications": [],
      "lawsuits_or_sanctions": [],
      "regulatory_violations": [],
      "red_flags": []
    },
    "reputation": {
      "news_sentiment": "",
      "reviews": [],
      "notable_clients": [],
      "red_flags": []
    },
    "key_personnel": [
      {
        "name": "",
        "role": "",
        "linkedin": "",
        "background_notes": ""
      }
    ],
    "recommendation": {
      "verdict": "APPROVED | CONDITIONAL | REJECTED",
      "conditions": [],
      "next_steps": []
    }
  },
  "sources": []
}
```

---

## Risk Score Logic

- **0-30**: Low risk — proceed with standard contract
- **31-60**: Medium risk — request additional documentation
- **61-80**: High risk — escalate to legal review
- **81-100**: Critical risk — do not proceed

Risk score factors (weighted):
- No online presence or recent activity: +20
- Negative news or lawsuits: +15 per incident
- No certifications for the required industry: +10
- Key personnel with questionable history: +10
- Less than 2 years in operation: +10
- Positive client references found: -10
- ISO or equivalent certifications verified: -10
- Strong LinkedIn presence and employee growth: -5

---

## Tech Stack

- **Language:** Python 3
- **LLM:** Claude claude-sonnet-4-6 via TokenRouter (OpenAI-compatible endpoint)
  - Base URL: `https://api.tokenrouter.com/v1`
  - Use the `openai` Python SDK pointing to this base URL
- **Tools implemented as Python functions** passed to the LLM as tool_use
- **No frameworks** — raw OpenAI SDK tool loop

---

## Agent Architecture

```
User Input (company name + context)
        ↓
[Agent Loop]
  LLM decides which tool to call
        ↓
  Tools: web_search() | fetch_page() | extract_structured_data()
        ↓
  LLM synthesizes findings into report sections
        ↓
Final Report (JSON + markdown)
```

The agent loop must:
1. Run up to 10 tool calls per report
2. Prioritize: identity verification → legal/compliance → financials → reputation → personnel
3. Stop early if critical red flags are found and explain why
4. Always produce a complete report even with partial data (mark fields as "not found" rather than failing)

---

## Entry Point

```bash
python src/agent.py "Acme Field Services" --industry "oil and gas" --country "Ecuador" --contract-value 500000
```

Output is printed to stdout as markdown and saved to `output/<company_slug>_report.md`.

---

## Demo Script (for hackathon presentation)

The live demo should show:
1. Run the agent against a real company name (have 2-3 examples ready)
2. Show the agent making tool calls in real time (stream tool use to terminal)
3. Present the final report — risk score, verdict, key findings
4. Emphasize: "This replaces 2-3 weeks of manual work. Businesses pay $30K to consultants for this. Our agent does it in 4 minutes."

Suggested demo companies:
- A well-known company (low risk, expected result) — validates correctness
- A company with some red flags in public records — shows the agent catches real issues
- A fictitious or minimal-presence company — shows graceful handling of unknowns

---

## What Success Looks Like

- Agent produces a complete, structured report in under 5 minutes
- Risk score is explainable (each factor traced to a source)
- The demo makes a judge say "I would pay for this"
- Code is clean enough to walk through in a 2-minute code review during demo

---

## Non-Goals (don't build these for the hackathon)

- Authentication / multi-user support
- Database persistence
- UI / frontend
- Paid data sources (Dun & Bradstreet, etc.) — public sources only
- Multi-language support — English output is fine

---

## Context for the Builder

This agent is being built for the **AI Agent Economy Hackathon** (San Francisco, April 2026), hosted by TokenRouter, BotLearn, and AgentHansa. The judging criteria are:

1. Does it solve a real B2B problem?
2. Would a business pay $500/month for this?
3. Is the demo clear and convincing in under 2 minutes?

The builder has domain expertise in **oil & gas field operations** and **ERP systems** (AltimuERP). Use this context to make the demo examples compelling and industry-specific. The agent should feel like it was built by someone who understands procurement pain in industrial operations — not a generic demo.
