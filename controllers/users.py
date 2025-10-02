from exceptions import FeatureNotImplementedError
from models.user import RegistrationRequest

def register_user(form: RegistrationRequest):
    raise FeatureNotImplementedError(message="User registration not implemented yet")
