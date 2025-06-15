from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from typing import Text
from app.core.database import Base

"""Model for storing polling job configurations"""
class PollingJobConfig(Base):
    __tablename__ = "polling_job_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, nullable=False, index=True)
    symbols = Column(String(50), nullable=False)  # JSON string
    interval = Column(Integer, nullable=False)  # seconds
    provider = Column(String(20), nullable=False)
    status = Column(String(20), nullable=False, default="active")  # active, paused, stopped
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)