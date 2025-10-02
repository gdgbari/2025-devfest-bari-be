from fastapi import APIRouter, Depends
from typing import List
from utils import UserAuthInfo, has_privileges
from utils import db, fire_to_dict
from utils import get_current_user
from models.user import User, UserRole

router = APIRouter(
    prefix="/users",
    dependencies=[Depends(get_current_user)],
    tags=["Users"],
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

@router.get("", response_model=List[User])
async def list_users(_ = Depends(has_privileges(UserRole.STAFF))):
    "List all registered users (Staff only)"
    return fire_to_dict(await db.collection("users").get(), id_as_key="uid")

@router.get("/me", response_model=User)
async def get_me(user: UserAuthInfo):
    "Endpoint to get info about the current authenticated user"
    return user
