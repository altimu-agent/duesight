import httpx
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Search the web using DuckDuckGo and return a list of {title, url, snippet}."""
    try:
        resp = httpx.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers=HEADERS,
            timeout=15,
            follow_redirects=True,
        )
        resp.raise_for_status()
    except Exception as e:
        return [{"error": str(e)}]

    soup = BeautifulSoup(resp.text, "html.parser")
    results = []

    for div in soup.find_all("div", class_="result", limit=max_results):
        title_el = div.find("a", class_="result__a")
        snippet_el = div.find("a", class_="result__snippet")
        if not title_el:
            continue
        results.append({
            "title": title_el.get_text(strip=True),
            "url": title_el.get("href", ""),
            "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
        })

    return results if results else [{"message": "No results found"}]
