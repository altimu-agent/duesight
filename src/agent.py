"""DueSight agent — entry point.

Usage:
    python src/agent.py "Acme Field Services" \
        --website acme.com \
        --industry "oil and gas" \
        --country Ecuador \
        --contract-value 500000 \
        --competitors "Halliburton,Schlumberger"
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
from prompts import SYSTEM_PROMPT
from tools.scraper import fetch_page
from tools.search import web_search

load_dotenv()

MODEL = os.getenv("MODEL", "claude-sonnet-4-6")
MAX_ITERATIONS = 12


def _client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv("TOKENROUTER_API_KEY"),
        base_url=os.getenv("TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1"),
    )

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web. Use targeted queries: "
                "'{company} funding crunchbase', '{company} reviews g2', "
                "'{company} lawsuit', '{company} vs <competitor>', "
                "'{industry} top vendors {country}', '{company} CEO linkedin'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "fetch_page",
            "description": "Fetch and read the readable text of a specific URL (homepage, pricing page, news article, etc.).",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL to fetch"}
                },
                "required": ["url"],
            },
        },
    },
]

TOOL_MAP = {
    "web_search": web_search,
    "fetch_page": fetch_page,
}


def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", name.strip().lower())
    return s.strip("_") or "company"


def strip_preamble(report: str) -> str:
    """Trim any model preamble before the first `# DueSight Report` heading.

    The system prompt forbids preamble, but models sometimes emit it anyway.
    This is a deterministic backstop.
    """
    idx = report.find("# DueSight Report")
    if idx <= 0:
        return report.lstrip()
    return report[idx:]


def _level_for(score: int) -> str:
    if score <= 30:
        return "LOW"
    if score <= 60:
        return "MEDIUM"
    if score <= 80:
        return "HIGH"
    return "CRITICAL"


def reconcile_score(report: str) -> tuple[str, dict]:
    """Recompute the risk score from the section-9 table and override JSON if mismatched.

    The model emits section 8 (JSON) before section 9 (table) in output order,
    so it sometimes writes a score that doesn't match its own table arithmetic.
    This re-derives the canonical score from the table — the source of truth —
    and surgically rewrites the JSON's risk_score / risk_level if needed.

    Returns (possibly-corrected report, info dict for logging).
    """
    info: dict = {
        "table_sum": None,
        "clamped": None,
        "json_score_before": None,
        "overrode": False,
    }

    # Locate section 9
    sec9_match = re.search(r"## 9\..*", report, re.DOTALL)
    if not sec9_match:
        return report, info
    sec9 = sec9_match.group(0)

    # Use the LAST scoring table in section 9 (model sometimes emits two if it
    # self-corrects mid-output). Anchor on the column-header row.
    headers = list(re.finditer(r"\|\s*Factor\s*\|\s*Adjustment\s*\|", sec9))
    if not headers:
        return report, info
    table_region = sec9[headers[-1].start():]

    # Match the Adjustment cell only — second pipe-delimited cell on each row.
    # Tolerate bold (`**…**`), unicode minus (U+2212), leading +, and arrow
    # decorations (`→ 0`). Skip header/divider rows.
    adjustments: list[int] = []
    for line in table_region.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        adj_cell = cells[1]
        if "Adjustment" in adj_cell or set(adj_cell) <= set("- :"):
            continue
        # Last signed integer in the cell (handles "→ 0", "**+10**", "−5", etc.)
        m = re.findall(r"[+\-−]?\d+", adj_cell.replace("−", "-"))
        if not m:
            continue
        try:
            adjustments.append(int(m[-1].replace("+", "")))
        except ValueError:
            continue

    if not adjustments:
        return report, info

    table_sum = sum(adjustments)
    clamped = max(0, min(100, table_sum))
    info["table_sum"] = table_sum
    info["clamped"] = clamped

    # Find and (if needed) rewrite the JSON's risk_score.
    score_match = re.search(r'"risk_score"\s*:\s*(\d+)', report)
    if not score_match:
        return report, info
    current = int(score_match.group(1))
    info["json_score_before"] = current

    if current == clamped:
        return report, info

    info["overrode"] = True
    new_report = re.sub(
        r'"risk_score"\s*:\s*\d+',
        f'"risk_score": {clamped}',
        report,
        count=1,
    )
    new_report = re.sub(
        r'"risk_level"\s*:\s*"[^"]+"',
        f'"risk_level": "{_level_for(clamped)}"',
        new_report,
        count=1,
    )
    return new_report, info


DISCOVER_SYSTEM_PROMPT = (
    "You are a competitive intelligence analyst. Given a company, identify the 3 most "
    "relevant DIRECT competitors — companies that sell to similar customers, solve a similar "
    "problem, and would credibly appear in the same buyer's shortlist. Mix incumbents and "
    "modern challengers when both exist.\n\n"
    "Output ONLY a valid JSON object — no markdown fences, no commentary, no preamble. "
    "Format:\n"
    '{"competitors": [{"name": "Acme Co", "tagline": "one-line positioning"}, ...]}'
)


def discover_competitors(
    company: str,
    website: str | None = None,
    industry: str | None = None,
    country: str | None = None,
) -> list[dict]:
    """Fast LLM-only competitor discovery — no tools, ~3-5s.

    Returns a list of {"name": str, "tagline": str}, possibly empty if parsing fails.
    """
    parts = [f"Company: {company}"]
    if website:
        parts.append(f"Website: {website}")
    if industry:
        parts.append(f"Industry: {industry}")
    if country:
        parts.append(f"Country: {country}")
    parts.append("\nReturn the 3 most relevant direct competitors as JSON.")
    user_msg = "\n".join(parts)

    try:
        response = _client().chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": DISCOVER_SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=512,
        )
        raw = (response.choices[0].message.content or "").strip()
    except Exception:
        return []

    # Strip ```json … ``` fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []

    competitors = data.get("competitors") or []
    cleaned: list[dict] = []
    for c in competitors:
        if not isinstance(c, dict):
            continue
        name = (c.get("name") or "").strip()
        if not name:
            continue
        cleaned.append({"name": name, "tagline": (c.get("tagline") or "").strip()})
    return cleaned[:5]


def build_user_message(
    company: str,
    website: str | None,
    industry: str | None,
    country: str | None,
    contract_value: int | None,
    competitors: list[str] | None,
) -> str:
    lines = [f"Generate a full DueSight report for: **{company}**.", "", "Inputs:"]
    lines.append(f"- Company: {company}")
    lines.append(f"- Website: {website or 'not provided — try to discover it'}")
    lines.append(f"- Industry: {industry or 'not provided — infer from research'}")
    lines.append(f"- Country: {country or 'not provided — infer from research'}")
    if contract_value:
        lines.append(f"- Contract value under consideration: ${contract_value:,} USD")
    if competitors:
        lines.append(f"- Known competitors to compare against: {', '.join(competitors)}")
    else:
        lines.append("- Competitors: not provided — infer 2–3 realistic ones")
    lines.append("")
    lines.append(
        "Use your tools to research, then output the full 9-section markdown report exactly as specified in your system instructions."
    )
    return "\n".join(lines)


def run_agent_stream(
    company: str,
    website: str | None = None,
    industry: str | None = None,
    country: str | None = None,
    contract_value: int | None = None,
    competitors: list[str] | None = None,
):
    """Generator: yields events as the agent runs.

    Event shapes:
        {"type": "competitors_discovered", "competitors": [{"name": str, "tagline": str}, ...]}
        {"type": "tool_call", "step": int, "name": str, "args": dict}
        {"type": "tool_result", "step": int, "name": str, "preview": str}
        {"type": "report", "content": str, "score_info": dict}
        {"type": "error", "message": str}
    """
    # Preflight: auto-discover competitors when not provided.
    if not competitors:
        discovered = discover_competitors(company, website, industry, country)
        if discovered:
            yield {"type": "competitors_discovered", "competitors": discovered}
            competitors = [c["name"] for c in discovered]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": build_user_message(
                company, website, industry, country, contract_value, competitors
            ),
        },
    ]
    client = _client()

    for i in range(MAX_ITERATIONS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            max_tokens=8192,
        )

        choice = response.choices[0]
        msg = choice.message
        messages.append(msg)

        if choice.finish_reason != "tool_calls":
            content = msg.content or ""
            content = strip_preamble(content)
            content, score_info = reconcile_score(content)
            yield {"type": "report", "content": content, "score_info": score_info}
            return

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}
            yield {"type": "tool_call", "step": i + 1, "name": name, "args": args}

            fn = TOOL_MAP.get(name)
            try:
                result = fn(**args) if fn else {"error": f"Unknown tool: {name}"}
            except Exception as e:
                result = {"error": f"{type(e).__name__}: {e}"}

            preview = json.dumps(result, ensure_ascii=False)
            if len(preview) > 240:
                preview = preview[:240] + "…"
            yield {
                "type": "tool_result",
                "step": i + 1,
                "name": name,
                "preview": preview,
            }

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    yield {"type": "error", "message": "Max iterations reached without final report."}


def run_agent(**kwargs) -> tuple[str, dict]:
    """Synchronous CLI/test wrapper. Returns (report, score_info).

    Logs tool calls to stderr as a side effect (preserves prior CLI UX).
    """
    final = "Max iterations reached without final report."
    score_info: dict = {}
    for event in run_agent_stream(**kwargs):
        if event["type"] == "tool_call":
            arg_str = ", ".join(f"{k}={v!r}" for k, v in event["args"].items())
            print(
                f"[step {event['step']}] -> {event['name']}({arg_str})",
                file=sys.stderr,
                flush=True,
            )
        elif event["type"] == "report":
            final = event["content"]
            score_info = event["score_info"]
        elif event["type"] == "error":
            print(f"ERROR: {event['message']}", file=sys.stderr)
    return final, score_info


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="duesight",
        description="DueSight — elite B2B intelligence agent (9-section report).",
    )
    p.add_argument("company", help="Company name (e.g. 'Acme Field Services')")
    p.add_argument("--website", help="Company website / domain")
    p.add_argument("--industry", help="Industry (e.g. 'oil and gas')")
    p.add_argument("--country", help="Country (e.g. 'Ecuador')")
    p.add_argument(
        "--contract-value",
        type=int,
        help="Contract value in USD — calibrates risk recommendation",
    )
    p.add_argument(
        "--competitors",
        help="Comma-separated competitor names. If omitted, the agent infers 2–3.",
    )
    p.add_argument(
        "--output-dir",
        default="output",
        help="Directory to save the report (default: output/)",
    )
    p.add_argument(
        "--no-save",
        action="store_true",
        help="Print to stdout only, do not save a file.",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not os.getenv("TOKENROUTER_API_KEY"):
        print(
            "ERROR: TOKENROUTER_API_KEY is not set. Copy .env.example to .env and fill it in.",
            file=sys.stderr,
        )
        sys.exit(2)

    competitors = (
        [c.strip() for c in args.competitors.split(",") if c.strip()]
        if args.competitors
        else None
    )

    print(f"DueSight — researching: {args.company}", file=sys.stderr)
    if args.industry or args.country:
        print(
            f"  industry={args.industry or '?'} | country={args.country or '?'}",
            file=sys.stderr,
        )
    print("", file=sys.stderr)

    report, score_info = run_agent(
        company=args.company,
        website=args.website,
        industry=args.industry,
        country=args.country,
        contract_value=args.contract_value,
        competitors=competitors,
    )
    if score_info.get("overrode"):
        print(
            f"[reconciled] table_sum={score_info['table_sum']} → "
            f"clamped={score_info['clamped']}; "
            f"overrode JSON risk_score (was {score_info['json_score_before']}).",
            file=sys.stderr,
        )

    print("\n" + "=" * 60)
    print(report)

    if not args.no_save:
        os.makedirs(args.output_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(args.output_dir, f"{slugify(args.company)}_{ts}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n[saved] {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
