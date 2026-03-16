# Web search via DuckDuckGo Instant Answer API — used by Agent 3
import urllib.request
import urllib.parse
import json
from dataclasses import dataclass
from typing import List


@dataclass
class WebResult:
    title: str
    snippet: str
    url: str

    def format(self) -> str:
        return f"[WEB] {self.title}\n  {self.snippet}\n  Source: {self.url}\n"


def web_search(query: str, max_results: int = 4) -> List[WebResult]:
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "no_html": "1",
        "skip_disambig": "1",
    })
    url = f"https://api.duckduckgo.com/?{params}"
    results = []
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "AI-Research-Helper/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
    except Exception:
        return []

    # main result
    if data.get("Abstract"):
        results.append(WebResult(
            title=data.get("Heading", query),
            snippet=data["Abstract"][:400],
            url=data.get("AbstractURL", ""),
        ))

    # related topics
    for topic in data.get("RelatedTopics", [])[:max_results]:
        if isinstance(topic, dict) and topic.get("Text"):
            results.append(WebResult(
                title=topic.get("Text", "")[:60],
                snippet=topic.get("Text", "")[:300],
                url=topic.get("FirstURL", ""),
            ))
        if len(results) >= max_results:
            break

    return results
