# The 4 specialized retrieval agents — each fetches from a different source, all run in parallel

import asyncio
import ollama
from typing import List

from tools.arxiv_tool import search_arxiv
from tools.web_tool import web_search
from tools.database_tool import query_structured
from config import FAST_MODEL


def _llm_summarize(system: str, user: str) -> str:
    # one-shot LLM call to summarize retrieved content
    response = ollama.chat(
        model=FAST_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    return response.message.content.strip()


# Agent 1: fetches factual data from Wikipedia (simulates SQL database)
async def agent1_structured(query: str, key_aspects: List[str]) -> dict:
    print(f"  Agent 1 (Structured)  → searching...")
    records = await asyncio.to_thread(query_structured, query, max_results=3)

    if not records:
        return {"agent": "Agent 1 (Structured Data)", "query": query,
                "findings": "No structured data found.", "sources": []}

    raw = "\n\n".join(r.format() for r in records)
    aspects = "\n".join(f"- {a}" for a in key_aspects)

    findings = await asyncio.to_thread(
        _llm_summarize,
        "You are a structured data analyst. Summarize factual, statistical findings relevant to the key aspects.",
        f"Key aspects:\n{aspects}\n\nRetrieved records:\n{raw}\n\nSummarize in 3-5 bullet points.",
    )

    print(f"  Agent 1 (Structured)  ✓ {len(records)} records")
    return {
        "agent": "Agent 1 (Structured Data / Wikipedia)",
        "query": query,
        "findings": findings,
        "sources": [r.source for r in records],
    }


# Agent 2: searches academic papers on arxiv
async def agent2_semantic(query: str, key_aspects: List[str]) -> dict:
    print(f"  Agent 2 (Academic)    → searching arxiv...")
    papers = await asyncio.to_thread(search_arxiv, query, max_results=4)

    if not papers:
        return {"agent": "Agent 2 (Academic Papers)", "query": query,
                "findings": "No papers found.", "sources": []}

    raw = "\n\n".join(p.format() for p in papers)
    aspects = "\n".join(f"- {a}" for a in key_aspects)

    findings = await asyncio.to_thread(
        _llm_summarize,
        "You are an academic research analyst. Summarize key insights from papers — methodologies, findings, contributions.",
        f"Key aspects:\n{aspects}\n\nPapers:\n{raw}\n\nSummarize in 3-5 bullet points. Cite paper titles.",
    )

    print(f"  Agent 2 (Academic)    ✓ {len(papers)} papers")
    return {
        "agent": "Agent 2 (Academic Papers / arxiv)",
        "query": query,
        "findings": findings,
        "sources": [p.title[:70] for p in papers],
    }


# Agent 3: retrieves real-time news and web results via DuckDuckGo
async def agent3_web(query: str, key_aspects: List[str]) -> dict:
    print(f"  Agent 3 (Web)         → searching...")
    results = await asyncio.to_thread(web_search, query, max_results=4)

    if not results:
        return {"agent": "Agent 3 (Web Search)", "query": query,
                "findings": "No web results found.", "sources": []}

    raw = "\n\n".join(r.format() for r in results)
    aspects = "\n".join(f"- {a}" for a in key_aspects)

    findings = await asyncio.to_thread(
        _llm_summarize,
        "You are a news analyst. Summarize recent developments, trends, and real-world context from web results.",
        f"Key aspects:\n{aspects}\n\nWeb results:\n{raw}\n\nSummarize in 3-5 bullet points.",
    )

    print(f"  Agent 3 (Web)         ✓ {len(results)} results")
    return {
        "agent": "Agent 3 (Web Search / DuckDuckGo)",
        "query": query,
        "findings": findings,
        "sources": [r.title[:60] for r in results if r.url],
    }


# Agent 4: explores related topics to broaden context (recommendation system)
async def agent4_recommend(topics: List[str], key_aspects: List[str]) -> dict:
    print(f"  Agent 4 (Recommend)   → exploring related topics...")
    related_data = []
    for topic in topics[:2]:
        records = await asyncio.to_thread(query_structured, topic, max_results=1)
        if records:
            related_data.append(records[0].format())

    related = "\n\n".join(related_data) if related_data else "No related data."
    aspects = "\n".join(f"- {a}" for a in key_aspects)

    findings = await asyncio.to_thread(
        _llm_summarize,
        "You are a knowledge graph specialist. Recommend related areas and connections that enrich the research.",
        f"Key aspects:\n{aspects}\n\nRelated topics: {', '.join(topics)}\n\nData:\n{related}\n\nRecommend 3-5 related areas.",
    )

    print(f"  Agent 4 (Recommend)   ✓ done")
    return {
        "agent": "Agent 4 (Recommendations)",
        "query": ", ".join(topics),
        "findings": findings,
        "sources": topics,
    }


# launches all 4 agents at the same time using asyncio.gather()
async def run_all_agents_parallel(plan: dict) -> List[dict]:
    print(f"  Launching all 4 agents in parallel...")

    results = await asyncio.gather(
        agent1_structured(plan["agent1_query"], plan["key_aspects"]),
        agent2_semantic(plan["agent2_query"], plan["key_aspects"]),
        agent3_web(plan["agent3_query"], plan["key_aspects"]),
        agent4_recommend(plan["agent4_topics"], plan["key_aspects"]),
    )

    print(f"  All agents done.\n")
    return list(results)
