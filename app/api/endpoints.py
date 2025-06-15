from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.core.database import get_db, init_db
from fastapi import Depends
from app.services.abstraction_service import DataProvider, AlphaVantageProvider, FinnhubProvider
from app.schemas.price_schemas import PriceResponse, PriceRequest
from app.services.price_services import PriceService

router = APIRouter(prefix="/prices", tags=["prices"])
@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(symbol: str = Query(..., description="Stock symbol" ), provider: Optional[str] = Query(None, description="Data provider"), db: Session = Depends(get_db)) -> Dict[str, Any]:

    await init_db()
    """
    Get the latest price for a given symbol from the specified provider.
    """
    if not db:
        raise ValueError("Database session is required")
    if not provider:
        provider = "alpha_vantage"
        
    price_service = PriceService()
    response = await price_service.get_latest_price(symbol=symbol, provider=provider, db=db)
    print(f"Response from get_latest_price: {response}")
    return response


    #     from app.services.alpha_vantage import get_latest_price as av_get_latest_price
    #     return await av_get_latest_price(symbol)
    # elif provider == "finnhub":
    #     from app.services.finnhub import get_latest_price as fh_get_latest_price
    #     return await fh_get_latest_price(symbol)
    # else:
    #     return {"error": "Unsupported provider"}