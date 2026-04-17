import os
import numpy as np
import requests
from sentence_transformers import SentenceTransformer

# -----------------------------
# CONFIG
# -----------------------------
# Get project root by going up one level from the agents directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DOC_PATH = os.path.join(PROJECT_ROOT, "data", "docs")
OLLAMA_URL = "http://localhost:11434/api/generate"

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# -----------------------------
# LOAD DOCUMENTS
# -----------------------------
documents = []
doc_texts = []

for file in os.listdir(DOC_PATH):
    file_path = os.path.join(DOC_PATH, file)

    if file.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

            documents.append({
                "name": file,
                "content": text
            })

            doc_texts.append(text)

# -----------------------------
# CREATE EMBEDDINGS
# -----------------------------
doc_embeddings = model.encode(doc_texts)


# -----------------------------
# RETRIEVAL FUNCTION
# -----------------------------
def retrieve_docs(query, top_k=2):
    query_embedding = model.encode([query])[0]

    # cosine similarity (dot product works since embeddings are normalized)
    similarities = np.dot(doc_embeddings, query_embedding)

    # get top matches
    top_indices = np.argsort(similarities)[-top_k:][::-1]

    results = [documents[i]["content"] for i in top_indices]

    return results


# -----------------------------
# MAIN DOC AGENT
# -----------------------------
def doc_agent(query):
    docs = retrieve_docs(query)

    context = "\n\n".join(docs)

    prompt = f"""
You are a business analyst.

Answer the question using ONLY the context below.

Question:
{query}

Context:
{context}

Instructions:
- Be concise and clear
- Focus on business insights
- Do not hallucinate
"""

    response = requests.post(OLLAMA_URL, json={
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    })

    return response.json()["response"]