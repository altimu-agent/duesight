"""Parallel research orchestrator: plan → fan-out (5 sub-agents) → reduce.

Replaces the single-loop iterative agent with a fan-out/fan-in design:
each research dimension runs as its own bounded sub-agent in parallel,
then a single reduce call synthesizes the 9-section report from their findings.
"""

import asyncio
import json
import os
import re
from typing import Any, AsyncGenerator

from openai import AsyncOpenAI

from prompts import SUBAGENT_SYSTEM_PROMPT, SYSTEM_PROMPT
from tools.scraper import fetch_page
from tools.search import web_search

MODEL = os.getenv("MODEL", "claude-sonnet-4-6")

# Budgets — see REDESIGN_PLAN.md for rationale.
SUBAGENT_BUDGET_S = 60.0
SUBAGENT_MAX_BATCHES = 3
LLM_TIMEOUT_S = 50.0          # per LLM call inside a sub-agent
REDUCE_BUDGET_S = 200.0       # reduce produces an 8K-token report
REDUCE_LLM_TIMEOUT_S = 180.0  # per LLM call for the reduce step

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web. Use targeted, specific queries.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "Fetch and read the readable text of a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string", "description": "Full URL to fetch"}},
                "required": ["url"],
            },
        },
    },
]
TOOL_MAP = {"web_search": web_search, "fetch_page": fetch_page}

DIMENSIONS = [
    {
        "key": "company",
        "label": "Company & people",
        "brief": (
            "Confirm identity (legal name, founding year, HQ, employee count) and key personnel "
            "(CEO, founders). Try queries like '{company} crunchbase', '{company} CEO linkedin', "
            "'{company} founders'."
        ),
    },
    {
        "key": "competitors",
        "label": "Competitor landscape",
        "brief": (
            "Identify the 2-3 most relevant DIRECT competitors and their positioning. "
            "Try '{company} vs', '{industry} top vendors {country}', '{company} alternatives'."
        ),
    },
    {
        "key": "website",
        "label": "Website & messaging",
        "brief": (
            "Fetch the homepage at {website} (or discover it). Analyze first impression, headline, "
            "value prop, CTAs, trust signals, friction. Optionally fetch /pricing or /about."
        ),
    },
    {
        "key": "financials",
        "label": "Financial signals",
        "brief": (
            "Funding history, revenue estimate, recent layoffs or down rounds, growth signals. "
            "Try '{company} funding crunchbase', '{company} revenue', '{company} layoffs', "
            "'{company} acquired'."
        ),
    },
    {
        "key": "trust",
        "label": "Legal & reputation",
        "brief": (
            "Lawsuits, sanctions, regulatory issues, customer reviews, news sentiment, certifications. "
            "Try '{company} lawsuit', '{company} reviews g2', '{company} news', '{company} fraud', "
            "'{company} certifications'."
        ),
    },
]


def _client(timeout_s: float = LLM_TIMEOUT_S) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=os.getenv("TOKENROUTER_API_KEY"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1"),
        timeout=timeout_s,
        max_retries=0,  # we own the retry/budget logic; SDK retries silently double timeouts
    )


class StepCounter:
    """Monotonic step counter shared across all sub-agents for the global tool_call stream."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._n = 0

    async def next(self) -> int:
        async with self._lock:
            self._n += 1
            return self._n


async def _exec_tool(name: str, args: dict) -> Any:
    fn = TOOL_MAP.get(name)
    if not fn:
        return {"error": f"Unknown tool: {name}"}
    try:
        return await asyncio.to_thread(fn, **args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def _parse_subagent_json(content: str, sources_seen: list[str]) -> dict:
    """Parse the sub-agent's JSON output, tolerating fences and stray text."""
    raw = re.sub(r"^```(?:json)?\s*", "", content.strip())
    raw = re.sub(r"\s*```$", "", raw)
    # If there's prose around the JSON, try to find the first {...} block.
    if not raw.startswith("{"):
        m = re.search(r"\{[\s\S]+\}", raw)
        if m:
            raw = m.group(0)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "summary": (content or "")[:400],
            "findings": [],
            "sources": list(sources_seen),
            "red_flags": [],
        }
    sources = list(set((data.get("sources") or []) + sources_seen))
    return {
        "summary": data.get("summary", "") or "",
        "findings": list(data.get("findings") or []),
        "sources": sources,
        "red_flags": list(data.get("red_flags") or []),
    }


async def _run_subagent(
    dim: dict,
    inputs: dict,
    queue: asyncio.Queue,
    counter: StepCounter,
) -> dict:
    """Run one research dimension to completion (or until SUBAGENT_MAX_BATCHES).

    Returns a result dict with keys: key, label, status, summary, findings, sources, red_flags.
    """
    label = dim["label"]
    brief = dim["brief"].format(
        company=inputs.get("company", ""),
        website=inputs.get("website") or "(unknown)",
        industry=inputs.get("industry") or "(unknown)",
        country=inputs.get("country") or "(unknown)",
    )

    user_msg = (
        f"Dimension: {label}\n"
        f"Brief: {brief}\n\n"
        f"Inputs:\n"
        f"- Company: {inputs.get('company')}\n"
        f"- Website: {inputs.get('website') or 'unknown'}\n"
        f"- Industry: {inputs.get('industry') or 'unknown'}\n"
        f"- Country: {inputs.get('country') or 'unknown'}\n\n"
        f"Make at most {SUBAGENT_MAX_BATCHES} batches of tool calls, then return your JSON findings."
    )

    messages: list[dict] = [
        {"role": "system", "content": SUBAGENT_SYSTEM_PROMPT},
        {"role": "user", "content": user_msg},
    ]
    client = _client()
    sources_seen: list[str] = []

    for _ in range(SUBAGENT_MAX_BATCHES):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=TOOLS,
                max_tokens=4096,
            )
        except Exception as e:
            return {
                "key": dim["key"], "label": label, "status": "error",
                "message": f"LLM call failed: {type(e).__name__}: {e}",
                "summary": "", "findings": [], "sources": sources_seen, "red_flags": [],
            }

        choice = response.choices[0]
        msg = choice.message
        messages.append(msg)

        if choice.finish_reason != "tool_calls":
            parsed = _parse_subagent_json(msg.content or "", sources_seen)
            return {"key": dim["key"], "label": label, "status": "ok", **parsed}

        tool_calls = msg.tool_calls or []

        async def _emit_and_run(tc):
            try:
                args = json.loads(tc.function.arguments) if tc.function.arguments else {}
            except json.JSONDecodeError:
                args = {}
            if tc.function.name == "fetch_page" and args.get("url"):
                sources_seen.append(args["url"])
            step = await counter.next()
            await queue.put({
                "type": "tool_call",
                "step": step,
                "name": tc.function.name,
                "args": args,
                "dimension": dim["key"],
            })
            result = await _exec_tool(tc.function.name, args)
            preview = json.dumps(result, ensure_ascii=False)
            if len(preview) > 240:
                preview = preview[:240] + "…"
            await queue.put({
                "type": "tool_result",
                "step": step,
                "name": tc.function.name,
                "preview": preview,
                "dimension": dim["key"],
            })
            return tc, result

        results = await asyncio.gather(*[_emit_and_run(tc) for tc in tool_calls])
        for tc, result in results:
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

    # Batches exhausted — force a JSON summary call without tools.
    messages.append({
        "role": "user",
        "content": "Stop. Return your findings as JSON now using only what you've gathered above.",
    })
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=2048,
        )
        parsed = _parse_subagent_json(
            response.choices[0].message.content or "", sources_seen
        )
        return {"key": dim["key"], "label": label, "status": "ok", **parsed}
    except Exception as e:
        return {
            "key": dim["key"], "label": label, "status": "error",
            "message": f"Final synthesis failed: {type(e).__name__}: {e}",
            "summary": "", "findings": [], "sources": sources_seen, "red_flags": [],
        }


async def _run_subagent_with_deadline(
    dim: dict, inputs: dict, queue: asyncio.Queue, counter: StepCounter,
) -> dict:
    await queue.put({
        "type": "dimension_started",
        "dimension": dim["key"],
        "label": dim["label"],
    })
    try:
        result = await asyncio.wait_for(
            _run_subagent(dim, inputs, queue, counter),
            timeout=SUBAGENT_BUDGET_S,
        )
        await queue.put({
            "type": "dimension_completed",
            "dimension": dim["key"],
            "status": result["status"],
            "summary_preview": (result.get("summary") or "")[:160],
        })
        return result
    except asyncio.TimeoutError:
        await queue.put({
            "type": "dimension_timeout",
            "dimension": dim["key"],
            "elapsed_s": SUBAGENT_BUDGET_S,
        })
        return {
            "key": dim["key"], "label": dim["label"], "status": "timeout",
            "summary": f"Research timed out after {SUBAGENT_BUDGET_S:.0f}s.",
            "findings": [], "sources": [], "red_flags": [],
        }


def _build_findings_dump(results: list[dict]) -> str:
    parts = ["# Research findings from parallel sub-agents", ""]
    for r in results:
        parts.append(f"## {r['label']} — status: {r['status']}")
        parts.append(f"Summary: {r.get('summary') or '(none)'}")
        if r.get("findings"):
            parts.append("Findings:")
            parts.extend(f"- {f}" for f in r["findings"])
        if r.get("red_flags"):
            parts.append("Red flags:")
            parts.extend(f"- {f}" for f in r["red_flags"])
        if r.get("sources"):
            parts.append("Sources:")
            parts.extend(f"- {s}" for s in r["sources"][:8])
        parts.append("")
    return "\n".join(parts)


def _build_reduce_user_message(inputs: dict, findings_dump: str) -> str:
    lines = [
        f"Generate the full DueSight 9-section report for: **{inputs['company']}**.",
        "",
        "Inputs:",
        f"- Company: {inputs['company']}",
        f"- Website: {inputs.get('website') or 'not provided'}",
        f"- Industry: {inputs.get('industry') or 'not provided'}",
        f"- Country: {inputs.get('country') or 'not provided'}",
    ]
    if inputs.get("contract_value"):
        lines.append(f"- Contract value: ${inputs['contract_value']:,} USD")
    if inputs.get("competitors"):
        lines.append(f"- Competitors: {', '.join(inputs['competitors'])}")
    lines += [
        "",
        "Research findings from 5 parallel sub-agents are below. Synthesize the report using ONLY "
        "this evidence — do NOT request more research, do NOT call any tools. For dimensions with "
        "status 'timeout' or 'error', write 'not found' in the corresponding sections.",
        "",
        findings_dump,
        "",
        "Produce the full 9-section markdown report exactly as specified in your system instructions.",
    ]
    return "\n".join(lines)


REDUCE_CHUNKS = [
    {
        "key": "snapshot_competitive",
        "label": "Snapshot & competitors",
        "instruction": (
            "OUTPUT ONLY sections 1-3 of the DueSight report. Start your output with "
            "`# DueSight Report — <Company>` exactly, then continue through section 3. "
            "End your output immediately after section 3's `--------------------------------------------------` divider. "
            "Do NOT generate sections 4-9 — those are produced by other workers."
        ),
    },
    {
        "key": "website_growth",
        "label": "Website & growth",
        "instruction": (
            "OUTPUT ONLY sections 4-7 of the DueSight report. Your first line MUST be "
            "`## 4. WEBSITE & CONVERSION ANALYSIS` — do NOT include the `# DueSight Report` H1, "
            "do NOT include sections 1-3, do NOT add any preamble. Continue through section 7. "
            "End immediately after section 7's `--------------------------------------------------` divider. "
            "Do NOT generate sections 8-9."
        ),
    },
    {
        "key": "due_diligence",
        "label": "Due diligence & scoring",
        "instruction": (
            "OUTPUT ONLY sections 8-9 of the DueSight report. Your first line MUST be "
            "`## 8. DUE DILIGENCE REPORT (STRUCTURED JSON)` — do NOT include the `# DueSight Report` H1, "
            "do NOT include sections 1-7, do NOT add any preamble. Continue through section 9. "
            "RULE 2 still applies: the section 8 risk_score MUST equal the clamped sum of section 9's table."
        ),
    },
]


async def _run_reduce_chunk(
    chunk: dict, inputs: dict, results: list[dict], queue: asyncio.Queue,
) -> str | None:
    """Stream one chunk of the report. Emits reduce_chunk_delta events as text arrives."""
    user_msg = _build_reduce_user_message(inputs, _build_findings_dump(results))
    user_msg += f"\n\n{chunk['instruction']}"

    await queue.put({
        "type": "reduce_chunk_started",
        "chunk": chunk["key"],
        "label": chunk["label"],
    })

    client = _client(timeout_s=REDUCE_LLM_TIMEOUT_S)
    parts: list[str] = []
    try:
        stream = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=4096,
            stream=True,
        )
        async for resp_chunk in stream:
            if not resp_chunk.choices:
                continue
            delta = resp_chunk.choices[0].delta.content
            if delta:
                parts.append(delta)
                await queue.put({
                    "type": "reduce_chunk_delta",
                    "chunk": chunk["key"],
                    "text": delta,
                })
    except Exception as e:
        await queue.put({
            "type": "reduce_chunk_error",
            "chunk": chunk["key"],
            "message": f"{type(e).__name__}: {e}",
        })
        return None

    content = "".join(parts).strip()
    await queue.put({
        "type": "reduce_chunk_completed",
        "chunk": chunk["key"],
        "char_count": len(content),
    })
    return content


async def _run_reduce(inputs: dict, results: list[dict], queue: asyncio.Queue) -> str:
    """Fan-out reduce: 3 chunks generated in parallel, streamed, then concatenated."""
    await queue.put({"type": "reduce_started"})

    chunk_tasks = [
        asyncio.create_task(_run_reduce_chunk(c, inputs, results, queue))
        for c in REDUCE_CHUNKS
    ]
    chunk_contents = await asyncio.gather(*chunk_tasks)

    if any(c is None for c in chunk_contents):
        # At least one chunk failed; concatenate what succeeded with a placeholder.
        parts = []
        for chunk, content in zip(REDUCE_CHUNKS, chunk_contents):
            if content is None:
                parts.append(f"\n\n## ⚠️ {chunk['label']} unavailable — chunk failed.\n")
            else:
                parts.append(content)
        return "\n\n".join(parts)

    return "\n\n".join(chunk_contents)


_QUEUE_SENTINEL = object()


async def orchestrate(
    company: str,
    website: str | None = None,
    industry: str | None = None,
    country: str | None = None,
    contract_value: int | None = None,
    competitors: list[str] | None = None,
    discover_competitors_fn=None,  # injected to avoid agent.py ↔ orchestrator.py cycle
) -> AsyncGenerator[dict, None]:
    """Async event generator. Yields the same shapes as the old run_agent_stream
    plus dimension_*/reduce_started events.

    The caller is expected to apply strip_preamble + reconcile_score on the
    final 'report' event content (this module emits 'report_raw' instead and
    lets the caller post-process — keeps reconciliation logic in one place).
    """
    inputs = {
        "company": company,
        "website": website,
        "industry": industry,
        "country": country,
        "contract_value": contract_value,
    }

    queue: asyncio.Queue = asyncio.Queue()
    counter = StepCounter()

    async def _runner() -> None:
        try:
            # Preflight competitor discovery (sync function, reuse via to_thread).
            if not competitors and discover_competitors_fn is not None:
                disc = await asyncio.to_thread(
                    discover_competitors_fn, company, website, industry, country
                )
                if disc:
                    await queue.put({"type": "competitors_discovered", "competitors": disc})
                    inputs["competitors"] = [c["name"] for c in disc]
                else:
                    inputs["competitors"] = []
            else:
                inputs["competitors"] = competitors or []

            # Fan-out: 5 sub-agents in parallel, each with its own deadline.
            sub_tasks = [
                asyncio.create_task(
                    _run_subagent_with_deadline(dim, inputs, queue, counter)
                )
                for dim in DIMENSIONS
            ]
            results = await asyncio.gather(*sub_tasks, return_exceptions=False)

            # Reduce: single LLM call, no tools.
            try:
                report = await asyncio.wait_for(
                    _run_reduce(inputs, results, queue), timeout=REDUCE_BUDGET_S
                )
            except asyncio.TimeoutError:
                await queue.put({
                    "type": "error",
                    "message": f"Reduce step timed out after {REDUCE_BUDGET_S:.0f}s.",
                })
                return
            except Exception as e:
                await queue.put({
                    "type": "error",
                    "message": f"Reduce failed: {type(e).__name__}: {e}",
                })
                return

            await queue.put({"type": "report_raw", "content": report})
        except Exception as e:
            await queue.put({
                "type": "error",
                "message": f"Orchestrator failed: {type(e).__name__}: {e}",
            })
        finally:
            await queue.put(_QUEUE_SENTINEL)

    runner = asyncio.create_task(_runner())
    try:
        while True:
            ev = await queue.get()
            if ev is _QUEUE_SENTINEL:
                break
            yield ev
    finally:
        if not runner.done():
            runner.cancel()
        try:
            await runner
        except (asyncio.CancelledError, Exception):
            pass
