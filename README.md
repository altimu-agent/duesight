# hackathon-agent

Agente B2B de sales intelligence para el AI Agent Economy Hackathon (abril 2026).

## Qué hace

Dado un dominio/empresa, genera un reporte con:
- Señales de compra (job postings, funding, tech stack)
- Objeciones comunes
- Pitch personalizado

## Stack

- Python 3
- TokenRouter como LLM endpoint (OpenAI-compatible)
- `https://api.tokenrouter.com/v1`

## Setup

```bash
cp .env.example .env
# Editar .env con tu TOKENROUTER_API_KEY
pip install -r requirements.txt
python src/agent.py example.com
```
