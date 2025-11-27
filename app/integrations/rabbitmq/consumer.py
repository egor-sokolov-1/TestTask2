import structlog
from faststream.rabbit import RabbitBroker, RabbitQueue
import asyncio
from app.core.config import settings

logger = structlog.get_logger()
broker: RabbitBroker | None = None

async def start_consumer(app):
    global broker
    
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            broker = RabbitBroker(url=settings.RABBIT_URL)  
            await broker.connect()
            
            @broker.subscriber(RabbitQueue("user_events"))
            async def handler(message: dict):
                """Обработчик сообщений из очереди user_events"""
                try:
                    trace_id = None
                    if hasattr(message, 'headers') and message.headers:
                        trace_id = message.headers.get("trace_id")
                    
                    logger.info("consumer.received", payload=message, trace_id=trace_id)
                    
                except Exception as e:
                    logger.error("consumer.error", error=str(e), payload=message)

            app.state.consumer = broker
            logger.info("consumer.started", attempt=attempt + 1)
            return
            
        except Exception as e:
            logger.warning(
                "consumer.connection_failed", 
                attempt=attempt + 1, 
                max_retries=max_retries,
                error=str(e)
            )
            if attempt < max_retries - 1:
                logger.info("consumer.retrying", delay=retry_delay)
                await asyncio.sleep(retry_delay)
            else:
                logger.error("consumer.failed_all_retries")
                raise

async def stop_consumer(app):
    global broker 
    if broker:
        await broker.close()
        logger.info("consumer.stopped")
        broker = None
