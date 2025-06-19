import asyncio
import json
import logging
from typing import List
from confluent_kafka import Consumer, KafkaError
from sqlalchemy.orm import Session
from sqlalchemy import desc
from concurrent.futures import ThreadPoolExecutor
from core.database import SessionLocal, AsyncSessionLocal
from core.config import settings
from models.market_data import ProcessedPricePoint
from models.moving_average import MovingAverage
from fastapi import Depends
from core.database import get_db
import threading

logger = logging.getLogger(__name__)

class StreamingService:
    def __init__(self):
        self.settings = settings
        self.consumer = None
        self.running = False
        
    async def start_consumer(self):
        """Start the streaming service"""
        print("Starting streaming service...")
        consumer_config = {
            'bootstrap.servers': self.settings.KAFKA_BOOTSTRAP_SERVERS,
            'group.id': 'market-data-consumer',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True
        }
        
        self.consumer = Consumer(consumer_config)
        self.consumer.subscribe([self.settings.KAFKA_PRICE_EVENTS_TOPIC])
        self.running = True
        
        self.consumer_thread = threading.Thread(
        target=self._consume_messages,
        daemon=True  # Dies when main program exits
        )
        
        self.consumer_thread.start()

    def _consume_messages(self):
        """Consume messages from Kafka and process them"""
        db = SessionLocal()
        try:   
            while self.running:
                # print("Polling for messages...")
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    # print("No message received, continuing...")
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    else:
                        print(f"Consumer error: {msg.error()}")
                        logger.error(f"Consumer error: {msg.error()}")
                        continue
                message_data = json.loads(msg.value().decode('utf-8'))
                self._process_price_event(message_data, db)
                print(f"Processed message: {message_data}")
                
                    
        except Exception as e:
            logger.error(f"Error processing message: {e}")
                
        finally:
            db.close()
            if self.consumer:
                self.consumer.close()
    
    def _process_price_event(self, message_data: dict, db: Session):
        """Process a price event and calculate moving average"""
        try:
            symbol = message_data['symbol']
            
            # Get last 5 price points for this symbol
            recent_prices = db.query(ProcessedPricePoint).filter(
                ProcessedPricePoint.symbol == symbol
            ).order_by(desc(ProcessedPricePoint.timestamp)).limit(5).all()
            
            print(len(recent_prices))
            if len(recent_prices) >= 5:
                # Calculate 5-point moving average
                prices = 0           
                for recent_price in recent_prices:
                    prices += recent_price.price
                moving_avg = prices / len(recent_prices)

                # Store moving average
                ma_record = MovingAverage(
                    symbol=symbol,
                    average_value=moving_avg,
                    period=5
                )
                
                db.add(ma_record)
                db.commit()
                
                logger.info(f"Calculated 5-point MA for {symbol}: {moving_avg}")
                
        except Exception as e:
            logger.error(f"Error calculating moving average: {e}")
            db.rollback()
    
    async def stop(self):
        """Stop the streaming service gracefully"""
        print("Stopping streaming service...")
        self.running = False
        
        # Wait for consumer thread to finish (with timeout)
        if hasattr(self, 'consumer_thread') and self.consumer_thread.is_alive():
            # Give thread time to finish gracefully
            await asyncio.sleep(2)
            
            # If thread is still alive after timeout, it will be killed when main exits
            # (because it's a daemon thread)
        
        if self.consumer:
            self.consumer.stop()
            self.consumer = None
    
    print("Streaming service stopped")