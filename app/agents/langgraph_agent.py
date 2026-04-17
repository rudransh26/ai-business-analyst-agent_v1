from langgraph.graph import StateGraph, END
from typing import TypedDict

from agents.planner_agent import planner_agent
from agents.sql_agent import sql_agent
from agents.doc_agent import doc_agent
from agents.combined_agent import combined_agent




""""
                ┌──────────────┐
                │   START      │
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │  PLANNER     │
                │ (LLM decides)│
                └──────┬───────┘
                       ↓
                ┌──────────────┐
                │   ROUTER     │
                └──────┬───────┘
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
   ┌────────┐     ┌────────┐     ┌──────────┐
   │  SQL   │     │  DOCS  │     │ COMBINED │
   └────┬───┘     └────┬───┘     └────┬─────┘
        ↓              ↓              ↓
                ┌──────────────┐
                │     END      │
                └──────────────┘


"""



# -----------------------------
# STATE
# -----------------------------
class AgentState(TypedDict):
    query: str
    decision: str
    result: str


# -----------------------------
# NODES
# -----------------------------
def planner_node(state: AgentState):
    decision = planner_agent(state["query"])
    print("\nPlanner Decision:", decision)

    return {"decision": decision}


def sql_node(state: AgentState):
    result = sql_agent(state["query"])
    return {"result": str(result)}


def doc_node(state: AgentState):
    result = doc_agent(state["query"])
    return {"result": result}


def combined_node(state: AgentState):
    result = combined_agent(state["query"])
    return {"result": result}


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

    return result["result"]