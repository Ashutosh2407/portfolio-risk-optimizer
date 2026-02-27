import sys
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# Add to path if not already there
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
import numpy as np
import pandas as pd
from unittest.mock import MagicMock,AsyncMock
from fastapi.testclient import TestClient
from src.api.main import app
from src.api.optimizer import get_optimizer
from src.api.processor import get_processor
from src.api.database import get_db
from src.models.optimizer import PortfolioOptimizer
from src.data.processor import MarketDataProcessor
from src.data.db_client import DatabaseClient


TICKERS = ["AAPL", "MSFT", "JPM"]
ANNUALIZATION_FACTOR = 252

@pytest.fixture
def sample_returns():
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
def sample_prices():
    """
    Create sample prices for testing.
    """
    np.random.seed(42)
    rng = np.random.default_rng(42)
    dates = pd.date_range('2023-01-01', periods = 252, freq = 'B')
    prices = pd.DataFrame({
        'AAPL': rng.integers(1,500,252),
        'MSFT': rng.integers(1,500,252),
        'JPM': rng.integers(1,500,252),
        'GS': rng.integers(1,500,252)
    }, index = dates)

    return prices

@pytest.fixture
def sample_weights():
    """Portfolio sample weights"""
    return {'AAPL':0.3,'GOOGL':0.5,'MSFT':0.1,'GS':0.1}

@pytest.fixture
def mock_db():
    db = MagicMock(spec=DatabaseClient)
    return db


def make_mock_db(row =None, rows = None):
    """
    Builds a fake AsyncSession that returns
    whatever row/rows you pass in.
    """
    mock_db = AsyncMock()
    #Mock the result of db.execute()
    mock_result = MagicMock()
    mock_result.mappings.return_value.first.return_value = row #for latest
    mock_result.mappings.return_value.all.return_value = rows or [] #for history
    mock_db.execute.return_value = mock_result

    return mock_db

@pytest.fixture
def fake_process_result(sample_returns):
    corr = sample_returns.corr()
    cov_daily = sample_returns.cov()
    cov_annual = cov_daily * ANNUALIZATION_FACTOR

    return {
        "returns":sample_returns,
        "corr":corr,
        "cov_daily":cov_daily,
        "cov_annual":cov_annual
    }

@pytest.fixture
def mock_processor(fake_process_result):
    mock = MagicMock(spec=MarketDataProcessor)
    mock.run.return_value = fake_process_result
    return mock

@pytest.fixture
def mock_optimizer():
    mock = MagicMock(spec = PortfolioOptimizer)
    mock.optimize_max_sharpe.return_value = {
        "strategy": "max_sharpe",
        "expected_annual_return": 0.15,
        "annual_volatility": 0.18,
        "sharpe_ratio": 1.2,
        "weights": {"AAPL": 0.4, "MSFT": 0.35, "JPM": 0.25},
    }
    mock.optimize_min_volatility.return_value = {
        "strategy": "min_volatility",
        "expected_annual_return": 0.12,
        "annual_volatility": 0.14,
        "sharpe_ratio": 1.0,
        "weights": {"AAPL": 0.33, "MSFT": 0.33, "JPM": 0.34},
    }
    return mock

@pytest.fixture
def client(mock_processor,mock_optimizer):
    app.dependency_overrides[get_processor] = lambda: mock_processor
    app.dependency_overrides[get_optimizer] = lambda:mock_optimizer
    app.dependency_overrides[get_db] = lambda:mock_db
    yield TestClient(app=app)
    app.dependency_overrides.clear()