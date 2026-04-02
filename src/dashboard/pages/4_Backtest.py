import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from api_client import get_tickers,get_backtest

st.set_page_config(page_title="Backtest",page_icon="📉", layout="wide")

st.title("Walk-Forward Backtest")
st.markdown("Train on historical data, test on out-of-sample period, compare against equal-weight benchmark.")

#Inputs----------------------------------------------------------
available_tickers = get_tickers()
if isinstance(available_tickers,dict) and "error" in available_tickers:
    st.error("Could not find tickers.")
    st.stop()

selected_tickers = st.multiselect(label="Select Tickers",
                                  options=available_tickers["tickers"],
                                  default=available_tickers["tickers"][:4])

strategy = st.selectbox(label="Strategy",
                        options=["max_sharpe", "min_vol"],
                        format_func= lambda x:"Max Sharpe" if x=="max_sharpe" else "Minimum Volatility")

if len(selected_tickers) <4:
    st.error("Please select at least 4 tickers.")
    st.stop()

#Run Backtest---------------------------------------
if st.button(label="Run Backtest", type="primary"):
    with st.spinner("Running walk-forward backtest... this may take a few seconds."):
        result = get_backtest(tickers=selected_tickers,strategy=strategy)
    
    if "optimal_weights" not in result:
        st.error("Backtest Failed.")
        st.stop()

    st.success(f"Backtest complete | Train Period: {result.get('train_period', 'N/A')} | Test Period: {result.get('test_period', 'N/A')}")
    st.divider()

# ── Summary Metrics ───────────────────────────────────────
    st.subheader("Performance Summary")
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Total Return", 
                f"{result["total_return"]:.2%}",
                delta = f"{(result["realized_return"]-result["benchmark_return"]):.2%} vs Benchmark")
    col2.metric("Sharpe Ratio",
                f"{result["realized_sharpe"]:.2f}",
                delta=f"{(result["realized_sharpe"] - result["benchmark_sharpe"]):.2f} vs Benchmark")
    col3.metric(
        "Volatility",
        f"{result['realized_volatility']:.2f}",
        delta=f"{result["realized_volatility"]-result["benchmark_volatility"]:.2%} vs Benchmark",
        delta_color="inverse"
    )
    col4.metric(
            "Max Drawdown",
            f"{result['max_drawdown']:.2%}",
            delta=f"{(result['max_drawdown'] - result['benchmark_max_drawdown']):.2%} vs benchmark",
            delta_color="inverse"
        )

    st.divider()

#Strategy vs Benchmark Table-------------------------
    st.subheader("Strategy vs Benchmark")
    comparison_df = pd.DataFrame({
        "Metric": ["Total Return", "Realized Return", "Volatility", "Sharpe Ratio", "Max Drawdown"],
        "Strategy":[
            f"{result['total_return']:.2%}",
            f"{result['realized_return']:.2%}",
            f"{result['realized_volatility']:.2%}",
            f"{result['realized_sharpe']:.2f}",
            f"{result['max_drawdown']:.2%}"
        ],
        "Benchmark": [
            f"{result['benchmark_total_return']:.2%}",
            f"{result['benchmark_return']:.2%}",
            f"{result['benchmark_volatility']:.2%}",
            f"{result['benchmark_sharpe']:.2f}",
            f"{result['benchmark_max_drawdown']:.2%}"
        ]
    })
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    st.divider()

#Cumulative Returns Chart ----------------------------
    st.subheader("Cumulative Returns Chart")
    cum_portfolio = pd.Series(result["cumulative_returns"])
    cum_benchmark = pd.Series(result["benchmark_cumulative"])
    cum_portfolio.index = pd.to_datetime(cum_portfolio.index)
    cum_benchmark.index = pd.to_datetime(cum_benchmark.index)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x = cum_portfolio.index,
        y = cum_portfolio.values,
        name="Strategy",
        line=dict(color="#00CC96", width=2)
    ))
    fig.add_trace(go.Scatter(
        x = cum_benchmark.index,
        y = cum_benchmark.values,
        name = "Benchmark (Equal Weight)",
        line = dict(color="#EF553B", width=2, dash="dash")
    ))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Cumulative Return (1=starting Value)",
        hovermode="x unified",
        legend=dict(orientation="h",yanchor="bottom", y=1.02)
    )
    fig.add_hline(y=1.0,line_dash="dot", line_color="gray",
                 annotation_text="Starting Value")
    st.plotly_chart(fig,use_container_width=True)

    st.divider()

    #---Drawdown Chart-----------------------
    st.subheader("📉 Drawdown")

    running_max = cum_portfolio.cummax()
    drawdown = (cum_portfolio-running_max)/running_max

    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown.values,
        fill="tozeroy",
        name="Drawdown",
        line = dict(color = "#EF553B"),
        fillcolor="rgba(239,85,59,0.3)"
    ))
    fig_dd.update_layout(
        xaxis_title="Date",
        yaxis_title="Drawdown",
        yaxis_tickformat = ".0%",
        hovermode = "x unified"
    )
    st.plotly_chart(fig_dd, use_container_width=True)

    #-----Optimal Weights-----------------
    st.subheader("⚖️ Trained Optimal Weights")
    weights = result.get("optimal_weights",{})
    if weights:
        fig_w = px.bar(
            x=list(weights.keys()),
            y=list(weights.values()),
            labels = {"x":"Ticker","y":"Weight"},
            text_auto=".0%",
            color=list(weights.keys())
        )
        fig_w.update_layout(yaxis_tickformat=".0%", showlegend=False)
        st.plotly_chart(fig_w, use_container_width=True)


