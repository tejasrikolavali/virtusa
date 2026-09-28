from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.graph import process_dispute

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "sample_inputs"

st.set_page_config(page_title="Transaction Dispute Copilot", layout="wide")
st.title("Transaction Dispute & Fraud-Triage Copilot")
st.caption("Synthetic demo system for dispute triage, policy retrieval, and risk review.")

sample_files = sorted(DATA_DIR.glob("dispute_*.json"))
selected = st.selectbox("Choose a sample input", [p.name for p in sample_files], index=0)
with open(DATA_DIR / selected, "r", encoding="utf-8") as handle:
    sample_payload = json.load(handle)

uploaded = st.file_uploader("Or upload a JSON dispute file", type=["json"])
if uploaded is not None:
    sample_payload = json.loads(uploaded.read().decode("utf-8"))

st.json(sample_payload)

if st.button("Run Copilot"):
    with st.spinner("Running the dispute workflow..."):
        result = process_dispute(sample_payload)
    st.subheader("Classification")
    st.write(result.get("dispute_type", "unknown"))
    st.subheader("Fraud / Risk")
    st.metric("Risk score", f"{result.get('fraud_score', 0):.1f}")
    st.write(result.get("fraud_factors", []))
    st.subheader("Retrieved policy evidence")
    st.json(result.get("retrieved_rules", []))
    st.subheader("Decision")
    st.json(result.get("decision", {}))
    st.subheader("Route history")
    st.write(result.get("route_history", []))
    st.subheader("Warnings")
    st.write(result.get("errors", []))
    st.caption("Synthetic-only demonstration. No real customer or PAN data is used.")
