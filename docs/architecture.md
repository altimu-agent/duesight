# Architecture

DueSight is a fan-out / fan-in agent — not a single iterative loop. This is what makes it fast.

```
                   ┌──────────────────────────┐
                   │  Discover competitors    │  preflight LLM call (~5s)
                   └────────────┬─────────────┘
                                │
        ┌──────────┬────────────┼────────────┬──────────┐
        ▼          ▼            ▼            ▼          ▼
   ┌────────┐ ┌────────┐  ┌─────────┐  ┌──────────┐ ┌───────┐
   │Company │ │Compet- │  │ Website │  │Financials│ │Trust &│   5 sub-agents
   │& people│ │ itors  │  │   &     │  │          │ │ legal │   in parallel
   │        │ │        │  │messaging│  │          │ │       │   (~45s wall)
   └───┬────┘ └───┬────┘  └────┬────┘  └─────┬────┘ └───┬───┘
       │          │            │             │          │
       └──────────┴────────────┼─────────────┴──────────┘
                               │
                  ┌────────────┴────────────┐
                  │      Reduce step        │
                  │  3 parallel chunks,     │  streaming
                  │  streamed token-by-token│  (~75s wall)
                  └────────────┬────────────┘
                               │
                  ┌────────────▼────────────┐
                  │   Score reconciliation  │  table sum, clamp [0,100]
                  └────────────┬────────────┘
                               │
                               ▼
                  9-section markdown report
```

Each sub-agent has its own LLM loop bounded to 3 tool batches and a 60-second deadline (`asyncio.wait_for`). One slow dimension cannot stall the others — `asyncio.gather(return_exceptions=True)` guarantees the reduce step always runs with whatever evidence finished in time.

The reduce step is also fan-out: the 9-section report is split into 3 chunks (sections 1-3, 4-7, 8-9) generated in parallel with `stream=True` and streamed token-by-token to the client.

## Performance

| Variant | Search backend | Wall time | Time to first content |
|---|---|---:|---:|
| v1 — single loop | DuckDuckGo HTML (timing out) | ~5:30 | ~5:30 |
| v2 — single loop | Brave Search API | ~3:25 | ~3:25 |
| **v3 — fan-out + streaming reduce** | Brave Search API | **~2:00** | **~50s** |

## Project layout

```
.
├── server.py                # FastAPI app + SSE endpoint
├── src/
│   ├── agent.py             # CLI + run_agent_stream wrapper + score reconciliation
│   ├── orchestrator.py      # async fan-out: sub-agents + streaming reduce
│   ├── prompts.py           # SYSTEM_PROMPT + SUBAGENT_SYSTEM_PROMPT
│   └── tools/
│       ├── search.py        # Brave Search API
│       └── scraper.py       # httpx + BeautifulSoup page fetcher
├── static/
│   ├── index.html           # markup only
│   ├── styles.css           # all styles
│   └── app.js               # form, SSE consumer, dimension cards, streaming render
├── docs/                    # this folder
├── REDESIGN_PLAN.md         # phased work + rationale
├── AGENT_PROMPT.md          # full master prompt + scoring spec
└── .env.example             # required env vars
```
