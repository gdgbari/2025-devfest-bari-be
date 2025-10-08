from firebase_admin import auth
from google.cloud.firestore import SERVER_TIMESTAMP
from utils import db
from models.user import UserRole, User
import asyncio
from concurrent.futures import ThreadPoolExecutor
from exceptions import NicknameAlreadyExistsError

# Thread pool for blocking Firebase Auth operations
executor = ThreadPoolExecutor(max_workers=4)

async def save_user(user: User):
    user_data = {
        "email": user.email,
        "name": user.name,
        "surname": user.surname,
        "nickname": user.nickname,
        "role": user.role,
        "group": None
    }

    # Save to Firestore
    await db.collection("users").document(user.uid).set(user_data)


async def create_user(email: str, password: str, name: str, surname: str) -> str:
    """
    Create a user with Firebase Authentication.

    Wraps the synchronous Firebase Admin SDK call in an async executor
    to prevent blocking the event loop.
    """
    loop = asyncio.get_event_loop()

    def _create_user_sync():
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=f"{name} {surname}"
        )
        return user_record.uid

    uid = await loop.run_in_executor(executor, _create_user_sync)
    return uid


async def delete_user(uid: str):
    """Delete user from Firebase Authentication (with async wrapper)"""
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, lambda: auth.delete_user(uid))


async def reserve_nickname(nickname: str):
    """
    Reserve a nickname by creating an empty document.
    The document ID (nickname) is the unique key.
    No need to store uid since we can query users collection.

    Return True when the nickname is reserved
    """
    try:
        await db.collection("nicknames").document(nickname).create({
            "nickname": nickname,
            "reserved_at": SERVER_TIMESTAMP
        })
    except Exception as e:
        if "ALREADY_EXISTS" in str(e) or "already exists" in str(e).lower():
            raise NicknameAlreadyExistsError()
        raise


async def release_nickname(nickname: str):
    """Release nickname reservation"""
    try:
        await db.collection("nicknames").document(nickname).delete()
    except:
        pass
