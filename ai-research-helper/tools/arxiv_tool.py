# Searches arxiv for academic papers — used by Agent 2
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List


@dataclass
class Paper:
    title: str
    authors: List[str]
    abstract: str
    url: str
    published: str

    def format(self) -> str:
        authors_str = ", ".join(self.authors[:3])
        if len(self.authors) > 3:
            authors_str += " et al."
        return (
            f"[PAPER] {self.title}\n"
            f"  Authors: {authors_str} ({self.published})\n"
            f"  URL: {self.url}\n"
            f"  Abstract: {self.abstract[:400]}...\n"
        )


def search_arxiv(query: str, max_results: int = 4) -> List[Paper]:
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": max_results,
        "sortBy": "relevance",
    })
    url = f"http://export.arxiv.org/api/query?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            xml_data = r.read().decode("utf-8")
    except Exception as e:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(xml_data)
    papers = []
    for entry in root.findall("atom:entry", ns):
        title = (entry.find("atom:title", ns).text or "").strip().replace("\n", " ")
        abstract = (entry.find("atom:summary", ns).text or "").strip().replace("\n", " ")
        url = (entry.find("atom:id", ns).text or "").strip()
        published = (entry.find("atom:published", ns).text or "")[:10]
        authors = [
            a.find("atom:name", ns).text
            for a in entry.findall("atom:author", ns)
            if a.find("atom:name", ns) is not None
        ]
        papers.append(Paper(title, authors, abstract, url, published))
    return papers
