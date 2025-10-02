import uvicorn
import os
import env
from fastapi import FastAPI, Depends, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from env import DEBUG
from utils import load_routers, TrailingSlashMiddleware
from exceptions import register_exception_handlers

os.chdir(os.path.dirname(os.path.realpath(__file__)))

app = FastAPI(
    debug=DEBUG,
    redoc_url=None,
    docs_url="/api/docs",
    version=env.VERSION,
    title="Devfest Bari Backend"
)

# This middleware allows requests like /path/ to be redirected to /path
# This will require to NEVER define routes with trailing slash (i.e. @app.get("/path/") is not allowed, use @app.get("/path") instead)
app.add_middleware(TrailingSlashMiddleware)
register_exception_handlers(app)

api = APIRouter(prefix="/api")
load_routers(api)
app.include_router(api)

if DEBUG:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == '__main__':
    uvicorn.run(
        "app:app",
        host="",
        port=8888,
        reload=DEBUG,
        access_log=True,
        workers=env.NTHREADS
    )
