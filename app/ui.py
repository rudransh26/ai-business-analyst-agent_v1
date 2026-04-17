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

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 AI Business Analyst Agent")
st.markdown("Ask business questions using data + market insights")

# -----------------------------
# INPUT
# -----------------------------
query = st.text_input(
    "Enter your question:",
    placeholder="e.g. Why is Indonesia performing well?"
)

# -----------------------------
# BUTTON
# -----------------------------
if st.button("Run Analysis"):
    if query.strip() == "":
        st.warning("Please enter a query")
    else:
        with st.spinner("Analyzing... 🤖"):
            try:
                result = run_agent(query)

                st.success("Analysis Complete ✅")

                st.markdown("### 📊 Result")
                st.write(result)

            except Exception as e:
                st.error(f"Error: {str(e)}")