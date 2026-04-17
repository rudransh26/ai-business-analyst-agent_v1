import requests

from agents.sql_agent import generate_sql, run_sql, validate_sql, fix_sql
from agents.doc_agent import retrieve_docs

OLLAMA_URL = "http://localhost:11434/api/generate"


def combined_agent(user_query):
    # -----------------------------
    # STEP 1: GET STRUCTURED DATA (SQL)
    # -----------------------------
    sql = generate_sql(user_query)
    print("\nGenerated SQL:\n", sql)

    try:
        validate_sql(sql)
        sql_result = run_sql(sql)

    except Exception as e:
        print("\nSQL Error:", e)

        sql = fix_sql(sql, str(e))
        print("\nFixed SQL:\n", sql)

        sql_result = run_sql(sql)

    # -----------------------------
    # STEP 2: GET DOCUMENT CONTEXT (RAG)
    # -----------------------------
    docs = retrieve_docs(user_query)
    context = "\n\n".join(docs)

    # -----------------------------
    # STEP 3: SYNTHESIS (LLM)
    # -----------------------------
    prompt = f"""
You are a senior business analyst.

User Question:
{user_query}

Structured Data (SQL Result):
{sql_result}

Market Context (Documents):
{context}

Your job:
1. Explain WHAT is happening (data)
2. Explain WHY it is happening (context)
3. Provide business interpretation
4. Suggest actionable recommendation

Rules:
- Be concise but insightful
- Use numbers from data where possible
- Do NOT hallucinate beyond given data

Output format:

📊 Insight:
...

📈 Data Evidence:
...

📄 Market Context:
...

📌 Interpretation:
...

🚀 Recommendation:
...
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"]