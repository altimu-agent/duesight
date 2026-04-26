import os

import httpx

BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web via the Brave Search API.

    Returns a list of {title, url, snippet} dicts. On error, returns a single
    {"error": "..."} item so the agent can decide whether to retry.
    """
    api_key = os.getenv("BRAVE_API_KEY")
    if not api_key:
        return [{"error": "BRAVE_API_KEY is not set in .env"}]

    try:
        resp = httpx.get(
            BRAVE_ENDPOINT,
            params={"q": query, "count": max_results},
            headers={
                "X-Subscription-Token": api_key,
                "Accept": "application/json",
            },
            timeout=10,
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        return [{"error": f"Brave API {e.response.status_code}: {e.response.text[:200]}"}]
    except Exception as e:
        return [{"error": f"{type(e).__name__}: {e}"}]

    items = (resp.json().get("web") or {}).get("results") or []
    results = [
        {
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("description", ""),
        }
        for item in items[:max_results]
    ]
    return results or [{"message": "No results found"}]
