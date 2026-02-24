from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field
from .database import get_db
from .optimizer import get_optimizer
from .processor import get_processor
from ..models.backtest import Backtester
from ..models.optimizer import PortfolioOptimizer
from ..models.risk import RiskMetrics
from ..models.backtest import Backtester
from ..data.db_client import DatabaseClient
from ..data.processor import MarketDataProcessor


app = FastAPI(title = "Portfolio Risk Optimizer API",
              version="1.0.0"
              )

db = DatabaseClient()

#Health Check
@app.get("/")
async def health_check():
    return {"status": "ok"}

#Latest Results
@app.get("/results/latest")
async def results_latest(db: AsyncSession = Depends(get_db)):
    query = text("""
        SELECT * FROM optimization_results
                 order by timestamp DESC
                 LIMIT(1)
                """)
    result = await db.execute(query)
    row = result.mappings().first()

    if row is None:
        raise HTTPException(status_code=404, detail = "No results found.")
    return dict(row)

#Results History
@app.get("/results/history")
async def results_history(limit: int = Query(20,ge=1,le=100), db: AsyncSession = Depends(get_db)):
    query = text("""
                SELECT * FROM optimization_results
                 order by timestamp DESC
                 LIMIT :limit
                """)
    result = await db.execute(query,{"limit":limit})
    rows= result.mappings().all()
    return {"results":[dict(r) for r in rows],"count": len(rows)}

class Strategy(str, Enum):
    max_sharpe = "max_sharpe"
    min_vol = "min_vol"
    benchmark = "benchmark"

class OptimizeModelResponse(BaseModel):
    tickers: List[str]
    strategy: Strategy
    weights: Dict[str,float]
    objective_value: Optional[float] = None
    timestamp: Optional[str] = None

#Optimize
@app.get("/optimize", response_model= OptimizeModelResponse)
async def optimize(
    tickers: List[str] = Query(...,min_length=1,description="Repeat param: ?tickers=AAPL&tickers=MSFT&tickers=JPM&tickers=BAC&tickers=V&tickers=GS"),
    strategy: Strategy = Strategy.max_sharpe,
    processor: MarketDataProcessor = Depends(get_processor),
    optimizer: PortfolioOptimizer = Depends(get_optimizer)
):
    clean_tickers = [t.strip().upper() for t in tickers if t and t.strip()]
    if len(clean_tickers) < 1:
        raise HTTPException(status_code=422, detail="Tickers cannot be empty.")
    
    n = len(clean_tickers)
    processor_result = processor.run(clean_tickers)
    
    if strategy == "max_sharpe":
        result = optimizer.optimize_max_sharpe(processor_result["returns"])
    elif strategy == "min_vol":
        result = optimizer.optimize_min_volatility(processor_result["returns"])
        
    d_weights = result["weights"]
    #weights = [d_weights[clean_ticker] for clean_ticker in clean_tickers]
    return OptimizeModelResponse(tickers=clean_tickers,strategy= strategy, weights=d_weights)

class RiskResponseModel(BaseModel):
    tickers: List[str]
    weights: Dict[str,float]
    volatility: Optional[float] = None
    max_drawdown: Optional[float] = None
    var_95: Optional[float] = None
    cvar: Optional[float] = None



#Risk
@app.get("/risk", response_model=RiskResponseModel)
async def risk(
    tickers: List[str] = Query(...),
    weights: List[float] = Query(..., description="Repeat: ?weights=0.5&weights=0.5, must sum to 1.0"),
    processor: MarketDataProcessor = Depends(get_processor),
    ):
    #Validate lenghts match
    if len(tickers) != len(weights):
        raise HTTPException(status_code=422, detail="Symbols and weights must have equal length.")

    if abs(sum(weights)-1.0) > 1e-4:
        raise HTTPException(status_code=422, detail=f"Weights must sum up to 1.0,got {sum(weights):.6f}")
    
    weights_dict = dict(zip(tickers,weights))

    #Build returns dataframe via Processor
    result = processor.run(tickers)
    returns = result["returns"]

    risk_metrics = RiskMetrics(returns=returns, weights=weights_dict)
    volatility = risk_metrics.portfolio_volatility()
    cvar = risk_metrics.conditional_var()
    max_drawdown = risk_metrics.maximum_drawdown()
    var_95 = risk_metrics.value_at_risk()

    return RiskResponseModel(tickers = tickers,
                             weights=weights_dict,
                             volatility = volatility,
                             max_drawdown=max_drawdown,
                             var_95=var_95,
                             cvar=cvar)
    


#Backtest
@app.get("/backtest")
async def backtest(
    tickers: List[str] = Query(...),
    weights: List[float] =Query(...),
    strategy:Strategy =Strategy.max_sharpe,
    processor:MarketDataProcessor = Depends(get_processor)
    ):

    if len(tickers) != len(weights):
        raise HTTPException(422, "symbols and weights must have equal length")
    if abs(sum(weights) - 1.0) > 1e-4:
        raise HTTPException(422, "weights must sum to 1.0")
    
    weights_dict = dict(zip(tickers,weights))
    # Build returns DataFrame
    result = await run_in_threadpool(processor.run,tickers)
    returns = result["returns"]
    if returns is None or returns.empty:
        raise HTTPException(status_code=404, detail="No returns data found for requested tickers.")
    
    backtester = Backtester(returns_data=returns,strategy=strategy)
    res = await run_in_threadpool(backtester.run_backtest)
    await run_in_threadpool(db.save_backtest_results,res)

    return res
    




    

