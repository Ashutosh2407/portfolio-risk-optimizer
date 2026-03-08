import numpy as np
import pandas as pd
from src.utils.logger import get_logger

logger = get_logger(__name__)

class RiskMetrics:
    """
    Calculate portfolio risk metrics.
    """
    def __init__(self,returns, weights=None):
        """
        Args:
            returns: DataFrame of asset returns (rows=dates, cols=symbols)
            weights: Dict of portfolio weights (optional, for portfolio-level metrics)
        """
        self.returns = returns
        self.weights = weights

        if self.weights:
            self.portfolio_returns = (self.returns * pd.Series(self.weights)).sum(axis=1)

    def value_at_risk(self, confidence_level = 0.95):
        """
        Calculate Value at Risk (VaR) - maximum expected loss at confidence level
        
        Args:
            confidence_level: 0.95 for 95% VaR, 0.99 for 99% VaR
        
        Returns:
            float: VaR as a negative number (loss)
        """
        if self.weights is None:
            raise ValueError("Weights required for Portfolio VaR.")
        logger.info(f"VAR: {np.percentile(self.portfolio_returns,(1-confidence_level)*100)
}")
        return np.percentile(self.portfolio_returns,(1-confidence_level)*100)

    
    def conditional_var(self, confidence_level=0.95):
        """
        Calculate Conditional VaR (CVaR) / Expected Shortfall
        Average loss beyond the VaR threshold
        
        Returns:
            float: CVaR as a negative number (loss)

        """
        if self.weights is None:
            raise ValueError("Weights required for Portfolio CVaR.")
        
        var = self.value_at_risk(confidence_level)
        return self.portfolio_returns[self.portfolio_returns <= var].mean()
    
    def maximum_drawdown(self, annualize = True):
        """
        Calculate maximum drawdown - largest peak to trough decline

        Returns:
            float: Max drawdown as a negative percentage
        """

        if self.weights is None:
            raise ValueError("Weights required for portfolio drawdown.")
        
        cumulative = (1+self.portfolio_returns).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative-running_max)/running_max
        logger.info(f"Maximum Drawdown:{drawdown.min()}")
        return drawdown.min()
    

    def portfolio_volatility(self, annualize = True):
        """
        Calculate portfolio volatility (standard deviation)
        
        Args:
            annualize: If True, annualize using sqrt(252)
        
        Returns:
            float: Portfolio volatility
        """
        if self.weights is None:
            raise ValueError("Weights required for portfolio volatility.")

        vol = self.portfolio_returns.std()

        if annualize:
            vol *= np.sqrt(252)
        logger.info(f"Volatility:{vol}")
        return vol

    

        


