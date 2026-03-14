#params: Tickers and Strategy
import streamlit as st
from api_client import run_optimizer
from api_client import get_tickers
import plotly.express as px

st.set_page_config(page_title="Optimizer",
                   page_icon="⚙️",
                   layout = "wide")

st.title("Optimization")
st.markdown("Enter the list of tickers and the strategy to generate optimal portfolio.")

#Inputs
tickers_list = get_tickers()["tickers"]
selected_tickers = st.multiselect("Select Tickers", options=tickers_list)


strategy = st.selectbox(
    "Strategy",
    options=["max_sharpe", "min_vol"],
    format_func= lambda x: "Maximum Sharpe Ratio" if x == "max_sharpe" else "Minimum Volatility",
    width= 300
)

#Run Button
if st.button("Run", type= "primary"):
    tickers = [t.strip().upper() for t in selected_tickers if t.strip()]
    if len(tickers) < 4:
        st.error("Please enter at least 4 stocks in your portfolio.")
    else:
        with st.spinner("Optimizing Portfolio..."):
            result = run_optimizer(tickers,strategy)

            if not result:
                st.error(f"Optimization Failed.")
            
            else:
                st.success("Optimization Complete!")
                weights = result.get("weights", {})

                #Metrics row
                col1,col2 = st.columns(2)
                col1.metric("Strategy", strategy.replace("_"," ").title())
                col2.metric("Number of Stocks", len(weights))

                #2 charts side by side
                col1,col2 = st.columns(2)
                with col1:
                    st.subheader("Weights Distribution")
                    fig_bar = px.bar(
                        x = list(weights.keys()),
                        y = list(weights.values()),
                        labels = {"x": "Tickers", "y": "Weight (in %)"},
                        title = "Optimal Weights"
                    )
                    st.plotly_chart(fig_bar,use_container_width=True)

                with col2:
                    st.subheader("Portfolio Allocation")
                    fig_bar = px.pie(
                        names = list(weights.keys()),
                        values = list(weights.values()),
                        title = "Weight Breakdown"
                    )
                    st.plotly_chart(fig_bar,use_container_width=True)
                
                st.subheader("Weights Allocation")
                st.dataframe(
                    {"Ticker":list(weights.keys()),"Weight":[f"{w:.2%}" for w in weights.values()]},
                    width = 400
                )


