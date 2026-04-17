import requests
from sqlalchemy import text
from db.connection import engine
import os
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_sql(user_query):
    prompt = f"""
    You are a PostgreSQL expert.

    Table: sales

    Columns:
    - billing_date (DATE)
    - billing_id (TEXT)
    - billing_document (TEXT)
    - billing_type (TEXT)
    - customer_number (INT)
    - sku (TEXT)
    - net_weight (FLOAT)
    - weight_unit (TEXT)
    - country_code (TEXT)
    - country_name (TEXT)

    Business Definitions:
    - total_weight = SUM(net_weight)
    - top country = highest total_weight

    Rules:
    - ONLY use the columns listed above
    - ONLY generate SELECT queries
    - ALWAYS use GROUP BY when using aggregation
    - DO NOT hallucinate columns
    - DO NOT explain anything

    User Query:
    {user_query}

    Return only SQL.
    """

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    sql = response.json()["response"].strip()
    # Remove markdown code block formatting if present
    if sql.startswith("```"):
        sql = sql.split("```")[1]
        # Remove 'sql' language identifier if present
        if sql.startswith("sql"):
            sql = sql[3:]
    sql = sql.strip()
    return sql

def validate_sql(sql):
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

    for word in forbidden:
        if word in sql.upper():
            raise ValueError("Unsafe SQL detected")

    return True
def fix_sql(sql, error):
    prompt = f"""
    The following SQL failed:

    SQL:
    {sql}

    Error:
    {error}

    Fix the SQL. Return only corrected SQL.
    """

    response = requests.post(OLLAMA_URL, json={
            "model": "llama3",
            "prompt": prompt,
            "stream": False
        })

    return response.json()["response"].strip()

def analyze_result(user_query, sql, result):
    prompt = f"""
    You are an expert business analyst.

    User Question:
    {user_query}

    SQL Query Used:
    {sql}

    Query Result:
    {result}

    Your job:
    1. Summarize key insight
    2. Highlight important numbers
    3. Give interpretation
    4. Suggest a recommendation

    Format:

    📊 Insight:
    ...

    📈 Data Evidence:
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

def run_sql(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return result.fetchall()


def sql_agent(user_query):
    sql = generate_sql(user_query)
    print("\nGenerated SQL:\n", sql)

    validate_sql(sql)

    try:
        result = run_sql(sql)

    except Exception as e:
        print("\nSQL Error:", e)

        sql = fix_sql(sql, str(e))
        print("\nFixed SQL:\n", sql)

        result = run_sql(sql)

    # NEW: Analyze result
    analysis = analyze_result(user_query, sql, result)

    return analysis
