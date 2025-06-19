from fastapi import APIRouter, Query, HTTPException
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from core.database import get_db, init_db
from fastapi import Depends
from services.abstraction_service import DataProvider, AlphaVantageProvider, FinnhubProvider
from schemas.price_schemas import PriceResponse, PollResponse, PollRequest
from services.price_services import PriceService
from services.polling_job_service import PollingJobService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/prices", tags=["prices"])
@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(symbol: str = Query(..., description="Stock symbol" ), provider: Optional[str] = Query(None, description="Data provider"), db: Session = Depends(get_db)) -> Dict[str, Any]:
    
    """
    Get the latest price for a given symbol from the specified provider.
    """
    if not db:
        raise ValueError("Database session is required")
        return {"error": "Internal server error", "status_code": 500}
    if not provider:
        provider = "alpha_vantage"

    price_service = PriceService()
    response = await price_service.get_latest_price(symbol=symbol, provider=provider, db=db)
        
    print(f"Response from get_latest_price: {response}")
    return response


@router.post("/poll", response_model=PollResponse, status_code=202)
async def create_poll_job(
    request: PollRequest,
    db: Session = Depends(get_db)
):
    """Create a polling job for multiple symbols"""
    try:
        service = PollingJobService()
        job_data = await service.create_polling_job(
            symbols=request.symbols,
            interval=request.interval,
            provider=request.provider,
            db=db
        )
        return PollResponse(**job_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "prices"}