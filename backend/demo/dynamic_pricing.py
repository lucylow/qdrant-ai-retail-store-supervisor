"""Live dynamic pricing dashboard: MARL + RAG agents in real time."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure app is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pandas as pd
import streamlit as st

from app.dynamic_pricing.supervisor import DynamicPricingSupervisor

st.set_page_config(page_title="Dynamic Pricing - MARL + RAG", layout="wide")
st.title("Live Dynamic Pricing - Multi-Agent RL + RAG")
st.markdown("**Watch 5 pricing agents collaborate in real time**")

sku = st.selectbox(
    "Select SKU",
    ["tshirt_blue_m", "jeans_slim_black", "dress_party_red"],
)
competitor_price = st.slider("Competitor price (avg)", 25.0, 45.0, 35.0)
inventory = st.slider("Inventory level", 10, 500, 150)

if st.button("Compute dynamic prices", type="primary"):
    with st.spinner("Agents collaborating..."):
        supervisor = DynamicPricingSupervisor()

        async def run():
            return await supervisor.compute_optimal_prices(
                sku=sku,
                store_id="store_001",
                competitor_prices=[competitor_price] * 3,
                inventory_level=float(inventory),
                demand_forecast=pd.Series(),
            )

        rec = asyncio.run(run())

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Base price", f"${rec.base_price:.2f}")
        delta_pct = ((rec.dynamic_price / rec.base_price) - 1) * 100 if rec.base_price else 0
        st.metric("Dynamic price", f"${rec.dynamic_price:.2f}", delta=f"{delta_pct:+.1f}%")
    with col2:
        st.metric("Elasticity", f"{rec.elasticity:.2f}")
        st.metric("Confidence", f"{rec.confidence:.1%}")
    with col3:
        st.metric("Action", rec.recommended_action)
        st.metric("Revenue lift", f"+{rec.expected_revenue_lift:.1f}%")

    st.subheader("Competitor context (RAG)")
    st.write(rec.competitor_prices)

    try:
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode="number+delta",
            value=rec.dynamic_price,
            delta={"reference": rec.base_price, "valueformat": ".2f", "suffix": " vs base"},
            title={"text": "Dynamic vs base price"},
        ))
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass
