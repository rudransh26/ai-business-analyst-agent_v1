from agents.langgraph_agent import run_agent

query = "Why is Indonesia performing well?"

result = run_agent(query)

print("\nFinal Output:\n")
print(result)