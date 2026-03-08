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
from ..utils.logger import get_logger

app = FastAPI(title = "Portfolio Risk Optimizer API",
              version="1.0.0"
              )

logger = get_logger(__name__)

#Health Check
@app.get("/")
async def health_check():
    logger.info("Healthcheck called.")
    return {"status": "ok"}

#Latest Results
@app.get("/results/latest")
async def results_latest(db: AsyncSession = Depends(get_db)):
    logger.info("Fetching latest optimization results.")
    query = text("""
        SELECT * FROM optimization_results
                 order by timestamp DESC
                 LIMIT(1)
                """)
    result = await db.execute(query)
    row = result.mappings().first()

    if row is None:
        logger.warning("No optimization results found in database.")
        raise HTTPException(status_code=404, detail = "No results found.")
    return dict(row)

#Results History
@app.get("/results/history")
async def results_history(limit: int = Query(20,ge=1,le=100), db: AsyncSession = Depends(get_db)):
    logger.info(f"Fetching optimization histroy | limit: {limit}")
    query = text("""
                SELECT * FROM optimization_results
                 order by timestamp DESC
                 LIMIT :limit
                """)
    result = await db.execute(query,{"limit":limit})
    rows= result.mappings().all()
    logger.info(f"Returned {len(rows)} historical results.")
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
    logger.info(f"Optimization requested | tickers={clean_tickers} | strategy={strategy}")
    if len(clean_tickers) < 1:
        logger.warning("Empty tickers list received")
        raise HTTPException(status_code=422, detail="Tickers cannot be empty.")
    
    n = len(clean_tickers)
    try:
        processor_result = processor.run(clean_tickers)
        if strategy == Strategy.max_sharpe:
            result = optimizer.optimize_max_sharpe(processor_result["returns"])
        elif strategy == Strategy.min_vol:
            result = optimizer.optimize_min_volatility(processor_result["returns"])
        logger.info(f"Optimization complete | strategy={strategy} | tickers={clean_tickers}")
        d_weights = result["weights"]
        #weights = [d_weights[clean_ticker] for clean_ticker in clean_tickers]
        return OptimizeModelResponse(tickers=clean_tickers,strategy= strategy, weights=d_weights)
    
    except Exception as e:
        logger.error(f"Optimization failed | tickers={clean_tickers} | strategy={strategy} | error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))




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
    logger.info(f"Risk metrics requested | tickers={tickers} | weights={weights}")
    #Validate lenghts match
    if len(tickers) != len(weights):
        logger.warning(f"Tickers/weights length mismatch | tickers={len(tickers)} weights={len(weights)}")
        raise HTTPException(status_code=422, detail="Symbols and weights must have equal length.")

    if abs(sum(weights)-1.0) > 1e-4:
        logger.warning(f"Weights do not sum to 1.0 | sum={sum(weights):.6f}")
        raise HTTPException(status_code=422, detail=f"Weights must sum up to 1.0,got {sum(weights):.6f}")
    try:
        clean_tickers = [t.strip().upper() for t in tickers if t and t.strip()]
        weights_dict = dict(zip(clean_tickers,weights))

        #Build returns dataframe via Processor
        result = processor.run(tickers)
        returns = result["returns"]

        risk_metrics = RiskMetrics(returns=returns, weights=weights_dict)
        volatility = risk_metrics.portfolio_volatility()
        cvar = risk_metrics.conditional_var()
        max_drawdown = risk_metrics.maximum_drawdown()
        var_95 = risk_metrics.value_at_risk()

        logger.info(f"Risk metrics computed | vol={volatility:.4f} | VaR={var_95:.4f} | CVaR={cvar:.4f} | drawdown={max_drawdown:.4f}")

        return RiskResponseModel(tickers = tickers,
                                weights=weights_dict,
                                volatility = volatility,
                                max_drawdown=max_drawdown,
                                var_95=var_95,
                                cvar=cvar)
    except Exception as e:
        logger.error(f"Risk calculation failed | tickers={tickers} | error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



    


#Backtest
@app.get("/backtest")
async def backtest(
    tickers: List[str] = Query(...),
    weights: List[float] =Query(...),
    strategy:Strategy =Strategy.max_sharpe,
    processor:MarketDataProcessor = Depends(get_processor),
    db:DatabaseClient = Depends(get_db)):
    logger.info(f"Backtest requested | tickers={tickers} | strategy={strategy}")

    if len(tickers) != len(weights):
        logger.warning("Tickers/weights length mismatch in backtest")
        raise HTTPException(422, "symbols and weights must have equal length")
    if abs(sum(weights) - 1.0) > 1e-4:
        logger.warning(f"Weights do not sum to 1.0 in backtest | sum={sum(weights):.6f}")
        raise HTTPException(422, "weights must sum to 1.0")
    
    try:
        weights_dict = dict(zip(tickers,weights))
    # Build returns DataFrame
        result = await run_in_threadpool(processor.run,tickers)
        returns = result["returns"]
        if returns is None or returns.empty:
            logger.warning(f"No returns data found for tickers={tickers}")
            raise HTTPException(status_code=404, detail="No returns data found for requested tickers.")
    
        backtester = Backtester(returns_data=returns,strategy=strategy)
        res = await run_in_threadpool(backtester.run_backtest)
        await run_in_threadpool(db.save_backtest_results,res)
        logger.info(f"Backtest complete and saved | tickers={tickers} | strategy={strategy}")
        return res
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest failed | tickers={tickers} | strategy={strategy} | error={e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


    




    

