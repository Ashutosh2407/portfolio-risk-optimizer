import sys
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add to path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
import pytest
from src.models.optimizer import PortfolioOptimizer

class Testoptimizer:
    @pytest.fixture
    def sample_returns(self):
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=252, freq='B')
        returns = pd.DataFrame({
            'AAPL': np.random.normal(0.001,0.02,252),
            'MSFT': np.random.normal(0.001,0.02,252),
            'JPM': np.random.normal(0.001,0.02,252),
            'GS': np.random.normal(0.001,0.02,252),
        },index=dates)
        return returns
    
    @pytest.fixture
    def sample_optimizer(self):
        return PortfolioOptimizer()
    
    def test_no_negative_weights_max_sharpe(self,sample_optimizer,sample_returns):
        result = sample_optimizer.optimize_max_sharpe(sample_returns)
        weights = result["weights"].values()
        assert all(x > 0 for x in weights),"Weights must be positive."

    def test_no_negative_weights_min_volatility(self,sample_optimizer,sample_returns):
        result = sample_optimizer.optimize_min_volatility(sample_returns)
        weights = result["weights"].values()
        assert all(x > 0 for x in weights),"Weights must be positive."

    def test_max_weight_constraint_respected_max_sharpe(self,sample_optimizer,sample_returns):
        result = sample_optimizer.optimize_max_sharpe(sample_returns)
        weights = result["weights"].values()
        assert all(x <= sample_optimizer.config.max_weight_per_asset for x in weights),"Weights cannot be greater than Max weight assigned."
    
    def test_max_weight_constraint_respected_min_volatility(self,sample_optimizer,sample_returns):
        result = sample_optimizer.optimize_min_volatility(sample_returns)
        weights = result["weights"].values()
        assert all(x <= sample_optimizer.config.max_weight_per_asset for x in weights),"Weights cannot be greater than Max weight assigned."

    def test_sharpe_ratio_is_calculated_max_sharpe(self,sample_optimizer,sample_returns):
        result = sample_optimizer.optimize_max_sharpe(sample_returns)
        sharpe_ratio = result["sharpe_ratio"]
        assert sharpe_ratio is not None, "Sharpe ratio must be calculated and cannot be None."

    def test_sharpe_ratio_is_calculated_min_volatility(self,sample_optimizer,sample_returns):
        result = sample_optimizer.optimize_min_volatility(sample_returns)
        sharpe_ratio = result["sharpe_ratio"]
        assert sharpe_ratio is not None, "Sharpe ratio must be calculated and cannot be None."
    