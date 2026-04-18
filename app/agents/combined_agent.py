import requests

OLLAMA_URL = "http://localhost:11434/api/generate"


def combined_agent(user_query, sql, sql_result, docs):
    context = "\n\n".join(docs)

    prompt = f"""
You are a senior business analyst.

User Question:
{user_query}

Structured Data:
{sql_result}

SQL Used:
{sql}

Market Context:
{context}

Your job:
1. Explain what is happening (data)
2. Explain why (context)
3. Provide interpretation
4. Give recommendation

Be concise and insightful.
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"]