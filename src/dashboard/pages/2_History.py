import streamlit as st
import plotly.express as px
import pandas as pd
from api_client import get_results_history
import requests

st.set_page_config(page_title="Results History", page_icon="📋", layout = "wide")

st.title("Optimization History")
st.markdown("All past optimization runs retrieved from the database.")

limit = st.slider("Number of results to display.", min_value=5,max_value=100,value=20)
try:
    data = get_results_history(limit=limit)
except requests.exceptions.RequestException as e:
    st.error("No history found.")
    st.stop()

if data is None or data["count"] == 0:
    st.warning("No history found.")
else:
    st.metric("Total Results", data["count"])
    df = pd.DataFrame(data["results"])
    st.dataframe(df, use_container_width=True)