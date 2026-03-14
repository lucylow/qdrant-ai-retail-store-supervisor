"""Live Hyper-Personalization Hub: 8-agent collaboration with Customer 360."""

from __future__ import annotations

import asyncio
from typing import Any, Dict

import streamlit as st
from app.personalization.supervisor import PersonalizationSupervisor

st.set_page_config(
    page_title="Hyper-Personalization Hub",
    page_icon="🧠",
    layout="wide",
)
st.title("🧠 Hyper-Personalization Hub - 8 Agent Collaboration")
st.markdown("**Live omni-channel personalization with Customer 360**")

customer_id = st.text_input("Customer ID", "cust_12345")
context: Dict[str, Any] = {
    "channel": st.selectbox(
        "Channel",
        ["web", "mobile", "email", "in_store"],
        key="channel",
    ),
    "location": st.selectbox(
        "Location",
        ["NYC", "LA", "Chicago", "Miami"],
        key="location",
    ),
    "time_of_day": st.select_slider(
        "Time",
        options=["morning", "afternoon", "evening"],
        key="time_of_day",
    ),
}

if st.button("🎯 GENERATE PERSONALIZED EXPERIENCE", type="primary"):
    supervisor = PersonalizationSupervisor()

    async def run():
        return await supervisor.personalize(customer_id, context)

    with st.spinner("8 personalization agents collaborating..."):
        result = asyncio.run(run())

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👤 Customer Profile")
        st.metric("Loyalty Tier", result.profile.segments.loyalty_tier)
        st.metric("RFM Score", f"{result.profile.rf_score:.1f}/5.0")
        st.metric("Price Sensitivity", f"{result.profile.price_sensitivity:.2f}")

    with col2:
        st.subheader("📊 Personalization Scores")
        st.metric("Recommendation Confidence", f"{result.confidence:.1%}")
        st.metric("A/B Test Variant", result.ab_test_variant)
        if result.gdpr_compliant:
            st.success("✅ GDPR Compliant")
        else:
            st.warning("⚠️ Check consent settings")

    st.subheader("🥇 Personalized Recommendations")
    for i, rec in enumerate(result.recommendations[:6]):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric(f"#{i+1}", rec.get("product_id", ""))
        with c2:
            scores = rec.get("scores", {})
            st.metric(
                "Relevance",
                f"{scores.get('relevance', 0):.1%}",
            )
        with c3:
            st.caption(rec.get("personalization_explanation", ""))

    st.subheader("🎁 Personalized Offers")
    for o in result.offers[:6]:
        st.write(
            f"**{o.get('product_id')}**: {o.get('message', '')} "
            f"(Free shipping: {o.get('free_shipping', False)})"
        )

    st.info(f"Next journey step: **{result.journey_next_step}**")
