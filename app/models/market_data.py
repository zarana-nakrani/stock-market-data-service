from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

"""Models for storing raw market data and processed price points"""

class RawMarketData(Base):
    __tablename__ = "raw_market_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    provider = Column(String(50), nullable=False)
    raw_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_raw_market_data_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_raw_market_data_provider', 'provider'),
    )

    processed_data = relationship("ProcessedPricePoint", back_populates="raw_data")


class ProcessedPricePoint(Base):
    __tablename__ = "processed_price_points"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    provider = Column(String(50), nullable=False)
    raw_response_id = Column(Integer, ForeignKey("raw_market_data.id"), nullable=True)
    
    __table_args__ = (
        Index('idx_processed_price_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_processed_price_provider', 'provider'),
    )

    raw_data = relationship("RawMarketData", back_populates="processed_data")