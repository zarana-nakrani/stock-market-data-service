from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base

"""Model for storing moving average of stock prices"""
class MovingAverage(Base):
    __tablename__ = "moving_averages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    average_value = Column(Float, nullable=False)
    period = Column(Integer, nullable=False, default=5)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_moving_average_symbol_timestamp', 'symbol', 'timestamp'),
        Index('idx_moving_average_period', 'period'),
    )