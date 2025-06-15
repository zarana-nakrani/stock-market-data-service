from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import yfinance as yf
import requests
import json
from datetime import datetime
from app.core.config import settings

class DataProvider(ABC):
    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        pass

class YahooFinanceProvider(DataProvider):
    def __init__(self):
        self.name = "yahoo_finance"
    
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")
            
            latest = hist.iloc[-1]
            return {
                "symbol": symbol.upper(),
                "price": float(latest['Close']),
                "volume": int(latest['Volume']),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "raw_data": hist.to_json()
            }
        except Exception as e:
            raise ValueError(f"Error fetching data from Yahoo Finance: {str(e)}")

class AlphaVantageProvider(DataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "alpha_vantage"
        self.base_url = settings.ALPHA_VANTAGE_API_URL or "https://www.alphavantage.co/query"
    
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not configured")
        
        params = {
            "function": "time_series_intraday",
            "interval": "1min",
            "symbol": symbol,
            "apikey": self.api_key,
            "outputsize": "compact"  
        }
        
        response = requests.get(self.base_url, params=params)
        data = response.json()

        if "Time Series (1min)" not in data:
            raise ValueError(f"Invalid response from Alpha Vantage: {data}")
        quote = data["Time Series (1min)"]
        latest_timestamp = max(quote.keys())
        latest_data = quote[latest_timestamp]
        response =  {
            "symbol": symbol.upper(),
            "price": float(latest_data["1. open"]),
            "volume": int(latest_data["5. volume"]),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw_data": json.dumps(data)
        }

        return response

        

class FinnhubProvider(DataProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "finnhub"
        self.base_url = "https://finnhub.io/api/v1"
    
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Finnhub API key not configured")
        
        headers = {"X-Finnhub-Token": self.api_key}
        response = requests.get(f"{self.base_url}/quote?symbol={symbol}", headers=headers)
        data = response.json()
        
        if "c" not in data:
            raise ValueError(f"Invalid response from Finnhub: {data}")
        
        return {
            "symbol": symbol.upper(),
            "price": float(data["c"]),  # current price
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "raw_data": json.dumps(data)
        }