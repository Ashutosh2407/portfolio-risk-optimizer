import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np
from api_client import get_risk, get_latest_result, get_tickers

st.set_page_config(page_title="Risk Analysis",page_icon="⚠️", layout= "wide")

st.title("Risk Analysis")
st.markdown("Calculate Portfolio Risk Metrics including VaR, CVaR and maximum drawdown.")

#Mode Toggle
mode = st.radio(label= "Select Mode",
         options = ["Use Latest Optimization Results", "Custom Tickers and Weights"],
         horizontal=True)

st.divider()

tickers_to_use = []
weights_to_use = []

#Mode 1
if mode == "Use Latest Optimization Results":
    latest = get_latest_result()
    
    if latest is None:
        st.error("Latest result not found.")
        st.stop()
    else:
        col1,col2 = st.columns(2)
        strategy = latest.get("strategy","N/A").replace("_"," ").title()
        col1.metric("Strategy", strategy)
        col2.metric("Sharpe Ratio", round(latest.get("sharpe_ratio",0),4) if latest.get("sharpe_ratio") else "N/A")

        if "weights" not in latest:
            st.error("No latest result found.")
            st.stop()
        weights_dict = latest.get("weights", {})
        tickers_to_use = list(weights_dict.keys())
        weights_to_use = list(weights_dict.values())
        st.markdown("Weights from Latest Optimization.")
        preview_df = pd.DataFrame({
            "Ticker": tickers_to_use,
            "Weights": [f"{w:.2%}" for w in weights_to_use]
        })
        preview_df.index = np.arange(1,len(preview_df)+1)
        st.dataframe(preview_df, width = 400)
#Mode 2:Custom Tickets
else:
    available_tickers = get_tickers()
    if "error" in available_tickers:
        st.error("Could not load tickers.")
        st.stop()
    
    selected_tickers = st.multiselect(label="Select Tickers",
                                      options = available_tickers["tickers"],
                                      default= available_tickers["tickers"][:4])

    if len(selected_tickers) < 4:
        st.warning("Please select at least 4 tickers.")
        st.stop()

    st.markdown("#### Set Weights")
    st.caption("Adjust weights for each ticker. They must sum up to 1.0")

    cols = st.columns(len(selected_tickers))
    weights = []
    for i, ticker in enumerate(selected_tickers):
        default_weight = round(1.0/len(selected_tickers),2)
        w = cols[i].number_input(
            ticker,
            min_value=0.0,
            max_value=1.0,
            value=default_weight,
            step = 0.05
            )
        weights.append(w)
    
    weight_sum = round(sum(weights),4)

    if abs(weight_sum-1.0) >1e-4:
        st.error(f"Weights must sum to 1.0 — current sum: {weight_sum:.4f}")
        st.stop()

    st.success(f"Weights sum: {weight_sum:.4f} ✓")

    tickers_to_use = selected_tickers
    weights_to_use = weights

# ── Calculate Risk ───────────────────────────────────────────
if st.button("Calculate Risk Metrics", type="primary"):
    with st.spinner("Calculating risk metrics..."):
        result = get_risk(tickers_to_use, weights_to_use)
        print(result)
    if result is None:
        st.error("Risk calculation failed.")
    else:
        st.divider()
        st.subheader("Risk Metrics")

        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Portfolio Volatility", f"{result["volatility"]:.2%}",
                    help="Annualized standard deviation of portfolio returns.")
        col2.metric("VaR (95%)", f"{result['var_95']:.2%}",
                    help="Maximum expected daily loss at 95% confidence.")
        col3.metric("CVaR", f"{result['cvar']:.2%}",
                    help="Expected loss beyond the VaR threshold.")
        col4.metric("Max Drawdown", f"{result['max_drawdown']:.2%}",
                    help="Largest peak-to-trough decline in portfolio value.")
        
        st.divider()
        col1,col2 = st.columns(2)

        with col1:
            st.subheader("Weight Allocation")
            fig_pie = px.pie(

                names=list(result["weights"].keys()),
                values = list(result["weights"].values()),
                title = "Portfolio Weights"
            )
            st.plotly_chart(fig_pie,use_container_width=True)

        with col2:
            st.subheader("Risk Metrics Comparison")
            metrics_df = pd.DataFrame({
                "Metric": ["Volatility", "VaR (95%)", "CVaR", "Max Drawdown"],
                "Value": [
                    result["volatility"],
                    abs(result["var_95"]),
                    abs(result["cvar"]),
                    abs(result["max_drawdown"])
                ]
            })
            fig_bar = px.bar(
                metrics_df,
                x="Metric",
                y="Value",
                title="Risk Metrics (absolute values)",
                color="Metric",
                text_auto=".2%"
            )
            fig_bar.update_layout(yaxis_tickformat=".0%")
            st.plotly_chart(fig_bar, use_container_width=True)




        
