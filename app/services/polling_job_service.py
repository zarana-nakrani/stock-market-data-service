from datetime import datetime, timedelta
from models.polling_job_congif import PollingJobConfig
import asyncio
import logging
from models.moving_average import MovingAverage
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from services.price_services import PriceService


logger = logging.getLogger(__name__)
class PollingJobService:
    async def create_polling_job(self, symbols: list[str], interval: int, db:Session, provider: Optional[str] = None ) -> Dict[str, Any]:
        try:
            provider_name = provider 
            job_id = f"poll_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(str(symbols))}"
            
            job = PollingJobConfig(
                job_id=job_id,
                symbols=[s.upper() for s in symbols],
                interval=interval,
                provider=provider_name,
            )
            
            db.add(job)
            db.commit()
            
            asyncio.create_task(self._background_polling_task(
                job_id, 
                symbols,
                interval,
                provider_name,
                db))
            
            return {
                "job_id": job_id,
                "status": "accepted",
                "config": {
                    "symbols": [s.upper() for s in symbols],
                    "interval": interval,
                    "provider": provider_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating polling job: {e}")
            db.rollback()
            raise ValueError(f"Failed to create polling job: {str(e)}")

    
    async def _background_polling_task(self,
        job_id: str, 
        symbols: list, 
        interval: int, 
        provider: str,
        db: Session
    ):
        """
        Background task function that runs after the API response is sent.
        """
        print(f"Starting background polling for job {job_id}")

        logger.info(f"Starting background polling for job {job_id}")
        price_service = PriceService()
        try:
            # Update job status to running
            job = db.query(PollingJobConfig).filter(PollingJobConfig.job_id == job_id).first()
            if job:
                job.status = "running"
                db.commit()
            db.close()
            
            # Poll each symbol once (simplified for demo)
            for symbol in symbols:
                try:
                    print(f"Polling {symbol} for job {job_id}")
                    logger.info(f"Polling {symbol} for job {job_id}")
                    
                    # Fetch market data
                    price_data = await price_service.get_latest_price(symbol, provider, db, interval)
                    print(f"Job {job_id} - {symbol}: ${price_data['price']}")
                    logger.info(f"Job {job_id} - {symbol}: ${price_data['price']}")
                    
                    # In a real implementation, you'd:
                    # 1. Store the data in database
                    # 2. Send to Kafka
                    # 3. Continue polling at intervals
                    
                except Exception as e:
                    logger.error(f"Error polling {symbol} in job {job_id}: {str(e)}")
            
            # Update job status to completed
            job = db.query(PollingJobConfig).filter(PollingJobConfig.job_id == job_id).first()
            if job:
                job.status = "completed"
                db.commit()
            db.close()
            print(f"Background polling completed for job {job_id}")
            logger.info(f"Background polling completed for job {job_id}")
            
        except Exception as e:
            logger.error(f"Background task failed for job {job_id}: {str(e)}")
            
            # Update job status to failed
            try:
                job = db.query(PollingJobConfig).filter(PollingJobConfig.job_id == job_id).first()
                if job:
                    job.status = "failed"
                    db.commit()
                db.close()
            except:
                pass
