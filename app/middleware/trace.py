import uuid
import time
import structlog
from typing import Callable
from starlette.types import ASGIApp, Receive, Scope, Send

logger = structlog.get_logger()

class TraceMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # helper to get header
        def get_header(name: str):
            for k, v in scope.get("headers", []):
                if k.decode().lower() == name:
                    return v.decode()
            return None

        trace_id = get_header("x-request-id") or str(uuid.uuid4())
        start_ts = time.time()

        bound = logger.bind(trace_id=trace_id, method=scope.get("method"), path=scope.get("path"))

        bound.info("request.start")

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status = message.get("status")
                duration_ms = int((time.time() - start_ts) * 1000)
                bound.info("request.finish", status=status, duration_ms=duration_ms)
                headers = message.setdefault("headers", [])
                headers.append((b"x-trace-id", trace_id.encode()))
            await send(message)

        await self.app(scope, receive, send_wrapper)
