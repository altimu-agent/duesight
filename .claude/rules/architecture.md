# Architecture

## Stack
- Python 3
- OpenAI SDK pointing to TokenRouter
- `src/agent.py` — main entry point
- `src/tools/` — agent tools (web search, scraping)

## Flow
1. Input: domain/company
2. Tools: searches for signals (job postings, LinkedIn, G2, web)
3. LLM: synthesizes into structured report
4. Output: JSON + human-readable text
