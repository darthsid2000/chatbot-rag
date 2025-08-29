import os
import uuid
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Wiki RAG", layout="centered")
st.title("Wiki RAG — Stormlight Fandom")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

q = st.text_input("Question")
k = st.slider("Top-K", 1, 8, 4)

if st.button("Ask") and q.strip():
    r = requests.post(f"{API_URL}/chat", json={"session_id": st.session_state.session_id, "question": q, "top_k": k}, timeout=120)
    if r.ok:
        data = r.json()
        st.markdown("**Answer**")
        st.write(data["answer"])
        if data.get("sources"):
            st.markdown("**Sources**")
            for s in data["sources"]:
                st.write(f"- {s.get('title','Unknown')} (chunk {s.get('chunk_id')})")
    else:
        st.error(f"{r.status_code}: {r.text}")