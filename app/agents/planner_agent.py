import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def planner_agent(query: str) -> str:
    prompt = f"""
You are an AI planner for a business analyst system.

Your job is to decide which tool(s) are needed to answer the query.

Available tools:
- sql → for numerical, aggregation, database queries
- docs → for explanations, market insights, trends
- combined → when both data AND explanation are required

Decision Rules:
- If query asks for numbers, totals, rankings → sql
- If query asks "why", "reason", "explain" → combined
- If query asks general trends or market insights → docs
- If unsure → use combined

Return ONLY one word:
sql OR docs OR combined

Query:
{query}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        }
    )

    decision = response.json()["response"].strip().lower()

    # -----------------------------
    # Safety Normalization
    # -----------------------------
    if "sql" in decision:
        return "sql"
    elif "docs" in decision:
        return "docs"
    else:
        return "combined"