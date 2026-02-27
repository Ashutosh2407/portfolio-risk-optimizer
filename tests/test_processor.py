import sys
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add to path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.data.processor import MarketDataProcessor, ProcessorConfig
import numpy as np
import pytest

class TestProcessor:
    """
    Unit Test for Processor
    """
    
    
    @pytest.fixture
    def processor(self,mock_db):
        config = ProcessorConfig(missing_prices="ffill")
        return MarketDataProcessor(db = mock_db,config = config)


    def test_return_matrix_has_no_nan(self,processor,sample_prices):
        returns = processor.generate_returns_matrix(sample_prices)
        assert returns is not None
        assert not returns.empty
        assert not returns.isnull().values.any(), "Returns must not contain NaN values"

    def test_generate_risk_metrics(self,processor,sample_prices):
        returns = processor.generate_returns_matrix(sample_prices)
        risk_metrics = processor.generate_risk_matrix(returns)
        cov_daily = risk_metrics["cov_daily"]
        cov_annual = risk_metrics["cov_annual"]
        corr = risk_metrics["corr"]

        assert np.array_equal(cov_daily,cov_daily.T), "Covariance matrix must be symmetrical."
        assert np.array_equal(cov_annual,cov_annual.T), "Covariance matrix must be symmetrical."
        assert np.array_equal(corr,corr.T), "Correlation matrix must be symmetrical."