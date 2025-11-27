from litestar import Litestar
from app.api.routes import route_handlers
from app.middleware.trace import TraceMiddleware
from app.lifespan import on_startup, on_shutdown

app = Litestar(
    route_handlers=route_handlers,
    middleware=[TraceMiddleware],  # ✅ Просто передаем класс без скобок
    on_startup=[on_startup],
    on_shutdown=[on_shutdown],
    openapi_config=None,
)