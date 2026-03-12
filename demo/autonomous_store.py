from __future__ import annotations

import asyncio
import logging
from typing import Sequence

import streamlit as st

from app.agents.supervisor import SupervisorAgent
from app.generation.multimodal import MultimodalProductGenerator
from app.promo.autonomous import AutonomousPromoPlanner, Opportunity
from app.promo.segmentation import Customer
from app.rag.self_improving import SelfImprovingRAG


logger = logging.getLogger(__name__)


async def run_supervisor(supervisor: SupervisorAgent, customer_query: str):
    return await supervisor.orchestrate(customer_query)


def visualize_reasoning_graph(graph) -> object:
    # Placeholder; Streamlit will just show JSON in this minimal version.
    return graph


def main() -> None:
    st.set_page_config(page_title="Autonomous Store Manager", layout="wide")

    supervisor = SupervisorAgent()
    rag = SelfImprovingRAG()
    generator = MultimodalProductGenerator()
    promo_planner = AutonomousPromoPlanner()

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        [
            "🧑‍💼 Live Agent Orchestration",
            "🧠 Self-Improving RAG",
            "🎨 Multi-Modal Generation",
            "📈 Autonomous Promotions",
            "📊 Reasoning Graphs",
            "🚀 Metrics & Benchmarks",
        ]
    )

    # Tab 1: REAL-TIME AGENT EXECUTION
    with tab1:
        customer_query = st.text_input(
            "Customer query",
            value="Blue dress €80 Berlin <3 days",
        )
        if st.button("Run Full Agent Pipeline"):
            # AUTONOMOUS-AGENT-HACKATHON: main judge demo run button.
            with st.spinner("Orchestrating autonomous store..."):
                result = asyncio.run(run_supervisor(supervisor, customer_query))
                graph_viz = visualize_reasoning_graph(result.graph)
                st.json(graph_viz.__dict__)
                st.metric("Success", "✅" if result.success else "❌")
                st.metric("Conversion rate", f"{result.metrics.get('conversion_rate', 0.0):.2f}")

    with tab2:
        if st.button("Run self-improvement cycle"):
            rag.daily_improvement_cycle()
            st.success("Self-improvement cycle completed")

    with tab3:
        st.write("Multi-modal bundle mockup")
        if st.button("Generate mockup (demo)"):
            image_url = generator.generate_bundle_mockup(products=[])
            st.write(image_url)

    with tab4:
        if st.button("Plan autonomous campaign"):
            customers = [
                Customer(
                    customer_id="c1",
                    monetary=250.0,
                    frequency=5,
                    recency_days=10,
                    features={},
                )
            ]
            opp = Opportunity(
                sku="SKU-BASE",
                store="Berlin-Store",
                customers=customers,
                event="Spring launch",
            )
            campaign = asyncio.run(promo_planner.plan_campaign(opp))
            st.json(
                {
                    "selected": campaign.selected_variant,
                    "lifts": {k: v.expected_lift_pct for k, v in campaign.lifts.items()},
                }
            )

    with tab5:
        st.write("Reasoning graphs will appear as they are stored.")

    with tab6:
        st.write("Metrics & benchmarks placeholder.")


if __name__ == "__main__":
    main()

