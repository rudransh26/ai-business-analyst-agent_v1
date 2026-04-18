from langgraph.graph import StateGraph, END
from typing import TypedDict

from agents.planner_agent import planner_agent
from agents.combined_agent import combined_agent
from agents.sql_agent import sql_tool
from agents.doc_agent import retrieve_docs, doc_agent







# -----------------------------
# STATE
# -----------------------------
class AgentState(TypedDict):
    query: str
    decision: str
    result: str
    sql: str
    docs: list

# -----------------------------
# NODES
# -----------------------------
def planner_node(state: AgentState):
    decision = planner_agent(state["query"])
    return {"decision": decision}



def sql_node(state: AgentState):
    sql, result = sql_tool(state["query"])

    return {
        "result": str(result),
        "sql": sql
    }


def doc_node(state: AgentState):
    docs = retrieve_docs(state["query"])
    result = doc_agent(state["query"])

    return {
        "result": result,
        "docs": docs
    }

def combined_node(state: AgentState):
    sql, sql_result = sql_tool(state["query"])
    docs= retrieve_docs(state["query"])

    final_result = combined_agent(
        state["query"],
        sql,
        sql_result,
        docs
    )

    return {
        "result": final_result,
        "sql": sql,
        "docs": docs
    }

# -----------------------------
# ROUTER
# -----------------------------
def route(state: AgentState):
    if state["decision"] == "sql":
        return "sql"
    elif state["decision"] == "docs":
        return "docs"
    else:
        return "combined"


# -----------------------------
# BUILD GRAPH
# -----------------------------
builder = StateGraph(AgentState)

builder.add_node("planner", planner_node)
builder.add_node("sql", sql_node)
builder.add_node("docs", doc_node)
builder.add_node("combined", combined_node)

builder.set_entry_point("planner")

builder.add_conditional_edges(
    "planner",
    route,
    {
        "sql": "sql",
        "docs": "docs",
        "combined": "combined"
    }
)

builder.add_edge("sql", END)
builder.add_edge("docs", END)
builder.add_edge("combined", END)

graph = builder.compile()


# -----------------------------
# RUN FUNCTION
# -----------------------------
def run_agent(query: str):
    result = graph.invoke({
        "query": query
    })

    return result