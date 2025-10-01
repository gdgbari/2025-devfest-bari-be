from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi import Depends
import traceback
import os
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore_async
from google.cloud.firestore import AsyncClient as FirestoreAsyncClient
from google.cloud.firestore import DocumentSnapshot
from google.cloud.firestore_v1.async_query import QueryResultsList
from google.cloud.firestore_v1.async_document import AsyncDocumentReference
from firebase_admin import auth
from models.auth import UserToken
from models.user import User, UserRole
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
ROUTERS_DIR_NAME = "routes"
ROUTERS_DIR = os.path.join(ROOT_DIR, ROUTERS_DIR_NAME)

def list_files(mypath):
    from os import listdir
    from os.path import isfile, join
    return [f for f in listdir(mypath) if isfile(join(mypath, f))]

def list_routers():
    return [ele[:-3] for ele in list_files(ROUTERS_DIR) if ele != "__init__.py" and " " not in ele and ele.endswith(".py")]

def load_routers(app: FastAPI|APIRouter):
    for route in list_routers():
        try:
            module = getattr(__import__(f"{ROUTERS_DIR_NAME}.{route}"), route, None)
            if not module:
                raise Exception()
        except Exception:
            traceback.print_exc()
            raise Exception(f"Error loading router {route}! Check if the file is correct")
        try:
            router = getattr(module, "router", None)
            if not router or not isinstance(router, APIRouter):
                raise Exception()
        except Exception:
            raise Exception(f"Error loading router {route} in every route has to be defined a 'router' APIRouter from fastapi!")
        app.include_router(router)

# Schema di sicurezza per estrarre il token dall'header Authorization
token_auth_scheme = HTTPBearer()

# Dependency per verificare il token
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(token_auth_scheme)) -> UserToken:
    """
    Verifica il token ID di Firebase. Se valido, restituisce i dati dell'utente.
    Altrimenti, solleva un'eccezione HTTPException.
    """
    token = creds.credentials
    try:
        # Verifica il token usando l'SDK di Firebase Admin
        decoded_token = auth.verify_id_token(token)
        return UserToken.model_validate(decoded_token)
    except Exception as e:
        # Gestisce vari errori di token (scaduto, non valido, ecc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token non valido o scaduto: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_user_info(user_token:UserToken = Depends(get_current_user)) -> User:
    additional_info = await db.collection("users").document(user_token.uid).get()
    user_db_info = fire_to_dict(additional_info)
    if not user_db_info:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not correctly registered",
        )
    return User.model_validate({**user_token.model_dump(), **user_db_info})

def has_privileges(min_role: UserRole):
    def _has_privileges(user: User = Depends(get_user_info)):
        if not user.has_privileges(min_role):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have the required privileges to access this resource",
            )
        return True
    return _has_privileges

UserAuthToken = Annotated[UserToken, Depends(get_current_user)]
UserAuthInfo = Annotated[User, Depends(get_user_info)] 

cred = credentials.Certificate("./secrets/firebase-keys.json")
firebase_admin.initialize_app(cred)
db:FirestoreAsyncClient = firestore_async.client()

def fire_to_dict(data: QueryResultsList[DocumentSnapshot], id_as_key: str|None = None):
    "This function converts Firestore documents to dictionaries, replacing document references with their IDs."
    def _doc_to_dict(ele: DocumentSnapshot):
        original_id = ele.id
        ele = ele.to_dict()
        if ele is None:
            return None
        if id_as_key:
            ele[id_as_key] = original_id
        for key, value in ele.items():
            if isinstance(value, AsyncDocumentReference):
                ele[key] = value.id
        return ele
    print("data:", data)
    if isinstance(data, DocumentSnapshot):
        return _doc_to_dict(data)
    elif isinstance(data, list) or isinstance(data, QueryResultsList):
        return [_doc_to_dict(ele) for ele in data]
    
    raise Exception("Data type not supported, requied list (or a single) DocumentSnapshot from firebase")

class TrailingSlashMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if  request.url.path.endswith("/") and len(request.url.path) > 1:
            request.scope["path"] = request.url.path[:-1]
        return await call_next(request)

# auth is used to be exported from here (this to be sure firebase has been initialized before)
__all__ = ["auth", "db", "UserAuthToken", "UserAuthInfo"]