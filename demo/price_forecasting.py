"""Multi-Agent Price Forecasting - Live Ensemble Dashboard."""

from __future__ import annotations

import asyncio
import streamlit as st
import plotly.graph_objects as go
from app.forecasting.price.supervisor import PriceForecastSupervisor

st.set_page_config(page_title="Price Forecasting", layout="wide")
st.title("📈 Multi-Agent Price Forecasting - Live Ensemble")
st.markdown("**7 Specialized Agents → Production Price Predictions**")

sku = st.selectbox(
    "SKU",
    ["tshirt_blue_m", "jeans_slim_black", "dress_party_red", "jacket_winter_gray", "sneakers_white"],
)
horizon = st.slider("Forecast Horizon (days)", 7, 90, 30)

if st.button("🔮 GENERATE PRICE FORECAST", type="primary"):
    supervisor = PriceForecastSupervisor()
    with st.spinner("7 agents forecasting collaboratively..."):
        forecast = asyncio.run(supervisor.forecast_price(sku, "store_001", horizon))

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=forecast.forecast_horizon,
            y=forecast.point_forecast,
            mode="lines+markers",
            name="Ensemble Forecast",
            line=dict(color="blue", width=3),
        )
    )
    upper = forecast.confidence_intervals["upper"].tolist()
    lower = forecast.confidence_intervals["lower"].tolist()
    fig.add_trace(
        go.Scatter(
            x=forecast.forecast_horizon.tolist() + forecast.forecast_horizon[::-1].tolist(),
            y=upper + lower[::-1],
            fill="toself",
            fillcolor="rgba(0,100,255,0.2)",
            line=dict(color="rgba(255,255,255,0)"),
            name="95% Confidence",
        )
    )
    for agent, weight in forecast.ensemble_weights.items():
        if weight > 0.05:
            fig.add_trace(
                go.Scatter(
                    x=forecast.forecast_horizon[:5],
                    y=forecast.point_forecast[:5].values * (1 + weight - 0.5),
                    mode="markers",
                    name=f"{agent} ({weight:.0%})",
                    marker=dict(size=8, opacity=0.6),
                )
            )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        height=450,
    )
    st.plotly_chart(fig, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Forecast Accuracy (1-MAPE)", f"{(1 - forecast.accuracy_score):.1%}")
    with col2:
        st.metric("Anomaly Risk", f"{forecast.anomaly_probability:.1%}")
    with col3:
        top_agent = max(forecast.ensemble_weights.items(), key=lambda x: x[1])
        st.metric("Top Agent", top_agent[0])
    with col4:
        st.metric("Trading Signal", forecast.recommended_action)

    with st.expander("Ensemble weights"):
        st.json(forecast.ensemble_weights)
