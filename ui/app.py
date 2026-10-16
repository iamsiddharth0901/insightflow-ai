import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("INSIGHTFLOW_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="InsightFlow AI", page_icon="📈", layout="wide")
st.title("InsightFlow AI")
st.caption("Evidence-first commercial intelligence — verified facts are separate from hypotheses.")

with st.sidebar:
    st.subheader("Document manager")
    uploaded = st.file_uploader("Upload a TXT or Markdown report", type=["txt", "md"])
    if uploaded and st.button("Index document"):
        response = requests.post(f"{API_URL}/ingest/documents", files={"file": (uploaded.name, uploaded.getvalue())}, timeout=20)
        st.success(response.json().get("doc_id", "Indexed"))
    if st.button("Reset demo data"):
        requests.post(f"{API_URL}/ingest/data", timeout=20)
        st.success("Demo data restored.")

if "answer" not in st.session_state:
    st.session_state.answer = None
question = st.chat_input("Ask, e.g. Why did South revenue decline in Q3 2026?")
if question:
    with st.spinner("Checking data and evidence…"):
        response = requests.post(f"{API_URL}/ask", json={"question": question}, timeout=30)
        response.raise_for_status()
        st.session_state.answer = response.json()

result = st.session_state.answer
if result:
    st.subheader("Answer")
    st.write(result["summary"])
    left, right = st.columns(2)
    with left:
        st.subheader("Verified facts")
        for fact in result["verified_facts"]:
            st.success(fact["statement"])
    with right:
        st.subheader("Hypotheses")
        for hypothesis in result["hypotheses"]:
            st.warning(f"{hypothesis['statement']} Needs validation.")
    for chart in result["charts"]:
        st.subheader(chart["title"])
        st.bar_chart(pd.DataFrame(chart["data"]).set_index(chart["x"])[chart["y"]])
    with st.expander("Evidence and trace"):
        st.json({"citations": result["citations"], "trace": result["trace"], "warnings": result["warnings"]})
