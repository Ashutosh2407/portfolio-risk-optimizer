from fastapi import FastAPI, Depends, Query, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .database import get_db
from ..models.backtest import Backtester
from ..models.optimizer import PortfolioOptimizer
from ..models.risk import RiskMetrics
from ..data.db_client import DatabaseClient


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

#Optimize
@app.get("/optimize")
async def optimize():
    pass


#Risk
@app.get("/risk")
async def risk():
    pass

#Backtest
@app.get("/backtest")
async def backtest():
    pass

