"""Live Knowledge Graph Explorer - Neo4j + Qdrant hybrid for 25+ agent reasoning."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from app.kg.neo4j_client import ProductionNeo4jClient
from app.kg.agents.reasoner import KGReasonerAgent

st.set_page_config(page_title="KG Explorer - Retail Ontology", layout="wide")
st.title("Knowledge Graph Explorer - Live Retail Ontology")
st.markdown("**Neo4j + Qdrant Hybrid → 25+ Agent Reasoning**")

# Sidebar: connection (optional secrets)
use_env = st.sidebar.checkbox("Use env (NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)", value=True)
if not use_env:
    neo4j_uri = st.sidebar.text_input("Neo4j URI", "bolt://localhost:7687")
    neo4j_user = st.sidebar.text_input("Neo4j User", "neo4j")
    neo4j_password = st.sidebar.text_input("Neo4j Password", type="password")
else:
    neo4j_uri = neo4j_user = neo4j_password = None

customer_id = st.text_input("Customer ID", value="cust_001", key="customer_id")
product_id = st.text_input("Product ID (for inventory/competitor)", value="prod_1", key="product_id")
query_type = st.selectbox(
    "Query Type",
    ["Similar Customers", "Product Recommendations", "Inventory Paths", "Competitor Analysis", "Raw Cypher"],
    key="query_type",
)

def get_client():
    if use_env or (neo4j_uri is None and neo4j_user is None):
        return ProductionNeo4jClient()
    return ProductionNeo4jClient(uri=neo4j_uri, user=neo4j_user, password=neo4j_password)

if st.button("Explore Knowledge Graph", type="primary"):
    client = get_client()
    if not client.verify_connectivity():
        st.error("Neo4j connection failed. Start Neo4j (e.g. docker-compose -f docker-compose.kg.yml up -d).")
        st.stop()
    reasoner = KGReasonerAgent(client)

    async def run():
        if query_type == "Similar Customers":
            return await reasoner.find_similar_customers(customer_id, max_results=10)
        if query_type == "Product Recommendations":
            return await reasoner.product_recommendation_paths(customer_id, max_results=20)
        if query_type == "Inventory Paths":
            return await reasoner.inventory_paths(product_id, max_results=20)
        if query_type == "Competitor Analysis":
            return await reasoner.competitor_products(product_id, max_results=20)
        if query_type == "Raw Cypher":
            cypher = st.text_area("Cypher", value="MATCH (n) RETURN n LIMIT 10", key="cypher")
            result = await reasoner.run_cypher(cypher)
            return result.records
        return []

    with st.spinner("Graph reasoning in progress..."):
        try:
            results = asyncio.run(run())
        except Exception as e:
            st.exception(e)
            st.stop()

    if not results:
        st.info("No results. Ingest data first: python scripts/kg/ingest_all.py")
    else:
        st.subheader("Results")
        if isinstance(results, list) and results and isinstance(results[0], dict):
            st.dataframe(results, use_container_width=True)
            st.json(results[:5])
        else:
            st.write(results)

    # Optional: subgraph visualization (text summary)
    if query_type in ("Similar Customers", "Product Recommendations") and results:
        st.subheader("Graph summary")
        st.caption("Node/relationship counts from last query. Use Neo4j Browser for full visualization.")
        try:
            summary_result = client.execute_cypher_sync(
                "MATCH (n) WITH labels(n)[0] AS l RETURN l, count(*) AS c ORDER BY c DESC LIMIT 10",
            )
            if summary_result.records:
                st.dataframe(summary_result.records)
        except Exception:
            pass

st.sidebar.markdown("---")
st.sidebar.markdown("**Quick start**")
st.sidebar.code("make kg-stack-up\nmake kg-ingest-full\nstreamlit run demo/kg_explorer.py", language="bash")
