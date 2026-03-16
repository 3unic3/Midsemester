# Coordinator Agent — analyzes the question and creates a search plan for each agent

import ollama
from config import STRONG_MODEL

COORDINATOR_SYSTEM = """You are a master coordinator agent for a multi-domain research system.
Your job is to analyze a research question and create a delegation plan.

You manage 4 specialized agents:
- Agent 1 (Structured Data): Queries encyclopedias and factual databases. Best for definitions, statistics, overviews.
- Agent 2 (Academic Papers): Searches arxiv for peer-reviewed research. Best for technical details, methodologies.
- Agent 3 (Web Search): Finds recent news, policies, reports. Best for current events and trends.
- Agent 4 (Recommendations): Suggests related topics. Best for broadening context.

Create targeted search queries for each agent. Always call the create_delegation_plan tool."""

DELEGATION_TOOL = {
    "type": "function",
    "function": {
        "name": "create_delegation_plan",
        "description": "Create a delegation plan for the 4 specialized retrieval agents.",
        "parameters": {
            "type": "object",
            "properties": {
                "agent1_query": {
                    "type": "string",
                    "description": "Query for Agent 1 (Structured Data / Wikipedia). Focus on factual, statistical aspects.",
                },
                "agent2_query": {
                    "type": "string",
                    "description": "Query for Agent 2 (Academic Papers / arxiv). Focus on technical and research aspects.",
                },
                "agent3_query": {
                    "type": "string",
                    "description": "Query for Agent 3 (Web Search). Focus on recent news, policy, trends.",
                },
                "agent4_topics": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "2-3 related topics for Agent 4 (Recommendations) to explore.",
                },
                "key_aspects": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-4 key aspects the final answer must address.",
                },
            },
            "required": ["agent1_query", "agent2_query", "agent3_query", "agent4_topics", "key_aspects"],
        },
    },
}


def run_coordinator(question: str) -> dict:
    print(f"  Analyzing query...")

    response = ollama.chat(
        model=STRONG_MODEL,
        messages=[
            {"role": "system", "content": COORDINATOR_SYSTEM},
            {"role": "user", "content": f"Research question: {question}"},
        ],
        tools=[DELEGATION_TOOL],
    )

    if response.message.tool_calls:
        plan = response.message.tool_calls[0].function.arguments
        print(f"  Plan ready. Key aspects: {len(plan['key_aspects'])}")
        return plan

    # fallback if model didn't call the tool
    print("  Using fallback plan.")
    return {
        "agent1_query": question,
        "agent2_query": question,
        "agent3_query": question,
        "agent4_topics": [question],
        "key_aspects": [question],
    }
