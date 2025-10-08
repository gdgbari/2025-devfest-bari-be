from fastapi import APIRouter
from models.responses import OkResponse
from models.requests import RegistrationRequest
from controllers.users import register_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=OkResponse, responses={
    400: {
        "description": "Registration failed - Bad Request",
        "content": {
            "application/json": {
                "examples": {
                    "email_exists": {
                        "summary": "Email already exists",
                        "value": {"detail": "Email already existing: user@example.com"}
                    },
                    "nickname_exists": {
                        "summary": "Nickname already taken",
                        "value": {"detail": "Nickname already existing: john"}
                    },
                    "generic_error": {
                        "summary": "Generic registration error",
                        "value": {"detail": "Registration failed: ..."}
                    }
                }
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
    await register_user(form)
    return OkResponse.detail("User registered successfully")
