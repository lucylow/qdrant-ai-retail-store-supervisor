import requests
import streamlit as st

st.title("Generative RAG Demo")

q = st.text_input(
    "Query",
    value="Write a short product caption for a 2-person tent under 200 CHF.",
)
collection = st.text_input("Collection", value="demo_retail")
if st.button("Generate"):
    with st.spinner("Calling RAG generator..."):
        try:
            r = requests.get(
                "http://localhost:8000/query",
                params={"q": q, "collection": collection},
                timeout=60,
            )
        except Exception as e:
            st.error(f"Request error: {e}")
        else:
            if r.status_code != 200:
                st.error(f"Error: {r.text}")
            else:
                res = r.json()
                st.subheader("Answer")
                st.write(res.get("answer"))
                st.subheader("Provenance")
                for p in res.get("provenance", []):
                    st.write(p)
                st.write("Confidence:", res.get("confidence"))

