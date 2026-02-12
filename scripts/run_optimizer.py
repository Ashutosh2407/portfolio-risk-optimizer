from src.data.db_client import DatabaseClient
from src.data.processor import MarketDataProcessor
from src.models.optimizer import PortfolioOptimizer

symbols = ["AAPL","MSFT","GOOGL","JNJ","JPM","XOM","WMT","SPY"]

db = DatabaseClient()
processor = MarketDataProcessor(db)
out = processor.run(tickers=symbols)

opt = PortfolioOptimizer()
res1 = opt.optimize_max_sharpe(out["prices"])
res2 = opt.optimize_min_volatility(out["prices"])

print(res1["strategy"], res1["sharpe_ratio"], res1["weights"])
print(res2["strategy"], res2["sharpe_ratio"], res2["weights"])