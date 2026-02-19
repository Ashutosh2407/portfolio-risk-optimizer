"""
Backtesting framework for portfolio optimization strategies.
Walk-forward testing on out-of-sample data.
"""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
from .optimizer import PortfolioOptimizer
from .risk import RiskMetrics



class Backtester:
    """Walk-forward backtesting for portfolio optimization strategies"""

    def __init__(self, returns_data, strategy = 'max_sharpe', rebalance_frequency = 'quarterly'):
        """
        Initialize backtester.
        
        Args:
            returns_data: DataFrame of asset returns (rows=dates, cols=symbols)
            strategy: 'max_sharpe' or 'min_volatility'
            rebalance_freq: 'monthly', 'quarterly', 'yearly' (for future use)
        """
        self.returns_data = returns_data
        self.strategy = strategy
        self.rebalance_frequency = rebalance_frequency
        self.optimizer = PortfolioOptimizer()

    def split_train_test(self, train_period_days = 252):
        """
        train_period_days: Number of days for training window (252 = 1 year)
        
        Returns:
            tuple: (train_data, test_data)
        """
        if len(self.returns_data) <252 :
            raise ValueError(f"Not Enough data. Need atleast {train_period_days} days of data.")
        
        train_data = self.returns_data.iloc[:train_period_days]
        test_data = self.returns_data.iloc[train_period_days:]

        return (train_data, test_data)
    
    def run_backtest(self, train_period_days=252, max_weight = 0.4):
        """
        Run walk-forward backtest.
        
        Args:
            train_period_days: Days to use for training (default 252 = 1 year)
            max_weight: Maximum weight per asset
        
        Returns:
            dict: Backtest results with metrics and comparison
        """
        print(f"\n🔄 Running {self.strategy} backtest...")
        # Split data
        train_data, test_data = self.split_train_test(train_period_days)
        print(f"   Train: {train_data.index[0].date()} to {train_data.index[-1].date()} ({len(train_data)} days)")
        print(f"   Test:  {test_data.index[0].date()} to {test_data.index[-1].date()} ({len(test_data)} days)")

        # # ===== DEBUG CHECKS =====
        # print("\n🔍 DEBUG: Checking train data quality...")
        # print(f"   Shape: {train_data.shape}")
        # print(f"   NaN count:\n{train_data.isna().sum()}")
        # print(f"   Inf count:\n{np.isinf(train_data).sum()}")
        # print(f"   Date range: {train_data.index[0]} to {train_data.index[-1]}")
        # print(f"   First rows:\n{train_data.head(3)}")
        # print(f"   Stats:\n{train_data.describe()}")
        
        # # Check for problematic values
        # print(f"\n   Values > 1 (>100% daily return):")
        # print(train_data[train_data > 1].dropna(how='all'))
        
        # print(f"\n   Values < -1 (<-100% daily return):")
        # print(train_data[train_data < -1].dropna(how='all'))
        # ========================

        # 2. Optimize on training data
        print(f"   Optimizing on training data...")
        if self.strategy == 'max_sharpe':
            result = self.optimizer.optimize_max_sharpe(train_data)
        elif self.strategy == "min_volatility":
            result = self.optimizer.optimize_min_volatility(train_data)
        else:
            raise ValueError(f"Unknown strategy: {self.strategy}.")
        
        optimal_weights = result["weights"]
        print(f"   Optimal weights: {optimal_weights}")

        # 3. Apply weights to test period (out-of-sample)
        test_portfolio_returns = (test_data * pd.Series(optimal_weights)).sum(axis=1)

        # 4. Calculate realized metrics
        realized_return = test_portfolio_returns.mean()*252 #Annualized
        realized_volatility = test_portfolio_returns.std() * np.sqrt(252) #Annualized
        realized_sharpe = realized_return / realized_volatility if realized_volatility > 0 else 0

        # 5. Calculate cumulative returns
        cumulative_returns = (1 + test_portfolio_returns).cumprod()

        # 6. Benchmark: Equal-weight portfolio
        equal_weights = {symbol: 1/len(test_data.columns) for symbol in test_data.columns}
        benchmark_returns = (test_data * pd.Series(equal_weights)).sum(axis =1)
        benchmark_cumulative = (1+benchmark_returns).cumprod()

        benchmark_return = benchmark_returns.mean() * 252 #Annualized
        benchmark_volatility = benchmark_returns.std() * np.sqrt(252) #Annualized
        benchmark_sharpe = benchmark_return /benchmark_volatility if benchmark_volatility >0 else 0

        # 7. Calculate Risk Metrics on test data
        risk_metrics = RiskMetrics(test_data, optimal_weights)
        max_drawdown = risk_metrics.maximum_drawdown(annualize=True)

        # 8. Calculate Risk Metrics on benchmark data
        benchmark_risk = RiskMetrics(test_data, equal_weights)
        benchmark_max_drawdown = benchmark_risk.maximum_drawdown(annualize=True)

        # Debug - check benchmark returns scale
        print(f"\nBenchmark returns sample:\n{benchmark_returns.head(10)}")
        print(f"Benchmark returns stats:\n{benchmark_returns.describe()}")

        # Check cumulative
        print(f"\nBenchmark cumulative:\n{benchmark_cumulative.head(10)}")
        print(f"Benchmark final value: {benchmark_cumulative.iloc[-1]}")

        return {
            'strategy': self.strategy,
            'train_period': f"{train_data.index[0].date()} to {train_data.index[-1].date()}",
            'test_period': f"{test_data.index[0].date()} to {test_data.index[-1].date()}",
            'train_days': len(train_data),
            'test_days' : len(test_data),
            'optimal_weights': optimal_weights,

            # Portfolio performance
            'realized_return': realized_return,
            'realized_volatility': realized_volatility,
            'realized_sharpe': realized_sharpe,
            'max_drawdown': max_drawdown,
            'total_return':cumulative_returns.iloc[-1]-1,

            # Benchmark Performance
            'benchmark_return': benchmark_return,
            'benchmark_volatility': benchmark_volatility,
            'benchmark_sharpe': benchmark_sharpe,
            'benchmark_max_drawdown': benchmark_max_drawdown,
            'benchmark_total_return':benchmark_cumulative.iloc[-1]-1,

            # Time series for visualization
            'portfolio_returns': test_portfolio_returns,
            'cumulative_returns': cumulative_returns,
            'benchmark_returns': benchmark_returns,
            'benchmark_cumulative': benchmark_cumulative,

        }







