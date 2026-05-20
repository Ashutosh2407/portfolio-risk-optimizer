import streamlit as st
from api_client import get_latest_result
import plotly.express as px

st.set_page_config(page_title="Portfolio Optimizer",
                   page_icon="📈",
                   layout = "wide")

st.title("📈 portfolio Risk Optimizer")

st.divider()

st.subheader("🕐 Latest Optimization Result")

data = get_latest_result()

if data is None:
    st.warning("No optimization results found. Run an optimization first.")
else:
    col1,col2,col3 = st.columns(3)
    col1.metric("Strategy", data.get("strategy", "N/A"))
    col2.metric("Sharpe Ratio", round(data.get("sharpe_ratio",0),4) if data.get("sharpe_ratio") else "N/A")
    col3.metric("Timestamp", str(data.get("timestamp", "N/A"))[:10])
    #Weights Pie chart
    weights = data.get("weights",{})
    st.subheader("Portfolio Allocation")
    fig = px.pie(
        values = list(weights.values()),
        names = list(weights.keys()),
        title= "Optimal Weight Distribution"
    )
    st.plotly_chart(fig,use_container_width=True)
