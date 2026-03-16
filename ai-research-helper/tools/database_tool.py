# Queries Wikipedia to simulate structured database retrieval — used by Agent 1 and 4
import urllib.request
import urllib.parse
import json
from dataclasses import dataclass
from typing import List


@dataclass
class StructuredRecord:
    source: str
    content: str
    category: str

    def format(self) -> str:
        return f"[STRUCTURED] {self.source} ({self.category})\n  {self.content[:400]}\n"


def query_structured(query: str, max_results: int = 3) -> List[StructuredRecord]:
    results = []
    # search Wikipedia for matching titles
    search_url = (
        "https://en.wikipedia.org/w/api.php?"
        + urllib.parse.urlencode({
            "action": "opensearch",
            "search": query,
            "limit": max_results,
            "format": "json",
        })
    )
    try:
        req = urllib.request.Request(search_url, headers={"User-Agent": "AI-Research-Helper/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            search_data = json.loads(r.read().decode("utf-8"))
        titles = search_data[1][:max_results]
    except Exception:
        return []

    for title in titles:
        summary_url = (
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + urllib.parse.quote(title)
        )
        try:
            req = urllib.request.Request(summary_url, headers={"User-Agent": "AI-Research-Helper/1.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                page = json.loads(r.read().decode("utf-8"))
            extract = page.get("extract", "")
            if extract:
                results.append(StructuredRecord(
                    source=f"Wikipedia: {title}",
                    content=extract[:500],
                    category="encyclopedia/structured",
                ))
        except Exception:
            continue

    return results
