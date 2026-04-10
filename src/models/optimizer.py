from __future__ import annotations
from dataclasses import dataclass
from typing import Dict,Optional
import pandas as pd
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import expected_returns, risk_models

@dataclass
class OptimizerConfig:
    risk_free_rate: float = 0.043
    weight_bounds: tuple = (0.0,1.0)
    max_weight_per_asset: Optional[float] = 0.30 # e.g., cap any single asset at 30%


class PortfolioOptimizer:
    """
    Mean-variance portfolio optimization.
    Inputs: price matrix (preferred) OR returns matrix.
    """
    def __init__(self,config: Optional[OptimizerConfig]=None):
        self.config = config or OptimizerConfig()

    def _build_mu_cov(self,returns:pd.DataFrame) -> tuple[pd.Series, pd.DataFrame]:
        #Expected returns from prices
        mu = expected_returns.mean_historical_return(returns, returns_data=True) #Annualized by default
        #Covariance from Prices
        S = risk_models.sample_cov(returns, returns_data=True) #Annualized By default
        # Alternative:
        # S = CovarianceShrinkage(prices).ledoit_wolf()
        return mu,S
    
    def optimize_max_sharpe(self, returns: pd.DataFrame) -> Dict:
        """
        Tangency portfolio (max Sharpe)
        """
        mu,S = self._build_mu_cov(returns)
        ef =EfficientFrontier(mu,S, weight_bounds=self.config.weight_bounds)

        #Constraint: Cap each weight
        if self.config.max_weight_per_asset is not None:
            ef.add_constraint(lambda w: w <= self.config.max_weight_per_asset)
        try:
            ef.max_sharpe(risk_free_rate=self.config.risk_free_rate)
            weights = ef.clean_weights() # rounds/clips near-zeros
            perf = ef.portfolio_performance(verbose= False, risk_free_rate=self.config.risk_free_rate) #(ret,vol,sharpe)
        except:
            return "Solver cannot solve under current constraints."
        
        return {
            "strategy": "max_sharpe",
            "expected_annual_return": perf[0],
            "annual_volatility":perf[1],
            "sharpe_ratio": perf[2],
            "weights":weights
        }
    
    def optimize_min_volatility(self, returns:pd.DataFrame)-> Dict:
        """
        Minimum volatility portfolio
        """
        mu, S = self._build_mu_cov(returns)
        ef = EfficientFrontier(mu,S, weight_bounds=self.config.weight_bounds)

        if self.config.max_weight_per_asset is not None:
            ef.add_constraint(lambda w: w <= self.config.max_weight_per_asset)

        ef.min_volatility()
        weights = ef.clean_weights()
        perf = ef.portfolio_performance(verbose=False, risk_free_rate= self.config.risk_free_rate)

        return {
            "strategy": "min_volatility",
            "expected_annual_return": perf[0],
            "annual_volatility":perf[1],
            "sharpe_ratio": perf[2],
            "weights":weights,
        }
