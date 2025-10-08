from firebase_admin import auth
from models.user import User, UserRole
from models.requests import RegistrationRequest
from repositories.users import save_user, create_user, delete_user, reserve_nickname, release_nickname
from exceptions import EmailAlreadyExistsError, RegistrationError, NicknameAlreadyExistsError

async def register_user(form: RegistrationRequest) -> User:
    """
    Register a new user with Firebase Authentication and store in Firestore.
    """
    uid = None
    nickname_reserved = False
    try:
        await reserve_nickname(form.nickname)
        nickname_reserved = True
        uid = await create_user(form.email, form.password, form.name, form.surname)
        user = User(
            uid = uid,
            email = form.email,
            name = form.name,
            surname = form.surname,
            nickname = form.nickname,
            role = UserRole.ATTENDEE,
            group = None
        )
        await save_user(user)
        return user

    except NicknameAlreadyExistsError:
         # Firebase raises if nickname is not unique
        raise NicknameAlreadyExistsError(f"Nickname already existing: {str(form.nickname)}")

    except auth.EmailAlreadyExistsError:
        # Firebase raises this if email is already in use
        await cleanup(uid, form.nickname, nickname_reserved)
        raise EmailAlreadyExistsError(f"Email already existing: {str(form.email)}")

    except Exception as e:
        # Catch any other errors and wrap them in RegistrationError
        # If we created the auth user but failed to save to Firestore,
        # we should ideally clean up (delete the auth user and nickname)
        # Cleanup
        await cleanup(uid, form.nickname, nickname_reserved)
        raise RegistrationError(f"Registration failed: {str(e)}")

async def cleanup(uid: str, nickname: str, nickname_reserved: bool):
    if uid is not None:
        try:
            await delete_user(uid)
        except:
            pass

    if nickname_reserved:
        try:
            await release_nickname(nickname)
        except:
            pass

