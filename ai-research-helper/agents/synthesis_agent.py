# Synthesis Agent — reads all 4 agent findings and writes the final answer (streamed)

import ollama
from typing import List
from config import STRONG_MODEL


SYNTHESIS_SYSTEM = """You are a research synthesis expert. You receive findings from 4 specialized agents:
- Agent 1: Structured/factual data
- Agent 2: Academic papers
- Agent 3: Recent news and web
- Agent 4: Related topic recommendations

Write a clear, concise answer (3-5 paragraphs). Cite sources inline.
End with a one-line "Key takeaway:"."""


def run_synthesis_agent(
    question: str,
    key_aspects: List[str],
    agent_results: List[dict],
) -> str:
    print(f"  Generating answer...\n")

    # combine all agent findings into one context block
    agent_context = ""
    for result in agent_results:
        agent_context += f"\n{'='*50}\n"
        agent_context += f"{result['agent']} (searched: '{result['query']}')\n"
        agent_context += f"Findings:\n{result['findings']}\n"
        if result["sources"]:
            agent_context += f"Sources: {', '.join(str(s) for s in result['sources'][:3])}\n"

    aspects_str = "\n".join(f"- {a}" for a in key_aspects)

    user_message = (
        f"Research Question: {question}\n\n"
        f"Key aspects to address:\n{aspects_str}\n\n"
        f"Agent Findings:\n{agent_context}\n\n"
        f"Synthesize a comprehensive answer integrating all sources."
    )

    full_response = []

    # stream tokens so the user sees the answer as it's written
    for chunk in ollama.chat(
        model=STRONG_MODEL,
        messages=[
            {"role": "system", "content": SYNTHESIS_SYSTEM},
            {"role": "user", "content": user_message},
        ],
        stream=True,
    ):
        token = chunk.message.content
        if token:
            print(token, end="", flush=True)
            full_response.append(token)

    print()  # final newline
    return "".join(full_response)
