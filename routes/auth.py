from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from models.user import RegistrationRequest
from models.requests import OkResponse
from controllers.users import register_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/sign-up", response_model=OkResponse, responses={
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
    """Public endpoint to register a new user"""
    register_user(form)
    return OkResponse.detail("User registered successfully")
