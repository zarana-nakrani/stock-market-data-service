from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic
import json
import logging
from typing import Dict, Any
import asyncio

from core.config import settings

logger = logging.getLogger(__name__)

class KafkaManager:
    def __init__(self):
        self.settings = settings
        self.producer = None
        self.consumer = None
        self.admin_client = None
        
    async def start(self):
        """Initialize Kafka connections"""
        try:
            # Producer configuration
            producer_config = {
                'bootstrap.servers': self.settings.KAFKA_BOOTSTRAP_SERVERS,
                'client.id': 'market-data-producer',
                'acks': 'all',
                'retries': 3,
                'enable.idempotence': True
            }
            
            self.producer = Producer(producer_config)
            
            # Admin client for topic management
            admin_config = {
                'bootstrap.servers': self.settings.KAFKA_BOOTSTRAP_SERVERS
            }
            self.admin_client = AdminClient(admin_config)
            
            # Create topics if they don't exist
            await self._create_topics()
            
            print("Kafka manager started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start Kafka manager: {e}")
            raise
            
    async def _create_topics(self):
        """Create required Kafka topics"""
        topics = [
            NewTopic(
                topic=self.settings.KAFKA_PRICE_EVENTS_TOPIC,
                num_partitions=3,
                replication_factor=1
            ),
            NewTopic(
                topic=self.settings.KAFKA_SYMBOL_AVERAGES_TOPIC,
                num_partitions=3,
                replication_factor=1
            )
        ]
        
        try:
            fs = self.admin_client.create_topics(topics)
            for topic, f in fs.items():
                try:
                    f.result()
                    print(f"Topic {topic} created successfully")
                except Exception as e:
                    if "already exists" not in str(e):
                        logger.error(f"Failed to create topic {topic}: {e}")
        except Exception as e:
            logger.error(f"Error creating topics: {e}")
    
    async def produce_message(self, topic: str, message: Dict[str, Any], key: str = None):
        """Produce message to Kafka topic"""
        try:
            def delivery_report(err, msg):
                if err is not None:
                    logger.error(f'Message delivery failed: {err}')
                else:
                    print(f'Message delivered to {msg.topic()} [{msg.partition()}]')
            
            if not self.producer:
                await self.start()
            
            
            self.producer.produce(
                topic,
                key=key,
                value=json.dumps(message),
                callback=delivery_report
            )
            
            self.producer.flush()
            
        except Exception as e:
            logger.error(f"Failed to produce message: {e}")
            raise
    
    async def stop(self):
        """Stop Kafka connections"""
        if self.producer:
            self.producer.flush()
        if self.consumer:
            self.consumer.close()
        print("Kafka manager stopped")