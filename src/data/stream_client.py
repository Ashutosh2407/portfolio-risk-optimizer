import websocket
import os
import json
import logging, threading
from typing import Callable,List, Optional
from datetime import datetime
import time
from dotenv import load_dotenv
from src.utils.logger import get_logger

load_dotenv()

logger = get_logger(__name__)

class StreamClient:
    """WebSocket client for real-time trade data from Finnhub"""
    def __init__(self,api_key,base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.url = f"{self.base_url}?token={self.api_key}"
        self.ws = None
        self.subscribed = set()
        self.running = False
   
    def on_error(self,ws,error):
        """
        Handle Websocket errors.
        
        :param self: Description
        :param ws: Description
        :param error: Description
        """
        logger.error(f"Websocker error: {error}")

    def on_message(self,ws,message):
        """
        Handle incoming WebSocket messages"
        
        :param self: Description
        :param ws: Description
        :param message: Description
        """
        try:
            data = json.loads(message)
            # Finnhub sends trades in this format
            if data.get('type') == "trade":
                trades = data.get('data', [])

                for trade in trades:
                    #PARSE the data
                    trade_info = {    
                        "symbol":trade.get("s"),
                        "price":trade.get("p"),
                        "volume":trade.get("v"),
                        "timestamp":datetime.fromtimestamp(trade.get("t")/1000)
                    }
                    logger.info(f"Trade: {trade_info['symbol']} @ ${trade_info['price']} @ {trade_info['timestamp']}")

        except Exception as e:
            logger.error("Error parsing information: {e}")

    def on_open(self,ws):
        """
        Handle WebSocket connection open
        
        :param self: Description
        :param ws: Description
        """
        logger.info("Establishing Websocket connection ...")
        #Subscribe to symbols
        for symbol in self.subscribed:
            subscribe_message = {
                'type':'subscribe',
                'symbol': symbol
            }
            ws.send(json.dumps(subscribe_message))
            logger.info(f"Subscribed to {symbol}")

    def on_close(self,ws,close_status_code,close_msg):
        """
        Handle WebSocket connection close
        
        :param self: Description
        :param ws: Description
        :param close_status_code: Description
        :param close_msg: Description
        """
        logger.info(f"Websocket closed: {close_status_code} - {close_msg}")
        self.running = False

        

    def subscribe(self, symbols):
        """
        Subscribe to new tickers.
        
        :param self: Description
        :param symbols: Description
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        self.subscribed.update(symbols)

        # If already connected, send subscribe messages
        if self.running and self.ws:
            for symbol in symbols:
                subscribe_message = {
                    'type':'subscribe',
                    'symbol': symbol
                    }  
                self.ws.send(json.dumps(subscribe_message))
                logger.info(f"Subscirbed to {symbol}.") 
    
    def unsubsribe(self, symbols):
        """
        Docstring for unsubsribe
        
        :param self: Description
        :param symbols: Description
        """
        if isinstance(symbols, str):
            symbols = [symbols]
        
        for symbol in symbols:
            self.subscribed.remove(symbol)

            if self.ws and self.running:
                unsubscribe_message = {
                    'type':'unsubscibe',
                    'symbol': symbol
                }
                self.ws.send(json.dumps(unsubscribe_message))
                logger.info(f"Unsubscribed from {symbol}.")

    def start(self):
        logger.info(f"Starting websocket connection...")
        self.running = True
        self.ws = websocket.WebSocketApp(
            self.url,
            on_message = self.on_message,
            on_error=self.on_error,
            on_open=self.on_open,
            on_close=self.on_close
        )
        # Run in a separate thread to not block
        ws_thread = threading.Thread(target=self.ws.run_forever)
        ws_thread.daemon = True
        ws_thread.start()

        logger.info("Websocket thread started ...")

    def stop(self):
        """
        Stop the websocket connection.
        
        :param self: Description
        """
        logger.info("Stopping websocket connection.")
        self.running = False
        if self.ws:
            self.ws.close()


def handle_trade(trade_data):
    """
    Custom callback to process trade data
    You can save to database, update cache, etc.
    """
    print(f"Received trade: {trade_data['symbol']} - ${trade_data['price']}")
    # Add your custom logic here
    # e.g., db_client.insert_trade(trade_data)

if __name__ == "__main__":
    
    # Initialize client with callback
    client = StreamClient(
        api_key=os.getenv("API_KEY_2"),
        base_url=os.getenv("BASE_URL_2")
    )
    
    # Subscribe to symbols
    #portfolio_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'JPM']
    portfolio_symbols = ['BINANCE:BTCUSDT']
    client.subscribe(portfolio_symbols)
    
    # Start streaming
    client.start()
    
    # Keep running (Ctrl+C to stop)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        client.stop()


