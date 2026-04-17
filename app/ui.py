import streamlit as st
from agents.langgraph_agent import run_agent

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="AI Business Analyst",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI Business Analyst Agent")

# -----------------------------
# SESSION STATE (MEMORY)
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# DISPLAY CHAT HISTORY
# -----------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# -----------------------------
# USER INPUT
# -----------------------------
query = st.chat_input("Ask a business question...")

if query:
    # Show user message
    st.chat_message("user").write(query)

    # Save user message
    st.session_state.messages.append({
        "role": "user",
        "content": query
    })

    # Generate response
    with st.spinner("Analyzing... 🤖"):
        try:
            result = run_agent(query)

        except Exception as e:
            result = f"Error: {str(e)}"

    # Show assistant response
    with st.chat_message("assistant"):
        st.write(result)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": result
    })