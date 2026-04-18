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

            # Display the final result
            final_answer = result.get("result", "No result generated")

            # Show assistant response
            with st.chat_message("assistant"):
                st.write(final_answer)

                # Show SQL if available
                if "sql" in result and result["sql"]:
                    st.code(result["sql"], language="sql")

                # Show documents if available
                if "docs" in result and result["docs"]:
                    with st.expander("📄 Retrieved Documents"):
                        for i, doc in enumerate(result["docs"], 1):
                            st.write(f"**Document {i}:**")
                            st.write(doc[:500] + "..." if len(doc) > 500 else doc)
                            st.divider()

        except Exception as e:
            final_answer = f"Error: {str(e)}"

            # Show error message
            with st.chat_message("assistant"):
                st.error(final_answer)

    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": final_answer
    })