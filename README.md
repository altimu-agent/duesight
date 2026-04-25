# hackathon-agent

B2B sales intelligence agent for the AI Agent Economy Hackathon (April 2026).

## What it does

Given a domain/company, it generates a report with:
- Buying signals (job postings, funding, tech stack)
- Common objections
- Personalized pitch

## Stack

- Python 3
- TokenRouter as LLM endpoint (OpenAI-compatible)
- `https://api.tokenrouter.com/v1`

## Setup

```bash
cp .env.example .env
# Edit .env with your TOKENROUTER_API_KEY
pip install -r requirements.txt
python src/agent.py example.com
```
