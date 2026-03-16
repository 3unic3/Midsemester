# AI Research Helper — Multi-Agent Agentic RAG (Section 4.2)
# Coordinator → 4 parallel retrieval agents → Synthesis Agent

import asyncio
import sys

from agents.coordinator import run_coordinator
from agents.specialized_agents import run_all_agents_parallel
from agents.synthesis_agent import run_synthesis_agent
from config import STRONG_MODEL, FAST_MODEL

BANNER = f"""
╔══════════════════════════════════════════════════════════════╗
║        AI Research Helper — Multi-Agent Agentic RAG          ║
╚══════════════════════════════════════════════════════════════╝"""

EXAMPLE_QUESTIONS = [
    "What are the economic and environmental impacts of renewable energy adoption?",
    "How does transformer attention mechanism work and what are its limitations?",
    "What are the main challenges in large language model alignment and safety?",
    "How do multi-agent systems improve AI planning and decision making?",
]

SEP  = "─" * 66
SEP2 = "═" * 66


async def run_pipeline(question: str) -> None:
    print(f"\nQuestion: {question}\n")

    print(f"[Step 1] Coordinator — planning research...")
    plan = run_coordinator(question)

    print(f"\n[Step 2] Retrieval — 4 agents running in parallel...")
    agent_results = await run_all_agents_parallel(plan)

    total_sources = sum(len(r["sources"]) for r in agent_results)
    print(f"  {total_sources} sources collected across all agents.\n")

    print(f"[Step 3] Synthesis — generating answer...\n")
    print("─" * 60)
    run_synthesis_agent(question, plan["key_aspects"], agent_results)
    print("─" * 60)


def main():
    print(BANNER)

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        print("Example questions:")
        for i, q in enumerate(EXAMPLE_QUESTIONS, 1):
            print(f"  {i}. {q}")
        print()
        choice = input("Enter your question (or press 1-4 for an example): ").strip()
        if choice in ("1", "2", "3", "4"):
            question = EXAMPLE_QUESTIONS[int(choice) - 1]
        elif choice:
            question = choice
        else:
            question = EXAMPLE_QUESTIONS[0]

    asyncio.run(run_pipeline(question))


if __name__ == "__main__":
    main()
