import os

import uvicorn
from api.include_routers import include_routers
from core.exception_handler import register_exception_handlers
from core.logging import setup_logging
from core.middleware import add_middlewares
from core.settings import settings
from fastapi import FastAPI

app = FastAPI(
    title="DevFest Bari 2025 Backend",
    description="APIs for engagement system - GDG Bari",
    debug=settings.debug,
    version=settings.version,
)

add_middlewares(app)
register_exception_handlers(app)
include_routers(app)
setup_logging()

if __name__ == "__main__":
    nthreads = len(os.sched_getaffinity(0))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        access_log=True,
        workers=nthreads,
    )
