import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.dirname(__file__))
from prompts import SYSTEM_PROMPT
from tools.scraper import fetch_page
from tools.search import web_search

load_dotenv()

client = OpenAI(
    api_key=os.getenv("TOKENROUTER_API_KEY"),
    base_url=os.getenv("TOKENROUTER_BASE_URL", "https://api.tokenrouter.com/v1"),
)
MODEL = os.getenv("MODEL", "claude-sonnet-4-6")

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": (
                "Search the web for information about a company. "
                "Use targeted queries like '{company} job postings', "
                "'{company} funding', '{company} tech stack', '{company} reviews g2'."
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
            "description": "Fetch and read the text content of a specific URL.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
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


def run_agent(company: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"Research and generate a B2B sales intelligence report for: {company}",
        },
    ]

    for _ in range(12):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            max_tokens=4096,
        )

        choice = response.choices[0]
        msg = choice.message
        messages.append(msg)

        if choice.finish_reason != "tool_calls":
            return msg.content

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            arg_str = ", ".join(f"{k}={repr(v)}" for k, v in args.items())
            print(f"  -> {name}({arg_str})", flush=True)

            fn = TOOL_MAP.get(name)
            result = fn(**args) if fn else {"error": f"Unknown tool: {name}"}

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )

    return "Max iterations reached."


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python src/agent.py <company_or_domain>")
        sys.exit(1)

    company = " ".join(sys.argv[1:])
    print(f"Researching: {company}\n")

    result = run_agent(company)
    print("\n" + "=" * 60)
    print(result)
