"""
Market Data API Client
Handles all API interactions with your market data provider
"""
import os
import requests
import time
from datetime import datetime,timedelta
from typing import List,Dict,Optional
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataClient:
    """Client for fetching market data through various endpoints."""

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        # Setup session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total = 3,
            backoff_factor=1,
            status_forcelist=[429,500,502,503,504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://",adapter)
        self.session.mount("https://",adapter)

        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })

    def get_ohlc(self,symbol,multiplier,timespan,start_date,end_date):
        """
        Fetch OHLC (Open, High, Low, Close) data
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            timeframe: Bar timeframe (1D, 1H, etc.)
        
        Returns:
            List of OHLC bars
        """
        try:
            params = {
                'adjusted':"true",
                'sort':"asc",
                'limit':120
            }
            endpoint = f"{self.base_url}/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{start_date}/{end_date}?adjusted={params['adjusted']}&sort={params['sort']}&limit={params['limit']}&apikey={self.api_key}"
            print(endpoint)
            response = self.session.get(endpoint,timeout=10)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Fetch {len(data.get('bars', []))} bars for {symbol}")
            return data
            #return data.get('bars', [])
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching OHLC for {symbol}: {e}")
            return []


        # m = MarketDataClient(api_key=os.getenv("API_KEY"), base_url= "https://api.massive.com/")
        # s = m.get_ohlc("AAPL",1,"day","2025-11-03","2025-11-28")
        # print(s)

    def get_ticker_snapshot(self,symbol):  #NEED PAID VERSION
        """
        Get current market snapshot for multiple symbols
        
        Args:
            symbols: List of ticker symbols
        
        Returns:
            Dictionary with current quotes
        """
        try:
            endpoint = f"{self.base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{symbol}?apiKey={self.api_key}"
            print(endpoint)
            response = self.session.get(endpoint,timeout = 10)
            response.raise_for_status()

            data= response.json()
            logger.info(f"Fetched snapshot for {symbol} ticker.")

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Unable to fetche snapshot for {symbol}: {e}")
            return {}
        

