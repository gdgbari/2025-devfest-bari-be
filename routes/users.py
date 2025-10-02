from fastapi import APIRouter, Depends
from typing import List
from utils import UserAuthInfo, has_privileges
from utils import db, fire_to_dict
from utils import get_current_user
from models.user import User, UserRole

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_current_user)],
    tags=["Users"]
)

@router.get("", response_model=List[User])
async def list_users(_ = Depends(has_privileges(UserRole.STAFF))):
    "List all registered users (Staff only)"
    return fire_to_dict(await db.collection("users").get(), id_as_key="uid")

@router.get("/me", response_model=User)
async def get_me(user: UserAuthInfo):
    "Endpoint to get info about the current authenticated user"
    return user
