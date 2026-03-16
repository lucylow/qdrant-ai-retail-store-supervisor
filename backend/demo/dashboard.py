from __future__ import annotations

import json

import streamlit as st

from app.agents.supervisor import SupervisorAgent


st.set_page_config(page_title="Retail Agent Supervisor", layout="wide")

st.title("Self-Improving Retail Agent Supervisor (Hackathon Demo)")

query = st.text_input("Shopping goal", "Plan a movie-night snack bundle under 30 CHF")

col_toggles, col_run = st.columns([3, 1])

with col_toggles:
    use_tool = st.checkbox("Enable dynamic tool", value=True)

with col_run:
    run_clicked = st.button("Run agents")

if "supervisor" not in st.session_state:
    st.session_state["supervisor"] = SupervisorAgent()


def _demo_tool_body() -> str:
    return """
result = {
    "bundle_price": sum(item.get("price", 0) for item in payload.get("items", [])),
    "count": len(payload.get("items", [])),
}
return result
"""


if run_clicked:
    ctx: dict[str, object] = {}
    if use_tool:
        ctx["tool_body"] = _demo_tool_body()
        ctx["tool_payload"] = {"items": []}  # CURSOR: wire to real products later.
    sup: SupervisorAgent = st.session_state["supervisor"]
    res = sup.run(query, context=ctx)

    st.subheader("Recommendation")
    inv = res.get("inventory", {})
    merch = res.get("merch", {})
    products = inv.get("products", [])
    layout = merch.get("layout", [])
    st.write(f"{len(products)} products considered.")
    st.json(layout)

    st.subheader("Agent trace")
    st.json(res.get("trace", []))

