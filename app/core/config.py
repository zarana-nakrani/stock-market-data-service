from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@postgres:5432/market_data"
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:9092"
    KAFKA_PRICE_EVENTS_TOPIC: str = "price-events"
    KAFKA_SYMBOL_AVERAGES_TOPIC: str = "symbol-averages"
    # Market Data Providers
    ALPHA_VANTAGE_API_KEY: Optional[str] = "Q2XYCDE5TMJ618FT"
    FINNHUB_API_KEY: Optional[str] = "d170f9hr01qkv5jdpfo0d170f9hr01qkv5jdpfog"
    ALPHA_VANTAGE_API_URL: str = "https://www.alphavantage.co/query"
    FINNHUB_API_URL: str = "https://finnhub.io/api/v1/quote"

    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Market Data Service"

    class Config:
        env_file = ".env"
settings = Settings()