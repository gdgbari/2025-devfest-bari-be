from fastapi import APIRouter, Depends
from typing import List
from utils import UserAuthInfo, has_privileges
from utils import db, fire_to_dict
from models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("", response_model=List[User])
async def list_users(_ = Depends(has_privileges(UserRole.STAFF))):
    "Privilaged endpoint to list all users"
    return fire_to_dict(await db.collection("users").get(), id_as_key="uid")

@router.get("/me", response_model=User)
async def get_current_user(user: UserAuthInfo):
    "Endpoint to get info about the current authenticated user"
    return user
