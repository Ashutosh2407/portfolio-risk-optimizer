import sys
import os

# Get the absolute path to the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.data.db_client import DatabaseClient
from src.data.processor import MarketDataProcessor
from src.models.optimizer import PortfolioOptimizer

import pandas as pd

symbols = [
        # Tech (25%)
        'AAPL', 'GOOGL', 'MSFT', 'NVDA', 'META',
        
        # Finance (20%)
        'JPM', 'BAC', 'V', 'GS',
        
        # Healthcare (15%)
        'JNJ', 'UNH', 'PFE',
        
        # Consumer (15%)
        'WMT', 'PG', 'KO',
        
        # Energy (10%)
        'XOM', 'CVX',
        
        # Industrial (10%)
        'CAT', 'BA',
        
        # Market Index (for beta calculation)
        'SPY'
    ]

db = DatabaseClient()
processor = MarketDataProcessor(db)
out = processor.run(tickers=symbols)

opt = PortfolioOptimizer()
res1 = opt.optimize_max_sharpe(out["prices"])
res2 = opt.optimize_min_volatility(out["prices"])

#print(res1["strategy"], res1["sharpe_ratio"], res1["weights"])
#print(res2["strategy"], res2["sharpe_ratio"], res2["weights"])

db.save_optimization_result({
    "strategy":res1["strategy"],
    "expected_annual_return":res1["expected_annual_return"],
    "annual_volatility":res1["annual_volatility"],
    "sharpe_ratio":res1[ "sharpe_ratio"],
    "weights":res1["weights"]
})

db.save_optimization_result({
    "strategy":res2["strategy"],
    "expected_annual_return":res2["expected_annual_return"],
    "annual_volatility":res2["annual_volatility"],
    "sharpe_ratio":res2[ "sharpe_ratio"],
    "weights":res2["weights"]
})