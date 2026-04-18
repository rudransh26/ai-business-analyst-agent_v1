import requests
from sqlalchemy import text
from db.connection import engine


OLLAMA_URL = "http://localhost:11434/api/generate"


# -----------------------------
# 1. GENERATE SQL
# -----------------------------


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

Rules:
- ONLY use columns above
- ONLY generate SELECT queries
- ALWAYS use GROUP BY when needed
- DO NOT hallucinate columns
- NO explanation

User Query:
{user_query}

Return only SQL.
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"].strip()


# -----------------------------
# 2. VALIDATE SQL
# -----------------------------
def validate_sql(sql):
    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER"]

    for word in forbidden:
        if word in sql.upper():
            raise ValueError("Unsafe SQL detected")

    return True


# -----------------------------
# 3. RUN SQL
# -----------------------------
def run_sql(sql):
    with engine.connect() as conn:
        result = conn.execute(text(sql))
        return result.fetchall()


# -----------------------------
# 4. FIX SQL (LLM RETRY)
# -----------------------------
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


# -----------------------------
# 5. TOOL: SQL TOOL (IMPORTANT)
# -----------------------------
def sql_tool(user_query):
    sql = generate_sql(user_query)

    # 🔥 CLEAN HERE
    sql = clean_sql(sql)

    try:
        validate_sql(sql)
        result = run_sql(sql)

    except Exception as e:
        print("\nSQL Error:", e)

        sql = fix_sql(sql, str(e))
        sql = clean_sql(sql)  # 🔥 CLEAN AGAIN AFTER FIX

        print("\nFixed SQL:\n", sql)

        result = run_sql(sql)

    return sql, result


# -----------------------------
# 6. ANALYZE RESULT (LLM)
# -----------------------------
def analyze_result(user_query, sql, result):
    prompt = f"""
You are a senior business analyst.

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
4. Suggest recommendation

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


# -----------------------------
# 7. AGENT: SQL AGENT
# -----------------------------
def sql_agent(user_query):
    sql, result = sql_tool(user_query)

    print("\nGenerated SQL:\n", sql)

    analysis = analyze_result(user_query, sql, result)

    return analysis


def clean_sql(sql: str) -> str:
    # Remove markdown code blocks
    sql = sql.strip()

    if sql.startswith("```"):
        sql = sql.replace("```sql", "").replace("```", "")

    return sql.strip()