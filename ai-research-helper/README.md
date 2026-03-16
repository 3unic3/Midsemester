# AI Research Helper — Multi-Agent Agentic RAG

## Architecture
```
User Query
    │
Coordinator Agent  (analyzes query, creates plan per agent)
  |            |               |             |
Agent 1      Agent 2        Agent 3        Agent 4
Structured   Academic        Web           Recommend
(Wikipedia)  (arxiv)      (DuckDuckGo)   (Wikipedia)

                        │  all run in parallel
                        
                 Synthesis Agent (combines all findings → final answer)

```
## Agents & Tools
**Coordinator Agent** - Analyzes the question, creates a tailored search plan for each agent using tool calling, Ollama LLM 
**Agent 1 — Structured** - Fetches factual and encyclopedic information, Wikipedia REST API 
**Agent 2 — Academic** - Searches peer-reviewed papers by semantic relevance, arxiv API 
**Agent 3 — Web** - Retrieves recent news, policies, real-world data, DuckDuckGo API 
**Agent 4 — Recommend** - Explores related topics to broaden context, Wikipedia + LLM 
**Synthesis Agent** - Reads all 4 agent outputs and writes the final answer (streamed), Ollama LLM 


## Project Structure

```
ai-research-helper/
│
├── main.py                   ← entry point, runs the full pipeline
├── config.py                 ← set your Ollama models here
├── requirements.txt
│
├── agents/
│   ├── coordinator.py        ← Coordinator Agent (tool calling)
│   ├── specialized_agents.py ← all 4 retrieval agents + parallel runner
│   └── synthesis_agent.py    ← Synthesis Agent (streaming)
│
└── tools/
    ├── arxiv_tool.py         ← used by Agent 2
    ├── web_tool.py           ← used by Agent 3
    └── database_tool.py      ← used by Agent 1 & 4
```

---

## Setup

**Requirements:** Python 3.8+, [Ollama](https://ollama.com) installed and running.

```bash
# Install dependencies
pip install -r requirements.txt
```

Configure your models in `config.py`:
```python
STRONG_MODEL = "gpt-oss:120b-cloud"      # coordinator + synthesis
FAST_MODEL   = "ministral-3:8b-cloud"    # 4 parallel agents
```

---

## Usage

```bash
# Interactive — pick from example questions
python3 main.py

# Direct question
python3 main.py "What are the economic and environmental impacts of renewable energy in Europe?"
python3 main.py "How do multi-agent systems improve AI planning?"
python3 main.py "What are the main challenges in LLM alignment and safety?"
```

---

## Example Output

```
Question: What are the economic and environmental impacts of renewable energy in Europe?

[Step 1] Coordinator — planning research...
  Analyzing query...
  Plan ready. Key aspects: 4

[Step 2] Retrieval — 4 agents running in parallel...
  Agent 1 (Structured)  → searching...
  Agent 2 (Academic)    → searching arxiv...
  Agent 3 (Web)         → searching...
  Agent 4 (Recommend)   → exploring related topics...
  Agent 2 (Academic)    ✓ 4 papers
  Agent 4 (Recommend)   ✓ done
  All agents done.

  7 sources collected across all agents.

[Step 3] Synthesis — generating answer...
────────────────────────────────────────────────────
Renewable energy adoption in Europe has delivered...
────────────────────────────────────────────────────
```

---

## Key Ideas from the Paper (Section 4.2)

1. **Modularity** — each agent is independent; add or remove agents without touching others
2. **Parallel Processing** — all 4 agents run simultaneously via `asyncio.gather()`, not one by one
3. **Task Specialization** — each agent is optimized for its domain (structured vs academic vs real-time vs recommendations)
4. **Coordinator Orchestration** — a master agent analyzes the question and creates tailored queries per agent
5. **LLM Synthesis** — the final agent integrates all sources into one coherent, cited answer
