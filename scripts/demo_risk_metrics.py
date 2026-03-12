"""
Demo script to showcase risk metrics on real portfolio data.
This is for manual testing and demonstration purposes.
"""


import sys
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)


import numpy as np
import pandas as pd
from src.models.risk import RiskMetrics
from src.data.collector import DataCollector
from src.data.processor import MarketDataProcessor
from src.data.db_client import DatabaseClient


def demo_risk_metrics():
    """Demonstrate risk metrics calculation"""
    
    # Example portfolio
    symbols = ['AAPL', 'GOOGL', 'MSFT']
    weights = {'AAPL': 0.3, 'GOOGL': 0.5, 'MSFT': 0.2}

    print("=" * 50)
    print("PORTFOLIO RISK METRICS DEMO")
    print("=" * 50)
    print(f"\nPortfolio: {symbols}")
    print(f"Weights: {weights}")

    # Load historical data
    print("\n📊 Loading historical data...")
    
    db = DatabaseClient()
    processor = MarketDataProcessor(db)
    # Adjust this based on your actual processor methods
    out = processor.run(tickers = symbols)
    returns = out['returns']
    print("Displaying Returns")
    print("=" * 50)
    print(returns)
    print("=" * 50)

    print("\n📈 Calculating risk metrics...")
    risk = RiskMetrics(returns, weights)
    print("\n" + "=" * 50)
    print("RISK METRICS RESULTS")
    print("=" * 50)

    vol = risk.portfolio_volatility()
    print(f"\n📊 Portfolio Volatility (Annual): {vol*100:.2f}%")
    
    var_95 = risk.value_at_risk(0.95)
    var_99 = risk.value_at_risk(0.99)
    print(f"\n⚠️  Value at Risk:")
    print(f"   95% VaR: {var_95*100:.2f}%")
    print(f"   99% VaR: {var_99*100:.2f}%")
    
    cvar_95 = risk.conditional_var(0.95)
    print(f"\n🔴 Conditional VaR (95%): {cvar_95*100:.2f}%")

    max_dd = risk.maximum_drawdown()
    print(f"\n📉 Maximum Drawdown: {max_dd*100:.2f}%")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    demo_risk_metrics()


   

    

    
    