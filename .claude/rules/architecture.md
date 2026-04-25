# Arquitectura

## Stack
- Python 3
- OpenAI SDK apuntando a TokenRouter
- `src/agent.py` — punto de entrada principal
- `src/tools/` — tools del agente (web search, scraping)

## Flujo
1. Input: dominio/empresa
2. Tools: busca señales (job postings, LinkedIn, G2, web)
3. LLM: sintetiza en reporte estructurado
4. Output: JSON + texto legible
