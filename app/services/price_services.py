from sqlalchemy.orm import Session
from app.models.market_data import RawMarketData, ProcessedPricePoint
from app.models.moving_average import MovingAverage
from app.models.polling_job_congif import  PollingJobConfig
from app.services.abstraction_service import DataProvider, YahooFinanceProvider, AlphaVantageProvider, FinnhubProvider
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta
from app.core.config import settings

"""Service for fetching and processing stock prices from various data providers."""
class PriceService:
    def __init__(self):
        self.providers = {
            "yahoo_finance": YahooFinanceProvider(),
            "alpha_vantage": AlphaVantageProvider(settings.ALPHA_VANTAGE_API_KEY),
            "finnhub": FinnhubProvider(settings.FINNHUB_API_KEY)
        }
    
    def get_provider(self, provider_name: str) -> DataProvider:
        """Get a data provider by name"""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name]
    
    async def get_latest_price(self, symbol: str, provider: str, db: Session) -> Dict[str, Any]:
        """Get the latest price for a given symbol from the specified provider"""
        data_provider = self.get_provider(provider)
        price_data = await data_provider.get_latest_price(symbol)
        
        # Store raw data
        raw_data = RawMarketData(
            symbol=symbol.upper(),
            provider=provider,
            raw_response=price_data["raw_data"],
            timestamp=datetime.utcnow()
        )
        db.add(raw_data)
        db.commit()
        db.refresh(raw_data)
        
        # Store processed price point
        processed_price = ProcessedPricePoint(
            symbol=symbol.upper(),
            price=price_data["price"],
            timestamp=datetime.utcnow(),
            provider=provider,
            raw_response_id=raw_data.id
        )
        db.add(processed_price)
        db.commit()
        
        return {
            "symbol": symbol.upper(),
            "price": price_data["price"],
            "timestamp": price_data["timestamp"],
            "provider": provider
        }
    
    def calculate_moving_averages(self, symbol: str, db: Session):
        """Calculate moving averages for common periods"""
        periods = [5, 10, 20, 50, 200]
        
        for period in periods:
            # Get last N price points
            prices = db.query(ProcessedPricePoint).filter(
                ProcessedPricePoint.symbol == symbol.upper()
            ).order_by(ProcessedPricePoint.timestamp.desc()).limit(period).all()
            
            if len(prices) >= period:
                avg_price = sum(p.price for p in prices) / len(prices)
                
                # Store moving average
                ma = MovingAverage(
                    symbol=symbol.upper(),
                    period=period,
                    value=avg_price,
                    timestamp=datetime.utcnow()
                )
                db.add(ma)
        
        db.commit()

