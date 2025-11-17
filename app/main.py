from fastapi import FastAPI

from api.include_routers import include_routers
from core.exception_handler import register_exception_handlers
from core.logging import setup_logging
from core.middleware import add_middlewares
from core.settings import settings

app = FastAPI(
    title="DevFest Bari 2025 Backend",
    description="APIs for engagement system - GDG Bari",
    debug=settings.debug,
    docs_url="/api/docs",
    version=settings.version,
)

add_middlewares(app)
register_exception_handlers(app)
include_routers(app)
setup_logging()