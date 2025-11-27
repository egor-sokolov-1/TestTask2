from faststream.rabbit import RabbitBroker
import structlog
import asyncio
from app.core.config import settings

producer: RabbitBroker | None = None
logger = structlog.get_logger()

async def init_producer(app) -> None:
    global producer
    
    max_retries = 10
    retry_delay = 3
    
    for attempt in range(max_retries):
        try:
            producer = RabbitBroker(url=settings.RABBIT_URL)
            await producer.connect()
            app.state.producer = producer
            logger.info("producer.init", attempt=attempt + 1)
            return
        except Exception as e:
            logger.warning(
                "producer.connection_failed", 
                attempt=attempt + 1, 
                max_retries=max_retries,
                error=str(e)
            )
            if attempt < max_retries - 1:
                logger.info("producer.retrying", delay=retry_delay)
                await asyncio.sleep(retry_delay)
            else:
                logger.error("producer.failed_all_retries")
                raise

async def shutdown_producer(app) -> None:
    global producer
    if producer:
        await producer.close()
        logger.info("producer.closed")
        producer = None

async def publish_event(routing_key: str, payload: dict, trace_id: str) -> None:
    if producer is None:
        logger.warning("producer.not_ready", trace_id=trace_id)
        return
    
    headers = {"trace_id": trace_id}
    
    try:
        await producer.publish(
            message=payload,
            routing_key=routing_key,
            headers=headers
        )
        logger.info("published.event", event=routing_key, trace_id=trace_id)
    except Exception as e:
        logger.error(
            "publish.event.failed", 
            event=routing_key, 
            trace_id=trace_id, 
            error=str(e)
        )
        raise
    