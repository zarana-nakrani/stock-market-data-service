import logging
from fastapi import BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from models.market_data import RawMarketData, ProcessedPricePoint

from services.abstraction_service import DataProvider, YahooFinanceProvider, AlphaVantageProvider, FinnhubProvider
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from core.config import settings
from services.kafka_client import KafkaManager
import asyncio
from services.streaming_services import StreamingService
# from services.streaming_services import consume_messages

logger = logging.getLogger(__name__)
"""Service for fetching and processing stock prices from various data providers."""
class PriceService:
    def __init__(self):
        self.providers = {
            "yahoo_finance": YahooFinanceProvider(),
            "alpha_vantage": AlphaVantageProvider(settings.ALPHA_VANTAGE_API_KEY),
            "finnhub": FinnhubProvider(settings.FINNHUB_API_KEY)
        }
        self.settings = settings
        self.kafka_manager = KafkaManager() # Initialize Kafka manager
        self.streaming_service = StreamingService() # Initialize streaming service
        self.kafka_started = False
        self.streaming_started = False

    def get_provider(self, provider_name: str) -> DataProvider:
        """Get a data provider by name"""
        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")
        return self.providers[provider_name]
    
    async def get_latest_price(self, symbol: str, provider: str, db: Session, interval: Optional[int] = None) -> Dict[str, Any]:
        try:
            # First check if we have recent data in database
            if not interval:
                latest_price = db.query(ProcessedPricePoint).filter(
                    ProcessedPricePoint.symbol == symbol.upper()
                ).order_by(desc(ProcessedPricePoint.timestamp)).first()
                
                # If we have recent data (within last 5 minutes), return it
                if latest_price and (datetime.utcnow() - latest_price.timestamp).seconds < 300:
                    return {
                        "symbol": latest_price.symbol,
                        "price": latest_price.price,
                        "timestamp": latest_price.timestamp.isoformat() + "Z",
                        "provider": latest_price.provider
                    }
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
            try:
                db.add(raw_data)
                db.commit()
                # db.refresh(raw_data)
            except Exception as e:
                logger.error(f"Error storing raw market data: {e}")
                db.rollback()
                response = {
                    "error": "Failed to store raw market data",
                    "details": str(e),
                    "status_code": 500
                }
                return response

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

            # Publish to Kafka
            kafka_message = {
                "symbol": symbol.upper(),
                "price": price_data["price"],
                "timestamp": price_data["timestamp"],
                "source": provider,
                "raw_response_id": str(raw_data.id)
            }
            
            # Start Kafka manager if not already started
            if not self.kafka_started:
                await self.kafka_manager.start()
                self.kafka_started = True
            
            
            await self.kafka_manager.produce_message(
                topic=settings.KAFKA_PRICE_EVENTS_TOPIC,
                message=kafka_message,
                key=symbol.upper()
            )

            # Start streaming service if not already started
            if not self.streaming_started:
                await self.streaming_service.start_consumer()
                self.streaming_started = True

            return {
                "symbol": symbol.upper(),
                "price": price_data["price"],
                "timestamp": price_data["timestamp"],
                "provider": provider,
                "status_code": 200
            }
        
        except Exception as e:
            db.rollback() 
            response = {
                "error": "Failed to fetch latest price",
                "details": str(e),
                "status_code": 500
            }
            logger.error(f"Error fetching latest price for {symbol} from {provider}: {str(e)}")
            return response
    
    

    """Create a new polling job for multiple symbols"""
    
