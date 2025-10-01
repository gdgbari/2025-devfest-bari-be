import uvicorn
import os
import env
from fastapi import FastAPI, Depends, APIRouter
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from env import DEBUG
from utils import load_routers, TrailingSlashMiddleware
from utils import get_current_user
from models.user import RegistrationRequest
from controllers.users import register_user
from models.requests import OkResponse
from fastapi import HTTPException

os.chdir(os.path.dirname(os.path.realpath(__file__)))

@asynccontextmanager
async def lifespan(app: FastAPI):
    load_routers(api) #Dynamic loading of routers in ./routes folder
    app.include_router(api)
    app.include_router(router)
    yield

app = FastAPI(
    debug=DEBUG,
    redoc_url=None,
    docs_url="/api/docs",
    lifespan=lifespan,
    version=env.VERSION,
    title="Devfest Bari Backend"
)

# This middleware allows requests like /path/ to be redirected to /path
# This will require to NEVER define routes with trailing slash (i.e. @app.get("/path/") is not allowed, use @app.get("/path") instead)
app.add_middleware(TrailingSlashMiddleware)

#Auth paths
api = APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_user)],
    responses={
        403: {
            "description": "Authentication Error",
            "content": {
                "application/json": {
                    "example": [
                        {"detail": "Not authenticated"},
                        {"detail": "User not correctly registered"}
                    ],
                    "schema": {"type": "object", "properties": {"detail": {"type": "string"}}}
                }
            }
        },
        401: {
            "description": "You don't have the required privileges to access this resource",
            "content": {
                "application/json": {
                    "example": {"detail": "You don't have the required privileges to access this resource"},
                    "schema": {"type": "object", "properties": {"detail": {"type": "string"}}}
                }
            }
        }
    }
)

router = APIRouter()
@router.post("/api/sign-up", tags=["Auth"], response_model=OkResponse, responses={
    400: {
        "description": "Registration failed",
        "content": {
            "application/json": {
                "example": {"detail": "Registration failed"},
                "schema": {"type": "object", "properties": {"detail": {"type": "string"}}}
            }
        }
    },
    200: {
        "description": "User registered successfully",
        "content": {
            "application/json": {
                "example": {"detail": "User registered successfully"},
                "schema": {"type": "object", "properties": {"detail": {"type": "string"}}}
            }
        }
    }
})
async def signup(form: RegistrationRequest):
    "Endpoint to register a new user"
    if register_user(form):
        return {"detail": "User registered successfully"}
    else:
        raise HTTPException(status_code=400, detail="Registration failed")

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
        
