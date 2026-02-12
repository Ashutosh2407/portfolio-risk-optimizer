from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable,Optional,Sequence

import numpy as np
import pandas as pd

from src.data.db_client import DatabaseClient

TRADING_DAYS_PER_YEAR = 252

@dataclass
class ProcessorConfig:
    annualization_factor:int = TRADING_DAYS_PER_YEAR
    # How to handle missing prices across symbols:
    # - "drop": drop any date with any missing symbol price
    # - "ffill": forward-fill then drop remaining NaNs
    missing_prices:str = "drop"


class MarketDataProcessor:
    """
    Docstring for MarketDataProcessor
    """
    def __init__(self,db:DatabaseClient,config: Optional[ProcessorConfig] = None):
        self.db = db
        self.config = config or ProcessorConfig()

    def load_ohlc(self,
        tickers: Sequence[str],
        start: Optional[str | datetime] = None,
        end: Optional[str | datetime] = None,
    ) -> pd.DataFrame:
        """
        LOAD OHLC DATA
        Expects DB table 'ohlc' with columns: ticker,timestamp,close.
        Returns a long dataframe: [timestamp, ticker, close]
        """
        if not tickers:
            raise ValueError("Tickers must not be an empty list.")
        
        tickers_sql = ",".join([f"'{t}'" for t in tickers])

        where = [f"ticker IN ({tickers_sql})"]

        if start is not None:
            where.append(f"timestamp >= '{pd.to_datetime(start).isoformat()}'")
        if end is not None:
            where.append(f"timestamp <= '{pd.to_datetime(end).isoformat()}'")
        
        query = f"""
        Select timestamp, ticker, close
        from ohlc
        WHERE {" AND ".join(where)}
        order by timestamp ASC
        """
        #print(query)
        df = pd.read_sql(query,self.db.engine, parse_dates=["timestamp"])
        return df
    
    def price_matrix(self, ohlc_long: pd.DataFrame) -> pd.DataFrame:
        """
        Convert long OHLC to wide prices matrix: index=timestamp, columns=symbol, values=close
        
        """
        prices = (
            ohlc_long.pivot(index = "timestamp", columns="ticker",values="close")
            .sort_index()
        )

        if self.config.missing_prices == "ffill":
            prices = prices.ffill()
        elif self.config.missing_prices == "drop":
            prices = prices.dropna(axis = 0, how='any')

        return prices
    
    def returns_matrix(self, prices: pd.DataFrame)-> pd.DataFrame:
        """
        Compute simple returns from prices using pct_change().
        pct_change computes fractional change (e.g., 0.01 = 1%).
        
        """
        returns = prices.pct_change(periods=1).dropna(how="any")
        return returns
    
    def risk_matrices(self, returns: pd.DataFrame) -> dict:
        """
        Compute correlation and (annualized) covariance from returns.
        
        """
        corr = returns.corr()
        cov_daily = returns.cov()
        cov_annual = cov_daily * self.config.annualization_factor

        return {
            "corr": corr,
            "cov_daily": cov_daily,
            "cov_annual": cov_annual,
        }

    def run(self, tickers: Sequence[str], start: Optional[str | datetime] = None, 
            end: Optional[str | datetime] =None) -> None:
        """
        End-to-end: DB -> prices -> returns -> cov/corr
    
        """
        ohlc = self.load_ohlc(tickers=tickers, start=start,end = end)
        prices = self.price_matrix(ohlc)
        returns = self.returns_matrix(prices)
        risk = self.risk_matrices(returns)

        return {
            "ohlc_long": ohlc,
            "prices": prices,
            "returns": returns,
            **risk,
        }
    
if __name__ == "__main__":
    db = DatabaseClient()
    processor = MarketDataProcessor(db)

    tickers = [
        "AAPL", "GOOGL", "MSFT", "NVDA", "META",
        "JPM", "BAC", "V", "GS",
        "JNJ", "UNH", "PFE",
        "WMT", "PG", "KO",
        "XOM", "CVX",
        "CAT", "BA",
        "SPY",
    ]

    out = processor.run(tickers = tickers)
    print("prices shape:", out["prices"].shape)
    print("returns shape:", out["returns"].shape)
    print("cov_annual shape:", out["cov_annual"].shape)
    print("Any NaNs in returns?:", out["returns"].isna().any().any())
    # #print("prices :", out["prices"][:4])
    # #print("returns :", out["returns"][:4])
    # #print("corr :", out["corr"]['AAPL'][:])
    # print("cov_daily :", out["cov_daily"]['AAPL'][:])
    # print("cov_annual :", out["cov_annual"]['AAPL'][:])