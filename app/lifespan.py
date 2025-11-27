from app.core.logging import configure_logging
from app.integrations.rabbitmq.producer import init_producer, shutdown_producer
from app.integrations.rabbitmq.consumer import start_consumer, stop_consumer

async def on_startup(app):
    configure_logging()
    await init_producer(app)
    await start_consumer(app)

async def on_shutdown(app):
    await stop_consumer(app)
    await shutdown_producer(app)