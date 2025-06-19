from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    provider: str
    
    class Config:
        from_attributes = True

class PriceRequest(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    provider: Optional[str] = None

class PollRequest(BaseModel):
    symbols: list[str] 
    interval: int = Field(60, ge=10, le=3600)  # 10 seconds to 1 hour
    provider: Optional[str] = None

class PollResponse(BaseModel):
    job_id: str
    status: str
    config: dict
    
    class Config:
        from_attributes = True
