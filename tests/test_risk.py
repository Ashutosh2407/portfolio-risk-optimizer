import sys
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add to path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}") 

import pytest
import numpy as np
import pandas as pd
from src.models.risk import RiskMetrics

class TestRiskMetrics:
    """
    Unit test for Risk calculations.
    """

    @pytest.fixture
    def sample_returns(self):
        """
        Create sample return data for testing.
        """
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods = 252, freq = 'D')
        returns = pd.DataFrame({
            'AAPL':np.random.normal(0.001,0.02,252),
            'GOOGL':np.random.normal(0.0008,0.025,252),
            'AAPL':np.random.normal(0.0012,0.018,252)
        }, index=dates)

        return returns
    
    @pytest.fixture
    def sample_weights(self):
        """Portfolio sample weights"""
        return {'AAPL':0.3,'GOOGL':0.5,'MSFT':0.2}
    
    def test_portfolio_volatility_positive(self,sample_returns,sample_weights):
        risk = RiskMetrics(sample_returns,sample_weights)
        vol = risk.portfolio_volatility()

        assert vol > 0, "Volatility must be positive."

    def test_portfolio_volatility_annualized(self,sample_returns, sample_weights):
        risk = RiskMetrics(sample_returns,sample_weights)
        vol_daily = risk.portfolio_volatility(annualize=False)
        vol_annualized = risk.portfolio_volatility(annualize=True)

        # Annual vol should be roughly sqrt(252) times daily vol
        assert vol_annualized > vol_daily
        assert np.isclose(vol_annualized, vol_daily*np.sqrt(252), rtol = 0.01)

    def test_var_is_negative(self,sample_returns, sample_weights):
        risk = RiskMetrics(sample_returns,sample_weights)
        var_95 = risk.value_at_risk(confidence_level=0.95)
        var_99 = risk.value_at_risk(confidence_level=0.99)

        # VaR should typically be negative (loss)
        assert var_95 < 0, "VaR should be negative (loss)"
        assert var_99 < 0, "VaR should be negative (loss)"

    def test_var_99_worse_than_var_95(self, sample_returns, sample_weights):
        risk = RiskMetrics(sample_returns,sample_weights)
        var_95 = risk.value_at_risk(confidence_level=0.95)
        var_99 = risk.value_at_risk(confidence_level=0.99)

        # 99% VaR should be more negative (worse loss) than 95%
        assert var_99 < var_95, "99% var must be worse than 95% var."

    def test_cvar_worse_than_var(self, sample_returns, sample_weights):
        """Test that CVaR is worse than VaR (tail risk)"""
        risk = RiskMetrics(sample_returns,sample_weights)
        var_95 = risk.value_at_risk(confidence_level=0.95)
        cvar_95 = risk.conditional_var(confidence_level=0.95)

        assert cvar_95 < var_95, "Conditional Var must be less than VaR."

    def test_requires_weight_for_portfolio_metrics(self,sample_returns):
        risk = RiskMetrics(sample_returns, weights = None)

        with pytest.raises(ValueError, match = "Weights required."):
            risk.value_at_risk(0.95)

        with pytest.raises(ValueError, match="Weights required"):
            risk.conditional_var(0.95)
        
        with pytest.raises(ValueError, match="Weights required"):
            risk.maximum_drawdown()
        
        with pytest.raises(ValueError, match="Weights required"):
            risk.portfolio_volatility()

    def test_weights_to_sum_to_one(self,sample_returns, sample_weights):
        """Test that weights sum to approximately 1.0"""
        assert np.isclose(sum(sample_weights.values()),1.0), "Weights should sum to 1."

    def test_max_drawdown_is_negative(self,sample_returns,sample_weights):
        risk = RiskMetrics(sample_returns,sample_weights)
        max_drawdown = risk.maximum_drawdown()
        assert max_drawdown < 0, "Maximum Drawdown must be negative."







