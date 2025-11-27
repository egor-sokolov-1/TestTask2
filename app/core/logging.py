import logging
import structlog
from app.core.config import settings

def configure_logging() -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")
    pre_chain = [
        structlog.stdlib.add_log_level,
        timestamper,
    ]

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            *pre_chain,
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )

    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)
    logging.getLogger("aio_pika").setLevel(logging.WARNING)
