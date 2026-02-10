"""
Historical Data Collector.
Backfills OHLC data from Polygon API into Timescale DB.

"""

import os
import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import List
from market_client import MarketDataClient
from db_client import DatabaseClient
import time

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level = logging.INFO,
    format = '%(asctime)s - %(leveltime)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataCollector:
    """
    Collects and stores historical market data.
    """
    def __init__(self, market_client, db_client):
        self.market_client = market_client
        self.db_client = db_client

    def collect_historical_ohlc(self, symbols, years):
        """
        Fetch and store historical OHLC data for multiple symbols
        
        :param self: Description
        :param symbols: Description
        :param years: Description
        """

        end_date = datetime.now()
        start_date = end_date - timedelta(days = years * 365)

        logger.info(f"Starting backfill for {len(symbols)} symbols")
        logger.info(f"Date range: {start_date.date()} to {end_date.date()}")

        success_count, fail_count = 0,0

        for i,symbol in enumerate(symbols):
            logger.info(f"[{i}/{len(symbols)}] Processing {symbol}...")

            try:
                # Fetch OHLC data from API
                data = self.market_client.get_ohlc(
                    symbol=symbol,
                    multiplier=1,
                    timespan='day',
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
                time.sleep(12)
                if not data or 'results' not in data:
                    logger.warning(f"No data returned for {symbol}.")
                    fail_count+=1
                    continue
                
                # Parse API response to DataFrame
                df = self._parse_polygon_response(data)
                # print(df.columns)
                # print(df.head(5))
                if df.empty:
                    logger.warning(f"Dataframe empty for {symbol}.")
                    fail_count+=1
                    continue

                #Insert rows into db
                self.db_client.insert_ohlc_batch(df)
                logger.info(f"  ✅ Inserted {len(df)} rows for {symbol}")
                success_count += 1
                

            except Exception as e:
                logger.error(f"  ❌ Error processing {symbol}: {e}")
                fail_count += 1
                continue
        
        logger.info("=" * 60)
        logger.info(f"Backfill complete!")
        logger.info(f"  Success: {success_count}/{len(symbols)}")
        logger.info(f"  Failed: {fail_count}/{len(symbols)}")
        logger.info("=" * 60)

    def _parse_polygon_response(self,ohlc_data):

        df= pd.DataFrame(ohlc_data['results'])
        
        if "t" in df.columns:
            df['t'] = pd.to_datetime(df['t'],unit='ms')
            #df.set_index("timestamp", inplace=True)
        
        column_mappings = {
                "v": "volume",
                "vw": "volume_weighted_avg_price",
                "o": "open",
                "c": "close",
                "h": "high",
                "l": "low",
                "t": "timestamp",
                "n": "transactions"             
            }
        
        df.rename(columns=column_mappings, inplace=True)
        df["ticker"] = ohlc_data['ticker']    
        # print(df.columns)
        # print(df.head(5))
        return df[["timestamp","ticker","open","high","low","close","volume","volume_weighted_avg_price","transactions"]]
    
    def collect_single_symbol(self,symbol,years):
        self.collect_historical_ohlc([symbol], years)


def main():
    """Main execution function"""
    logger.info("=" * 60)
    logger.info("HISTORICAL DATA BACKFILL")
    logger.info("=" * 60)

    #Initialize Clients
    market_client = MarketDataClient(
        api_key = os.getenv("API_KEY"),
        base_url=os.getenv("BASE_URL")
        )
    
    db_client = DatabaseClient()

    datacollector = DataCollector(market_client=market_client,db_client=db_client)

    # Define portfolio symbols to backfill
    # Diversified across sectors for portfolio optimization
    portfolio_symbols = [
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
    #remaining_symbols = ['JPM','BAC','WMT','PG','KO','XOM','CVX','CAT','BA','SPY']
    logger.info(f"Portfolio: {len(portfolio_symbols)} symbols")
    logger.info(f"Symbols: {', '.join(portfolio_symbols)}")

    datacollector.collect_historical_ohlc(portfolio_symbols, 3)

    logger.info("\n✅ Backfill script completed!")
    logger.info("Next step: Run processor.py to calculate returns")

if __name__ == "__main__":
    main()




