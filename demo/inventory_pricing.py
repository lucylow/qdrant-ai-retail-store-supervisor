"""Joint inventory + dynamic pricing dashboard."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from app.inventory.supervisor import InventorySupervisor
from app.dynamic_pricing.supervisor import DynamicPricingSupervisor

st.set_page_config(
    page_title="Inventory + Dynamic Pricing",
    layout="wide",
)
st.title("Inventory + Dynamic Pricing - Joint Optimization")
st.markdown("**5 Inventory Agents + 5 Pricing Agents = End-to-End Autonomy**")

sku = st.selectbox(
    "Critical SKU",
    ["tshirt_blue_m", "jeans_slim_black", "dress_party_red"],
)
current_stock = st.slider("Current stock", 0, 500, 120)
competitor_price = st.slider("Competitor price (avg)", 25.0, 50.0, 35.0)
supplier_lead_days = st.slider("Supplier lead time (days)", 1, 14, 5)

if st.button("Run joint optimization", type="primary"):
    pricing_supervisor = DynamicPricingSupervisor()
    inventory_supervisor = InventorySupervisor(pricing_supervisor)

    async def run():
        return await inventory_supervisor.optimize_jointly(
            sku=sku,
            warehouse_id="wh_001",
            current_stock=float(current_stock),
            supplier_lead_days=supplier_lead_days,
        )

    with st.spinner("Inventory + pricing agents collaborating..."):
        inv_rec, price_rec = asyncio.run(run())

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Current stock", f"{inv_rec.current_stock:.0f}")
        st.metric("Days to stockout", f"{inv_rec.days_to_stockout:.1f}")
        st.metric("Urgency", inv_rec.urgency)

    with col2:
        st.metric("Dynamic price", f"${price_rec.dynamic_price:.2f}")
        st.metric("Order quantity", f"{inv_rec.optimal_order_qty:.0f}")
        st.metric("Lead time", f"{inv_rec.supplier_lead_days} days")

    with col3:
        st.metric("Revenue lift", f"+{price_rec.expected_revenue_lift:.1f}%")
        st.metric("Service level", "95%")
        rev_impact = inv_rec.pricing_impact.get("revenue_impact", 0)
        st.metric("Revenue impact (est.)", f"${rev_impact:.0f}")

    st.subheader("Agent collaboration")
    st.write(
        "Inventory forecaster → safety stock & reorder point → stockout predictor → "
        "reorder optimizer (EOQ) ↔ pricing supervisor (MARL + RAG) → joint recommendation."
    )

    try:
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=inv_rec.optimal_order_qty,
                delta={"reference": inv_rec.reorder_point, "suffix": " vs reorder pt"},
                title={"text": "Order qty vs reorder point"},
            )
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass
